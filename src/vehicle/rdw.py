"""Asynchronous Python client providing RDW vehicle information."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from typing import Any, Self

import orjson
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .const import Dataset
from .exceptions import RDWConnectionError, RDWError, RDWUnknownLicensePlateError
from .models import Fuel, Recall, Vehicle


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
            The response body as a string.

        Raises:
        ------
            RDWConnectionError: An error occurred while communicating with
                the Socrata API.
            RDWError: Received an unexpected response from the Socrata API.

        """
        url = URL("https://opendata.rdw.nl/resource/").join(
            URL(f"{dataset.value}.json"),
        )

        headers = {
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url.with_query(data),
                    headers=headers,
                )
                response.raise_for_status()
        except TimeoutError as exception:
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

    def _resolve_license_plate(self, license_plate: str | None = None) -> str:
        """Resolve the license plate to use for a request.

        Args:
        ----
            license_plate: License plate to use, or None to fall back
                to the instance-level license plate.

        Returns:
        -------
            The normalized license plate.

        Raises:
        ------
            RDWError: No license plate provided.

        """
        license_plate = license_plate or self.license_plate
        if license_plate is None:
            msg = "No license plate provided"
            raise RDWError(msg)
        return self.normalize_license_plate(license_plate)

    async def vehicle(self, license_plate: str | None = None) -> Vehicle:
        """Get information about a vehicle.

        Args:
        ----
            license_plate: License plate of the vehicle, if not provided
                the license plate of the object will be used.

        Returns:
        -------
            A Vehicle object with information about the vehicle.

        Raises:
        ------
            RDWError: No license plate provided.
            RDWUnknownLicensePlateError: License plate not found in RDW Socrata DB.

        """
        normalized = self._resolve_license_plate(license_plate)
        data = await self._request(
            Dataset.PLATED_VEHICLES,
            data={"kenteken": normalized},
        )
        # pylint: disable=no-member
        vehicles = orjson.loads(data)
        if not vehicles:
            msg = (
                f"License plate {license_plate or self.license_plate}"
                " not found in RDW Socrata database"
            )
            raise RDWUnknownLicensePlateError(msg)

        return Vehicle.from_dict(vehicles[0])

    async def fuel(self, license_plate: str | None = None) -> list[Fuel]:
        """Get fuel and emission information for a vehicle.

        A vehicle can have multiple fuel entries, e.g., a hybrid has both
        a combustion engine and an electric motor.

        Args:
        ----
            license_plate: License plate of the vehicle, if not provided
                the license plate of the object will be used.

        Returns:
        -------
            A list of Fuel objects with fuel and emission information.

        Raises:
        ------
            RDWError: No license plate provided.

        """
        normalized = self._resolve_license_plate(license_plate)
        data = await self._request(
            Dataset.FUEL,
            data={"kenteken": normalized},
        )
        # pylint: disable=no-member
        return [Fuel.from_dict(item) for item in orjson.loads(data)]

    async def recalls(self, license_plate: str | None = None) -> list[Recall]:
        """Get recall information for a vehicle.

        Args:
        ----
            license_plate: License plate of the vehicle, if not provided
                the license plate of the object will be used.

        Returns:
        -------
            A list of Recall objects with recall information.

        Raises:
        ------
            RDWError: No license plate provided.

        """
        normalized = self._resolve_license_plate(license_plate)
        data = await self._request(
            Dataset.RECALLS,
            data={"kenteken": normalized},
        )
        # pylint: disable=no-member
        return [Recall.from_dict(item) for item in orjson.loads(data)]

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
