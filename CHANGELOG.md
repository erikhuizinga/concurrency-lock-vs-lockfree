# Changelog

All notable changes to this skill are documented in this file.

## 0.2.0 - 2026-08-27

### Added

- GitHub issue-based tracking automation and regression tests for terminology
  discovery.

### Changed

- Improved skill metadata, README terminology, and related trigger terms for
  lock-free, CAS, and memory-ordering requests.
- Refined `SKILL.md` to make measured lock/high-level designs the default and
  custom atomic synchronization expert-only.
- Added explicit decision completion criteria and an escalation gate covering
  evidence, ownership, reclamation, formal reasoning, stress validation, and
  expert review.
- Expanded atomic hazard guidance for composition, relaxed publication,
  ordering, weak-memory architectures, ABA, lifetime, progress, and
  maintainability.
- Expanded performance and testing guidance to require mutex baselines,
  cross-architecture validation, race detection, stress testing, and
  specialized verification where appropriate.

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
