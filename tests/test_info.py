"""Tests for the vehicle Library."""

import json
import re

import aiohttp
import pytest
from aioresponses import aioresponses
from syrupy import SnapshotAssertion

from vehicle import (
    RDW,
    RDWError,
    RDWUnknownLicensePlateError,
    Vehicle,
    VehicleType,
)

from . import load_fixture

RDW_URL = re.compile(r"https://opendata\.rdw\.nl/resource/m9d7-ebf2\.json.*")


@pytest.mark.parametrize(
    "license_plate",
    [
        "11ZKZ3",
        "0001TJ",
        "VXJ99N",
    ],
)
async def test_vehicle_data(
    license_plate: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting Vehicle information."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=200,
            body=load_fixture(f"{license_plate}.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            vehicle: Vehicle = await rdw.vehicle(license_plate)
            assert vehicle == snapshot
            assert vehicle.to_json() == snapshot


@pytest.mark.parametrize(
    "voertuigsoort",
    [
        "Autonome aanhangwagen",
        "Mobiele machine",
        "Motorfiets met zijspan",
        "Motorrijtuig met beperkte snelheid",
        "Oplegger",
    ],
)
async def test_vehicle_type(voertuigsoort: str) -> None:
    """Test every vehicle type RDW reports can be parsed."""
    data = json.loads(load_fixture("11ZKZ3.json"))
    data[0]["voertuigsoort"] = voertuigsoort
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=200,
            body=json.dumps(data),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            vehicle = await rdw.vehicle("11ZKZ3")
            assert vehicle.vehicle_type is VehicleType(voertuigsoort)


async def test_no_vehicle() -> None:
    """Test getting non-existing Vehicle."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=200,
            body=load_fixture("no_vehicles.json"),
            content_type="application/json",
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
