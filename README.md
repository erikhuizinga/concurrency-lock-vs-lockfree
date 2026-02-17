# concurrency-lock-vs-lockfree

Language-agnostic agent skill for deciding when to use locks and high-level
concurrency primitives versus lock-free atomic algorithms.

## Install

```bash
npx skills add erikhuizinga/concurrency-lock-vs-lockfree
```

## Use

- Explicit invocation: `$concurrency-lock-vs-lockfree`
- Typical intent: lock-vs-lock-free design decisions, atomic/CAS correctness and
  performance tradeoffs, memory-ordering risk assessment.

## Repository Layout

- `SKILL.md`: skill trigger metadata and playbook
- `agents/openai.yaml`: UI/invocation metadata
- `references/language-mapping.md`: language-specific primitive mapping
- `docs/principles.md`: distilled design/testing/performance guidance
- `docs/trigger-tests.md`: trigger precision/recall scenarios
- `docs/tracking.md`: post-release discovery and install tracking
- `CHANGELOG.md`: release notes (including `0.1.0`)

## Attribution

This skill is adapted from the guidance in Abseil's atomic operations article:
`https://abseil.io/docs/cpp/atomic_danger`.

See `THIRD_PARTY_NOTICES.md` for source attribution details.
