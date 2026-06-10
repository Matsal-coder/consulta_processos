# Checklist de release — JuriScan

## Antes do build

- [ ] Estar na branch `main` atualizada
- [ ] Rodar `ruff check .`
- [ ] Rodar `pytest`
- [ ] Confirmar `.env.example` atualizado
- [ ] Confirmar `MANUAL_USUARIO.md` atualizado

## Build

- [ ] Rodar `scripts\build_release_zip.bat`
- [ ] Confirmar existência de `dist\JuriScan\JuriScan.exe`
- [ ] Confirmar existência de `dist\JuriScan\MANUAL_USUARIO.md`
- [ ] Confirmar existência de `dist\JuriScan-portable.zip`

## Teste local

- [ ] Extrair zip em uma pasta nova
- [ ] Abrir `JuriScan.exe`
- [ ] Confirmar abertura automática no navegador
- [ ] Confirmar criação de `.env`
- [ ] Confirmar criação de `data/`
- [ ] Confirmar criação de `config/`
- [ ] Confirmar criação de `logs/`
- [ ] Confirmar criação de `reports/`
- [ ] Rodar monitoramento manual sem processos cadastrados
- [ ] Confirmar mensagem amigável
- [ ] Confirmar criação de log

## Teste de segurança Windows

- [ ] Confirmar se aparece aviso do Firewall
- [ ] Marcar apenas redes privadas
- [ ] Confirmar se aparece SmartScreen
- [ ] Testar opção “Mais informações” → “Executar assim mesmo”

## Entrega

- [ ] Enviar apenas `JuriScan-portable.zip`
- [ ] Orientar usuário a extrair a pasta antes de abrir
- [ ] Não rodar diretamente de dentro do zip