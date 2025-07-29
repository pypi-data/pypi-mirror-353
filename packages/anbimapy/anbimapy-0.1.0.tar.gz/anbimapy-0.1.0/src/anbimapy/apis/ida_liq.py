import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class IdaLiq:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def carteira_ida(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/ida-liq/carteira-teorica-ida",
            params={
                "mes": month.month,
                "ano": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def carteira_ida_previa(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/ida-liq/previa-carteira-teorica-ida",
            params={
                "mes": month.month,
                "ano": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def resultados_ida(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/ida-liq/resultados-ida",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
