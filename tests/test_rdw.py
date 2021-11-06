"""Tests for the vehicle Library."""
# pylint: disable=protected-access
import asyncio

import aiohttp
import pytest

from vehicle import RDW
from vehicle.const import Dataset
from vehicle.exceptions import RDWConnectionError, RDWError


@pytest.mark.asyncio
async def test_json_request(aresponses):
    """Test JSON response is handled correctly."""
    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        response = await rdw._request(Dataset.PLATED_VEHICLES)
        assert response["status"] == "ok"
        await rdw.close()


@pytest.mark.asyncio
async def test_internal_session(aresponses):
    """Test JSON response is handled correctly."""
    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with RDW() as rdw:
        response = await rdw._request(Dataset.PLATED_VEHICLES)
        assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_timeout(aresponses):
    """Test request timeout."""
    # Faking a timeout by sleeping
    async def response_handler(_):
        """Response handler for this test."""
        await asyncio.sleep(2)
        return aresponses.Response(body="Goodmorning!")

    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        response_handler,
    )

    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session, request_timeout=1)
        with pytest.raises(RDWConnectionError):
            assert await rdw._request(Dataset.PLATED_VEHICLES)


@pytest.mark.asyncio
async def test_http_error400(aresponses):
    """Test HTTP 404 response handling."""
    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        aresponses.Response(text="OMG PUPPIES!", status=404),
    )

    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        with pytest.raises(RDWError):
            assert await rdw._request(Dataset.PLATED_VEHICLES)


@pytest.mark.asyncio
async def test_unexpected_response(aresponses):
    """Test unexpected response handling."""
    aresponses.add(
        "opendata.rdw.nl",
        f"/resource/{Dataset.PLATED_VEHICLES}.json",
        "GET",
        aresponses.Response(text="OMG PUPPIES!", status=200),
    )

    async with aiohttp.ClientSession() as session:
        rdw = RDW(session=session)
        with pytest.raises(RDWError):
            assert await rdw._request(Dataset.PLATED_VEHICLES)


@pytest.mark.asyncio
async def test_license_plate_normalization():
    """Test normalization of license plates."""
    assert RDW.normalize_license_plate("AB-12-34") == "AB1234"
    assert RDW.normalize_license_plate("AB1234") == "AB1234"
    assert RDW.normalize_license_plate("AB1-23-4") == "AB1234"
    assert RDW.normalize_license_plate(" Ab1-23-4 ") == "AB1234"
