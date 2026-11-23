import subprocess, sys, tempfile, unittest, importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "heist_stats.py"

P1_LOG = """2026/11/23 10:00:00 1000 [INFO Client 1] : You have entered The Rogue Harbour.
2026/11/23 10:01:00 1001 [INFO Client 1] : You have entered Bunker.
2026/11/23 10:03:00 1002 [INFO Client 1] : You have entered The Rogue Harbour.
2026/11/23 10:03:40 1003 [INFO Client 1] : You have entered Mansion.
2026/11/23 10:05:40 1004 [INFO Client 1] : You have entered The Rogue Harbour.
2026/11/23 10:06:10 1005 [INFO Client 1] : You have entered Mansion.
2026/11/23 10:08:10 1006 [INFO Client 1] : You have entered The Rogue Harbour.
2026/11/23 10:10:00 1007 [INFO Client 1] : Вы вошли в область Заражённая Дюны.
2026/11/23 10:14:00 1008 [INFO Client 1] : Сестра Кассия: О! Как чудесно!
2026/11/23 10:14:30 1009 [INFO Client 1] : Вы вошли в область Убежище.
2026/11/23 10:15:00 1010 [INFO Client 1] : You have entered Blight-ravaged Strand.
2026/11/23 10:20:00 1011 [INFO Client 1] : Sister Cassia: The ichor pump has been destroyed!
2026/11/23 10:20:30 1012 [INFO Client 1] : You have entered Hideout.
2026/11/23 10:21:00 1013 [INFO Client 1] : @From Trader: Hi, buy Golden Oil
"""

P2_LOG = """2026/11/23 11:00:00 2000 [INFO Client 2] : You have entered The Ziggurat Encampment.
2026/11/23 11:01:00 2001 [INFO Client 2] : You have entered Trial of the Sekhemas.
2026/11/23 11:04:00 2002 [INFO Client 2] : You have entered Trial of the Sekhemas.
2026/11/23 11:08:00 2003 [INFO Client 2] : You have entered The Burning Monolith.
2026/11/23 11:12:00 2004 [INFO Client 2] : You have entered Hideout.
"""
class TestExilePace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p1 = Path(self.tmp.name) / "C1.txt"
        self.p2 = Path(self.tmp.name) / "C2.txt"
        self.emp = Path(self.tmp.name) / "Empty.txt"
        self.p1.write_text(P1_LOG, encoding="utf-8")
        self.p2.write_text(P2_LOG, encoding="utf-8")
        self.emp.write_text("broken line\n", encoding="utf-8")

        spec = importlib.util.spec_from_file_location("heist_stats", str(SCRIPT))
        self.mod = importlib.util.module_from_spec(spec)
        sys.argv = ["heist_stats.py"]
        spec.loader.exec_module(self.mod)

    def tearDown(self):
        self.tmp.cleanup()

    def test_heist(self):
        self.mod.log_path, self.mod.start_date = str(self.p1), None
        r = self.mod.stats_poe1()
        self.assertEqual((r["c"], r["bp"], r["w"]), (1, 1, 2))

    def test_blight(self):
        self.mod.log_path, self.mod.start_date = str(self.p1), None
        r = self.mod.stats_blight()
        self.assertEqual((r["bl"], r["rav"], r["wins"], r["fails"], r["oils"]), (1, 1, 1, 1, 1))

    def test_poe2(self):
        self.mod.log_path, self.mod.start_date = str(self.p2), None
        r = self.mod.stats_poe2()
        self.assertEqual((r["sek_r"], r["sek_f"], r["pins"]), (1, 2, 1))

    def test_empty(self):
        self.mod.log_path, self.mod.start_date = str(self.emp), None
        self.assertEqual(self.mod.stats_poe1()["c"], 0)
        self.assertEqual(self.mod.stats_blight()["bl"], 0)
        self.assertEqual(self.mod.stats_poe2()["maps"], 0)

    def test_cli(self):
        out = subprocess.check_output([sys.executable, str(SCRIPT), "--version"], text=True)
        self.assertIn("MuonSuzuki", out)

if __name__ == "__main__":
    unittest.main(verbosity=2)
