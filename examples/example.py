# pylint: disable=W0621
"""Asynchronous Python client providing RDW vehicle information."""

import asyncio

from vehicle import RDW, Vehicle


async def main():
    """Show example of fetching RDW vehicle info from Socrata API."""
    async with RDW() as rdw:
        vehicle: Vehicle = await rdw.vehicle(license_plate="11ZKZ3")
        print(vehicle)

        vehicle: Vehicle = await rdw.vehicle(license_plate="0001TJ")
        print(vehicle)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
