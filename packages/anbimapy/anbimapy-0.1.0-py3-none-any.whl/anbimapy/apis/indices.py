import datetime as dt
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class PuIntradiario(TypedDict): ...


class Resultados:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def ida_fechado(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-ida-fechado",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def idka(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-idka",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ihfa_fechado(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-ihfa-fechado",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima_intradiarios(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-intradiarios-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()


class Indices:
    def __init__(self, http: "Anbima") -> None:
        self.http = http
        self.resultados = Resultados(http)

    def pu_intradiario(self, data: dt.date) -> list[PuIntradiario]:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/pu-intradiario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
