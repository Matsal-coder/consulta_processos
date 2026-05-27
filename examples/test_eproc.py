from consulta_processos.bases.eproc import EprocClient

client = EprocClient(
    "tjrj",
    headless=False,
    salvar_debug_html=True,
)

resultado = client.consultar(
    "3016257-70.2025.8.19.0001"
)

print()
print("Fonte:", resultado.fonte)
print("Erro:", resultado.erro)
print("URL:", resultado.url)
print("Quantidade:", len(resultado.movimentos))

for mov in resultado.movimentos[:10]:
    print(mov.data)
    print(mov.descricao)
    print()
print()