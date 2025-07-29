import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class Fidc:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def mercado_secundario(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/fidc/mercado-secundario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
