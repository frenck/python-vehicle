"""Tests for the vehicle Library."""

import aiohttp
import pytest
from aresponses import ResponsesMockServer
from syrupy import SnapshotAssertion

from vehicle import (
    RDW,
    RDWError,
    RDWUnknownLicensePlateError,
    Vehicle,
)

from . import load_fixture


@pytest.mark.parametrize(
    "license_plate",
    [
        "11ZKZ3",
        "0001TJ",
        "VXJ99N",
    ],
)
async def test_vehicle_data(
    aresponses: ResponsesMockServer,
    license_plate: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting Vehicle information."""
    aresponses.add(
        "opendata.rdw.nl",
        "/resource/m9d7-ebf2.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"{license_plate}.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        vehicle: Vehicle = await rdw.vehicle(license_plate)
        assert vehicle == snapshot


async def test_no_vehicle(aresponses: ResponsesMockServer) -> None:
    """Test getting non-existing Vehicle."""
    aresponses.add(
        "opendata.rdw.nl",
        "/resource/m9d7-ebf2.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("no_vehicles.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        with pytest.raises(RDWUnknownLicensePlateError):
            await rdw.vehicle("00-00-00")


async def test_no_license_plate_provided() -> None:
    """Test getting Vehicle without license plate."""
    rdw = RDW()
    with pytest.raises(RDWError):
        await rdw.vehicle()
