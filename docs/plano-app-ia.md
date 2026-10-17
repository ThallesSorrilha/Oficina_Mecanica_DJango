## 1. Visão do projeto

O projeto é uma aplicação Django para gestão de uma oficina mecânica.

- `website`: páginas institucionais (`index`, contato e sobre) e autenticação de usuários (cadastro, login, logout e mudança de senha).
- `mecanica`: cadastro e gerenciamento de clientes, carros, serviços, peças, funcionários, mecânicos, consultores técnicos, ordens de serviço e itens de peças/serviços.
- `ia`: porta de entrada de provedores de IA, configuração global e configuração por usuário; o app já foi criado no estado atual do projeto.
- Django: 5.2.11.
- Model de usuário: usuário padrão do Django (`django.contrib.auth.models.User`); não há `AUTH_USER_MODEL` configurado.
- `TIME_ZONE`: `America/Sao_Paulo`.
- `.env`: carregado em `config/settings.py` por `python-dotenv`, usando `load_dotenv()`.
- Variáveis ligadas ao Google encontradas: `GEMINI_API_KEY`.
- Publicação: existe `app.yaml`, configurado para Google App Engine com runtime Python 3.12 e Gunicorn. Não há configuração de Cloud Run identificada.
- ID do projeto Google Cloud: não aparece no repositório.
- Template base: `website/templates/website/base.html`. Blocos existentes: `title`, `extra_css`, `content` e `extra_js`.
- Framework de CSS: Bootstrap 5.3.3 via CDN, com uma folha adicional estática do projeto.
- Chaves primárias: inteiros `BigAutoField` por padrão; não há uso de UUID como chave primária.
- Entidade dona dos dados: não existe entidade de empresa, conta, loja, clínica ou turma. Os dados operacionais pertencem ao domínio da oficina e são relacionados principalmente por `Cliente`, `Carro` e `OrdemServico`.
- Relação usuário-dados: o usuário autenticado não possui relacionamento com `Cliente`, `OrdemServico` ou outra entidade operacional. O app `ia` possui configuração global e uma configuração opcional `ConfiguracaoIAUsuario` ligada individualmente ao usuário.

## 2. O que já existe de IA

- Versão do `google-genai` em `requirements.txt`: dependência declarada sem versão fixada.
- Models de configuração de IA:
  - `ia.models.ConfiguracaoIA`: configuração global única do provedor, modelo, temperatura, tokens, raciocínio, tentativas, timeout, cotas, limites de arquivos/PDF, retenção e preços.
  - `ia.models.ConfiguracaoIAUsuario`: configuração opcional por usuário, com habilitação, limite mensal e observação.
- Chamadas a modelo de IA:
  - `ia/provedores/gemini.py:89`: chamada `self.cliente.models.generate_content`, destinada a gerar texto e, quando solicitado, dados estruturados validados por um schema Pydantic.
- A implementação de `ia/provedores/gemini.py` também cria o cliente Gemini em `ia/provedores/gemini.py:46` e converte histórico/arquivos/configuração para o formato do SDK.
- Não há chamadas de IA fora do app `ia` identificadas na busca solicitada.

## 3. Propostas

- Dono da cota: o usuário autenticado, porque o projeto não possui entidade organizacional ligada aos usuários. A configuração global pode definir o limite padrão, e `ConfiguracaoIAUsuario` pode sobrescrevê-lo ou desabilitar a IA por usuário.
- Chamada atual do provedor Gemini: finalidade `app_ia_geracao`. Referência sugerida: uma referência neutra recebida pelo chamador, como o identificador do fluxo ou registro de negócio. Motivo: a chamada atual é genérica e não deve ser acoplada a uma tela ou entidade específica antes de existir um caso de uso.
- Chatbot futuro: finalidade `app_chatbot`. Referência sugerida: um identificador neutro de conversa/sessão. Motivo: permite agrupar chamadas do mesmo diálogo sem presumir que a conversa pertença a uma ordem de serviço, cliente ou outro registro.
- Para chamadas vinculadas a uma ordem de serviço no futuro: finalidade `app_ordem_servico` e referência `ordem_servico:<id>`. Motivo: mantém a auditoria agrupável sem duplicar relacionamentos específicos em cada chamada.

## 4. Riscos

- A chave `GEMINI_API_KEY` é lida do ambiente, mas o repositório contém um `SECRET_KEY` Django literal em `config/settings.py`; qualquer exposição do repositório deve ser tratada como risco de segredo.
- Não há chave de API no banco; esse padrão deve ser preservado. A chave deve permanecer somente no ambiente/`.env` e nunca ser registrada na auditoria.
- Dados pessoais de clientes podem ser enviados à IA se o chamador incluir dados de `Cliente`, `Carro`, `OrdemServico` ou observações. CPF, telefone, placa, VIN e textos livres exigem minimização ou anonimização.
- Descrições e observações de ordens de serviço podem conter informação sensível ou instruções não confiáveis; há risco de prompt injection e de vazamento para o provedor.
- A auditoria futura poderá armazenar texto bruto, arquivos ou respostas com dados pessoais; retenção, mascaramento e controle de acesso precisam ser definidos antes de registrar esses conteúdos.
- Não há ainda registro de cada chamada, controle efetivo de cota mensal ou proteção contra concorrência; sem isso, múltiplas requisições podem ultrapassar limites.
- O limite global, o limite por usuário, o custo e o modelo estão configuráveis, mas precisam de validação administrativa para evitar valores incompatíveis com orçamento ou capacidade do provedor.
- O `app.yaml` usa App Engine e não informa o ID do projeto; uma configuração de ambiente incorreta pode direcionar custos para a conta errada.
- A configuração global pode ser editada no admin; sem autorização administrativa adequada, usuário não autorizado pode alterar modelo, limites ou preços.
- O provedor atual depende diretamente do SDK Gemini; a porta neutra precisa continuar isolando erros, tokens, motivos de finalização e modelos futuros.

## 5. Perguntas

1. Como você vai acessar o Gemini?
   (a) API Key do Google AI Studio (GEMINI_API_KEY), ou
   (b) Enterprise / Vertex AI, cobrado na conta de faturamento do Google Cloud (ex.: crédito
       educacional). Se for (b), qual o ID do projeto no Google Cloud?

   Sugestão: (a), pois `GEMINI_API_KEY` já é carregada pelo `.env` e o código atual já usa `genai.Client(api_key=...)`; informe o ID do projeto apenas se escolher (b).

2. A cota mensal deve pertencer ao usuário autenticado, sem uma entidade de oficina/empresa compartilhada?

   Sugestão: sim, usar o usuário como dono da cota e manter `ConfiguracaoIAUsuario` como override do limite padrão.

3. A auditoria deve guardar o texto completo de entrada e saída, ou apenas metadados, tokens, duração, situação e referência?

   Sugestão: guardar metadados e uma versão sanitizada/limitada do texto, sem arquivos e sem segredos, para reduzir exposição de dados pessoais.

4. A referência neutra deve ser um texto livre informado pelo chamador ou um par fixo de tipo e identificador?

   Sugestão: usar tipo e identificador opcionais, por exemplo `ordem_servico` e `123`, evitando formatos de string difíceis de consultar.

5. O chatbot futuro deverá compartilhar a mesma cota mensal e a mesma auditoria das chamadas internas?

   Sugestão: sim, compartilhar a porta única, a cota do usuário e o registro de chamadas, diferenciando a finalidade como `app_chatbot`.

6. O texto bruto de prompts e respostas deve ter prazo de retenção configurável ou deve ser descartado após a chamada?

   Sugestão: não armazenar texto/arquivos por padrão; registrar somente metadados e permitir retenção explícita apenas quando houver necessidade operacional.
