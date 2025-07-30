# python-ridewithgps

A simple Python client for the [RideWithGPS API](https://ridewithgps.com/api).

Note: This client isn't used for a lot yet, so it may not work quite right. Read
the code before you use it, and report any bugs you find.

Also Note: The Ride With GPS API is JSON based and under active development. It
doesn't have full documentation published, and the best way to figure out how
things work is to use the dev tools in your browser to watch actual requests.

[![PyPI version](https://img.shields.io/pypi/v/ridewithgps.svg)](https://pypi.org/project/ridewithgps/)
[![PyPI downloads](https://img.shields.io/pypi/dm/ridewithgps.svg)](https://pypi.org/project/ridewithgps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/ridewithgps.svg)](https://pypi.org/project/ridewithgps/)

[![black](https://github.com/ckdake/python-ridewithgps/actions/workflows/black.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/black.yml)
[![flake8](https://github.com/ckdake/python-ridewithgps/actions/workflows/flake8.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/flake8.yml)
[![mypy](https://github.com/ckdake/python-ridewithgps/actions/workflows/mypy.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/mypy.yml)
[![pylint](https://github.com/ckdake/python-ridewithgps/actions/workflows/pylint.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/pylint.yml)
[![pytest](https://github.com/ckdake/python-ridewithgps/actions/workflows/pytest.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/pytest.yml)

## Features

- Authenticates with the [RideWithGPS API](https://ridewithgps.com/api)
- Makes any API request, get or put, to the API.
- Built-in rate limiting

## Installation

The package is published on [PyPI](https://pypi.org/project/ridewithgps/).

---

## Usage

First, install the package:

```sh
pip install ridewithgps
```

Then, in your Python code:

```python
from ridewithgps import RideWithGPS

client = RideWithGPS(api_key="yourapikey")

# Authenticate client and return user_info as an object
try:
    user_info = client.authenticate(email="your@email.com", password="yourpassword")
except RideWithGPSAPIError as e:
    print("API error:", e)
    # Optionally inspect e.response for more details

print(user_info.id, user_info.display_name)

# Update the name of an activity (trip)
activity_id = "123456"
new_name = "Morning Ride"
response = client.put(
    f"/trips/{activity_id}.json",
    {"name": new_name}
)
updated_name = response.trip.name if hasattr(response, "trip") else None
if updated_name == new_name:
    print(f"Activity name updated to: {updated_name}")
else:
    print("Failed to update activity name.")

# Get a list of 20 rides for this user (returned as objects)
rides = client.get(f"/users/{user_info.id}/trips.json", {
    "offset": 0,
    "limit": 20
})
for ride in rides.results:
    print(ride.name, ride.id)

# Get the gear, and update an activity
gear = {}
gear_results = client.get(f"/users/{user_info.id}/gear.json", {
    "offset": 0,
    "limit": 100
}).results
for g in gear_results:
    gear[g.id] = g.nickname
print(gear)

gear_id = "example"
activity_id = "123456"
response = client.put(
    f"/trips/{activity_id}.json",
    {"gear_id": gear_id}
)
if hasattr(response, "trip") and getattr(response.trip, "gear_id", None) == gear_id:
    print("Gear updated successfully!")
else:
    print("Failed to update gear.")
```

**Note:**  
- All API responses are automatically converted from JSON to Python objects with attribute access.
- You must provide your own RideWithGPS credentials and API key.
- The `get`, `put`, `post`, and `delete` methods are the recommended interface for making API requests; see the code and [RideWithGPS API docs](https://ridewithgps.com/api) for available endpoints and parameters.

---

## Development

### Set up environment

If you use this as VS Dev Container, you can skip using a venv.

```sh
python3 -m venv env
source env/bin/activate
pip install -r requirements-dev.txt
```

Or, for local development with editable install:

```sh
git clone https://github.com/ckdake/ridewithgps.git
cd ridewithgps
pip install -e . -r requirements-dev.txt
```

### Run tests

```sh
python -m pytest --cov=ridewithgps --cov-report=term-missing -v
```

### Linting and Formatting

Run these tools locally to check and format your code:

- **pylint** (static code analysis):

    ```sh
    pylint ridewithgps
    ```

- **flake8** (style and lint checks):

    ```sh
    flake8 ridewithgps
    ```

- **black** (auto-formatting):

    ```sh
    black ridewithgps
    ```

- **mypy** (type checking):

    ```sh
    mypy ridewithgps
    ```

### Updating Integration Cassettes

If you need to update the VCR cassettes for integration tests:

1. **Set required environment variables:**
   - `RIDEWITHGPS_EMAIL`
   - `RIDEWITHGPS_PASSWORD`
   - `RIDEWITHGPS_KEY`

   Example:
   ```sh
   export RIDEWITHGPS_EMAIL=your@email.com
   export RIDEWITHGPS_PASSWORD=yourpassword
   export RIDEWITHGPS_KEY=yourapikey
   ```

2. **Run the integration test to generate a new cassette:**
   ```sh
   python -m pytest --cov=ridewithgps --cov-report=term-missing -v
   ```

3. **Scrub sensitive data from the cassette:**
   ```sh
   python scripts/scrub_cassette.py
   ```
   - This will back up your cassette to `ridewithgps_integration.yaml.original` (if not already present).
   - The sanitized cassette will overwrite `ridewithgps_integration.yaml`.

4. **Re-run tests to verify:**
   ```sh
   python -m pytest --cov=ridewithgps --cov-report=term-missing -v
   ```

### Publishing to PyPI

To publish a new version of this package to [PyPI](https://pypi.org/):

1. **Update the version number**  
   Edit `pyproject.toml` and `setup.py` and increment the version.

2. **Install build tools**  
   ```sh
   pip install -r requirements-dev.txt
   ```

3. **Build the distribution**  
   ```sh
   python -m build
   ```
   This will create `dist/ridewithgps-<version>.tar.gz` and `.whl` files.

4. **Check the distribution (optional but recommended)**  
   ```sh
   twine check dist/*
   ```

5. **Upload to PyPI**  
   ```sh
   twine upload dist/*
   ```
   You will be prompted for your PyPI API key.

6. **Open your package on PyPI (optional)**  
   ```sh
   $BROWSER https://pypi.org/project/ridewithgps/
   ```

**Note:**  
- Configure your `~/.pypirc` is configured if you want to avoid entering credentials each time.
- For test uploads, use `twine upload --repository testpypi dist/*` and visit [TestPyPI](https://test.pypi.org/).

---

- [PyPI: ridewithgps](https://pypi.org/project/ridewithgps/)
- [RideWithGPS API documentation](https://ridewithgps.com/api)

---

## License

MIT License

---

*This project is not affiliated with or endorsed by RideWithGPS.*
