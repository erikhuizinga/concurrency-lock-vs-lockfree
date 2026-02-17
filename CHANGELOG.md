# Changelog

All notable changes to this skill are documented in this file.

## 0.1.0 - 2026-02-17

### Added

- Initial skill `concurrency-lock-vs-lockfree`.
- Balanced trigger metadata for lock-vs-lock-free design prompts.
- Language-agnostic decision playbook with lock-first default.
- `agents/openai.yaml` metadata for implicit and explicit invocation.
- Reference guides:
  - `references/principles.md`
  - `references/language-mapping.md` (20 popular languages)
  - `references/trigger-tests.md`
- Source attribution and licensing notice in `THIRD_PARTY_NOTICES.md`.

### Attribution

- Guidance adapted from Abseil's "The Danger of Atomic Operations":
  `https://abseil.io/docs/cpp/atomic_danger`
