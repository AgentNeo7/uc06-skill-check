# UC06 — Salesforce Skill Check

Qualify repeated sf apex run test JSON exports against unique execution IDs, native test outcomes and skill/host provenance.

This is a Salesforce DX prototype with actual Apex, Flow, custom-object, validation-rule and permission-set metadata. The offline Node CLI inspects Salesforce artifacts. No Python runtime is used. Source API version64.0 is an explicit compatibility target, not a claim that it is the newest API.

## Run locally

Requires Node22 or later. Use a clean checkout:

```sh
npm ci --ignore-scripts
npm test
npm run example
node src/cli.mjs --project . --config examples/config.json
```

The CLI prints JSON. `pass` means the supplied artifact satisfies the supported local check; `unknown` means coverage/evidence is incomplete; `fail` means a concrete supported check failed. CLI exit code2 means invalid input. A business finding stays in JSON; CI must gate on `status`. The UC08 example intentionally flags a synthetic sensitive-field grant, and UC10 intentionally leaves FSC mappings unknown.

## Salesforce validation

No org is accessed by the offline CLI. Validate only in an explicitly authorized development org. Replace the placeholder with its confirmed alias:

```sh
sf project deploy start --dry-run --test-level RunLocalTests --target-org explicit-sandbox --source-dir force-app
```

The package includes ReviewActionTest. **The supplied metadata and Apex test package passed native Developer-org dry-run validation.** This scoped result is separate from full functional acceptance. Test-created records roll back with Apex test transactions. The Flow is Draft. The sample action queries and updates in user mode, checks explicit synthetic correlation IDs and consent, and never calls an external service. The synthetic consent Boolean is a demo contract, not legal consent verification.

Every tool contains the same small synthetic servicing fixture so it can be cloned independently. Do not deploy all copies into one org as different applications: they intentionally use the same metadata names. Validate packages independently or share the common fixture layer. Runtime isolation and sharing/FLS require org tests with approved identities.

## Acceptance coverage

| Requirement | Original acceptance check | Current coverage | Status |
|---|---|---|---|
| UC06-R01 | Success cannot be awarded solely by the evaluated agent’s self-report. | Versioned skill and host values required with sf test execution provenance. | Partial; broader acceptance pending |
| UC06-R02 | Adapter reports actual available capabilities and unsupported controls. | Distinct repeat execution IDs and nonempty native-shaped test arrays verified. | Partial; broader acceptance pending |
| UC06-R03 | Nominal installation compatibility is distinguished from successful execution. | Failed tests/summary outcomes reject qualification; missing metadata unknown. | Partial; broader acceptance pending |
| UC06-R04 | Failures and uncertainty are included alongside successful runs. | Real host adapters and provider/version drift evaluation pending. | Partial; broader acceptance pending |
| UC06-R05 | A failing update can be held while the prior qualified version remains reproducible. | Local CLI result supports regression consumption; public host qualification unproven. | Partial; broader acceptance pending |

Real coding-host runs, actual skill version artifacts, broader task outcomes, independent qualification workloads and native org execution remain pending.

## Evidence and comparison

`evidence/frozen-oracles.json` records synthetic oracle intents before implementation. `evidence/offline-tests-final.log` records internal Node checks. Failed attempts remain beside the final log. `evidence/example-result.json` is a simulation generated from shipped metadata/test exports; it is not org evidence. Existing native Salesforce facilities are a baseline to evaluate, not an absent capability. No differentiation or independent recognition is asserted. See `evidence/sources.json` for retrieved official-source boundaries.

New code and synthetic examples were authored by AI under Balaji's Salesforce focus and publication direction. That is not evidence that Balaji personally wrote all code. His architectural review, changed decisions, native results and external use must be recorded separately before any contribution claim. No legal outcome is promised.

Shared helper: `src/common.mjs` (same reviewed source copied to standalone UC01–10); XML parser pinned by `package-lock.json`. It rejects malformed XML, DTD/entity declarations and foreign Metadata API namespaces. It is not a full Salesforce schema validator or Apex compiler.

Experimental source preview only. Full acceptance and supported release remain gated.

Native remediation: USER_MODE query results now materialize before iteration to avoid the observed native tmpVar1 query failure. DML uses a sparse Id/Status object. Tests use a Standard User with only Review_Operator permission assignment and owned synthetic records. Runtime permissions grant read/edit on the custom request and read-only consent; universally required custom fields do not accept separately configurable FLS. Sensitive notes are not granted to the operator. UC08's separate Exposure_Probe fixture is intentionally unassigned.

## Distribution

Salesforce is the primary implementation. Historical Python source is under `legacy/python-prototype`. See `RELEASE_STATUS.md` and `SALESFORCE_VALIDATION.json`. Full acceptance remains partial.
