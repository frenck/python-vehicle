"""Asynchronous Python client providing RDW vehicle information."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

import async_timeout
import orjson
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .const import Dataset
from .exceptions import RDWConnectionError, RDWError, RDWUnknownLicensePlateError
from .models import Vehicle


@dataclass
class RDW:
    """Main class for handling data fetching from RDW."""

    session: ClientSession | None = None
    license_plate: str | None = None
    request_timeout: int = 10
    _close_session: bool = False

    @staticmethod
    def normalize_license_plate(license_plate: str) -> str:
        """Normalize license plate.

        Args:
        ----
            license_plate: License plate.

        Returns:
        -------
            Normalized license plate.
        """
        return license_plate.upper().replace("-", "").replace(" ", "").strip()

    async def _request(
        self,
        dataset: Dataset,
        *,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to a RDW open data (Socrata).

        A generic method for sending/handling HTTP requests done against
        the public RDW data.

        Args:
        ----
            dataset: Identifier for the Socrata dataset to query.
            data: Dictionary of data to send to the Socrata API.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the API.

        Raises:
        ------
            RDWConnectionError: An error occurred while communicating with
                the Socrata API.
            RDWError: Received an unexpected response from the Socrata API.
        """
        version = metadata.version(__package__)
        url = URL("https://opendata.rdw.nl/resource/").join(
            URL(f"{dataset.value}.json"),
        )

        headers = {
            "User-Agent": f"PythonVehicle/{version}",
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url.with_query(data),
                    headers=headers,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Socrata API"
            raise RDWConnectionError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with Socrata API"
            raise RDWConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        text = await response.text()
        if "application/json" not in content_type:
            msg = "Unexpected response from the Socrata API"
            raise RDWError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return text

    async def vehicle(self, license_plate: str | None = None) -> Vehicle:
        """Get devices information about a Vehicle.

        Args:
        ----
            license_plate: License plate of the vehicle, if not provided
                the license plate of the object will be used.

        Returns:
        -------
            A Vehicle object, with information about the vehicle.

        Raises:
        ------
            RDWError: No license plate provided.
            RDWUnknownLicensePlateError: License plate not found in RDW Socrata DB.
        """
        license_plate = license_plate or self.license_plate
        if license_plate is None:
            msg = "No license plate provided"
            raise RDWError(msg)

        data = await self._request(
            Dataset.PLATED_VEHICLES,
            data={"kenteken": self.normalize_license_plate(license_plate)},
        )
        # pylint: disable=no-member
        vehicles = orjson.loads(data)
        if not vehicles:
            msg = f"License plate {license_plate} not found in RDW Socrata database"
            raise RDWUnknownLicensePlateError(msg)

        return Vehicle.from_dict(vehicles[0])

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The RDW object.
        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
