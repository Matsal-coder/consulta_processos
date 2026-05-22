from consulta_processos.bases.esaj import ESAJClient


client = ESAJClient("tjsp")

resultado = client.consultar(
    "1020749-11.2023.8.26.0068"
)

print()
print("Quantidade:", len(resultado.movimentos))
print()

for mov in resultado.movimentos[:10]:
    print(mov.data)
    print(mov.descricao)
    print()