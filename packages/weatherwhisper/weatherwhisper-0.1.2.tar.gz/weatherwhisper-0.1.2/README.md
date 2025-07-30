# WeatherWhisper 🌦️

![WeatherWhisper banner](images/banner.png)

[![PyPI](https://img.shields.io/pypi/v/weatherwhisper?color=brightgreen)](https://pypi.org/project/weatherwhisper/) [![License](https://img.shields.io/github/license/yourname/weatherwhisper?color=blue)](LICENSE) [![CI](https://github.com/yourname/weatherwhisper/actions/workflows/ci.yml/badge.svg)](https://github.com/yourname/weatherwhisper/actions/workflows/ci.yml) [![Downloads](https://static.pepy.tech/badge/weatherwhisper)](https://pepy.tech/project/weatherwhisper)

**WeatherWhisper** is a lightning‑fast, cross‑platform CLI for real‑time weather data and five‑day forecasts—no browser, no bloat. Powered by the free [OpenWeatherMap](https://openweathermap.org/api) API.

---

## 📑 Table of Contents

1. [Features](#features)
2. [Quick Demo](#quick-demo)
3. [Installation](#installation)
4. [Get an API Key](#get-an-api-key)
5. [Usage](#usage)

   * [Command Reference](#command-reference)
   * [Output Formats](#output-formats)
6. [Configuration](#configuration)
7. [Caching & Rate Limits](#caching--rate-limits)
8. [Examples](#examples)
9. [Development](#development)
10. [Roadmap](#roadmap)
11. [Contributing](#contributing)
12. [License](#license)

---

## Features

* **Current conditions & 5‑day / hourly forecast** for any city or `lat,lon`
* Metric *or* Imperial units (`-u metric|imperial`)
* ANSI colour themes that match temperature & conditions *(toggle with `--no-color`)*
* ASCII art icons for common weather types *(toggle with `--no-ascii`)*
* Output views: **brief**, **detailed**, **json**, **forecast**
* Save unlimited **favourites** for one‑command lookup
* Transparent on‑disk **caching** to reduce API calls
* Sunrise / sunset, wind, humidity, pressure, visibility, clouds
* Extensible plug‑in architecture (see *Roadmap*)

---

## Installation

```bash
pip install --upgrade weatherwhisper   # Python ≥ 3.7
```

First launch creates `~/.weatherwhisper/config.ini`.

### Alternate Install

```bash
git clone https://github.com/danushgopinath/weatherwhisper.git
cd weatherwhisper
python -m venv venv && source venv/bin/activate
pip install -e .
```

---

## Get an API Key

1. Sign up at [https://openweathermap.org/api](https://openweathermap.org/api).
2. Copy the 32‑character key.
3. One‑time setup:

```bash
weatherwhisper config --api-key YOUR_KEY
```

The key is stored in `config.ini` so you only set it once.

---

## Usage

### Command Reference

| Command               | Purpose                 | Notes                   |                                  |                                       |
| --------------------- | ----------------------- | ----------------------- | -------------------------------- | ------------------------------------- |
| `current <location>`  | Current conditions      | City name or `lat,lon`  |                                  |                                       |
| `forecast <location>` | 5‑day / 3‑hour forecast | Same locations as above |                                  |                                       |
| \`favorites add       | list                    | remove\`                | Manage favourites                | 1st favourite is the default location |
| \`config show         | set\`                   | View or change config   | Any flag can be saved as default |                                       |

Run `weatherwhisper --help` or `<command> --help` for every flag.

#### Common Flags

* `-u, --units metric|imperial`  – Choose °C/m or °F/mi
* `-f, --format brief|detailed|json|forecast` – Output view
* `--no-color` – Disable ANSI colours (logs & scripts)
* `--no-ascii` – Hide ASCII weather icons
* `--cache <minutes>` – Override default cache TTL

### Output Formats

| View         | Example                                 |
| ------------ | --------------------------------------- |
| **Brief**    | ![brief](images/brief.png)              |
| **Forecast** | ![forecast](images/forecast.png)        |
| **JSON**     | `{ "temp": 15.3, "condition": "Rain" }` |

---

## Configuration

`~/.weatherwhisper/config.ini` (created on first run):

```ini
[general]
api_key = YOUR_KEY_HERE
units = metric
color = true
ascii = true
cache_minutes = 15
```

Edit by hand *or* use the CLI:

```bash
weatherwhisper config set --units imperial --no-color
weatherwhisper config show
```

![Config sample](images/config.png)

---

## Caching & Rate Limits

* All responses are cached on disk for **15 minutes** by default.
* Cache is keyed by **endpoint + location + units**.
* Pass `--cache 0` to force a live API request.

This keeps most users well below the free‐tier limit of **60 calls / minute**.

---

## Examples

```bash
# Brief, coloured output
weatherwhisper current "Paris"

# JSON for scripting
weatherwhisper current "51.5074,-0.1278" -f json | jq .temp

# Forecast grid with no ASCII art
weatherwhisper forecast "Tokyo" --no-ascii

# Use the first favourite automatically
weatherwhisper current
```

---

## Development

📁 **Repo layout**

```text
weatherwhisper/
 ├─ images/              # PNG assets (banner, output samples)
 ├─ __init__.py
 ├─ api.py               # API request & response logic
 ├─ cli.py               # Main CLI entry point
 ├─ config.py            # Config file parsing & CLI setters
 ├─ formatter.py         # Output formatting (color, ASCII)
LICENSE
pyproject.toml
setup.py
README.md
```

\### Set Up Dev Env

```bash
git clone https://github.com/danushgopinath/weatherwhisper.git
cd weatherwhisper
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"      # pytest, ruff, black, pre‑commit
pre-commit install
```

Run from source:

```bash
python -m weatherwhisper current "London"
```

Tests:

```bash
pytest -q
```

---

## Roadmap

![Plugin architecture](images/plugin_arch.png)

* 🔌 **Plugin system** – drop‑in providers (AccuWeather, WeatherKit…)
* 📈 Historical weather (paid API)
* 🚨 Severe weather alerts
* 📍 Auto‑detect location (IP/GPS)
* 🖼️ GUI wrapper (Tkinter / Electron)

Track progress in the [project board](https://github.com/danushgopinath/weatherwhisper/projects).

---

## Contributing

1. **Fork** → clone → create a feature branch.
2. `pre-commit install` (runs *black*, *ruff*, & tests automatically).
3. Write or update **tests**.
4. Open a **Pull Request** with a clear description.

All feedback & PRs are welcome—check outstanding [issues](https://github.com/danushgopinath/weatherwhisper/issues) or open a new one.

---

## License

MIT © 2025 Danush Gopinath

---

*Made with ☕ and a love of clouds.*
