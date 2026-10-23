import socket

from google import genai
from google.genai import types
from google.genai.errors import APIError
from google.auth.exceptions import DefaultCredentialsError

from .base import (
    BloqueioSeguranca,
    ErroConfiguracao,
    ErroPermanente,
    ErroTemporario,
    PedidoIA,
    ProvedorIA,
    RespostaInvalida,
    RespostaIA,
    TempoEsgotado,
    UsoTokens,
)


def _achatar_esquema(schema):
    defs = schema.pop("$defs", {})

    def resolver(valor):
        if isinstance(valor, dict):
            referencia = valor.get("$ref")
            if referencia:
                nome = referencia.rsplit("/", 1)[-1]
                return resolver(defs[nome])
            return {chave: resolver(item) for chave, item in valor.items()}
        if isinstance(valor, list):
            return [resolver(item) for item in valor]
        return valor

    return resolver(schema)


def _texto_erro(exc):
    return str(exc) or exc.__class__.__name__


class ProvedorGemini(ProvedorIA):
    def __init__(self, config):
        super().__init__(config)
        try:
            opcoes = {"http_options": types.HttpOptions(timeout=config.timeout_s * 1000)}
            if config.modo_acesso == "enterprise":
                opcoes.update(
                    enterprise=True,
                    project=config.projeto_gcp,
                    location=config.regiao,
                )
            else:
                opcoes["api_key"] = config.api_key
            try:
                self.cliente = genai.Client(**opcoes)
            except TypeError:
                if config.modo_acesso != "enterprise":
                    raise
                opcoes.pop("enterprise")
                opcoes["vertexai"] = True
                self.cliente = genai.Client(**opcoes)
        except (TimeoutError, socket.timeout) as exc:
            raise TempoEsgotado(str(exc), modelo=config.modelo) from exc
        except DefaultCredentialsError as exc:
            raise ErroConfiguracao(
                "Não foi possível obter as credenciais do Enterprise.",
                modelo=config.modelo,
            ) from exc
        except Exception as exc:
            raise ErroTemporario(
                f"Não foi possível conectar ao Gemini: {_texto_erro(exc)}",
                modelo=config.modelo,
            ) from exc

    def gerar(self, pedido: PedidoIA) -> RespostaIA:
        contents = [
            types.Content(
                role=mensagem.papel,
                parts=[types.Part(text=mensagem.texto)],
            )
            for mensagem in pedido.historico
        ]
        partes = [
            types.Part.from_bytes(data=arquivo.conteudo, mime_type=arquivo.mime)
            for arquivo in pedido.arquivos
        ]
        partes.append(types.Part(text=pedido.texto))
        contents.append(types.Content(role="user", parts=partes))

        config_kwargs = {
            "system_instruction": pedido.instrucoes,
            "temperature": float(self.config.temperatura),
            "max_output_tokens": self.config.max_tokens_saida,
        }
        if self.config.nivel_raciocinio:
            config_kwargs["thinking_config"] = types.ThinkingConfig(
                thinking_level=self.config.nivel_raciocinio
            )
        if pedido.esquema is not None:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_json_schema"] = _achatar_esquema(
                pedido.esquema.model_json_schema()
            )

        try:
            resposta = self.cliente.models.generate_content(
                model=self.config.modelo,
                contents=contents,
                config=types.GenerateContentConfig(**config_kwargs),
            )
        except (TimeoutError, socket.timeout) as exc:
            raise TempoEsgotado(
                _texto_erro(exc), modelo=self.config.modelo
            ) from exc
        except APIError as exc:
            self._levantar_api_error(exc)
        except (ConnectionError, OSError) as exc:
            raise ErroTemporario(
                _texto_erro(exc), modelo=self.config.modelo
            ) from exc
        except Exception as exc:
            raise ErroTemporario(
                _texto_erro(exc), modelo=self.config.modelo
            ) from exc

        uso = self._obter_uso(resposta)
        motivo = self._obter_motivo(resposta)
        texto = resposta.text or ""
        if motivo in {"SAFETY", "PROHIBITED_CONTENT"}:
            raise BloqueioSeguranca(
                "A resposta foi bloqueada pelo provedor.",
                uso=uso,
                texto_bruto=texto,
                modelo=self.config.modelo,
            )
        if motivo == "MAX_TOKENS":
            erro = RespostaInvalida(
                "A resposta atingiu o limite máximo de tokens.",
                uso=uso,
                texto_bruto=texto,
                modelo=self.config.modelo,
            )
            erro.motivo_fim = motivo
            raise erro

        dados = None
        if pedido.esquema is not None:
            try:
                dados = pedido.esquema.model_validate_json(texto)
            except Exception as exc:
                erro = RespostaInvalida(
                    f"A resposta não corresponde ao esquema: {_texto_erro(exc)}",
                    uso=uso,
                    texto_bruto=texto,
                    modelo=self.config.modelo,
                )
                erro.motivo_fim = motivo
                raise erro from exc

        return RespostaIA(
            texto=texto,
            dados=dados,
            uso=uso,
            modelo=self.config.modelo,
            motivo_fim=motivo,
            id_resposta=getattr(resposta, "response_id", "") or "",
        )

    def _levantar_api_error(self, exc):
        codigo = getattr(exc, "code", None)
        mensagem = _texto_erro(exc)
        if codigo in {401, 403, 404} or (
            codigo == 400
            and any(
                termo in mensagem.lower()
                for termo in ("model", "parameter", "invalid", "modelo", "parâmetro")
            )
        ):
            raise ErroConfiguracao(mensagem, modelo=self.config.modelo) from exc
        if codigo == 429 or (codigo is not None and codigo >= 500):
            raise ErroTemporario(mensagem, modelo=self.config.modelo) from exc
        if codigo is not None and 400 <= codigo < 500:
            raise ErroPermanente(mensagem, modelo=self.config.modelo) from exc
        raise ErroTemporario(mensagem, modelo=self.config.modelo) from exc

    @staticmethod
    def _obter_uso(resposta):
        metadados = getattr(resposta, "usage_metadata", None)
        entrada = getattr(metadados, "prompt_token_count", 0) or 0
        raciocinio = getattr(metadados, "thoughts_token_count", 0) or 0
        saida = (getattr(metadados, "candidates_token_count", 0) or 0) + raciocinio
        return UsoTokens(entrada=entrada, saida=saida, raciocinio=raciocinio)

    @staticmethod
    def _obter_motivo(resposta):
        candidatos = getattr(resposta, "candidates", None) or []
        if not candidatos:
            return ""
        motivo = getattr(candidatos[0], "finish_reason", "")
        return getattr(motivo, "name", None) or str(motivo)
