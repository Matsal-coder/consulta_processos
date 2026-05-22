# Consulta Processos API

Projeto educacional para consulta automatizada de movimentações processuais.
Bases atualmente suportadas:
- TJSP e-SAJ
- DataJud (TJRJ, TJSP, TJES, TJBA, TJAM, TRF2)

## Funcionalidades

- Consulta de processos por número CNJ;
- Integração com API pública do DataJud;
- Retorno estruturado em JSON;
- API REST com FastAPI;
- Documentação automática via Swagger;
- Testes automatizados com pytest;
- Validação de payload com Pydantic.

---

# Tecnologias

- Python 3.12
- FastAPI
- Pydantic
- Requests
- Pytest
- Ruff

---

# Instalação

## 1. Clonar repositório

```bash
git clone URL_DO_REPOSITORIO
cd consulta-processos
```

## 2. Criar ambiente virtual

```bash
python -m venv .venv
```

## 3. Ativar ambiente virtual

### Windows Git Bash

```bash
source .venv/Scripts/activate
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

---

## 4. Instalar dependências

```bash
pip install -r requirements.txt
pip install -e .
```

---

# Configuração

## Criar arquivo `.env`

Copie `.env.example`:

```bash
cp .env.example .env
```

E preencha:

```env
DATAJUD_API_KEY=sua_chave_aqui
```

---

# Rodando a API

## Opção 1 — Terminal

```bash
uvicorn consulta_processos.api:app --reload
```

---

## Opção 2 — Windows

Execute:

```text
run_api.bat
```

---

# Documentação Swagger

Após subir a API:

```text
http://127.0.0.1:8000/docs
```

---

# Exemplo de payload

```json
{
  "processos": [
    {
      "numero_processo": "0964024-67.2024.8.19.0001",
      "base": "tjrj_datajud",
      "data_base": "2025-01-01"
    }
  ]
}
```

---

# Rodando testes

```bash
pytest -v
```

---

# Lint

```bash
ruff check src tests
```

---

# Observações

A API pública do DataJud pode apresentar defasagem em relação ao sistema original do tribunal.