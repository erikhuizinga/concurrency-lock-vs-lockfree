---
name: concurrency-lock-vs-lockfree
description: Language-agnostic guidance for deciding between locks, higher-level concurrency, and custom lock-free atomics. Use when tasks mention atomics, CAS/compare-and-swap, lock-free queues/stacks/pools, memory ordering or memory fences, ABA, weak-memory behavior, replacing mutexes/locks for performance, designing synchronization primitives, or debugging rare shared-memory races and corruption.
---

# Concurrency: Lock vs Lock-Free

Treat custom atomic synchronization as expert-only code. Prefer higher-level
concurrency primitives and lock-based designs unless measured evidence proves
they are insufficient.

Use this playbook to make explicit, auditable decisions.

## Decision Process

1. Map the shared state: list shared accesses, invariants, ownership and
   lifetime, operations that must be indivisible, and the required progress
   guarantee. Complete this step when every invariant has an owner and each
   indivisible operation has a candidate linearization point.
2. Establish a baseline with existing high-level components and a lock-based
   design. Measure the actual bottleneck, including contention, cache behavior,
   latency, and throughput. Complete this step when the proposed change has a
   concrete baseline and evidence for the bottleneck it addresses.
3. Try simpler scaling techniques first: reduce lock scope, shard or partition
   state, batch updates, use thread-local buffering or aggregation, hand off
   ownership with safe references, or use a mature concurrent container or
   RCU-like facility. Complete this step when each rejected option has a
   specific reason grounded in the target workload.
4. Choose custom lock-free atomics only when the escalation gate below is
   satisfied. Complete this step when the evidence, owner, and review path are
   recorded.
5. If custom atomics remain justified, model ordering, atomicity, lifetime,
   reclamation, ABA, interleavings, and progress before implementation.
   Complete this step when the invariants and failure cases are written down
   well enough for an independent reviewer to challenge them.

## Default Recommendation

- Prefer existing concurrency libraries and runtime primitives.
- Prefer mutexes/locks over custom lock-free algorithms.
- Prefer partitioning/sharding, batching, and thread-local buffering before
  introducing lock-free shared structures.
- Compare any atomic design with a mutex baseline; mutex operations are often
  cheaper than a cache miss, and lock-free code may add read-modify-write and
  memory-fence costs.

## Lock-Free Escalation Gate

Recommend a custom lock-free algorithm only when all are true:

1. Performance evidence shows lock contention is the bottleneck.
2. Simpler alternatives (sharding, batching, lock scope reduction, library
   data structures) were evaluated and rejected with evidence.
3. The team has memory-model expertise for the target language and every
   deployed hardware architecture.
4. Object ownership, lifetime, and reclamation are explicit and reviewable.
5. A correctness plan exists: invariants and linearizability reasoning, formal
   or specialized tools where appropriate, and long-running stress testing.
6. A small group of concurrency experts owns, independently reviews, and can
   maintain the implementation.

If any gate item is missing, recommend the safest lock-based or library-based
alternative and name the missing evidence.

## Atomic Hazard Checklist (When Atomics Are Proposed)

- Atomicity and composition:
  - An atomic access protects one access, not a multi-step protocol. Treat
    every sequence of atomic operations as interruptible; define its
    linearization point and account for failed CAS paths and every relevant
    interleaving.
  - Keep all shared accesses data-race-free under the target language memory
    model. A relaxed flag does not by itself publish adjacent non-atomic data.
- Ordering and visibility:
  - Specify the happens-before or equivalent visibility relation for each
    dependent access, and justify every atomic ordering.
  - Sequential consistency can simplify reasoning but is not automatically
    faster: on weakly ordered ARM/POWER-like systems, its fences or special
    loads may cost more than a mutex.
- Cross-platform behavior:
  - Treat x86 results as insufficient evidence. Account for compiler
    reordering, optimization changes, and every weak-memory architecture in
    the deployment set.
- Non-atomic sequences:
  - Make the larger critical section explicit; use a lock or a proven
    higher-level abstraction when the invariant spans multiple locations.
- Lifetime and reclamation:
  - Define safe reclamation (hazard pointers, epochs/RCU-like patterns, etc.).
- ABA exposure:
  - Detect and mitigate ABA risks in CAS loops.
- Progress guarantees:
  - State lock-free/wait-free/obstruction-free claim precisely.
- Maintainability:
  - Keep the algorithm, invariants, and proof understandable to independent
    maintainers; reserve this code for a small expert-owned surface.

## Performance Guidance

Before recommending lock-free structures, prioritize:

1. Data layout and cache locality improvements.
2. Lock partitioning (shard by key/hash/core).
3. Reduced critical section scope.
4. Batched updates and per-thread/local aggregation.
5. Ownership transfer, reference counting, or read-copy-update patterns where
   they fit.
6. Existing concurrent containers in mature libraries.

Benchmark the selected design against the lock-based baseline on representative
workloads and target architectures; a lock-free label is not a performance
result.

## Testing and Verification Guidance

Require:

1. Invariant assertions and linearizability reasoning before relying on tests.
2. Stress testing under heavy concurrency and long runs; unit tests cover only
   a tiny fraction of possible interleavings.
3. Race detection tooling where applicable, including ThreadSanitizer for
   mutex-based code as well as atomic code.
4. Variation across compilers, optimization levels, and architectures; include
   weak-memory hardware rather than treating x86 as universal evidence.
5. Formal or specialized checkers and review by several concurrency experts for
   non-trivial lock-free algorithms.

## Response Format

When advising, produce:

1. Decision:
   - `Use locks/high-level primitives` or `Lock-free justified`.
2. Rationale:
   - Evidence-backed tradeoffs, not preferences.
3. Safer alternative:
   - Concrete lock-based/library-based option first.
4. If lock-free:
   - Linearization points, ordering/visibility model, lifetime and reclamation
     plan, ABA mitigation, progress claim, expert owner, and test plan.
5. Validation:
   - Benchmarks against a lock-based baseline plus the correctness checks
     needed before adoption.

## Language-Specific Mapping

For concrete primitive choices by language, use
`references/language-mapping.md`.

## Related Terminology

The following terms are closely related to this skill's scope and intent:

- lockfree
- lock free
- lock-free
- lockless
- compare-and-swap
- CAS loop
- atomic operations
- mutex vs lock-free
- synchronization strategy
- memory ordering
- ABA problem
- linearizability
- hazard pointers

## Source Credit

Primary source guidance adapted from Abseil:
`https://abseil.io/docs/cpp/atomic_danger`
