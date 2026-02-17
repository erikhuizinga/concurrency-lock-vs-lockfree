# Core Principles

This reference distills the full guidance from Abseil's atomic danger article
into language-agnostic rules for agent decisions.

## 1) Prefer Existing Components

- Use mature, higher-level concurrency components before custom synchronization.
- Reuse library/runtime primitives for one-time init, barriers, futures/promises,
  thread-local state, queues, and rate limiting where available.
- Choose custom lock-free algorithms only when existing options fail specific,
  measured requirements.

## 2) Understand Atomic Hazard Classes

Atomic algorithms fail in two main ways:

1. Ordering/reordering hazards:
   - Compilers and CPUs can reorder accesses under weaker ordering models.
   - Correctness arguments that "look obvious" often break under optimization or
     weaker hardware memory models.
2. Composition hazards:
   - Individual atomic operations do not make multi-step logic atomic.
   - CAS loops can suffer ABA and subtle interleavings.
   - Lifetime/reclamation becomes difficult without coarse mutual exclusion.

## 3) Treat x86 as Insufficient Evidence

- Do not rely on x86 behavior as universal truth.
- Validate reasoning for weak-memory architectures and compiler transforms.
- Specify correctness in language memory-model terms, not hardware folklore.

## 4) Avoid "Lock-Free Is Faster" by Default

- Lock acquisition/release cost is often not the dominant bottleneck.
- Cache misses, cache-line contention, and data movement frequently dominate.
- Commonly better first moves:
  - Shard/partition state.
  - Reduce critical-section scope.
  - Batch updates.
  - Use thread-local caches and aggregation.

## 5) Testing Requirements Are Higher for Lock-Free

- Unit tests cover only a tiny fraction of thread interleavings.
- Require broad stress and race-detection strategies.
- Vary architecture/compiler/optimization in validation.
- Use formal/specialized tools for non-trivial lock-free code when feasible.

## 6) Learn from Long-Lived Production Bugs

Historically, lock-free and atomic-based bugs can persist for years before
detection. Treat this as a risk multiplier:

- Prefer simple synchronization when adequate.
- Demand explicit invariants and ownership models.
- Demand review by experienced concurrency engineers.
