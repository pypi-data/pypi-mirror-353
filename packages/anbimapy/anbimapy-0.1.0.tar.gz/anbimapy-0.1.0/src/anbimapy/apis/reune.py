import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class Reune:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def previas(self, data: dt.date, instrumento: str, faixa: str = "24:00") -> None:
        response = self.http.get(
            url="/precos-indices/v1/reune/previas-do-reune",
            params={
                "data": f"{data:%Y-%m-%d}",
                "instrumento": instrumento,
                "faixa": faixa,
            },
        )
        response.raise_for_status()
        return response.json()
