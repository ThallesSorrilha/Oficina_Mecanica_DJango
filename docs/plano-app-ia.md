## 1. Visão do projeto

O projeto é uma aplicação Django para gestão de uma oficina mecânica.

- `website`: páginas institucionais (`index`, contato e sobre) e autenticação de usuários (cadastro, login, logout e mudança de senha).
- `mecanica`: cadastro, consulta, alteração e exclusão de clientes, carros, serviços, peças, mecânicos, consultores técnicos, ordens de serviço e itens de peças/serviços.
- `ia`: porta de entrada de provedores de IA (`chamar_ia`), configuração global única (`ConfiguracaoIA`), configuração por usuário (`ConfiguracaoIAUsuario`), auditoria (`RequisicaoIA`), consumo mensal (`ConsumoIA`), cota, preparo de arquivos e telas em `/ia/`.
- Django: `5.2.11`, conforme `requirements.txt`.
- Model de usuário: `django.contrib.auth.models.User`; não há `AUTH_USER_MODEL` configurado em `config/settings.py`.
- `TIME_ZONE`: `America/Sao_Paulo`, em `config/settings.py`.
- Variável ligada ao Google: o arquivo `.env` contém o nome `GEMINI_API_KEY`, mas o código não a lê mais. A chave do modo `api_key` fica em `ConfiguracaoIA.api_key`, preenchida pela tela `/ia/configuracao/` ou pelo Admin. O `.env` é ignorado pelo Git (`.gitignore:2`).
- Publicação no Google Cloud: existe `app.yaml`, configurado para Google App Engine com runtime Python 3.12 e Gunicorn. Não foi identificada configuração de Cloud Run. O ID do projeto Google Cloud não aparece no repositório.
- Templates base: `website/templates/website/base.html` (blocos `title`, `extra_css`, `content`, `extra_js`) e `website/templates/website/modelo.html` (blocos `hero`, `conteudo`), usado pelas telas de `mecanica` e `ia`.
- Framework de CSS: Bootstrap 5.3.3 via CDN, com `static/css/estilo.css`; formulários com django-crispy-forms no padrão `bootstrap5`.
- Chaves primárias: inteiros (`BigAutoField` por padrão); não há uso de UUID como chave primária.
- Entidade dona dos dados: não existe entidade de empresa, conta, loja, clínica ou turma. Os dados operacionais pertencem ao domínio da oficina e se relacionam principalmente por `Cliente`, `Carro` e `OrdemServico`. O usuário autenticado não possui relacionamento com esses dados operacionais; no app `ia`, `ConfiguracaoIAUsuario` se liga individualmente ao usuário.

## 2. O que já existe de IA

- Versão do `google-genai`: dependência declarada em `requirements.txt:13`, sem versão fixada. Também constam `Pillow` (`requirements.txt:15`) e `pypdf` (`requirements.txt:16`).
- Models de configuração e consumo de IA:
  - `ia/models.py:7` (`ConfiguracaoIA`): configuração global única com provedor, modo de acesso, chave, projeto, região, modelo, tokens, raciocínio, tentativas, timeout, cotas, limites e preços.
  - `ia/models.py` (`ConfiguracaoIAUsuario`): habilitação, limite mensal próprio e observação por usuário.
  - `ia/models.py` (`RequisicaoIA`): auditoria de cada tentativa, sem prompt completo nem arquivos.
  - `ia/models.py` (`ConsumoIA`): consumo mensal por dono da cota.
- Chamadas a modelo de IA:
  - `ia/provedores/gemini.py:57` e `ia/provedores/gemini.py:63`: criação do cliente `genai.Client`, no modo `api_key` ou Enterprise/Vertex AI.
  - `ia/provedores/gemini.py:108`: `self.cliente.models.generate_content`, que gera texto e, quando há esquema, dados estruturados validados por Pydantic.
  - `ia/chamada.py:113`: `provedor.gerar(pedido)`, chamado por `chamar_ia` (`ia/chamada.py:67`).
  - `ia/chamada.py:183`: `testar_conexao` chama `chamar_ia` com esquema mínimo para validar a configuração (definida em `ia/chamada.py:172`).
- Não há chamadas de IA fora do app `ia`. Não foram encontradas referências a `openai`, `anthropic` ou `google.generativeai`.

## 3. Propostas

- Dono da cota: o usuário autenticado (`ConsumoIA.dono`), conforme a decisão registrada. `ConfiguracaoIA.limite_mensal_usuario` define o padrão, e `ConfiguracaoIAUsuario.limite_mensal` pode sobrescrevê-lo ou desabilitar a IA.
- Chamada de geração (`ia/provedores/gemini.py:108`, chamada por `ia/chamada.py:113`): finalidade sugerida `app_ia_geracao`; referência `(tipo, id)` opcional, informada pelo chamador. O motivo é manter a chamada genérica e agrupável.
- Teste de conexão (`ia/chamada.py:183`): finalidade `teste_conexao`, sem referência. Deve continuar separada de uso de negócio para não poluir o consumo operacional.
- Chatbot futuro: finalidade sugerida `app_chatbot`; referência `(tipo, id)` apontando para a conversa/sessão, quando existir um model dela. Isso separa o chatbot das chamadas internas, mantendo a mesma porta, cota e auditoria.
- Chamadas ligadas a uma ordem de serviço no futuro: finalidade sugerida `app_ordem_servico`; referência `(OrdemServico, id)`. O agrupamento usa o `ContentType` já previsto em `RequisicaoIA.referencia_tipo`, sem campos específicos por uso.

## 4. Riscos

- Chave em arquivo local: `GEMINI_API_KEY` continua no `.env`. O arquivo é ignorado pelo Git (`.gitignore:2`), mas o segredo fica em texto puro; qualquer cópia, print ou compartilhamento o expõe. Sugestão: remover a variável do `.env` depois de confirmar a chave do banco.
- Chave no banco: `ConfiguracaoIA.api_key` é texto simples no PostgreSQL. Quem tiver acesso ao banco, a backups ou ao superusuário pode lê-la. O campo é exibido com `render_value=True` no Admin e em `/ia/configuracao/`.
- Segredo versionado: `config/settings.py:30` contém um `SECRET_KEY` literal e `config/settings.py:33` mantém `DEBUG = True`. Isso é um risco independente de exposição do repositório.
- Dados pessoais: `Cliente`, `Carro` e `OrdemServico` têm CPF, telefone, placa e observações. Se o chamador incluir esses dados em `PedidoIA.texto`, eles vão ao provedor externo. O `contexto_hash` identifica o conteúdo, mas não o protege.
- Prompt injection: textos livres de `OrdemServico` podem conter instruções que alteram a resposta da IA.
- Auditoria: `RequisicaoIA.resposta` guarda até 20.000 caracteres da resposta, e `RequisicaoIA.erro` guarda mensagens de erro. Podem conter dados pessoais devolvidos pelo modelo. `reter_requisicoes_dias` existe, mas nenhum processo o aplica.
- Limite sem bloqueio atômico: a cota é verificada antes da chamada e o consumo é gravado depois. Chamadas simultâneas do mesmo usuário podem ultrapassar o limite.
- Teto e preços: `limite_mensal_sistema`, `preco_entrada_milhao` e `preco_saida_milhao` são editáveis pelo superusuário; valores incorretos distorcem o controle de custo.
- Autorização: as telas `/ia/` usam `is_superuser`; não há grupo específico nem registro de quem alterou a configuração.
- Publicação: `app.yaml` não informa projeto Google Cloud. `ConfiguracaoIA.projeto_gcp` só é usado no modo Enterprise; projeto ou credencial errados podem gerar custo em outra conta.

## 5. Perguntas

1. Como você vai começar acessando o Gemini? (Os dois modos ficam prontos e você pode trocar depois na tela Configuração da IA; a resposta define o valor inicial e os passos que vou te passar.)
   (a) API Key do Google AI Studio, ou
   (b) Enterprise / Vertex AI, cobrado na conta de faturamento do Google Cloud (ex.: crédito educacional). Se for (b), qual o ID do projeto no Google Cloud?

   Sugestão: começar com (a), porque é a decisão já registrada em "## 6. Decisões" e o código lê a chave de `ConfiguracaoIA.api_key`.

2. A cota mensal deve continuar pertencendo ao usuário autenticado, sem uma entidade de oficina/empresa compartilhada?

   Sugestão: sim, manter o usuário como dono da cota, como já implementado em `ia/cota.py`.

3. A auditoria deve continuar guardando até 20.000 caracteres da resposta, ou somente metadados, tokens, duração, situação, motivo de fim e referência?

   Sugestão: remover o texto da resposta da auditoria e manter somente os metadados.

4. Qual deve ser o prazo de retenção de `RequisicaoIA` (`reter_requisicoes_dias`), e quem executa a limpeza?

   Sugestão: 60 dias, com um comando de limpeza executado manualmente pelo superusuário, sem exigir agendador externo.

5. A chave da API deve permanecer em texto no banco (`ConfiguracaoIA.api_key`), ou deve ser lida somente do `.env`?

   Sugestão: manter em `ConfiguracaoIA.api_key`, que é o contrato atual, e remover `GEMINI_API_KEY` do `.env` depois de confirmar que a chave do banco funciona.

## 6. Decisões

1. Começar com o modo `api_key` (Google AI Studio / Gemini Developer API), mantendo o modo `enterprise` preparado para troca posterior.
