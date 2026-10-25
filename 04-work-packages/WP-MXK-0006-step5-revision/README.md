# WP-MXK-0006 — Revision of step 5 after independent review

The independent review of step 5 found two real holes. I reproduced both before fixing them:

- a genuine Operator signature could be reused to record a different effect than the one
  signed (a waiver replayed as an abort);
- a degenerate public key could "verify" anything.

This package closes both. It also tightens every claim the review found too strong, and adds
tests that fail if any one of the 33 defences is removed.
