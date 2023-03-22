"""Tests for the vehicle Library."""
from datetime import date

import aiohttp
import pytest
from aresponses import ResponsesMockServer
from vehicle import (
    RDW,
    RDWError,
    RDWUnknownLicensePlateError,
    Vehicle,
    VehicleInterior,
    VehicleOdometerJudgement,
    VehicleType,
)
from vehicle.const import Dataset

from . import load_fixture


async def test_vehicle_data(  # pylint: disable=too-many-statements
    aresponses: ResponsesMockServer,
) -> None:
    """Test getting Vehicle information."""
    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("11ZKZ3.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        vehicle: Vehicle = await rdw.vehicle("11-ZKZ-3")
        assert vehicle
        assert vehicle.apk_expiration == date(2022, 1, 4)
        assert vehicle.ascription_date == date(2021, 11, 4)
        assert vehicle.ascription_possible is True
        assert vehicle.brand == "Skoda"
        assert vehicle.energy_label == "A"
        assert vehicle.engine_capacity == 999
        assert vehicle.exported is False
        assert vehicle.first_admission == date(2013, 1, 4)
        assert vehicle.interior == VehicleInterior.HATCHBACK
        assert vehicle.last_odometer_registration_year == 2021
        assert vehicle.liability_insured is False
        assert vehicle.license_plate == "11ZKZ3"
        assert vehicle.list_price == 10697
        assert vehicle.mass_driveable == 940
        assert vehicle.mass_empty == 840
        assert vehicle.model == "Citigo"
        assert vehicle.number_of_cylinders == 3
        assert vehicle.number_of_doors == 0
        assert vehicle.number_of_seats == 4
        assert vehicle.number_of_wheelchair_seats == 0
        assert vehicle.number_of_wheels == 4
        assert vehicle.odometer_judgement == VehicleOdometerJudgement.LOGICAL
        assert vehicle.pending_recall is False
        assert vehicle.taxi is None
        assert vehicle.vehicle_type == VehicleType.PASSENGER_CAR

    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("0001TJ.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        vehicle = await rdw.vehicle("00-01-TJ")
        assert vehicle
        assert vehicle.apk_expiration == date(2023, 7, 26)
        assert vehicle.ascription_date == date(2013, 7, 25)
        assert vehicle.ascription_possible is True
        assert vehicle.brand == "Ford"
        assert vehicle.energy_label is None
        assert vehicle.engine_capacity is None
        assert vehicle.exported is False
        assert vehicle.first_admission == date(1972, 1, 13)
        assert vehicle.interior is None
        assert vehicle.last_odometer_registration_year == 2021
        assert vehicle.liability_insured is True
        assert vehicle.license_plate == "0001TJ"
        assert vehicle.list_price is None
        assert vehicle.mass_driveable == 950
        assert vehicle.mass_empty == 850
        assert vehicle.model == "Escort Mexico"
        assert vehicle.number_of_cylinders == 4
        assert vehicle.number_of_doors == 2
        assert vehicle.number_of_seats is None
        assert vehicle.number_of_wheelchair_seats is None
        assert vehicle.number_of_wheels == 4
        assert vehicle.odometer_judgement == VehicleOdometerJudgement.NO_JUDGEMENT
        assert vehicle.pending_recall is False
        assert vehicle.taxi is False
        assert vehicle.vehicle_type == VehicleType.PASSENGER_CAR


async def test_no_vehicle(aresponses: ResponsesMockServer) -> None:
    """Test getting non-existing Vehicle."""
    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
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
