"""Asynchronous Python client providing RDW vehicle information."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
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

_NOT_REGISTERED = {"Niet geregistreerd", "N.v.t."}


class StringIsBoolean(SerializationStrategy):
    """Boolean serialization strategy for Dutch textual strings."""

    def serialize(self, value: bool) -> str:  # noqa: FBT001
        """Serialize a boolean to a Dutch string."""
        return "Ja" if value else "Nee"

    def deserialize(self, value: str) -> bool:
        """Deserialize a Dutch string to a boolean."""
        return value == "Ja"


class DateStrategy(SerializationStrategy):
    """String serialization strategy to handle the date format."""

    def serialize(self, value: date) -> str:
        """Serialize date to their specific format."""
        return datetime.strftime(value, "%Y%m%d")

    def deserialize(self, value: str) -> date:
        """Deserialize their date format to a date."""
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=UTC).date()


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
        engine_capacity: Engine capacity of the vehicle in CC.
        european_vehicle_category: EU vehicle category (e.g. M1, N1, L).
        exported: Whether the vehicle is exported or not.
        first_admission: First date of registration.
        first_admission_netherlands: First registration date in the Netherlands.
        interior: Interior of the vehicle.
        last_odometer_registration_year: Last year odometer was registered.
        length: Length of the vehicle in cm.
        liability_insured: Whether the vehicle is insured or not.
        license_plate: Normalized license plate of the vehicle.
        list_price: List price of the vehicle.
        mass_driveable: Mass of the vehicle when driveable in kg.
        mass_empty: Empty mass of the vehicle in kg.
        maximum_permitted_mass: Maximum permitted mass in kg.
        model: Model of the vehicle.
        number_of_cylinders: Number of cylinders of the vehicle.
        number_of_doors: Number of doors of the vehicle.
        number_of_seats: Number of seats of the vehicle.
        number_of_wheelchair_seats: Number of wheelchair seats of the vehicle.
        number_of_wheels: Number of wheels of the vehicle.
        odometer_judgement: Odometer judgement of the vehicle.
        pending_recall: Whether the vehicle has a pending recall or not.
        primary_color: Primary color of the vehicle.
        secondary_color: Secondary color of the vehicle.
        taxi: Whether the vehicle is a taxi or not.
        vehicle_type: Type of the vehicle.
        wheelbase: Wheelbase of the vehicle in cm.

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
    european_vehicle_category: str | None = field(
        default=None, metadata=field_options(alias="europese_voertuigcategorie")
    )
    exported: bool | None = field(
        default=None, metadata=field_options(alias="export_indicator")
    )
    first_admission: date | None = field(
        default=None, metadata=field_options(alias="datum_eerste_toelating")
    )
    first_admission_netherlands: date | None = field(
        default=None,
        metadata=field_options(alias="datum_eerste_tenaamstelling_in_nederland"),
    )
    interior: VehicleInterior | None = field(
        default=None, metadata=field_options(alias="inrichting")
    )
    last_odometer_registration_year: int | None = field(
        default=None,
        metadata=field_options(alias="jaar_laatste_registratie_tellerstand"),
    )
    length: int | None = field(default=None, metadata=field_options(alias="lengte"))
    liability_insured: bool | None = field(
        default=None, metadata=field_options(alias="wam_verzekerd")
    )
    list_price: int | None = field(
        default=None, metadata=field_options(alias="catalogusprijs")
    )
    mass_driveable: int | None = field(
        default=None, metadata=field_options(alias="massa_rijklaar")
    )
    mass_empty: int | None = field(
        default=None, metadata=field_options(alias="massa_ledig_voertuig")
    )
    maximum_permitted_mass: int | None = field(
        default=None,
        metadata=field_options(alias="toegestane_maximum_massa_voertuig"),
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
    primary_color: str | None = field(
        default=None, metadata=field_options(alias="eerste_kleur")
    )
    secondary_color: str | None = field(
        default=None, metadata=field_options(alias="tweede_kleur")
    )
    taxi: bool | None = field(
        default=None, metadata=field_options(alias="taxi_indicator")
    )
    vehicle_type: VehicleType | None = field(
        default=None, metadata=field_options(alias="voertuigsoort")
    )
    wheelbase: int | None = field(
        default=None, metadata=field_options(alias="wielbasis")
    )

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        """Handle some fields that have some weirdness.

        Args:
        ----
            d: The values of the model.

        Returns:
        -------
            The adjusted values of the model.

        """
        # Convert certain values to None.
        for key in (
            "eerste_kleur",
            "inrichting",
            "tellerstandoordeel",
            "tweede_kleur",
            "voertuigsoort",
        ):
            if d.get(key) in _NOT_REGISTERED:
                d[key] = None

        # Make Brand and Model pretty
        for key in ("merk", "handelsbenaming"):
            d[key] = d[key].strip().title()

        # Title-case colors
        for key in ("eerste_kleur", "tweede_kleur"):
            if d.get(key) is not None:
                d[key] = d[key].strip().title()

        return d


@dataclass
# pylint: disable-next=too-many-instance-attributes
class Fuel(DataClassORJSONMixin):
    """Object holding fuel and emission information for a vehicle.

    A vehicle can have multiple fuel entries (e.g., a hybrid has both
    a combustion engine and an electric motor).

    Attributes
    ----------
        fuel_type: Fuel type description (e.g. Benzine, Diesel, Elektriciteit).
        co2_combined: Combined CO2 emissions in g/km.
        co2_emission_class: CO2 emission class.
        consumption_combined: Combined fuel consumption in l/100km.
        consumption_city: City fuel consumption in l/100km.
        consumption_highway: Highway fuel consumption in l/100km.
        consumption_electric_wltp: Electric consumption in Wh/km (WLTP).
        emission_standard: Emission standard (e.g. EURO 5, EURO 6).
        hybrid_electric_class: Hybrid/electric class (OVC-HEV, NOVC-HEV).
        max_power: Net maximum power in kW.
        max_power_electric: Net maximum electric power in kW.
        noise_level_driving: Noise level while driving in dB.
        noise_level_stationary: Noise level while stationary in dB.
        range: Range in km.
        range_electric_city_wltp: Electric-only city range in km (WLTP).
        range_electric_wltp: Electric-only range in km (WLTP).
        range_externally_chargeable: Range when externally charged in km.

    """

    fuel_type: str = field(metadata=field_options(alias="brandstof_omschrijving"))
    co2_combined: int | None = field(
        default=None, metadata=field_options(alias="co2_uitstoot_gecombineerd")
    )
    co2_emission_class: str | None = field(
        default=None, metadata=field_options(alias="co2_emissieklasse")
    )
    consumption_combined: float | None = field(
        default=None,
        metadata=field_options(alias="brandstofverbruik_gecombineerd"),
    )
    consumption_city: float | None = field(
        default=None, metadata=field_options(alias="brandstofverbruik_stad")
    )
    consumption_highway: float | None = field(
        default=None, metadata=field_options(alias="brandstofverbruik_buiten")
    )
    consumption_electric_wltp: float | None = field(
        default=None,
        metadata=field_options(alias="elektrisch_verbruik_enkel_elektrisch_wltp"),
    )
    emission_standard: str | None = field(
        default=None, metadata=field_options(alias="uitlaatemissieniveau")
    )
    hybrid_electric_class: str | None = field(
        default=None,
        metadata=field_options(alias="klasse_hybride_elektrisch_voertuig"),
    )
    max_power: float | None = field(
        default=None, metadata=field_options(alias="nettomaximumvermogen")
    )
    max_power_electric: float | None = field(
        default=None,
        metadata=field_options(alias="netto_max_vermogen_elektrisch"),
    )
    noise_level_driving: int | None = field(
        default=None, metadata=field_options(alias="geluidsniveau_rijdend")
    )
    noise_level_stationary: int | None = field(
        default=None, metadata=field_options(alias="geluidsniveau_stationair")
    )
    range: int | None = field(default=None, metadata=field_options(alias="actieradius"))
    range_electric_city_wltp: int | None = field(
        default=None,
        metadata=field_options(alias="actie_radius_enkel_elektrisch_stad_wltp"),
    )
    range_electric_wltp: int | None = field(
        default=None,
        metadata=field_options(alias="actie_radius_enkel_elektrisch_wltp"),
    )
    range_externally_chargeable: int | None = field(
        default=None,
        metadata=field_options(alias="actieradius_extern_oplaadbaar"),
    )


@dataclass
class Recall(DataClassORJSONMixin):
    """Object holding recall information for a vehicle.

    Attributes
    ----------
        reference_code: RDW reference code for the recall.
        status: Human-readable status description.
        status_code: Single-character status code (O=open, P=repaired).

    """

    reference_code: str = field(metadata=field_options(alias="referentiecode_rdw"))
    status: str = field(metadata=field_options(alias="status"))
    status_code: str = field(metadata=field_options(alias="code_status"))
