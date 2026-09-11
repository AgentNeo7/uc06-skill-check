"""AI-authored deterministic local prototype. Synthetic checks do not verify Salesforce."""
import argparse
import json
import math
from pathlib import Path
import sys


def need(value, kind, name):
    if not isinstance(value, kind) or (kind in (int, float) and isinstance(value, bool)):
        raise ValueError("invalid " + name)
    return value


def unique(items, key):
    values = [need(x[key], str, key) for x in items]
    if any(not x for x in values) or len(set(values)) != len(values):
        raise ValueError("duplicate or empty " + key)


def flag(value, name):
    if type(value) is not bool:
        raise ValueError("invalid boolean " + name)
    return value


def result(status, **data):
    return dict(status=status, evidence_status="simulated", **data)


def bounded(value, depth=0):
    if depth > 30:
        raise ValueError("nesting exceeds 30")
    if isinstance(value, (list, dict)):
        if len(value) > 1000:
            raise ValueError("container exceeds 1000 entries")
        for x in value.values() if isinstance(value, dict) else value:
            bounded(x, depth + 1)
    if type(value) is int and value.bit_length() > 512:
        raise ValueError("integer exceeds supported numeric envelope")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite number")


def load(path):
    if path.stat().st_size > 2_000_000:
        raise ValueError("input exceeds 2MB")
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate JSON key")
            out[k] = v
        return out
    value = json.loads(path.read_text(), object_pairs_hook=pairs)
    bounded(value)
    return need(value, dict, "root")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected", type=Path, help="Optional exact comparison; mismatch exits 1")
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve() or (args.expected and args.expected.resolve() == args.output.resolve()):
            raise ValueError("output must not overwrite input or oracle")
        report = analyze(load(args.input))
        payload = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
        expected = load(args.expected) if args.expected else None
        args.output.write_text(payload)
        return 1 if expected is not None and report != expected else 0
    except (ValueError, TypeError, KeyError, IndexError, OSError, RecursionError) as exc:
        print("invalid input/execution: " + str(exc), file=sys.stderr)
        return 2

def analyze(data):
    matrix = need(data["matrix"], list, "matrix")
    contracts = need(data["contracts"], dict, "contracts")
    runs = need(data["runs"], list, "runs")
    keys = [tuple(row[k] for k in ["host", "task", "version"]) for row in matrix]
    if not keys or len(keys) != len(set(keys)): raise ValueError("matrix must have unique rows")
    for run in runs:
        if tuple(run[k] for k in ["host", "task", "version"]) not in keys: raise ValueError("run outside declared matrix")
    groups = []
    for row, key in zip(matrix, keys):
        contract = contracts[row["task"]]
        wanted = need(contract["artifact"], dict, "artifact contract")
        forbidden = need(contract["forbidden_effects"], list, "forbidden_effects")
        selected = [r for r in runs if tuple(r[k] for k in ["host", "task", "version"]) == key]
        passed, failed, unknown = 0, 0, 0 if selected else 1
        for run in selected:
            complete = flag(run["complete"], "complete")
            artifact = need(run["artifact"], dict, "artifact")
            effects = need(run["effects"], list, "effects")
            # Evaluated agent self-report never supplies acceptance evidence.
            prohibited = bool(set(effects) & set(forbidden))
            wrong = any(k in artifact and (type(artifact[k]) is not type(v) or artifact[k] != v) for k,v in wanted.items())
            if prohibited or wrong: failed += 1
            elif not complete or not wanted or any(k not in artifact for k in wanted): unknown += 1
            else: passed += 1
        groups.append(dict(row, passes=passed, failures=failed, unknown=unknown))
    return result("fail" if any(g["failures"] for g in groups) else "unknown" if any(g["unknown"] for g in groups) else "pass", groups=groups)

if __name__ == "__main__":
    sys.exit(main())
