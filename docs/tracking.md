# skills.sh Tracking Plan

Track adoption and discoverability weekly after public release.

## 1) Query-Based Ranking Checks

Use `skills.sh` search API with fixed queries:

- `lock-free`
- `atomic`
- `mutex`
- `concurrency`
- `ABA`
- `memory ordering`

Endpoint shape:

`https://skills.sh/api/search?q=<query>&limit=10`

Record:

- date
- query
- result rank
- installs shown
- exact returned source/skill id

## 2) Install Count Trend

Track installs from search/listing responses week-over-week.

Primary signal:

- non-zero installs
- positive trend over 2-4 weeks

## 3) Local Validation Signal

Periodically verify discovery and install flow:

1. `npx skills find lock-free`
2. `npx skills add erikhuizinga/concurrency-lock-vs-lockfree`

## 4) Repository Signals

Track public repo indicators:

- stars
- forks
- watchers
- release engagement on `v0.1.0`

## 5) Optimization Loop

If discoverability is weak:

1. Tune `SKILL.md` description trigger terms.
2. Tune `agents/openai.yaml` short description.
3. Add practical examples to README.
4. Re-check query rankings after each change set.
