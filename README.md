# Python: Asynchronous Python client providing RDW vehicle information

[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE.md)

[![Build Status][build-shield]][build]
[![Code Coverage][codecov-shield]][codecov]
[![OpenSSF Scorecard][scorecard-shield]][scorecard]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Sponsor Frenck via GitHub Sponsors][github-sponsors-shield]][github-sponsors]

[![Support Frenck on Patreon][patreon-shield]][patreon]

Asynchronous Python client providing RDW vehicle information.

## About

This package allows you to get information from the RDW
(Netherlands Vehicle Authority) about a specific vehicle by its license plate.

It queries three RDW open data datasets:

- **Vehicle information**: brand, model, color, dimensions, mass, APK status,
  and more.
- **Fuel & emissions**: fuel type, CO2, consumption, power, emission standard,
  electric range, and WLTP data.
- **Recalls**: open and resolved recall actions.

## Installation

```bash
pip install vehicle
```

## Usage

```python
import asyncio

from vehicle import RDW, Vehicle


async def main() -> None:
    """Show example of fetching RDW vehicle info from Socrata API."""
    async with RDW() as rdw:
        vehicle: Vehicle = await rdw.vehicle(license_plate="11ZKZ3")
        print(vehicle)

        # Fuel and emission data (can return multiple entries for hybrids)
        fuels = await rdw.fuel(license_plate="11ZKZ3")
        for fuel in fuels:
            print(fuel.fuel_type, fuel.co2_combined, fuel.max_power)

        # Recall status
        recalls = await rdw.recalls(license_plate="11ZKZ3")
        for recall in recalls:
            print(recall.reference_code, recall.status)


if __name__ == "__main__":
    asyncio.run(main())
```

## Command-line interface

This package ships with an optional CLI that is handy for quickly looking
up vehicle information. Install it with the `cli` extra:

```bash
pip install "vehicle[cli]"
```

Look up a vehicle by its license plate:

```bash
# Human-readable table output
vehicle 11ZKZ3

# Machine-readable JSON output
vehicle 11ZKZ3 --json

# Dashes and spaces in license plates are automatically normalized
vehicle "11-ZKZ-3"
```

Run `vehicle --help` for the full reference.

## Behavior & error handling

Each API call is a single HTTP GET to the RDW open data (Socrata) API;
the client does **not** retry on transient failures. If you need retries
with backoff, wrap the calls in your own retry loop (or use something
like [`backoff`][backoff]).

Requests are bounded by a per-call timeout, which defaults to 10 seconds
and can be overridden via the `request_timeout` constructor argument:

```python
async with RDW(request_timeout=5) as rdw:
    vehicle = await rdw.vehicle(license_plate="11ZKZ3")
```

All exceptions inherit from `RDWError`:

| Exception                     | Raised when                                            |
| ----------------------------- | ------------------------------------------------------ |
| `RDWConnectionError`          | Request timed out or the network / API was unreachable |
| `RDWUnknownLicensePlateError` | The license plate was not found in the RDW database    |
| `RDWError`                    | Any other unexpected response from the API             |

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality. The format of the log is based on
[Keep a Changelog][keepchangelog].

Releases are based on [Semantic Versioning][semver], and use the format
of `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented
based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](.github/CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The easiest way to start, is by opening a CodeSpace here on GitHub, or by using
the [Dev Container][devcontainer] feature of Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project is fully managed using the [Poetry][poetry] dependency manager. But also relies on the use of NodeJS for certain checks during development.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]
- NodeJS 24+ (including NPM)

To install all packages, including all development requirements:

```bash
npm install
poetry install
```

As this repository uses the [prek][prek] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run prek run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## Authors & contributors

The original setup of this repository is by [Franck Nijhof][frenck].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

MIT License

Copyright (c) 2021-2026 Franck Nijhof

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[backoff]: https://github.com/litl/backoff
[build-shield]: https://github.com/frenck/python-vehicle/actions/workflows/tests.yaml/badge.svg
[build]: https://github.com/frenck/python-vehicle/actions/workflows/tests.yaml
[codecov-shield]: https://codecov.io/gh/frenck/python-vehicle/branch/main/graph/badge.svg
[codecov]: https://codecov.io/gh/frenck/python-vehicle
[contributors]: https://github.com/frenck/python-vehicle/graphs/contributors
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/frenck/python-vehicle
[frenck]: https://github.com/frenck
[github-sponsors-shield]: https://frenck.dev/wp-content/uploads/2019/12/github_sponsor.png
[github-sponsors]: https://github.com/sponsors/frenck
[keepchangelog]: http://keepachangelog.com/en/1.0.0/
[license-shield]: https://img.shields.io/github/license/frenck/python-vehicle.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[patreon-shield]: https://frenck.dev/wp-content/uploads/2019/12/patreon.png
[patreon]: https://www.patreon.com/frenck
[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[prek]: https://github.com/j178/prek
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[pypi]: https://pypi.org/project/vehicle/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/vehicle
[releases-shield]: https://img.shields.io/github/release/frenck/python-vehicle.svg
[releases]: https://github.com/frenck/python-vehicle/releases
[scorecard-shield]: https://api.scorecard.dev/projects/github.com/frenck/python-vehicle/badge
[scorecard]: https://scorecard.dev/viewer/?uri=github.com/frenck/python-vehicle
[semver]: http://semver.org/spec/v2.0.0.html
