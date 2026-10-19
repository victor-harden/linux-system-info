#!/usr/bin/env python3
"""Compact Linux system summary."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

CPUINFO = Path("/proc/cpuinfo")
MEMINFO = Path("/proc/meminfo")
UPTIME = Path("/proc/uptime")
OS_RELEASE = Path("/etc/os-release")


def parse_os_release(text: str) -> dict:
    data = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def parse_cpuinfo(text: str) -> dict:
    model = None
    cores = 0
    for line in text.splitlines():
        if line.startswith("processor"):
            cores += 1
        elif line.lower().startswith("model name") and model is None:
            model = line.split(":", 1)[1].strip()
    return {"model": model or "unknown", "cores": cores}


def parse_meminfo_kb(text: str) -> dict:
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        parts = rest.split()
        if parts and parts[0].isdigit():
            values[key.strip()] = int(parts[0])
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    used = max(total - available, 0)
    return {"total_kb": total, "available_kb": available, "used_kb": used,
            "used_percent": round(100 * used / total, 1) if total else 0.0}


def parse_uptime_seconds(text: str) -> float:
    try:
        return float(text.split()[0])
    except (IndexError, ValueError):
        return 0.0


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def collect(paths) -> dict:
    os_release = parse_os_release(read_text(OS_RELEASE))
    cpu = parse_cpuinfo(read_text(CPUINFO))
    memory = parse_meminfo_kb(read_text(MEMINFO))
    uptime = parse_uptime_seconds(read_text(UPTIME))
    disks = []
    for path in paths:
        try:
            usage = shutil.disk_usage(path)
        except OSError:
            continue
        disks.append({
            "path": path,
            "total_gb": round(usage.total / 1e9, 1),
            "used_gb": round(usage.used / 1e9, 1),
            "used_percent": round(100 * usage.used / usage.total, 1) if usage.total else 0.0,
        })
    return {
        "distribution": os_release.get("PRETTY_NAME", "unknown"),
        "kernel": read_text(Path("/proc/sys/kernel/osrelease")).strip() or "unknown",
        "cpu": cpu,
        "memory": memory,
        "uptime_seconds": uptime,
        "disks": disks,
    }


def render(info: dict) -> str:
    mem = info["memory"]
    lines = [
        f"distribution: {info['distribution']}",
        f"kernel:       {info['kernel']}",
        f"cpu:          {info['cpu']['model']} ({info['cpu']['cores']} cores)",
        f"memory:       {mem['used_kb'] // 1024} MiB used of {mem['total_kb'] // 1024} MiB"
        f" ({mem['used_percent']}%)",
        f"uptime:       {format_duration(info['uptime_seconds'])}",
    ]
    for disk in info["disks"]:
        lines.append(f"disk {disk['path']:<8} {disk['used_gb']} GB used of "
                     f"{disk['total_gb']} GB ({disk['used_percent']}%)")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Linux system summary")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths", nargs="+", default=["/"])
    args = parser.parse_args(argv)

    info = collect(args.paths)
    print(json.dumps(info, indent=2) if args.json else render(info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
