## 1. Visão do projeto

O projeto é uma aplicação Django para gestão de uma oficina mecânica.

- `website`: páginas institucionais (`index`, contato e sobre) e autenticação de usuários (cadastro, login, logout e mudança de senha).
- `mecanica`: cadastro, consulta, alteração e exclusão de clientes, carros, serviços, peças, mecânicos, consultores técnicos, ordens de serviço e itens de peças/serviços.
- `ia`: porta de entrada de provedores de IA, configuração global e configuração por usuário; o app já existe no estado atual do projeto.
- Django: `5.2.11`, conforme `requirements.txt`.
- Model de usuário: `django.contrib.auth.models.User`; não há `AUTH_USER_MODEL` configurado em `config/settings.py`.
- `TIME_ZONE`: `America/Sao_Paulo`, em `config/settings.py`.
- Variável ligada ao Google encontrada: `GEMINI_API_KEY`, no `.env` e lida em `ia/provedores/__init__.py`.
- Publicação no Google Cloud: existe `app.yaml`, configurado para Google App Engine com runtime Python 3.12 e Gunicorn. Não foi identificada configuração de Cloud Run. O ID do projeto Google Cloud não aparece no repositório.
- Template base: `website/templates/website/base.html`. Blocos existentes: `title`, `extra_css`, `content` e `extra_js`.
- Framework de CSS: Bootstrap 5.3.3 via CDN, com a folha estática adicional `static/css/estilo.css`.
- Chaves primárias: inteiros (`BigAutoField` por padrão); não há uso de UUID como chave primária.
- Entidade dona dos dados: não existe entidade de empresa, conta, loja, clínica ou turma. Os dados operacionais pertencem ao domínio da oficina e se relacionam principalmente por `Cliente`, `Carro` e `OrdemServico`. O usuário autenticado não possui relacionamento com esses dados operacionais; no app `ia`, `ConfiguracaoIAUsuario` se liga individualmente ao usuário.

## 2. O que já existe de IA

- Versão do `google-genai`: dependência declarada em `requirements.txt` sem versão fixada.
- Models de configuração de IA:
  - `ia.models.ConfiguracaoIA`: configuração global única do provedor, modelo, temperatura, tokens, raciocínio, tentativas, timeout, cotas, limites de arquivos/PDF, retenção e preços.
  - `ia.models.ConfiguracaoIAUsuario`: configuração opcional por usuário, com habilitação, limite mensal e observação.
- Chamada a modelo de IA:
  - `ia/provedores/gemini.py:89`: `self.cliente.models.generate_content`, usada pelo provedor Gemini para gerar texto e, quando solicitado, dados estruturados validados por um schema Pydantic.
- A criação do cliente Gemini ocorre em `ia/provedores/gemini.py:46`.
- Não foram encontradas chamadas a `openai`, `anthropic`, `google.generativeai` ou outras chamadas de modelo fora do app `ia`.

## 3. Propostas

- Dono da cota: o usuário autenticado. O projeto não possui uma entidade organizacional ligada aos usuários; `ConfiguracaoIAUsuario` já oferece o vínculo individual. `ConfiguracaoIA` pode definir o limite padrão, e a configuração por usuário pode sobrescrevê-lo ou desabilitar a IA.
- Chamada existente em `ia/provedores/gemini.py:89`: finalidade sugerida `app_ia_geracao` e referência neutra recebida pelo chamador, preferencialmente um tipo e identificador opcionais. Isso mantém a chamada genérica e permite agrupar a auditoria sem acoplá-la a uma tela ou entidade.
- Chatbot futuro: finalidade sugerida `app_chatbot` e referência neutra de conversa/sessão. Isso permite distinguir o chatbot de chamadas internas e manter a mesma porta de entrada, cota e auditoria.
- Chamadas futuras vinculadas a uma ordem de serviço: finalidade sugerida `app_ordem_servico` e referência composta pelo tipo e identificador da ordem. Isso permite agrupamento sem criar relacionamentos específicos para cada uso de IA.

## 4. Riscos

- `GEMINI_API_KEY` está configurada no `.env`; o arquivo não deve ser versionado nem exposto. A chave não deve aparecer no código, em arquivo JSON ou no Git.
- `config/settings.py` contém um `SECRET_KEY` Django literal; isso é um risco independente para qualquer exposição do repositório.
- Dados pessoais de `Cliente`, `Carro` e `OrdemServico`, como CPF, telefone, placa, VIN e observações, podem ser enviados à IA se o chamador os incluir.
- Textos livres de ordens de serviço podem conter instruções não confiáveis, criando risco de prompt injection e de vazamento de dados.
- Registrar prompts, respostas, arquivos ou conteúdo bruto na auditoria pode aumentar a exposição de dados pessoais e segredos; retenção e mascaramento precisam ser definidos.
- Ainda não há registro efetivo de cada chamada, controle de cota mensal ou proteção contra concorrência; chamadas simultâneas podem ultrapassar limites.
- Modelo, preços, limites e cotas editáveis precisam de autorização administrativa e validação para evitar configurações incompatíveis com orçamento ou capacidade do provedor.
- O `app.yaml` não informa o ID do projeto Google Cloud; uma configuração de ambiente incorreta pode direcionar custos para a conta errada.
- O provedor atual depende diretamente do SDK Gemini; a porta neutra deve continuar isolando erros, tokens, motivos de finalização e futuros provedores.

## 5. Perguntas

1. Como você vai começar acessando o Gemini? (Os dois modos ficam prontos e você pode trocar depois na tela Configuração da IA; a resposta define o valor inicial e os passos que vou te passar.)
   (a) API Key do Google AI Studio, ou
   (b) Enterprise / Vertex AI, cobrado na conta de faturamento do Google Cloud (ex.: crédito educacional). Se for (b), qual o ID do projeto no Google Cloud?

   Sugestão: começar com (a), porque `GEMINI_API_KEY` já existe no `.env` e o código atual já cria o cliente com uma chave; manter o modo Enterprise preparado para a troca posterior.

2. A cota mensal deve pertencer ao usuário autenticado, sem uma entidade de oficina/empresa compartilhada?

   Sugestão: sim, usar o usuário como dono da cota e manter `ConfiguracaoIAUsuario` como override do limite padrão.

3. A auditoria deve guardar o texto completo de entrada e saída, ou apenas metadados, tokens, duração, situação e referência?

   Sugestão: guardar somente metadados, tokens, duração, situação e referência, sem texto completo nem arquivos por padrão.

4. A referência neutra deve ser um texto livre informado pelo chamador ou um par fixo de tipo e identificador?

   Sugestão: usar tipo e identificador opcionais, para manter consultas e agrupamentos consistentes sem acoplar a auditoria a um único model.

5. O chatbot futuro deverá compartilhar a mesma cota mensal e a mesma auditoria das chamadas internas?

   Sugestão: sim, compartilhar a porta única, a cota do usuário e o registro de chamadas, diferenciando a finalidade como `app_chatbot`.

6. O texto bruto de prompts e respostas deve ter prazo de retenção configurável ou deve ser descartado após a chamada?

   Sugestão: não armazenar texto bruto nem arquivos por padrão; permitir retenção explícita somente quando houver necessidade operacional e regra definida.

## 6. Decisões

1. Começar com o modo `api_key` (Google AI Studio / Gemini Developer API), mantendo o modo `enterprise` preparado para troca posterior.
