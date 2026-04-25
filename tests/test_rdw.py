"""Tests for the vehicle Library."""

# pylint: disable=protected-access
import re
import socket

import aiohttp
import pytest
from aioresponses import aioresponses

from vehicle import RDW, Vehicle
from vehicle.const import Dataset
from vehicle.exceptions import RDWConnectionError, RDWError, RDWUnknownLicensePlateError
from vehicle.models import Fuel, Recall

from . import load_fixture

RDW_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
RDW_URL_PATTERN = re.compile(r"https://opendata\.rdw\.nl/resource/m9d7-ebf2\.json.*")
FUEL_URL_PATTERN = re.compile(r"https://opendata\.rdw\.nl/resource/8ys7-d773\.json.*")
RECALLS_URL_PATTERN = re.compile(
    r"https://opendata\.rdw\.nl/resource/t49b-isb7\.json.*"
)


async def test_json_request() -> None:
    """Test JSON response is handled correctly."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=200,
            body='{"status": "ok"}',
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            response = await rdw._request(Dataset.PLATED_VEHICLES)
            assert response == '{"status": "ok"}'
            await rdw.close()


async def test_internal_session() -> None:
    """Test the client manages its own session as a context manager."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=200,
            body='{"status": "ok"}',
            content_type="application/json",
        )
        async with RDW() as rdw:
            response = await rdw._request(Dataset.PLATED_VEHICLES)
            assert response == '{"status": "ok"}'


async def test_timeout() -> None:
    """Test request timeout."""
    with aioresponses() as mocked:
        mocked.get(RDW_URL, exception=TimeoutError())
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session, request_timeout=1)
            with pytest.raises(RDWConnectionError):
                assert await rdw._request(Dataset.PLATED_VEHICLES)


async def test_connection_error() -> None:
    """Test socket.gaierror is wrapped in RDWConnectionError."""
    with aioresponses() as mocked:
        mocked.get(RDW_URL, exception=socket.gaierror())
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            with pytest.raises(RDWConnectionError):
                await rdw._request(Dataset.PLATED_VEHICLES)


async def test_http_error400() -> None:
    """Test HTTP 404 response handling."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=404,
            body="OMG PUPPIES!",
            content_type="text/plain",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            with pytest.raises(RDWError):
                assert await rdw._request(Dataset.PLATED_VEHICLES)


async def test_unexpected_response() -> None:
    """Test unexpected response handling."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL,
            status=200,
            body="OMG PUPPIES!",
            content_type="text/plain",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            with pytest.raises(RDWError):
                assert await rdw._request(Dataset.PLATED_VEHICLES)


async def test_license_plate_normalization() -> None:
    """Test normalization of license plates."""
    assert RDW.normalize_license_plate("AB-12-34") == "AB1234"
    assert RDW.normalize_license_plate("AB1234") == "AB1234"
    assert RDW.normalize_license_plate("AB1-23-4") == "AB1234"
    assert RDW.normalize_license_plate(" Ab1-23-4 ") == "AB1234"


async def test_vehicle_with_constructor_license_plate() -> None:
    """Test looking up a vehicle using the constructor-level license plate."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL_PATTERN,
            status=200,
            body=load_fixture("11ZKZ3.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session, license_plate="11ZKZ3")
            vehicle: Vehicle = await rdw.vehicle()
            assert vehicle.license_plate == "11ZKZ3"
            assert vehicle.brand == "Skoda"


async def test_close_external_session_not_closed() -> None:
    """Test that an externally-provided session is not closed by RDW."""
    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        await rdw.close()
        assert not session.closed


async def test_close_without_session() -> None:
    """Test that close() is safe to call when no session exists."""
    rdw = RDW()
    await rdw.close()  # Should not raise


async def test_unknown_license_plate() -> None:
    """Test RDWUnknownLicensePlateError includes the license plate in the message."""
    with aioresponses() as mocked:
        mocked.get(
            RDW_URL_PATTERN,
            status=200,
            body=load_fixture("no_vehicles.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            with pytest.raises(RDWUnknownLicensePlateError, match="XX-XX-XX"):
                await rdw.vehicle("XX-XX-XX")


async def test_fuel() -> None:
    """Test fetching fuel and emission information."""
    with aioresponses() as mocked:
        mocked.get(
            FUEL_URL_PATTERN,
            status=200,
            body=load_fixture("fuel_11ZKZ3.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            fuels = await rdw.fuel("11ZKZ3")
            assert len(fuels) == 1
            assert isinstance(fuels[0], Fuel)
            assert fuels[0].fuel_type == "Benzine"
            assert fuels[0].co2_combined == 95
            assert fuels[0].consumption_combined == 4.1
            assert fuels[0].max_power == 44.0
            assert fuels[0].emission_standard == "EURO 5"
            assert fuels[0].noise_level_driving == 71
            assert fuels[0].noise_level_stationary == 78


async def test_fuel_electric() -> None:
    """Test fetching fuel information for an electric vehicle."""
    with aioresponses() as mocked:
        mocked.get(
            FUEL_URL_PATTERN,
            status=200,
            body=load_fixture("fuel_electric.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            fuels = await rdw.fuel("00BTV8")
            assert len(fuels) == 1
            fuel = fuels[0]
            assert fuel.fuel_type == "Elektriciteit"
            assert fuel.max_power_electric == 135.0
            assert fuel.range_electric_wltp == 287
            assert fuel.range_electric_city_wltp == 365
            assert fuel.consumption_electric_wltp == 290.0
            assert fuel.co2_emission_class == "5"


async def test_fuel_empty() -> None:
    """Test fetching fuel information when none is available."""
    with aioresponses() as mocked:
        mocked.get(
            FUEL_URL_PATTERN,
            status=200,
            body=load_fixture("fuel_empty.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            fuels = await rdw.fuel("XX0000")
            assert fuels == []


async def test_recalls() -> None:
    """Test fetching recall information."""
    with aioresponses() as mocked:
        mocked.get(
            RECALLS_URL_PATTERN,
            status=200,
            body=load_fixture("recalls.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            recalls = await rdw.recalls("00BBL8")
            assert len(recalls) == 2
            assert isinstance(recalls[0], Recall)
            assert recalls[0].reference_code == "MGP130086"
            assert recalls[0].status_code == "P"
            assert recalls[0].status == "Producent heeft herstel gemeld"
            assert recalls[1].status_code == "O"
            assert recalls[1].status == "Openstaande terugroepactie"


async def test_recalls_empty() -> None:
    """Test fetching recalls when none exist."""
    with aioresponses() as mocked:
        mocked.get(
            RECALLS_URL_PATTERN,
            status=200,
            body=load_fixture("recalls_empty.json"),
            content_type="application/json",
        )
        async with aiohttp.ClientSession() as session:
            rdw = RDW(session=session)
            recalls = await rdw.recalls("11ZKZ3")
            assert recalls == []


async def test_fuel_no_license_plate() -> None:
    """Test fuel() raises when no license plate is provided."""
    rdw = RDW()
    with pytest.raises(RDWError, match="No license plate provided"):
        await rdw.fuel()


async def test_recalls_no_license_plate() -> None:
    """Test recalls() raises when no license plate is provided."""
    rdw = RDW()
    with pytest.raises(RDWError, match="No license plate provided"):
        await rdw.recalls()
