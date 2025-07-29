from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_V1
from surepetcare.enums import ProductId


class DualScanConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_CONNECT

    def refresh(self):
        def parse(response):
            self._data = response["data"]
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V1}/device/{self.id}",
            callback=parse,
        )
