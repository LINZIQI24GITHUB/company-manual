from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ManualRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        result = subprocess.run(
            [sys.executable, "bin/manual.py", "--all", "--out", str(cls.out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + "\n" + result.stderr)
        cls.nvda = (cls.out / "manual-nvda.html").read_text(encoding="utf-8")
        cls.zjxc = (cls.out / "manual-zjxc.html").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_outputs_exist(self) -> None:
        self.assertIn("NVIDIA", self.nvda)
        self.assertIn("中际旭创", self.zjxc)
        self.assertGreater(len(self.nvda), 20_000)
        self.assertGreater(len(self.zjxc), 20_000)

    def test_no_fixed_page_wrappers(self) -> None:
        for html in (self.nvda, self.zjxc):
            self.assertNotIn('<article class="page">', html)
            self.assertIn('class="cover-page', html)
            self.assertIn('class="entry"', html)

    def test_no_slogan_or_badge(self) -> None:
        for html in (self.nvda, self.zjxc):
            self.assertNotIn("A company is not a score", html)
            self.assertNotIn("FACTS ONLY", html)
            self.assertNotIn("只列事实", html)

    def test_sources_present(self) -> None:
        self.assertIn("SEC EDGAR", self.nvda)
        self.assertIn("东方财富", self.zjxc)

    def test_conditional_sections(self) -> None:
        # NVIDIA has dividends/buybacks; the A-share demo has segment data.
        self.assertIn("Capital allocation", self.nvda)
        self.assertIn("业务结构", self.zjxc)
        self.assertNotIn("业务结构", self.nvda)


if __name__ == "__main__":
    unittest.main()
