# Atualizando o JuriScan

## Antes de atualizar

Feche o JuriScan completamente.

## O que substituir

Substitua apenas:

```text
JuriScan.exe
_internal/
scripts/
MANUAL_USUARIO.md
```

## O que não apagar

Não apague:

```text
.env
data/
config/
logs/
reports/
```
Esses arquivos guardam:

- histórico local;
- processos monitorados;
- configurações;
- logs.

## Atualização recomendada

1. Baixe a nova versão.
2. Extraia o .zip.
3. Copie os arquivos novos para a pasta antiga.
4. Quando o Windows perguntar, escolha:
    - substituir arquivos existentes.

## Em caso de erro

Verifique:
```text
logs/juriscan.log
```