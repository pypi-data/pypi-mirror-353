from dataclasses import dataclass
from typing import Any

from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_V1
from surepetcare.enums import BowlPosition
from surepetcare.enums import FoodType
from surepetcare.enums import ProductId


@dataclass
class BowlState:
    position: BowlPosition
    food_type: FoodType


class BowlMixin:
    _data: dict[str, Any]

    @property
    def lid_delay(self) -> float:
        return int(self._data["control"]["lid"]["close_delay"])

    @property
    def bowls(self) -> list:
        settings = self._data["control"]["bowls"]["settings"]
        return [
            BowlState(BowlPosition(index), FoodType(bowl["food_type"])) for index, bowl in enumerate(settings)
        ]


class FeederConnect(SurepyDevice, BowlMixin):
    @property
    def product(self) -> ProductId:
        return ProductId.FEEDER_CONNECT

    def refresh(self):
        def parse(response):
            self._data = response["data"]
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V1}/device/{self.id}",
            callback=parse,
        )
