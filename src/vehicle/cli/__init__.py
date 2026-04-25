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
    from vehicle.models import Vehicle

cli = AsyncTyper(
    help="Look up vehicle information from the RDW (Netherlands Vehicle Authority).",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

JsonFlag = Annotated[
    bool,
    typer.Option(
        "--json",
        help="Emit machine-readable JSON output",
    ),
]

FIELD_LABELS: dict[str, str] = {
    "license_plate": "License plate",
    "brand": "Brand",
    "model": "Model",
    "vehicle_type": "Vehicle type",
    "interior": "Interior",
    "first_admission": "First admission",
    "apk_expiration": "APK expiration",
    "ascription_date": "Ascription date",
    "ascription_possible": "Ascription possible",
    "engine_capacity": "Engine capacity (cc)",
    "number_of_cylinders": "Cylinders",
    "number_of_doors": "Doors",
    "number_of_seats": "Seats",
    "number_of_wheelchair_seats": "Wheelchair seats",
    "number_of_wheels": "Wheels",
    "mass_empty": "Mass empty (kg)",
    "mass_driveable": "Mass driveable (kg)",
    "list_price": "List price",
    "energy_label": "Energy label",
    "odometer_judgement": "Odometer judgement",
    "last_odometer_registration_year": "Last odometer year",
    "exported": "Exported",
    "liability_insured": "Liability insured",
    "pending_recall": "Pending recall",
    "taxi": "Taxi",
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


def _vehicle_to_dict(vehicle: Vehicle) -> dict[str, object]:
    """Convert a Vehicle to a JSON-serializable dict with English keys."""
    # pylint: disable-next=import-outside-toplevel
    from dataclasses import fields  # noqa: PLC0415

    result: dict[str, object] = {}
    for f in fields(vehicle):
        val = getattr(vehicle, f.name)
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
    license_plate: Annotated[
        str,
        typer.Argument(
            help="License plate of the vehicle to look up",
            show_default=False,
        ),
    ],
    output_json: JsonFlag = False,
) -> None:
    """Look up vehicle information by license plate."""
    async with RDW() as rdw:
        vehicle = await rdw.vehicle(license_plate=license_plate)

    if output_json:
        typer.echo(json.dumps(_vehicle_to_dict(vehicle), indent=2))
        return

    table = Table(
        title=f"Vehicle {vehicle.license_plate}",
    )
    table.add_column("Field", style="cyan bold")
    table.add_column("Value")

    for field_name, label in FIELD_LABELS.items():
        value = getattr(vehicle, field_name, None)
        table.add_row(label, _format_value(value))

    console.print(table)
