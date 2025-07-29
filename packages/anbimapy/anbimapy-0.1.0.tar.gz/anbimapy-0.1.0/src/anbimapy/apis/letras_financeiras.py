import datetime as dt
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class LetrasFinanceiras:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def matrizes_vertices_emissor(self, tipo_lf: Iterable[str], data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/letras-financeiras/matrizes-vertices-emissor",
            params={
                "tipo-lf": list(tipo_lf),
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
