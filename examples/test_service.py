from datetime import date

from consulta_processos.bases.service import (
    consultar_atualizacoes_por_base,
)

resultado = consultar_atualizacoes_por_base(
    numero_processo="5140460-06.2025.4.02.5101",
    base="eproc_jfrj",
    data_base=date(2026, 5, 1),
)

print("Fonte:", resultado.fonte)
print("Quantidade:", len(resultado.movimentos))

for mov in resultado.movimentos:
    print(mov.data)
    print(mov.descricao)
    print()
