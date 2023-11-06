"""Asynchronous Python client providing RDW vehicle information."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import SerializationStrategy

from .const import (
    VehicleInterior,
    VehicleOdometerJudgement,
    VehicleType,
)


class StringIsBoolean(SerializationStrategy):
    """Boolean serialization strategy for Dutch textual strings."""

    def serialize(self, value: bool) -> str:  # noqa: FBT001
        """Serialize a boolean to an Dutch string."""
        return "Ja" if value else "Nee"

    def deserialize(self, value: str) -> bool:
        """Deserialize an Dutch string to a boolean."""
        return value == "Ja"


class DateStrategy(SerializationStrategy):
    """String serialization strategy to handle the date format."""

    def serialize(self, value: date) -> str:
        """Serialize date to their specific format."""
        return datetime.strftime(value, "%Y%m%d")

    def deserialize(self, value: str) -> date:
        """Deserialize their date format to a date."""
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=timezone.utc).date()


@dataclass
# pylint: disable-next=too-many-instance-attributes
class Vehicle(DataClassORJSONMixin):
    """Object holding vehicle information.

    Attributes
    ----------
        apk_expiration: Expiry date of the APK.
        ascription_date: Date of naming registration of the vehicle.
        ascription_possible: Whether the vehicle is nameable or not.
        brand: Brand of the vehicle.
        energy_label: Energy label of the vehicle.
        engine_capacity: Engine capacity of the vehicle in CC
        exported: Whether the vehicle is exported or not.
        first_admission: First date of registration.
        interior: Interior of the vehicle.
        last_odometer_registration_year: Last year odometer was registered.
        liability_insured: Whether the vehicle is insured or not.
        license_plate: Normalized license plate of the vehicle.
        list_price: List price of the vehicle.
        mass_driveable: Mass of the vehicle when driveable in KG.
        mass_empty: Empty mass of the vehicle in KG.
        model: Model of the vehicle.
        number_of_cylinders: Number of cylinders of the vehicle.
        number_of_doors: Number of doors of the vehicle.
        number_of_seats: Number of seats of the vehicle.
        number_of_wheelchair_seats: Number of wheelchair seats of the vehicle.
        number_of_wheels: Number of wheels of the vehicle.
        odometer_judgement: Odometer judgement of the vehicle.
        pending_recall: Whether the vehicle has a pending recall or not.
        taxi: Whether the vehicle is a taxi or not.
        vehicle_type: Type of the vehicle.
    """

    # pylint: disable-next=too-few-public-methods
    class Config(BaseConfig):
        """Mashumaro configuration."""

        serialization_strategy = {bool: StringIsBoolean(), date: DateStrategy()}  # noqa: RUF012
        serialize_by_alias = True

    brand: str = field(metadata=field_options(alias="merk"))
    license_plate: str = field(metadata=field_options(alias="kenteken"))
    model: str = field(metadata=field_options(alias="handelsbenaming"))
    apk_expiration: date | None = field(
        default=None, metadata=field_options(alias="vervaldatum_apk")
    )
    ascription_date: date | None = field(
        default=None, metadata=field_options(alias="datum_tenaamstelling")
    )
    ascription_possible: bool | None = field(
        default=None, metadata=field_options(alias="tenaamstellen_mogelijk")
    )
    energy_label: str | None = field(
        default=None, metadata=field_options(alias="zuinigheidslabel")
    )
    engine_capacity: int | None = field(
        default=None, metadata=field_options(alias="cilinderinhoud")
    )
    exported: bool | None = field(
        default=None, metadata=field_options(alias="export_indicator")
    )
    interior: VehicleInterior | None = field(
        default=None, metadata=field_options(alias="inrichting")
    )
    last_odometer_registration_year: int | None = field(
        default=None,
        metadata=field_options(alias="jaar_laatste_registratie_tellerstand"),
    )
    liability_insured: bool | None = field(
        default=None, metadata=field_options(alias="wam_verzekerd")
    )
    list_price: int | None = field(
        default=None, metadata=field_options(alias="catalogusprijs")
    )
    first_admission: date | None = field(
        default=None, metadata=field_options(alias="datum_eerste_toelating")
    )
    mass_empty: int | None = field(
        default=None, metadata=field_options(alias="massa_ledig_voertuig")
    )
    mass_driveable: int | None = field(
        default=None, metadata=field_options(alias="massa_rijklaar")
    )
    number_of_cylinders: int | None = field(
        default=None, metadata=field_options(alias="aantal_cilinders")
    )
    number_of_doors: int | None = field(
        default=None, metadata=field_options(alias="aantal_deuren")
    )
    number_of_seats: int | None = field(
        default=None, metadata=field_options(alias="aantal_zitplaatsen")
    )
    number_of_wheelchair_seats: int | None = field(
        default=None,
        metadata=field_options(alias="aantal_rolstoelplaatsen"),
    )
    number_of_wheels: int | None = field(
        default=None, metadata=field_options(alias="aantal_wielen")
    )
    odometer_judgement: VehicleOdometerJudgement | None = field(
        default=None,
        metadata=field_options(alias="tellerstandoordeel"),
    )
    pending_recall: bool | None = field(
        default=None,
        metadata=field_options(alias="openstaande_terugroepactie_indicator"),
    )
    taxi: bool | None = field(
        default=None, metadata=field_options(alias="taxi_indicator")
    )
    vehicle_type: VehicleType | None = field(
        default=None, metadata=field_options(alias="voertuigsoort")
    )

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        """Handle some fields that have some weirdness.

        Args:
        ----
            data: The values of the model.

        Returns:
        -------
            The adjusted values of the model.
        """
        # Convert certain values to None.
        for key in ("inrichting", "tellerstandoordeel", "voertuigsoort"):
            if d.get(key) in {"Niet geregistreerd", "N.v.t."}:
                d[key] = None

        # Make Brand and Model pretty
        for key in ("merk", "handelsbenaming"):
            d[key] = d[key].strip().title()

        return d
