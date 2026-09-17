from consulta_processos.bases.registry import (
    consultar_processo,
)

resultado = consultar_processo(
    numero_processo="1020749-11.2023.8.26.0068",
    base="esaj_tjsp",
)

print()
print("Fonte:", resultado.fonte)
print("Quantidade:", len(resultado.movimentos))
print()

for mov in resultado.movimentos[:5]:
    print(mov.data)
    print(mov.descricao)
    print()
