# Trigger Test Matrix

Use this matrix to check that invocation is broad enough for lock-vs-lock-free
 decisions but not noisy for unrelated concurrency work.

## Should Trigger (Explicit Terms)

1. "Design a lock-free queue with CAS."
2. "We use `memory_order_relaxed`; is this safe?"
3. "Investigate ABA bugs in our stack implementation."
4. "Can we replace these mutexes with atomics for speed?"
5. "How should we use compare-and-swap in this pool?"

Expected behavior:

- Recommend lock/high-level alternatives first.
- Explain lock-free risks before proposing low-level changes.

## Should Trigger (Implicit Design Choice)

1. "Our hot path has lock contention; should we redesign synchronization?"
2. "We see rare concurrency corruption under load; current design uses custom
   synchronization."
3. "Would lock sharding be better than a lock-free global structure?"

Expected behavior:

- Surface tradeoffs and safer alternatives.
- Require evidence before lock-free recommendation.

## Should Usually Not Trigger

1. "Explain async/await basics."
2. "How do I use promises/futures in this framework?"
3. "Set up a cron job and retry policy."
4. "Fix database deadlock in SQL transaction ordering."

Expected behavior:

- Do not inject lock-free atomic guidance unless the prompt shifts toward
  shared-memory synchronization design.

## Output Quality Checks

When triggered, verify output includes:

1. Decision statement (locks/high-level vs lock-free justified).
2. Evidence-backed rationale.
3. Safer alternative recommendation.
4. If lock-free: memory-ordering + ABA + reclamation + validation plan.
