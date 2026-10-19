import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import system_info


class ParserTests(unittest.TestCase):
    def test_parse_os_release(self):
        data = system_info.parse_os_release('NAME="Arch Linux"\nPRETTY_NAME="Arch Linux"\n')
        self.assertEqual(data["PRETTY_NAME"], "Arch Linux")

    def test_parse_cpuinfo(self):
        text = "processor\t: 0\nmodel name\t: Test CPU\n\nprocessor\t: 1\nmodel name\t: Test CPU\n"
        cpu = system_info.parse_cpuinfo(text)
        self.assertEqual(cpu["model"], "Test CPU")
        self.assertEqual(cpu["cores"], 2)

    def test_parse_meminfo(self):
        text = "MemTotal:       16000000 kB\nMemAvailable:    8000000 kB\n"
        mem = system_info.parse_meminfo_kb(text)
        self.assertEqual(mem["total_kb"], 16000000)
        self.assertEqual(mem["used_kb"], 8000000)
        self.assertEqual(mem["used_percent"], 50.0)

    def test_uptime(self):
        self.assertAlmostEqual(system_info.parse_uptime_seconds("12345.67 900.0"), 12345.67)

    def test_uptime_invalid(self):
        self.assertEqual(system_info.parse_uptime_seconds(""), 0.0)

    def test_format_duration(self):
        self.assertEqual(system_info.format_duration(90000), "1d 1h 0m")
        self.assertEqual(system_info.format_duration(3660), "1h 1m")
        self.assertEqual(system_info.format_duration(120), "2m")

    def test_collect_and_render(self):
        info = system_info.collect(["/"])
        self.assertIn("cpu", info)
        self.assertTrue(info["disks"])
        text = system_info.render(info)
        self.assertIn("kernel:", text)

    def test_cli_json(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = system_info.main(["--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertIn("distribution", payload)


if __name__ == "__main__":
    unittest.main()
