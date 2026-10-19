# linux-system-info

Print a compact summary of the machine you are on: distribution, kernel, CPU model
and cores, memory usage, uptime and disk usage for the main mount points. Works
with plain `/proc` and standard library calls, and can emit JSON for scripts.

## Features

- Parses `/proc/cpuinfo`, `/proc/meminfo`, `/proc/uptime` and `/etc/os-release`.
- Disk usage through `shutil.disk_usage` for `/` and any extra mount points.
- Human-readable table or `--json`.
- Parser functions are unit-tested with fixture text, so tests run anywhere.

## Installation

```bash
git clone https://github.com/victor-harden/linux-system-info.git
cd linux-system-info
```

## Usage

```bash
python3 system_info.py
python3 system_info.py --json
python3 system_info.py --paths / /home
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
