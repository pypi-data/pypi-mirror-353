import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class ResultadosMais:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def ida(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-ida",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def idka(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-idka",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ihfa(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v2/indices-mais/resultados-ihfa",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima_intradiarios(self, data: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-intradiarios-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()


class CarteirasMais:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def ida_previa(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/previa-carteira-teorica-ida",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ida(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/carteira-teorica-ida",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ihfa(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v2/indices-mais/carteira-teorica-ihfa",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ima(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/carteira-teorica-ima",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ima_previa(self, month: dt.date) -> None:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/previa-carteira-teorica-ima",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()


class IndicesMais:
    def __init__(self, http: "Anbima") -> None:
        self.http = http
        self.resultados = ResultadosMais(http)
        self.carteiras = CarteirasMais(http)
