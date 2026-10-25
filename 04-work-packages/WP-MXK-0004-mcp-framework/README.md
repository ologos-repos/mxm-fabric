# WP-MXK-0004 — Self-contained MCP framework

Lets any code assistant or model that speaks MCP run under the kernel, with nothing to install
and no network. The kernel offers such an engine exactly two tools: read the constitution, and
propose an action as the Assistant. Each server is launched with a delegation that says which
tools and work units it may touch. A subagent's delegation can only be narrower than its
parent's.
