# JuriScan

Aplicativo local para consulta e monitoramento de processos.

## Como abrir

Clique duas vezes em:

```text
JuriScan.exe
```
O navegador abrirá automaticamente.

## O que não apagar

Não apague estas pastas:

```text
data/
config/
logs/
reports/
```
Elas guardam os dados locais do aplicativo.

## Configuração

O arquivo .env guarda configurações como:

```text
- chave do DataJud;
- envio de email;
- remetente;
- destinatário.
```

## Dados locais

O histórico fica em:

```text
data/consulta_processos.db
```

Os processos monitorados ficam em:

```text
config/processos_monitorados.json
```

## Logs

Em caso de erro, veja:

```text
logs/juriscan.log
```

Que também pode ser aberto diretamente pela aba Automação no app

## Como fechar

Feche a aba do navegador.

Se o aplicativo continuar rodando, feche o JuriScan pela barra de tarefas do Windows.

## Atualizações

Consulte:
```text
UPDATE_GUIDE.md
```
