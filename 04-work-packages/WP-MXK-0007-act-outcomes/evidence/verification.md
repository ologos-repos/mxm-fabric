# WP-MXK-0007 verification

## Follow-up findings and their disposition

| # | Finding | Checked | Disposition |
|---|---|---|---|
| 1 | A non-mapping tool return raises past the port | **Not reproduced.** `Broker.execute` wraps every result as `{"tool", "receipt"}`, so a tool returning `None` is handled. | No change. |
| 2 | An evidence write failure after an effect is ignored | Confirmed by code reading | `evidence_unwritable` halts; the next kernel closes the obligation as `unknown` (test: an_unwritable_evidence_record_halts) |
| 3 | The logged decision of a failed effect stays `allow` | Confirmed | Defined: the logged decision is the authorization, and the closing record's `outcome` is the result (SPEC §8) |
| 4 | An unsigned no-effect principal record passes replay | **Reproduced** | Principal records must be signed except unverified denials; attribution is checked (5 forgery cases) |
| 5 | SPEC §7 vs §8 anchor claims | Confirmed | Reconciled: the anchor does not prevent appends; kernel records are not authenticated |
| 6 | An obligation is stranded after an anchor-failure halt | Confirmed | `not_executed` is recorded at the halt; any orphan is closed as `unknown` on catch-up |

## Suites

- `python3 -m pytest -q 05-mxm-construct`: all pass, with 3 strict xfails (F-08, F-18, F-20).
- The stdlib runner on the enforcement suites reports 161 passed and 3 xfailed, matching pytest
  and pinned by the release test.

## Mutation check (`evidence/mutations.py`, run from `05-mxm-construct/means/`)

All 40 defences fail the suite when disabled. On the first run, 10 older defences were not
caught. The new principal and outcome checks rejected the older tests' forgeries first,
because those forgeries named no principal and stated no outcome, so each test no longer
isolated its own defence.

`forge()` now makes a forgery valid in every respect except the one under test. With that
change, each of the 40 is caught at its own test.

Human-Curated, AI-Enabled (HCAE)
