# WP-MXK-0005 — Signed act-bound authorizations and one event log

Makes Operator and Advisor authority something the kernel can check rather than trust.
Each Operator or Advisor act needs a signature from that person's own key. The signature
covers exactly that act, on that unit, once. The kernel keeps only public keys, so nothing
that can read its files can forge one.

Everything the kernel knows lives in one tamper-evident log, which every kernel re-checks
as it reads. As a result:

- work survives a restart;
- separate processes (the Operator's tool and an engine's MCP server) share it safely;
- a record that did not come from a conforming kernel stops the kernel instead of taking
  effect.
