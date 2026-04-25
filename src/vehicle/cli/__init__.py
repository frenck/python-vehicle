"""Command-line interface for looking up RDW vehicle information."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from vehicle.exceptions import RDWConnectionError, RDWUnknownLicensePlateError
from vehicle.rdw import RDW

from .async_typer import AsyncTyper

if TYPE_CHECKING:
    from vehicle.models import Fuel, Vehicle

cli = AsyncTyper(
    help="Look up vehicle information from the RDW (Netherlands Vehicle Authority).",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

LicensePlate = Annotated[
    str,
    typer.Argument(
        help="License plate of the vehicle to look up",
        show_default=False,
    ),
]

JsonFlag = Annotated[
    bool,
    typer.Option(
        "--json",
        help="Emit machine-readable JSON output",
    ),
]

VEHICLE_FIELD_LABELS: dict[str, str] = {
    "license_plate": "License plate",
    "brand": "Brand",
    "model": "Model",
    "vehicle_type": "Vehicle type",
    "interior": "Interior",
    "primary_color": "Primary color",
    "secondary_color": "Secondary color",
    "first_admission": "First admission",
    "first_admission_netherlands": "First admission (NL)",
    "apk_expiration": "APK expiration",
    "ascription_date": "Ascription date",
    "ascription_possible": "Ascription possible",
    "european_vehicle_category": "EU category",
    "engine_capacity": "Engine capacity (cc)",
    "number_of_cylinders": "Cylinders",
    "number_of_doors": "Doors",
    "number_of_seats": "Seats",
    "number_of_wheelchair_seats": "Wheelchair seats",
    "number_of_wheels": "Wheels",
    "length": "Length (cm)",
    "wheelbase": "Wheelbase (cm)",
    "mass_empty": "Mass empty (kg)",
    "mass_driveable": "Mass driveable (kg)",
    "maximum_permitted_mass": "Max permitted mass (kg)",
    "list_price": "List price",
    "energy_label": "Energy label",
    "odometer_judgement": "Odometer judgement",
    "last_odometer_registration_year": "Last odometer year",
    "exported": "Exported",
    "liability_insured": "Liability insured",
    "pending_recall": "Pending recall",
    "taxi": "Taxi",
}

FUEL_FIELD_LABELS: dict[str, str] = {
    "fuel_type": "Fuel type",
    "max_power": "Power (kW)",
    "max_power_electric": "Electric power (kW)",
    "emission_standard": "Emission standard",
    "co2_combined": "CO\u2082 combined (g/km)",
    "co2_emission_class": "CO\u2082 emission class",
    "consumption_combined": "Consumption combined (l/100km)",
    "consumption_city": "Consumption city (l/100km)",
    "consumption_highway": "Consumption highway (l/100km)",
    "consumption_electric_wltp": "Electric consumption (Wh/km)",
    "range": "Range (km)",
    "range_electric_wltp": "Electric range WLTP (km)",
    "range_electric_city_wltp": "Electric range city WLTP (km)",
    "range_externally_chargeable": "Range ext. chargeable (km)",
    "hybrid_electric_class": "Hybrid/electric class",
    "noise_level_driving": "Noise driving (dB)",
    "noise_level_stationary": "Noise stationary (dB)",
}


@cli.error_handler(RDWUnknownLicensePlateError)
def unknown_plate_handler(_: RDWUnknownLicensePlateError) -> None:
    """Handle unknown license plate errors."""
    message = """
    The provided license plate was not found in the RDW database.
    Please double-check the license plate and try again.
    """
    panel = Panel(
        message,
        expand=False,
        title="License plate not found",
        border_style="red bold",
    )
    console.print(panel)
    sys.exit(1)


@cli.error_handler(RDWConnectionError)
def connection_error_handler(_: RDWConnectionError) -> None:
    """Handle connection errors."""
    message = """
    Could not connect to the RDW API. Please check your internet
    connection and try again.
    """
    panel = Panel(
        message,
        expand=False,
        title="Connection error",
        border_style="red bold",
    )
    console.print(panel)
    sys.exit(1)


def _format_value(value: object) -> str:
    """Format a vehicle field value for display."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def _object_to_dict(obj: Vehicle | Fuel) -> dict[str, object]:
    """Convert a dataclass to a JSON-serializable dict with English keys."""
    # pylint: disable-next=import-outside-toplevel
    from dataclasses import fields  # noqa: PLC0415

    result: dict[str, object] = {}
    for f in fields(obj):
        val = getattr(obj, f.name)
        if val is None:
            result[f.name] = None
        elif hasattr(val, "isoformat"):
            result[f.name] = val.isoformat()
        elif hasattr(val, "value"):
            result[f.name] = val.value
        elif isinstance(val, bool):
            result[f.name] = val
        else:
            result[f.name] = val
    return result


@cli.command()
async def lookup(
    license_plate: LicensePlate,
    output_json: JsonFlag = False,
) -> None:
    """Look up vehicle information by license plate."""
    async with RDW() as rdw:
        vehicle = await rdw.vehicle(license_plate=license_plate)
        fuels = await rdw.fuel(license_plate=license_plate)

    if output_json:
        payload = _object_to_dict(vehicle)
        payload["fuel"] = [_object_to_dict(f) for f in fuels]
        typer.echo(json.dumps(payload, indent=2))
        return

    table = Table(title=f"Vehicle {vehicle.license_plate}")
    table.add_column("Field", style="cyan bold")
    table.add_column("Value")

    for field_name, label in VEHICLE_FIELD_LABELS.items():
        value = getattr(vehicle, field_name, None)
        table.add_row(label, _format_value(value))

    console.print(table)

    for fuel in fuels:
        fuel_table = Table(title=f"Fuel: {fuel.fuel_type}")
        fuel_table.add_column("Field", style="cyan bold")
        fuel_table.add_column("Value")

        for field_name, label in FUEL_FIELD_LABELS.items():
            value = getattr(fuel, field_name, None)
            if value is not None:
                fuel_table.add_row(label, _format_value(value))

        console.print(fuel_table)
