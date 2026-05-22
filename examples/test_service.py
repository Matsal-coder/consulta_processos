from datetime import date

from consulta_processos.bases.service import (
    consultar_atualizacoes_por_base,
)


resultado = consultar_atualizacoes_por_base(
    numero_processo="1020749-11.2023.8.26.0068",
    base="esaj_tjsp",
    data_base=date(2026, 5, 1),
)

print("Fonte:", resultado.fonte)
print("Quantidade:", len(resultado.movimentos))

for mov in resultado.movimentos:
    print(mov.data)
    print(mov.descricao)
    print()