import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class CriCra:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def mercado_secundario(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/cri-cra/mercado-secundario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def projecoes(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/cri-cra/projecoes",
            params={
                "mes": month.month,
                "ano": month.year,
            },
        )
        response.raise_for_status()
        return response.json()
