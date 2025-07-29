import datetime as dt
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class TitulosPublicos:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def curva_intradiaria(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/curva-intradiaria",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def curvas_juros(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/curvas-juros",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def difusao_taxas(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/difusao-taxas",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def estimativa_selic(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/estimativa-selic",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def mercado_secundario_tpf(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/mercado-secundario-TPF",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def projecoes(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/projecoes",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def pu_intradiario(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/pu-intradiario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def vna(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/vna",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
