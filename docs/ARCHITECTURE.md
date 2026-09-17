# JuriScan — Architecture Baseline

## 1. Visão geral

O JuriScan é uma aplicação local-first para Windows voltada à consulta, organização e monitoramento de processos judiciais.

A aplicação possui diferentes formas de execução:

* interface web local com Streamlit;
* launcher desktop empacotado com PyInstaller;
* API HTTP com FastAPI;
* jobs independentes para monitoramento e envio de relatórios;
* automação no Windows por meio do Task Scheduler.

O projeto utiliza uma arquitetura baseada em serviços, providers de fontes processuais, repositories de persistência e componentes de interface separados por responsabilidade.

Esta documentação representa o estado arquitetural atual do projeto e não implica proposta de refatoração.

---

## 2. Visão geral do fluxo

### 2.1 Consulta interativa

```text
Streamlit
    ↓
UI
    ↓
services/consulta_service.py
    ↓
bases/registry.py
    ↓
provider
    ↓
DataJud / ESAJ / eproc
    ↓
modelo normalizado
    ↓
repositories / histórico
    ↓
SQLite
```

A interface recebe os dados fornecidos pelo usuário e delega a consulta ao serviço de consulta.

O serviço utiliza o registry de bases para selecionar o provider apropriado.

Cada provider consulta sua fonte externa e converte o resultado para um modelo processual normalizado utilizado pelo restante da aplicação.

Quando o histórico local está habilitado, processos e movimentações podem ser persistidos no SQLite.

---

## 3. Monitoramento automatizado

O fluxo de monitoramento é executado de forma independente da interface Streamlit.

```text
Windows Task Scheduler
    ↓
script .bat
    ↓
job
    ↓
processos monitorados
    ↓
consulta processual
    ↓
detecção de novas movimentações
    ↓
persistência de histórico
    ↓
relatório
    ↓
e-mail
```

Os processos monitorados são carregados da persistência local própria de monitoramento.

O job consulta os processos, compara as movimentações obtidas com o histórico persistido e identifica movimentações novas.

Quando existem novidades, podem ser gerados relatórios CSV e enviados relatórios por e-mail, conforme a configuração local.

---

## 4. Pontos de entrada

### 4.1 `app.py`

Principal ponto de entrada da interface Streamlit.

Responsabilidades:

* configurar logging;
* carregar configurações;
* inicializar o banco local quando habilitado;
* executar o bootstrap da estrutura local;
* configurar a página Streamlit;
* criar as abas da aplicação;
* delegar a renderização para os módulos de `ui/`.

As principais áreas da interface são:

* Consulta;
* Histórico local;
* Monitorados;
* Clientes;
* Automação.

---

### 4.2 `src/consulta_processos/desktop_launcher.py`

Ponto de entrada utilizado pela distribuição desktop.

Responsabilidades:

* localizar o `app.py`;
* iniciar o Streamlit;
* executar o servidor apenas localmente;
* utilizar `127.0.0.1` na porta `8501`;
* aguardar a inicialização do servidor;
* abrir o navegador automaticamente;
* oferecer compatibilidade com execução normal e aplicação empacotada por PyInstaller.

O launcher não implementa regras de negócio.

---

### 4.3 `src/consulta_processos/api.py`

Ponto de entrada da API FastAPI.

Endpoints atuais:

```text
GET /health
POST /consultar-processos
```

A API reutiliza o mesmo serviço de consulta utilizado por outras partes da aplicação.

Ela também converte exceções conhecidas da aplicação em respostas HTTP apropriadas.

---

## 5. Camada de interface

Diretório:

```text
src/consulta_processos/ui/
```

A interface Streamlit é dividida em módulos especializados.

Estrutura atual:

```text
ui/
├── automacao_tab.py
├── cached_services.py
├── clientes_tab.py
├── consulta_tab.py
├── historico_tab.py
└── monitorados_tab.py
```

Cada módulo concentra a renderização e interação de uma área funcional da aplicação.

A camada de UI deve delegar lógica de consulta e persistência para os componentes apropriados sempre que possível.

---

## 6. Serviço de consulta

Arquivo principal:

```text
src/consulta_processos/services/consulta_service.py
```

Responsabilidades:

* receber o modelo de entrada da consulta;
* solicitar consultas ao registry de providers;
* filtrar movimentações conforme a data-base;
* converter retornos dos providers para os modelos internos;
* consolidar os resultados.

O serviço atua como intermediário entre os consumidores da aplicação e as implementações específicas das fontes processuais.

---

## 7. Providers processuais

Diretório:

```text
src/consulta_processos/bases/
```

Estrutura atual:

```text
bases/
├── base.py
├── catalog.py
├── datajud.py
├── eproc.py
├── esaj.py
├── registry.py
└── service.py
```

Os providers encapsulam integrações específicas com as diferentes fontes processuais.

As fontes atualmente representadas são:

* DataJud;
* ESAJ;
* eproc.

### `base.py`

Define estruturas e contratos compartilhados pelos providers.

### `catalog.py`

Mantém o catálogo de fontes processuais conhecidas.

### `registry.py`

Resolve o provider apropriado a partir do identificador da base.

O fluxo conceitual é:

```text
base solicitada
    ↓
registry
    ↓
catalog
    ↓
factory
    ↓
provider
```

### `datajud.py`, `esaj.py` e `eproc.py`

Contêm as implementações específicas de consulta das respectivas fontes.

---

## 8. Modelos

Arquivo principal:

```text
src/consulta_processos/models.py
```

O projeto utiliza modelos Pydantic para representar entradas e saídas normalizadas da aplicação.

Esses modelos permitem que UI, API, serviços e jobs trabalhem com estruturas de dados consistentes, independentemente da fonte processual consultada.

---

## 9. Persistência

O projeto utiliza atualmente mais de uma estratégia de persistência local.

### 9.1 SQLite

Arquivo de infraestrutura:

```text
src/consulta_processos/database.py
```

Por padrão, o banco é criado em:

```text
data/consulta_processos.db
```

O caminho pode ser sobrescrito por configuração.

As tabelas atualmente criadas são:

```text
processos_cadastrados
movimentacoes_consultadas
```

#### `processos_cadastrados`

Armazena:

* número do processo;
* base;
* cliente;
* apelido;
* data de criação.

#### `movimentacoes_consultadas`

Armazena:

* processo;
* base;
* descrição;
* data da movimentação;
* comentário;
* data de criação.

Existe restrição de unicidade destinada a impedir duplicação da mesma movimentação.

---

## 10. Repositories

Os repositories encapsulam operações de persistência.

### `process_repository.py`

Responsável principalmente por:

* cadastro de processos;
* consulta de clientes;
* consulta de processos por cliente;
* atualização de apelidos;
* comentários em movimentações;
* remoção de processos.

### `history_repository.py`

Responsável pelo histórico de movimentações e identificação de novidades já conhecidas ou ainda não persistidas.

### `monitoring_repository.py`

Responsável pelo estado dos processos monitorados.

Atualmente essa persistência não utiliza SQLite.

Os monitorados são armazenados em:

```text
config/processos_monitorados.json
```

Esse arquivo é estado local da aplicação e é criado automaticamente quando necessário.

---

## 11. Jobs

Diretório:

```text
src/consulta_processos/jobs/
```

### `monitorados_report.py`

Executa o fluxo de consulta dos processos monitorados.

Principais responsabilidades:

* carregar processos monitorados;
* montar o payload de consulta;
* consultar os providers;
* identificar movimentações novas;
* salvar histórico;
* gerar relatórios CSV.

Os relatórios são gravados na estrutura local:

```text
reports/
```

Podem existir:

```text
reports/
├── relatorio_completo_YYYY-MM-DD_HH-MM.csv
└── clientes/
    └── Cliente/
        └── Processo/
            └── relatorio_YYYY-MM-DD_HH-MM.csv
```

Esses arquivos são outputs de execução e não fazem parte do código-fonte.

### `email_monitorados_report.py`

Executa o fluxo relacionado ao envio do relatório por e-mail.

O envio depende da configuração SMTP definida no ambiente local.

---

## 12. E-mail

Arquivo principal:

```text
src/consulta_processos/email_service.py
```

O serviço encapsula o envio de mensagens por SMTP.

As credenciais e configurações são obtidas do ambiente local e não devem ser versionadas.

---

## 13. Configuração

Arquivo principal:

```text
src/consulta_processos/settings.py
```

A aplicação utiliza `pydantic-settings` para configuração.

As configurações locais podem ser definidas em:

```text
.env
```

O arquivo `.env` não deve ser versionado.

O repositório mantém:

```text
.env.example
```

como referência de configuração.

---

## 14. Paths locais

Arquivo:

```text
src/consulta_processos/paths.py
```

Esse módulo centraliza a resolução dos principais caminhos utilizados durante a execução.

Estrutura local padrão:

```text
data/
config/
logs/
reports/
.env
```

Principais arquivos derivados:

```text
data/consulta_processos.db
config/processos_monitorados.json
logs/juriscan.log
.env
```

Os diretórios são relativos à pasta da aplicação.

Quando executado por meio do binário empacotado, a pasta do executável é utilizada como referência.

---

## 15. Bootstrap

Arquivo:

```text
src/consulta_processos/bootstrap.py
```

Responsável pela preparação da aplicação na primeira execução.

O bootstrap:

* cria `data/`;
* cria `config/`;
* cria `logs/`;
* cria `reports/`;
* cria `.env` com configuração padrão quando inexistente;
* cria `config/processos_monitorados.json` quando inexistente;
* inicializa o SQLite.

Isso permite que a distribuição portátil seja utilizada sem preparação manual prévia da estrutura de dados.

---

## 16. Logging

Arquivo:

```text
src/consulta_processos/logging_config.py
```

Os logs locais da aplicação são gravados em:

```text
logs/juriscan.log
```

O diretório `logs/` contém estado gerado durante a execução e não deve ser versionado.

---

## 17. Automação no Windows

O projeto possui scripts destinados à execução e integração com o Windows Task Scheduler.

Diretório:

```text
scripts/
```

Entre as responsabilidades dessa camada estão:

* iniciar a aplicação;
* iniciar a API;
* executar jobs;
* instalar tarefas agendadas;
* remover tarefas agendadas.

A automação é externa à UI e permite que o monitoramento funcione mesmo sem interação manual com o Streamlit.

---

## 18. Packaging

O projeto utiliza PyInstaller para gerar uma distribuição local para Windows.

Arquivo de configuração:

```text
JuriScan.spec
```

O launcher desktop é utilizado como entrypoint da distribuição.

O processo de build gera uma aplicação do tipo `onedir`.

O projeto também possui scripts e documentação para criação de distribuição portátil em ZIP.

Artefatos de build como:

```text
build/
dist/
```

não fazem parte do código-fonte versionado.

---

## 19. Dependências

O projeto atualmente mantém:

```text
pyproject.toml
requirements.txt
```

### `pyproject.toml`

É a fonte declarativa das dependências diretas do projeto.

Também registra as ferramentas de desenvolvimento no grupo opcional:

```text
dev
```

que inclui atualmente:

* pytest;
* Ruff;
* PyInstaller.

O arquivo também contém as configurações de pytest e Ruff.

### `requirements.txt`

Mantém um snapshot pinado do ambiente utilizado para reprodução da instalação.

Ele inclui dependências diretas e transitivas com versões conhecidas.

As dependências não devem ser atualizadas indiscriminadamente apenas para acompanhar versões mais recentes.

---

## 20. Testes e qualidade

Os testes ficam em:

```text
tests/
```

Framework:

```text
pytest
```

A configuração atual determina:

```text
pythonpath = ["src"]
testpaths = ["tests"]
```

A qualidade estática é verificada com Ruff.

Comandos principais:

```bash
pytest -v
ruff check .
ruff format --check .
```

Na baseline do Bloco 1:

```text
pytest: 36 testes passando
ruff check: passando
ruff format --check: 48 arquivos ainda necessitam formatação
```

A pendência de formatação é estado conhecido da baseline e não representa regressão introduzida pela documentação.

---

## 21. Estrutura arquitetural resumida

```text
                         ┌─────────────────┐
                         │   Streamlit UI  │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │ ConsultaService │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │ Provider Registry│
                         └────────┬────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
           ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
           │ DataJud │       │  ESAJ   │       │  eproc  │
           └────┬────┘       └────┬────┘       └────┬────┘
                └─────────────────┼─────────────────┘
                                  │
                         ┌────────▼────────┐
                         │ Modelos internos│
                         └────────┬────────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
              ┌──────▼──────┐          ┌──────▼──────┐
              │ Repositories│          │    Jobs     │
              └──────┬──────┘          └──────┬──────┘
                     │                         │
              ┌──────▼──────┐          ┌──────▼──────┐
              │   SQLite    │          │Reports/Email│
              └─────────────┘          └─────────────┘
```

---

## 22. Persistência atual resumida

| Informação            | Persistência atual               |
| --------------------- | -------------------------------- |
| Processos cadastrados | SQLite                           |
| Movimentações         | SQLite                           |
| Clientes              | SQLite, associados aos processos |
| Apelidos              | SQLite                           |
| Comentários           | SQLite                           |
| Processos monitorados | JSON local                       |
| Configuração          | `.env`                           |
| Logs                  | arquivo local                    |
| Relatórios            | CSV local                        |

---

## 23. Dívidas técnicas confirmadas

### 23.1 Persistência de monitorados separada

Os processos monitorados utilizam atualmente:

```text
config/processos_monitorados.json
```

enquanto outros dados da aplicação utilizam SQLite.

Essa diferença está documentada como estado atual e não é corrigida neste bloco.

### 23.2 Dois manifests relacionados a dependências

O projeto mantém simultaneamente:

```text
pyproject.toml
requirements.txt
```

Os papéis foram definidos como:

* `pyproject.toml`: declaração das dependências diretas e configuração de desenvolvimento;
* `requirements.txt`: snapshot pinado utilizado para reprodução do ambiente.

### 23.3 Formatação Ruff ainda não normalizada

A baseline atual possui arquivos que ainda seriam reformatados por:

```bash
ruff format .
```

Essa normalização não foi realizada no Bloco 1 para evitar uma alteração ampla e essencialmente estética misturada às mudanças de baseline.

---

## 24. Decisões deliberadamente adiadas

Esta baseline não altera:

* persistência dos monitorados;
* estrutura dos repositories;
* arquitetura dos providers;
* estrutura geral de diretórios;
* banco de dados;
* framework da UI;
* mecanismo de automação;
* formato dos relatórios;
* estratégia de deploy;
* funcionalidades de negócio.

Esses temas devem ser avaliados nos blocos posteriores do projeto.

---

## 25. Objetivo desta documentação

Este documento serve como referência do estado arquitetural conhecido do JuriScan ao final da etapa de baseline.

Antes de alterações estruturais futuras, ele permite identificar:

* responsabilidades existentes;
* fluxos atuais;
* formas de persistência;
* pontos de entrada;
* dependências entre componentes;
* dívidas técnicas já confirmadas.

Mudanças arquiteturais futuras devem atualizar este documento quando alterarem significativamente essas responsabilidades ou fluxos.
