"""Asynchronous Python client providing RDW vehicle information."""
from __future__ import annotations

from datetime import date, datetime, timezone

try:
    from pydantic.v1 import BaseModel, Field, validator
except ImportError:  # pragma: no cover
    from pydantic import (  # type: ignore[assignment] # pragma: no cover
        BaseModel,
        Field,
        validator,
    )

from .const import (
    VehicleInterior,
    VehicleOdometerJudgement,
    VehicleType,
)


class Vehicle(BaseModel):
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

    apk_expiration: date | None = Field(None, alias="vervaldatum_apk")
    ascription_date: date | None = Field(None, alias="datum_tenaamstelling")
    ascription_possible: bool | None = Field(None, alias="tenaamstellen_mogelijk")
    brand: str = Field(..., alias="merk")
    energy_label: str | None = Field(None, alias="zuinigheidslabel")
    engine_capacity: int | None = Field(None, alias="cilinderinhoud")
    exported: bool | None = Field(None, alias="export_indicator")
    interior: VehicleInterior | None = Field(None, alias="inrichting")
    last_odometer_registration_year: int | None = Field(
        None,
        alias="jaar_laatste_registratie_tellerstand",
    )
    liability_insured: bool | None = Field(None, alias="wam_verzekerd")
    license_plate: str = Field(..., alias="kenteken")
    list_price: int | None = Field(None, alias="catalogusprijs")
    first_admission: date | None = Field(None, alias="datum_eerste_toelating")
    mass_empty: int | None = Field(None, alias="massa_ledig_voertuig")
    mass_driveable: int | None = Field(None, alias="massa_rijklaar")
    model: str = Field(..., alias="handelsbenaming")
    number_of_cylinders: int | None = Field(None, alias="aantal_cilinders")
    number_of_doors: int | None = Field(None, alias="aantal_deuren")
    number_of_seats: int | None = Field(None, alias="aantal_zitplaatsen")
    number_of_wheelchair_seats: int | None = Field(
        None,
        alias="aantal_rolstoelplaatsen",
    )
    number_of_wheels: int | None = Field(None, alias="aantal_wielen")
    odometer_judgement: VehicleOdometerJudgement = Field(
        None,
        alias="tellerstandoordeel",
    )
    pending_recall: bool | None = Field(
        None,
        alias="openstaande_terugroepactie_indicator",
    )
    taxi: bool | None = Field(None, alias="taxi_indicator")
    vehicle_type: VehicleType | None = Field(None, alias="voertuigsoort")

    @validator(
        "apk_expiration",
        "ascription_date",
        "first_admission",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def parse_date(cls, value: str) -> date:
        """Parse date from string.

        Args:
        ----
            value: String to parse.

        Returns:
        -------
            Parsed date.
        """
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=timezone.utc).date()

    @validator(
        "ascription_possible",
        "exported",
        "liability_insured",
        "pending_recall",
        "taxi",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def parse_bool(cls, value: str) -> bool | None:
        """Parse boolean from string.

        Args:
        ----
            value: String to parse.

        Returns:
        -------
            Parsed boolean.
        """
        return value == "Ja"

    @validator("brand", "model", allow_reuse=True)
    @classmethod
    def make_pretty(cls, value: str) -> str:
        """Parse date from string.

        Args:
        ----
            value: String to make pretty.

        Returns:
        -------
            Pretty string.
        """
        return value.strip().title()

    @validator(
        "interior",
        "odometer_judgement",
        "vehicle_type",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def filter_empty(cls, value: str) -> str | None:
        """Filter out empty values.

        Args:
        ----
            value: String to filter.

        Returns:
        -------
            Filtered string.
        """
        if value in {"Niet geregistreerd", "N.v.t."}:
            return None
        return value


Vehicle.update_forward_refs()
