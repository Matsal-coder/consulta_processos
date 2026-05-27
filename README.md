# JuriScan — Documentação Atualizada

# Visão Geral

O JuriScan é uma aplicação desktop/web desenvolvida em Python para:

* consultar movimentações processuais;
* monitorar processos automaticamente;
* identificar novidades;
* salvar histórico local;
* gerar relatórios automáticos;
* organizar processos por cliente.

A aplicação foi construída com foco em:

* facilidade operacional;
* arquitetura extensível;
* suporte a múltiplas bases processuais;
* automação futura via scheduler e email.

---

# Features atuais

## Consulta de processos

* Consulta individual ou múltipla;
* Suporte multi-base;
* Resultado consolidado em tabela;
* Exportação CSV.

---

## Monitoramento de processos

* Adicionar processos aos monitorados;
* Remover processos monitorados;
* Atualizar todos automaticamente;
* Identificação de novas movimentações;
* Histórico local persistente.
* Relatórios automáticos por cliente/processo
* Envio automático de email

---

## Clientes

Os monitorados podem ser associados a clientes.

Formato:

```text
cliente;numero_processo;base
```

Exemplo:

```text
Cliente XPTO;0964024-67.2024.8.19.0001;tjrj_datajud
```

---

## Gestão em massa

* Importação em lote;
* Exportação CSV;
* Limpeza completa dos monitorados.

---

## Relatórios automáticos

### Relatório local

```bash
python -m consulta_processos.jobs.monitorados_report
```

### Relatório por email

```bash
python -m consulta_processos.jobs.email_monitorados_report
```
#### Configuração de email

Necessário configurar SMTP no `.env`.

Exemplo:

EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_FROM=
EMAIL_TO=


Funções:

* consulta todos os monitorados;
* identifica novidades;
* salva histórico local;
* gera relatório consolidado;
* gera relatórios por cliente/processo.

Estrutura:

```text
reports/
├── relatorio_completo_YYYY-MM-DD_HH-MM.csv
└── clientes/
    └── Cliente/
        └── Processo/
            └── relatorio_YYYY-MM-DD_HH-MM.csv
```

---

# Bases suportadas

## DataJud

* TJRJ
* Outros tribunais compatíveis

## EPROC

* TRF2
* JFRJ
* JFES

## ESAJ

* Bases ESAJ compatíveis

---

# Estrutura do projeto

```text
src/consulta_processos/
├── bases/
├── jobs/
├── ui/
├── utils/
├── database.py
├── history_repository.py
├── monitoring_repository.py
├── services.py
└── desktop_launcher.py
```

---

# Banco de dados

Atualmente o SQLite armazena:

## movimentacoes_consultadas

* numero_processo
* base
* descricao
* data_movimentacao
* created_at

---

# Configuração

## .env

Exemplo:

```env
DATAJUD_API_KEY=sua_chave

ENABLE_LOCAL_HISTORY=true
CONSULTA_PROCESSOS_DB_PATH=data/consulta_processos.db
```

---

# Executando localmente

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Rodar Streamlit

```bash
streamlit run app.py
```

---

## Rodar API

```bash
uvicorn consulta_processos.api:app --reload
```

---

## Rodar job de relatório

```bash
python -m consulta_processos.jobs.monitorados_report
```

---

# Executável Desktop

Geração via PyInstaller.

Exemplo:

```bash
pyinstaller \
  --onedir \
  --name JuriScan \
  --paths src \
  --add-data "app.py;." \
  --add-data "src/consulta_processos;consulta_processos" \
  --collect-all streamlit \
  --collect-all seleniumbase \
  src/consulta_processos/desktop_launcher.py
```

Executável final:

```text
dist/JuriScan/JuriScan.exe
```

---

# Testes

## Rodar pytest

```bash
pytest -v
```

---

## Rodar Ruff

```bash
ruff check .
```

---

# Roadmap

## Curto prazo

* scheduler Windows;
* melhorias UX desktop.

---

## Médio prazo

* aba Cliente;
* apelidos de processos;
* comentários em movimentações;
* timeline processual.

---

## Longo prazo

* novas bases processuais;
* OCR;
* classificação automática de movimentações;
* priorização inteligente.
