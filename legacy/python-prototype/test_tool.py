"""Internal AI-authored tests; expected examples were frozen before implementation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import tool

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / "examples" / name).read_text())

class ToolTests(unittest.TestCase):
    def test_frozen_oracles(self):
        for name, digest in read("frozen.json")["sha256"].items():
            self.assertEqual(hashlib.sha256((HERE / "examples" / name).read_bytes()).hexdigest(), digest)

    def test_positive(self):
        self.assertEqual(tool.analyze(read("input.json")), read("expected.json"))

    def test_frozen_controls(self):
        cases = HERE / "examples" / "cases.json"
        if cases.exists():
            for row in json.loads(cases.read_text()):
                with self.subTest(row["id"]):
                    self.assertEqual(tool.analyze(row["input"]), row["expected"])
        else:
            fixtures = read("input.json")["fixtures"]
            self.assertEqual({f["oracle"]["status"] for f in fixtures}, {"safe", "breaking", "unknown"})
            self.assertEqual(tool.analyze({"fixtures":fixtures})["mismatches"], 0)

    def test_deterministic_no_mutation(self):
        value = read("input.json"); saved = copy.deepcopy(value)
        self.assertEqual(tool.analyze(value), tool.analyze(copy.deepcopy(value)))
        self.assertEqual(value, saved)

    def test_cli_success_and_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output.json"
            args = [sys.executable, str(HERE / "tool.py"), "--input", str(HERE / "examples/input.json"), "--output", str(out), "--expected", str(HERE / "examples/expected.json")]
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertEqual(json.loads(out.read_text()), read("expected.json"))
            bad = Path(tmp) / "bad.json"; bad.write_text('{"wrong":true}')
            args[-1] = str(bad)
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 1)

    def test_invalid_input_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"; out = Path(tmp) / "out.json"
            for raw in ['{}', '[]', '{bad', '{"duplicate":1,"duplicate":2}', '{"nonfinite":NaN}']:
                source.write_text(raw)
                with self.subTest(raw):
                    proc = subprocess.run([sys.executable, str(HERE / "tool.py"), "--input", str(source), "--output", str(out)], capture_output=True)
                    self.assertEqual(proc.returncode, 2, proc.stderr)
                    self.assertFalse(out.exists())

    def test_no_oracle_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "data.json"; p.write_text(json.dumps(read("input.json")))
            before = p.read_bytes()
            self.assertEqual(tool.main(["--input", str(p), "--output", str(p)]), 2)
            self.assertEqual(p.read_bytes(), before)

    def test_bounded_input(self):
        with self.assertRaises(ValueError): tool.bounded([0] * 1001)
        with self.assertRaises(ValueError): tool.bounded(float("inf"))

    def test_repeated_trials_preserve_failure(self):
        x=read("input.json"); run=copy.deepcopy(x["runs"][0]); run["effects"]=["send"];x["runs"].append(run)
        r=tool.analyze(x); self.assertEqual(r["status"],"fail");self.assertEqual(r["groups"][0]["passes"],1)
    def test_missing_artifact_not_pass(self):
        x=read("input.json");x["runs"][0]["artifact"]={}
        self.assertEqual(tool.analyze(x)["status"],"unknown")

if __name__ == "__main__":
    unittest.main()
