# UC06 — Salesforce Skill Check

Aggregate repeated synthetic host/task/version runs against declared artifact assertions and forbidden effects; ignore agent self-reported success. It does not execute coding hosts.

Distribution: **independent-software-prototype**. Status: local_prototype. Full catalog requirements remain partial. This is useful local tooling with no claim of novelty, production readiness or independent validation.

## Run

Requires Python 3.13 (checked with 3.13.14), standard library only. Copy this whole folder anywhere; no parent repository imports or installed packages are required.

```sh
python3.13 tool.py --input examples/input.json --output result.json --expected examples/expected.json
python3.13 -m unittest -v test_tool.py
```

`--expected` is optional and compares the complete output against an explicit oracle. Exit 0 means report generation completed; it can include failures or unknowns. Exit 1 means the explicit comparison mismatched. Exit 2 means invalid input or execution error. The output never authorizes a deployment. Root input must be an object, at most 2 MB, with at most 1,000 members per container and 30 levels. Duplicate JSON keys and nonfinite numbers are rejected. Output cannot overwrite the input or oracle.

## Input and evidence

`examples/input.json` demonstrates the complete input contract for this bounded utility. `examples/expected.json` is the frozen expected result. Additional positive, negative and unknown examples live in `examples/cases.json` (UC02 instead reuses 24 original fixtures). `examples/frozen.json` pins their hashes before implementation. `test_tool.py` adds adversarial checks. `checks.json` records actual checks and outcomes.

All example records, identities, outputs and business scenarios are synthetic. Input observations are assertions supplied by the caller; this tool does not independently collect them. Reports label scenario evidence simulated. Internal AI-authored oracles are separate from generated outputs but are not independent evaluation.

## Limits and remaining acceptance

Assertions and run evidence are synthetic and caller-supplied. No deployment validation or independently controlled host execution. No statistical confidence calculation.

`requirements.json` preserves the five original requirement rows, acceptance text, bounded coverage, checks and remaining blockers. `capability.json` records scope and release state. No full requirement is certified by a small fixture suite. Native behavior, domain authority, real integration, independent reproduction and maintainable releases remain gated.

Comparator to evaluate: Installation checks + single-org CI; sf-skills/ADLC/SF Pi workflows. Current features have not been independently benchmarked by this prototype. Sources in `capability.json` are catalog research leads except UC03, whose pinned public-source inspection is in `research-sources.json` and `research.md`.

## Authorship and rights

AI authored the code, examples and internal tests in this run. Balaji supplied the portfolio direction and constraints; this does not attribute all implementation work to him. No private employer, customer or petition records appear in these examples. Original code is licensed under MIT; see LICENSE. No permission to publish third-party or employer-owned assets is implied.

## Source preview status

Experimental offline source; scoped tests passed, full original acceptance is incomplete. See [release status](RELEASE_STATUS.md), [checks](release-checks.json), [requirements](requirements.json) and [attribution](ATTRIBUTION.md). No production, independent-validation or differentiation claim.
