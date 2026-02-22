# skills.sh Tracking Plan

Track adoption and discoverability weekly after public release using a dedicated
GitHub issue entity, not repository commits or PRs.

## Tracking Entity

- Repository: `erikhuizinga/concurrency-lock-vs-lockfree`
- Issue title: `Tracking dashboard`
- Issue number source: repository variable `TRACKING_ISSUE_NUMBER`

The automation writes:

1. Weekly raw output to issue comments (one comment per ISO week, updated on rerun).
2. Aggregated view to the issue body between marker comments:
   - `<!-- tracking-summary:start -->`
   - `<!-- tracking-summary:end -->`

## Workflow

- File: `.github/workflows/tracking.yml`
- Trigger:
  - Weekly schedule: Monday at `00:00 UTC` (`0 0 * * 1`)
  - Manual run: `workflow_dispatch`
- Permissions:
  - `contents: read`
  - `issues: write`
- Script entrypoint: `python scripts/tracking.py`

## Queries

The script tracks the following fixed query set:

- `lock-free`
- `atomic`
- `mutex`
- `concurrency`
- `synchronization`
- `ABA`
- `memory ordering`

## Related Terminology Queries

When validating discoverability manually against `skills.sh/api/search`, also
track this set:

- `lockfree`
- `lock free`
- `lockless`
- `compare-and-swap`
- `CAS`
- `mutex vs lock-free`
- `memory ordering`
- `ABA problem`
- `linearizability`
- `hazard pointers`
- `concurrency-lock-vs-lockfree`
- `erikhuizinga/concurrency-lock-vs-lockfree`

Endpoint:

- `https://skills.sh/api/search?q=<query>&limit=10`

Matching target:

- Source equals `erikhuizinga/concurrency-lock-vs-lockfree`

## Weekly Comment Format

Each weekly comment contains:

1. Run metadata (timestamp/status/week key)
2. Normalized query table
3. Nested collapsed raw output:
   - top-level `<details>` for all raw outputs
   - nested `<details>` per query
4. Machine-readable payload block:
   - `<!-- tracking-json:start -->`
   - `<!-- tracking-json:end -->`

## Aggregated Issue Body View

The issue body summary includes:

- latest run timestamp/status
- latest query snapshot (rank/install/found)
- 4-week trend deltas
- recent runs table
- warning section (missing query hits/API partial failures)

## Security Notes

To reduce PR tampering risk:

1. Do not trigger tracking on `pull_request` or `push`.
2. Use only `schedule` + `workflow_dispatch`.
3. Keep write scope minimal (`issues: write` only, no contents write).
4. Protect `.github/workflows/tracking.yml` and `scripts/tracking.py` with
   CODEOWNERS + required reviews.

## Manual Validation

After configuration:

1. Confirm `TRACKING_ISSUE_NUMBER` is set.
2. Trigger workflow manually once.
3. Verify:
   - weekly comment created/updated in issue
   - summary block updated in issue body
   - no repository files were changed by the run
