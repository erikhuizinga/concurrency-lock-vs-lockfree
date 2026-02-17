# Language Mapping (Top 20)

Use this reference to map lock-vs-lock-free guidance to common language
ecosystems.

## Mapping Table

| Language | Prefer First | Atomic / Lock-Free Escalation Notes |
| --- | --- | --- |
| JavaScript | Web Workers message passing, immutable state updates, queues, IndexedDB/DB transactions for coordination | Shared-memory atomics only apply with `SharedArrayBuffer` + `Atomics` across workers. Treat as advanced and avoid custom lock-free protocols unless proven necessary. |
| TypeScript | Same as JavaScript plus typed concurrency boundaries in worker contracts | Same runtime behavior as JavaScript. Types help API safety but do not simplify memory ordering. |
| Python | `threading.Lock/RLock`, `queue.Queue`, `concurrent.futures`, multiprocessing for CPU-bound parallelism | GIL does not make compound operations atomic across all runtimes/extensions. Shared-memory atomics are niche; prefer process isolation and queues first. |
| Java | `synchronized`, `ReentrantLock`, `ReadWriteLock`, `ConcurrentHashMap`, executors | Use `java.util.concurrent.atomic` only with explicit Java Memory Model reasoning. Prefer concurrent collections before custom CAS loops. |
| C# | `lock`, `Monitor`, `SemaphoreSlim`, `ConcurrentDictionary`, channels/tasks | `Interlocked`/`Volatile` are powerful but subtle. Prefer .NET concurrent primitives before custom lock-free structures. |
| C++ | `std::mutex`, `std::shared_mutex`, condition variables, existing concurrent containers | `std::atomic` ordering and ABA/lifetime issues are high risk. Use lock-free atomics only with strict invariants and heavy validation. |
| C | `pthread_mutex_t`, reader-writer locks, condition variables, bounded queues | C atomics are low-level and fragile under weak memory models. Prefer coarse synchronization unless extreme constraints require otherwise. |
| Go | `sync.Mutex/RWMutex`, channels, worker pools, ownership via goroutines | `sync/atomic` requires clear ordering assumptions and race-aware design. Prefer channels/mutexes for maintainability. |
| Rust | `std::sync::Mutex/RwLock`, channels, `Arc<T>`, actor/task isolation | Atomic orderings are explicit and still difficult. Prefer safe abstractions (`Mutex`, channels, crates) before lock-free custom code. |
| Kotlin | Coroutines, channels/flows, `Mutex` (coroutines), JVM concurrent collections | On JVM, inherit Java memory model concerns for atomics. Prefer coroutine/channel patterns or JVM mature primitives before CAS-heavy logic. |
| Swift | Actors, structured concurrency (`Task`, task groups), `DispatchQueue`, `NSLock` | Swift Atomics exist but are advanced. Prefer actor isolation and queues unless measured needs justify low-level atomics. |
| PHP | Process/request isolation, DB transactions, Redis/queue-based coordination, file/DB locks | Typical workloads are not shared-memory threaded. Avoid lock-free shared-memory design unless in specialized extensions/environments. |
| Ruby | `Mutex`, `Queue`, process models, background job systems | MRI GVL does not eliminate synchronization needs for shared objects and native extensions. Prefer straightforward locking/queues. |
| Dart | Isolates and message passing, stream-based coordination | Shared mutable memory is minimized by design. Atomics are uncommon; prefer isolate boundaries over shared-state lock-free logic. |
| Scala | JVM concurrent collections, Akka/actor model, futures/promises, locks from Java libs | JVM atomics follow JMM complexity; prefer actor/message designs or proven concurrent data structures. |
| Elixir | OTP processes, supervisors, message passing, ETS patterns | Actor model is default. Shared-memory lock-free algorithms are usually the wrong abstraction in standard Elixir architecture. |
| Erlang | Processes, mailbox protocols, supervision trees, ETS strategies | Same as Elixir: prefer actor/process coordination; avoid shared-state lock-free design by default. |
| Julia | Channels/tasks, locks (`ReentrantLock`), data partitioning for threaded sections | Atomics exist but require careful memory-model understanding. Prefer partitioning + locks unless profiling proves otherwise. |
| Objective-C | Grand Central Dispatch queues, `@synchronized`, `NSLock`/`NSRecursiveLock` | Use C/OS atomics only with explicit ordering/lifetime reasoning; prefer GCD queue ownership where possible. |
| Lua | Runtime-specific: cooperative scheduling, message passing in host framework, explicit mutexes where host supports threads | Standard Lua is often single-threaded; lock-free shared-memory approaches are typically outside normal runtime design. |

## Frontend-Specific Note

For browser/front-end work (JavaScript/TypeScript):

1. Prefer worker message passing and ownership transfer.
2. Treat `SharedArrayBuffer` + `Atomics` as advanced, high-risk tooling.
3. Consider latency goals and UI responsiveness first; avoid custom lock-free
   shared structures unless there is strong profiling evidence.
