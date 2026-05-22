from consulta_processos.bases.eproc import EprocClient


client = EprocClient("jfrj")

resultado = client.consultar(
    "5140460-06.2025.4.02.5101"
)

print()
print("Fonte:", resultado.fonte)
print("Erro:", resultado.erro)
print("URL:", resultado.url)
print()