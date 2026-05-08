# Consulta Processos

Projeto educacional para consultar atualizações de processos em bases públicas a partir de um JSON de entrada.

## Objetivo

Receber uma lista de processos com:

- número do processo;
- base de consulta;
- data-base.

E retornar as atualizações encontradas após a data-base.

## Exemplo de entrada

```json
{
  "processos": [
    {
      "numero_processo": "0000000-00.0000.0.00.0000",
      "base": "tjsp",
      "data_base": "2024-01-01"
    }
  ]
}
```