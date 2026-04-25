"""Tests for the Vehicle CLI."""

# pylint: disable=redefined-outer-name
from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.main import get_command
from typer.testing import CliRunner

from vehicle import Fuel, Vehicle
from vehicle.cli import cli
from vehicle.exceptions import RDWConnectionError, RDWUnknownLicensePlateError

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion


@pytest.fixture(autouse=True)
def stable_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force deterministic Rich rendering for stable snapshots."""
    monkeypatch.setenv("COLUMNS", "100")
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("TERM", "dumb")


@pytest.fixture
def runner() -> CliRunner:
    """Return a CLI runner for invoking the Typer app."""
    return CliRunner()


def mock_rdw_class(
    vehicle_data: Vehicle,
    fuel_data: list[Fuel] | None = None,
) -> MagicMock:
    """Return a MagicMock that stands in for the RDW class."""
    client = AsyncMock()
    client.vehicle.return_value = vehicle_data
    client.fuel.return_value = fuel_data or []

    instance = AsyncMock()
    instance.__aenter__.return_value = client
    instance.__aexit__.return_value = None

    return MagicMock(return_value=instance)


def invoke(
    runner: CliRunner,
    args: list[str],
    vehicle_data: Vehicle,
    fuel_data: list[Fuel] | None = None,
) -> tuple[int, str, MagicMock]:
    """Invoke the CLI with a mocked RDW class and return the result."""
    mock_cls = mock_rdw_class(vehicle_data, fuel_data)
    with patch("vehicle.cli.RDW", mock_cls):
        result = runner.invoke(cli, args)
    return result.exit_code, result.stdout, mock_cls


@pytest.fixture
def sample_vehicle() -> Vehicle:
    """Return a sample Vehicle for CLI tests."""
    return Vehicle.from_dict(
        {
            "merk": "SKODA",
            "kenteken": "11ZKZ3",
            "handelsbenaming": "CITIGO",
            "vervaldatum_apk": "20220104",
            "datum_tenaamstelling": "20211104",
            "tenaamstellen_mogelijk": "Ja",
            "zuinigheidslabel": "A",
            "cilinderinhoud": 999,
            "export_indicator": "Nee",
            "inrichting": "hatchback",
            "eerste_kleur": "GRIJS",
            "tweede_kleur": "Niet geregistreerd",
            "europese_voertuigcategorie": "M1",
            "lengte": 356,
            "wielbasis": 241,
            "toegestane_maximum_massa_voertuig": 1290,
            "datum_eerste_tenaamstelling_in_nederland": "20130104",
            "jaar_laatste_registratie_tellerstand": 2021,
            "wam_verzekerd": "Nee",
            "catalogusprijs": 10697,
            "datum_eerste_toelating": "20130104",
            "massa_ledig_voertuig": 840,
            "massa_rijklaar": 940,
            "aantal_cilinders": 3,
            "aantal_deuren": 0,
            "aantal_zitplaatsen": 4,
            "aantal_rolstoelplaatsen": 0,
            "aantal_wielen": 4,
            "tellerstandoordeel": "Logisch",
            "openstaande_terugroepactie_indicator": "Nee",
            "taxi_indicator": "Nee",
            "voertuigsoort": "Personenauto",
        }
    )


@pytest.fixture
def sample_fuel() -> list[Fuel]:
    """Return a sample Fuel list for CLI tests."""
    return [
        Fuel.from_dict(
            {
                "brandstof_omschrijving": "Benzine",
                "brandstofverbruik_buiten": "3.60",
                "brandstofverbruik_gecombineerd": "4.10",
                "brandstofverbruik_stad": "5.00",
                "co2_uitstoot_gecombineerd": "95",
                "geluidsniveau_rijdend": "71",
                "geluidsniveau_stationair": "78",
                "nettomaximumvermogen": "44.00",
                "uitlaatemissieniveau": "EURO 5",
            }
        )
    ]


def test_cli_structure(snapshot: SnapshotAssertion) -> None:
    """The CLI exposes the expected parameters."""
    command = get_command(cli)
    structure = sorted(param.name for param in command.params)
    assert structure == snapshot


def test_lookup(
    runner: CliRunner,
    sample_vehicle: Vehicle,
    sample_fuel: list[Fuel],
    snapshot: SnapshotAssertion,
) -> None:
    """Lookup prints a table of vehicle and fuel information."""
    exit_code, output, _ = invoke(
        runner,
        ["11ZKZ3"],
        sample_vehicle,
        sample_fuel,
    )
    assert exit_code == 0
    assert output == snapshot


def test_lookup_json(
    runner: CliRunner,
    sample_vehicle: Vehicle,
    sample_fuel: list[Fuel],
    snapshot: SnapshotAssertion,
) -> None:
    """Lookup emits JSON when --json is given."""
    exit_code, output, _ = invoke(
        runner,
        ["11ZKZ3", "--json"],
        sample_vehicle,
        sample_fuel,
    )
    assert exit_code == 0
    assert output == snapshot


@pytest.fixture
def minimal_vehicle() -> Vehicle:
    """Return a Vehicle with only required fields, all optionals None."""
    return Vehicle.from_dict(
        {
            "merk": "TESLA",
            "kenteken": "ABC123",
            "handelsbenaming": "MODEL 3",
        }
    )


def test_lookup_minimal_vehicle(
    runner: CliRunner,
    minimal_vehicle: Vehicle,
    snapshot: SnapshotAssertion,
) -> None:
    """Lookup renders None fields as dashes."""
    exit_code, output, _ = invoke(
        runner,
        ["ABC123"],
        minimal_vehicle,
    )
    assert exit_code == 0
    assert output == snapshot


def test_lookup_minimal_vehicle_json(
    runner: CliRunner,
    minimal_vehicle: Vehicle,
    snapshot: SnapshotAssertion,
) -> None:
    """Lookup JSON emits null for missing fields."""
    exit_code, output, _ = invoke(
        runner,
        ["ABC123", "--json"],
        minimal_vehicle,
    )
    assert exit_code == 0
    assert output == snapshot


def test_unknown_plate_handler(
    capsys: pytest.CaptureFixture[str],
    snapshot: SnapshotAssertion,
) -> None:
    """Unknown plate handler prints a panel and exits with 1."""
    handler = cli.error_handlers[RDWUnknownLicensePlateError]
    with pytest.raises(SystemExit) as exc_info:
        handler(RDWUnknownLicensePlateError("not found"))
    assert exc_info.value.code == 1
    assert capsys.readouterr().out == snapshot


def test_connection_error_handler(
    capsys: pytest.CaptureFixture[str],
    snapshot: SnapshotAssertion,
) -> None:
    """Connection error handler prints a panel and exits with 1."""
    handler = cli.error_handlers[RDWConnectionError]
    with pytest.raises(SystemExit) as exc_info:
        handler(RDWConnectionError("unreachable"))
    assert exc_info.value.code == 1
    assert capsys.readouterr().out == snapshot
