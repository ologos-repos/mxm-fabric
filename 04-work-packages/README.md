# 04-work-packages/

Authored **work packages** for coherent multi-step delivery.

```text
04-work-packages/WP-<SLUG>-NNNN-slug/package.yaml
```

Schema inherited from `mxm-assistant-001`.

| Field | Meaning |
|---|---|
| `id` | Stable id (e.g. `WP-<SLUG>-0001`) |
| `title` | Short name |
| `scope` | In / out of scope |
| `authority_boundary` | What is allowed without re-asking |
| `actions` | Planned actions (list) |
| `verification` | How done is proven |
| `disposition` | open / approve / merge / defer / cancel |
| `status` | proposed \| approved \| in_progress \| done \| cancelled |

**`authority_boundary` is the field that matters most.** It is where the principal's reserved
decisions become structural rather than remembered. A package that could touch a commitment,
an external publication, or a verdict says so there, explicitly, before work starts.

## Optional: `commitment`

For repos where some work is investigation rather than delivery, add
`commitment: committed | stretch`.

- **committed** — bounded and mechanical; it will land.
- **stretch** — the commitment is to run the attempt to a **recorded resolution, not to a
  positive result.** A recorded refutation closes a stretch package *successfully*.

That distinction is worth carrying deliberately: without it, a negative result gets logged as a
cost against the work rather than as the completed work it actually is.
