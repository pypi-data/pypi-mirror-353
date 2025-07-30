"""AL-KO: Init"""
import logging

from aiohttp import ClientResponse
from typing import List

from .const import BASE_URL
from .objects.base import AlkoBase
from .objects.device import AlkoDevice
from .client import AlkoClient


class Alko(AlkoBase):
    """Interacting with AL-KO API."""

    logger = logging.getLogger(__name__)

    def __init__(self, client: "AlkoClient", client_id: str) -> None:
        """Initialize the appliance."""
        self._client = client
        self._client_id = client_id
        self._devices: List[AlkoDevice] = []
        self._devices_dict: dict = {}

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def devices(self) -> dict:
        return self._devices

    @property
    def devices_dict(self) -> dict:
        return self._devices_dict

    async def get_devices(self) -> None:
        """Get Devices."""
        response: ClientResponse = await self._client.get(
            f"{BASE_URL}?pimInfo=true&thingState=true&accesses=true&thingCategory=ALKO-ROBOLINHO"
        )
        json = await response.json()
        self._devices = [
            AlkoDevice(self._client, thingName) for thingName in json or []
        ]
        self._devices_dict: dict = {}
        for device in self._devices:
            self._devices_dict[device.thingName] = device

    async def update_device(
        self,
        device: AlkoDevice,
        rtc=None,
        ecoMode=None,
        rainDelay=None,
        rainSensor=None,
        operationState=None,
        thingNotification=None,
        **kwargs
    ) -> ClientResponse:
        """Update Device."""
        self.logger.debug("Update Device")

        data = {}

        if rtc is not None:
            data["rtc"] = rtc

        if ecoMode is not None:
            data["ecoMode"] = ecoMode

        if rainDelay is not None:
            data["rainDelay"] = rainDelay

        if rainSensor is not None:
            data["rainSensor"] = rainSensor

        if operationState is not None:
            data["operationState"] = operationState

        if thingNotification is not None:
            data["thingNotification"] = thingNotification

        # Add any additional kwargs to the data dictionary
        data.update(kwargs)

        return await self._client.patch(
            f"{BASE_URL}/{device.thingName}/state/desired",
            json=data,
        )
