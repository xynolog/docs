# Testing

The commands below run inside the appropriate tooling container or a provisioned CI runner;
they are not instructions to install language SDKs on the host. Each repository's `Makefile`
runs its suites that way: `make help` lists its targets.

How Xynolog's test suites are organized, configured and run, and what CI gates on.

## The suites

| Suite | Where | What it exercises | Needs |
|---|---|---|---|
| Workspace suites | every npm workspace of sdk's `typescript/` with a `test` script, and images' `browser` | Units and in-process integration: components, hooks, SDK namespaces, services composed over test doubles | Nothing running |
| Rust | the Cargo workspaces of sdk's `rust/` and of images (`cargo test --workspace`) | The Rust SDK (its session, cache, bus and live queries, and the shared case tables), its transport, and the gateway's and dispatcher's own crates | The toolchain [`rust-toolchain.toml`](https://github.com/xynolog/sdk/blob/main/rust/rust-toolchain.toml) names |
| Go | cli, and sdk's `go/` | The launcher driving a fake runtime through real start and stop lifecycles; the Go bus client's wire contract | The Go toolchain each `go.mod` names |
| Kotlin | sdk's `kotlin/sdk` (`./gradlew check`) | The Kotlin SDK: its transport, sign-in and session, its client, cache and live queries, its state units, a worker's claims, the shared case tables, and the programs its README shows, in Kotlin and in Java; the tests under `src/javaTest` call it as a Java program does, and `src/refusals` holds programs that must not compile | Nothing but a container runtime: the JDK image its `.java-version` names |
| Swift | sdk's `swift/sdk` | SDK and generator tests, shared state cases, and compile-failure checks | The pinned Swift toolchain in a Linux container or on the native macOS runner |
| Python | sdk's `python/sdk` (`uv run pytest`) | The Python SDK: its transport, sign-in and session, its client, cache and live queries, the shared case tables, and the programs its README shows, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `shared/python/inference` (`uv run pytest`) | The Python inference drivers: each driver against a provider the test plays over HTTP, what a driver raises, the extras, the telemetry rows against the spec, and the program its README shows, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `shared/python/service` (`uv run pytest`) | What every Python service is built on: a configuration document read and refused, the health endpoint asked over a socket, each form of the log, the readings a process takes of itself against the telemetry table, a resource's bytes, its annotations and the record by position read from an Archivist a test plays over HTTP, how a follower of the record takes each log against its case table and beyond it (the stream it watches, a sweep tried again, a log taken again, its cursors' file), where a file of the record is filed against its case table, what white space is, and what the package is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `worker` (`uv run pytest`) | The Worker service's Python code: the case tables that state how a failure is classed, where a text is cut and how its pieces are planned, and what the project is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `shared/python/graph` (`uv run pytest`) | The Python graph stores: the codecs against the case table of what the graph holds, one store contract against the in-memory store, the two Gremlin stores against fake clients, the extras, and what the package is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `shared/python/graph` (`uv run pytest tests/neo4j_live.py`) | The same store contract against a real neo4j, which it clears | The above, and a neo4j of its own, named in `NEO4J_HOST` and `NEO4J_PASSWORD` |
| Python | images' `shared/python/vectors` (`uv run pytest`) | The Python vector stores and embedding providers: what a point is against its case table, one store contract of both case tables against the in-memory store, each provider against one the test plays over HTTP, and what the package is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `shared/python/vectors` (`uv run pytest tests/qdrant_live.py`) | The same store contract against a real Qdrant, what the Qdrant then holds of each point, and two knowledge bases' indexes on one Qdrant; it deletes every collection of that Qdrant | The above, and a Qdrant of its own, named in `QDRANT_HOST` |
| Python | images' `weaver` (`uv run pytest`) | The Weaver's Python code: the fold against the case table of what each event does to the graph, and the Weaver over a scripted transport and a graph in the process (its order, its fold taken as a follower's take, a store that fails, a start, a rewound record, reconcile, rebuild, what it refuses to start on), and what the project is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Python | images' `smelter` (`uv run pytest`) | The Smelter's Python code: reading a PDF with PDFium and a scanned page with the `tesseract` program, each against the real engine; the rules that make a document's text, against the case table of what deriving a PDF's text comes to; how a text is cut and the work a start plans, each against its case table; the anchored-text store, its entries held to their schema; the Smelter over a scripted transport and an index in the process (what each event does, its order, what it decides, reconcile, rebuild, what it refuses to start on); and what the project is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later, `uv`, and the `tesseract` program with its English data |
| Python | images' `librarian` (`uv run pytest`) | The Librarian's Python code, over a fake of everything it reads by: the protocols it is handed, and what the project is made of, under `mypy` and `pyright`, both strict | Python 3.12 or later and `uv` |
| Gateway conformance | [`protocol/conformance/gateway`](https://github.com/xynolog/protocol/blob/main/conformance/gateway/README.md) | A running gateway, black-box, against `protocol/specs/`: every declared operation, every response and stream message, and hand-written protocol cases, on both signal planes | A built gateway; `nats-server` 2.10 or later on `PATH` |
| Dispatcher conformance | [`protocol/conformance/dispatcher`](https://github.com/xynolog/protocol/blob/main/conformance/dispatcher/README.md) | A running dispatcher, black-box, behind a real gateway on a real JetStream broker, against [JOBS.md](https://github.com/xynolog/protocol/blob/main/contract/JOBS.md) and every channel's schema | A built gateway and dispatcher; `nats-server` |
| Archivist conformance | [`protocol/conformance/archivist`](https://github.com/xynolog/protocol/blob/main/conformance/archivist/README.md) | A running Archivist, black-box, on the bus through a real gateway, at its HTTP surface and in the files it keeps, against [ARCHIVIST.md](https://github.com/xynolog/protocol/blob/main/contract/ARCHIVIST.md) | A built gateway and Archivist; `git`; `nats-server` |
| SDK conformance | [`protocol/conformance/sdk`](https://github.com/xynolog/protocol/blob/main/conformance/sdk/README.md) | Every SDK, through a driver, as a client of a real gateway: one corpus of cases, on the wire and in live queries | A built gateway and the Rust drivers; `@xynolog/sdk` built; `uv` and Python 3.12 or later, for the Python drivers; `nats-server` |
| Worker conformance | [`protocol/conformance/worker`](https://github.com/xynolog/protocol/blob/main/conformance/worker/README.md) | A worker written on each SDK, through a driver, with the suite playing the dispatcher, against [WORKER-CONTRACT.md](https://github.com/xynolog/protocol/blob/main/contract/WORKER-CONTRACT.md) | A built gateway and the Rust drivers; the packages built; `uv` and Python 3.12 or later, for the Python driver; `nats-server` |
| Worker-service conformance | [`protocol/conformance/worker-service`](https://github.com/xynolog/protocol/blob/main/conformance/worker-service/README.md) | The Worker service as a running process, black-box, behind a real gateway, with the suite playing the dispatcher, the record, the Smelter and the model's provider, against [WORKER-SERVICE.md](https://github.com/xynolog/protocol/blob/main/contract/WORKER-SERVICE.md) | A built gateway; `@xynolog/core` built; the Worker service's environment, which `uv` makes; `nats-server` |
| Weaver conformance | [`protocol/conformance/weaver`](https://github.com/xynolog/protocol/blob/main/conformance/weaver/README.md) | The Weaver as a running process, black-box, behind a real gateway and a real Archivist, writing a real neo4j that the suite reads back with a reader of its own, and exporting telemetry the suite receives, against [WEAVER.md](https://github.com/xynolog/protocol/blob/main/contract/WEAVER.md) | A built gateway and Archivist; the Weaver's Python environment (`uv sync --locked --no-dev --all-extras --project images/weaver`); `@xynolog/core` built; `git`; `nats-server`; a neo4j of its own, named in `NEO4J_HOST` and `NEO4J_PASSWORD` |
| Smelter conformance | [`protocol/conformance/smelter`](https://github.com/xynolog/protocol/blob/main/conformance/smelter/README.md) | The Smelter as a running process, black-box, behind a real gateway and a real Archivist, with an embedding provider the suite plays, writing a real Qdrant that the suite reads back, and exporting telemetry the suite receives, against [SMELTER.md](https://github.com/xynolog/protocol/blob/main/contract/SMELTER.md) | A built gateway and Archivist; `@xynolog/core` built; the Smelter's Python environment (`uv sync --locked --no-dev --project images/smelter`) and the `tesseract` program; `git`; `nats-server`; a Qdrant of its own, named in `QDRANT_HOST` |
| Librarian conformance | [`protocol/conformance/ocaml/librarian`](https://github.com/xynolog/protocol/blob/main/conformance/ocaml/librarian/README.md) | The Librarian as a running process, black-box, behind a real gateway and a real Archivist, reading a neo4j a real Weaver writes and a Qdrant a real Smelter writes, with an embedding provider and two models the suite plays, and exporting telemetry the suite receives, against [LIBRARIAN.md](https://github.com/xynolog/protocol/blob/main/contract/LIBRARIAN.md) | Everything the Weaver's and the Smelter's suites need, since it starts both: a built gateway and Archivist; `@xynolog/core` built; the Librarian's, the Weaver's and the Smelter's Python environments and the `tesseract` program; `git`; `nats-server`; a neo4j and a Qdrant of its own, named in `NEO4J_HOST`, `NEO4J_PASSWORD` and `QDRANT_HOST` |
| End-to-end | [`images/e2e`](https://github.com/xynolog/images/blob/main/e2e/README.md) | The live Browser against a live gateway and knowledge base | A running stack and a user at its issuer |

The conformance suites import nothing from what they check. A run names the implementations it tests in a file of its own ([the implementation manifest](https://github.com/xynolog/protocol/blob/main/conformance/README.md#implementation-manifest)), so the same cases judge any implementation of the same spec.

The tools: **Vitest** runs every TypeScript suite; **React Testing Library**, with the `jest-dom` and `jest-axe` matchers, tests components under jsdom; **Playwright** drives the end-to-end suite; Go's `testing` package, Cargo's test harness and **pytest** cover the rest.

## How suites are configured

There is no test orchestrator and no test environment to select. A suite's configuration is its own config file, and anything else a test needs it builds for itself: a temporary directory, a test double, a child process. No variable selects a profile.

### One shared Vitest config

[`vitest.shared.config.ts`](https://github.com/xynolog/sdk/blob/main/typescript/vitest.shared.config.ts), beside the TypeScript packages, holds what every workspace suite has in common:

- `globals: true` and the `node` environment;
- the test files, `src/**/*.test.{ts,tsx}`, excluding `node_modules` and `dist`;
- coverage: the `v8` provider; the reporters `text`, `json`, `json-summary`, `html`, `lcov` and `cobertura`; and the excludes — test files, config files, declaration files, `index.ts` barrels and generated `types.ts`.

It sets no coverage thresholds.

Each workspace's `vitest.config.*` merges it with `mergeConfig` and adds only what is local, and does not re-declare `coverage.reporter`: `mergeConfig` concatenates arrays, so a local list would run every reporter twice.

### What each workspace adds

| Workspace | Local configuration |
|---|---|
| images' `browser` | `jsdom`; [`vitest.setup.ts`](https://github.com/xynolog/images/blob/main/browser/vitest.setup.ts); the React plugin; the `@` → `src` alias; the `threads` pool with `maxConcurrency: 2`; `dangerouslyIgnoreUnhandledErrors`, for tests that throw on purpose; `tsconfig.test.json` for `vitest typecheck`; extra coverage excludes |
| sdk's `typescript/react-ui` | `jsdom`; [`vitest.setup.ts`](https://github.com/xynolog/sdk/blob/main/typescript/react-ui/vitest.setup.ts); the `@` → `src` alias; a coverage `include` of `src/**/*.{ts,tsx}` |
| sdk's `typescript/core` | the `@` → `src` alias; a coverage `include` of `src/**/*.ts` |
| sdk's `typescript/` `http-transport`, `observability`, `sdk` | nothing |

A coverage `include` also reports the files it matches that no test loads; without one, a report covers only the files the tests load.

The two jsdom setup files:

- **The Browser's** adds the jest-dom matchers; polyfills `DOMMatrix`, `matchMedia` and `getAnimations`; fixes `window.location` at `http://localhost:3000/`; stubs `URL.createObjectURL`; resolves relative `fetch` URLs against `http://localhost:3000`; mocks `react-router`'s hooks, `react-i18next` (serving the real English strings from the generated `messages/en.json`) and `@/i18n/routing`; and cleans up after each test.
- **react-ui's** adds the jest-dom and jest-axe matchers; fills jsdom's gaps (`DOMMatrix`, `scrollIntoView`, a `focus` that moves `document.activeElement`); cleans up after each test; and replaces `globalThis.fetch` with one that throws `Unit test attempted a network request: <url>`.

### Environment variables

No Vitest suite takes configuration from the shell. A test that exercises code which reads a variable sets it and restores it; a setup file sets only what production code in its process reads.

`NODE_ENV` selects nothing. Vitest sets it to `test` when it is unset; no code compares it to `test`, and the only reads — react-ui's error boundaries and the Browser's translation manager — check for `development` to show diagnostics.

### Test doubles, not services

Workspace suites run with nothing listening. CI's package matrix starts no database, vector store or model server.

- **The SDK.** `@xynolog/sdk/testing` provides a real `XynologClient` (`createTestClient`) or `XynologSession` (`createTestSession`) over `FaultyTransport`, the scriptable in-memory transport from `@xynolog/core/testing`. An operation the test did not script throws `No response scripted for bus operation "<op>"` rather than answering with a fabricated reply. `stubGateway()` supplies gateway operations that each reject with their own name; `inMemoryContent()` stores content and throws on an unknown id. The other SDKs ship the same doubles for what is built on them: Rust's `xynolog::testing`, Python's `xynolog.testing`, Go's `xynologtest`, Kotlin's `xynolog.testing` (for Kotlin and Java tests alike), Swift's `XynologTesting`, C#'s `Xynolog.Testing`, OCaml's `Xynolog.Testing` and Haskell's `Xynolog.Testing`. Each double is given its global channels, as a wire transport is, and carries only what that transport's stream would: a frame on one of those channels, or on a resource-scoped channel while its resource is held. A helper that builds a full client gives the double the generated full-client set (`BRIDGED_CHANNELS`); a test that needs other channels, such as a worker's claim channels, passes its own list.
- **React.** `@xynolog/react-ui/test-utils` assembles those doubles into providers: `renderWithProviders` renders inside a real `XynologBrowser` whose active session runs on them. The Browser's tests import it directly.
- **Property axioms.** `@xynolog/core/testing/axioms` holds the StateUnit and liveness axiom harnesses. It needs `fast-check` in the importing package's devDependencies.
- **An identity provider.** `@xynolog/core/testing/issuer` is an in-process OIDC issuer: signing keys, signed tokens, and the discovery and JWKS documents. It serves nothing; the consumer answers the two URLs.
- **A real broker where a mock would prove nothing.** The conformance suite's NATS plane spawns `nats-server` from `PATH`. A missing binary fails the run with instructions; it never skips.

### How the conformance suites are configured

[`protocol/conformance/vitest.config.ts`](https://github.com/xynolog/protocol/blob/main/conformance/vitest.config.ts) is its own config, not derived from the shared one. It holds eight projects over one shared harness: `gateway`, `dispatcher`, `archivist`, `sdk`, `worker`, `worker-service`, `weaver` and `smelter`. The `librarian` suite runs on the OCaml harness instead ([`conformance/ocaml/librarian`](https://github.com/xynolog/protocol/blob/main/conformance/ocaml/librarian/README.md)). It uses the `forks` pool with up to four workers, since each file boots its own gateways, issuer and broker, and a 60-second test timeout.

Each gateway the suite starts gets a fresh temporary directory holding its `GatewayConfig` document, and an environment of `PATH` plus the variables the case sets, such as `JWT_SECRET` and `XYNOLOG_OIDC_CLIENT_ID`. Nothing else from your shell reaches it.

## Running tests

Each repository runs its own suites, in containers, from its `Makefile`; `make help` lists them, and its README says what each needs:

| Repository | Its suites |
|---|---|
| [sdk](https://github.com/xynolog/sdk/blob/main/README.md#development) | Every SDK's, each in its language's container |
| [images](https://github.com/xynolog/images) | The Browser's, the Rust workspace's and each Python project's |
| [protocol](https://github.com/xynolog/protocol/blob/main/conformance/README.md) | The conformance suites, against the implementations a run names |
| [cli](https://github.com/xynolog/cli/blob/main/README.md#development) | The launcher's, which takes minutes |
| [desktop](https://github.com/xynolog/desktop) | Desktop's, its control client's among them |

The Browser's own guide is [TESTING.md](https://github.com/xynolog/images/blob/main/browser/docs/TESTING.md), react-ui's is [TESTING.md](https://github.com/xynolog/sdk/blob/main/typescript/react-ui/docs/TESTING.md), and the gateway's is [TESTING.md](https://github.com/xynolog/images/blob/main/gateway/docs/TESTING.md).

**`node_modules` holds native binaries for the platform that installed it** (rolldown, lightningcss). Run tests in the same image family you installed with. An install made under the Alpine image (`node:<version>-alpine`) fails under the glibc one (`node:<version>`) with a `*.linux-<arch>-gnu.node` module-not-found, and the reverse fails the other way.

**The conformance suites need `nats-server`** on `PATH`. A missing binary fails the run with instructions; it never skips.

## Writing tests

### Code that talks to a knowledge base

Script the transport, then observe through a real client:

```typescript
import { createTestClient } from '@xynolog/sdk/testing'

const { client, transport } = createTestClient()
transport.queueReply('browse:resources-requested', { resources: [], total: 0, offset: 0, limit: 20 })
// Hand `client` to the unit under test. An operation nobody scripted throws
// "No response scripted for bus operation ..." instead of answering.
```

`queueReply` scripts what the gateway answers; the transport's `schedule` scripts the wire (`deliver`, `drop-reply`, `delay`, `duplicate-reply`, `reject-emit`); `fail` reports a failure on the transport's `errors$`, as a transport reports a request the gateway refused. A reply that names what it answers for beside its response, as a gathered context names its resource, takes that from the request, so a test queues the response alone. A reply is held to what its schema requires, as the gateway's is: one that lacks a member fails its request, so a test scripts complete replies. For components, `renderWithProviders` from `@xynolog/react-ui/test-utils` renders inside a `XynologBrowser` on the same doubles. The patterns are in [react-ui's testing guide](../builder/react-ui/TESTING.md).

Do not mock the transport by hand. A hand-rolled mock encodes its author's model of the contract, and the contract moves:

```typescript
// Not this
vi.mock('@xynolog/http-transport', () => ({
  HttpTransport: vi.fn(() => ({ emit: vi.fn() }))
}))
```

### Components

Assert what a person can see or do, and find elements by role and accessible name rather than by test id:

```typescript
const button = screen.getByRole('button', { name: /submit/i })
expect(screen.getByText('Modal content')).toBeInTheDocument()
```

### Two Vitest traps

**Give `beforeEach` and `beforeAll` a block body.** Vitest treats a function *returned* from a setup hook as that test's teardown. `mockClear()`, `mockReset()` and `mockRestore()` return the mock itself, so a concise-arrow hook registers the mock as teardown, and the runner calls it after every test.

```typescript
// Returns the mock; Vitest calls it as teardown after each test
beforeEach(() => scrollSpy.mockClear());

// Block body returns undefined
beforeEach(() => { scrollSpy.mockClear(); });
```

This stays invisible until the mock is given a throwing implementation. Then the test's assertions pass, teardown invokes the mock, and the test fails at the error's construction site with no assertion diff.

**Import mock types by name.** `vi.MockedFunction` in a type annotation does not always resolve; `import type { MockedFunction } from 'vitest'` does.

### When a test fails oddly

| It says | What happened |
|---|---|
| `Unit test attempted a network request: <url>` | react-ui's setup file refuses every `fetch`. Build the client from `@xynolog/sdk/testing`, or through `renderWithProviders`, and script the response |
| `No response scripted for bus operation "<op>"` | The unit reached an operation the test did not script. Add `transport.queueReply('<op>', <response>)` |
| ``a payload on <channel> is not that channel's: it has no `<member>` `` | The reply the test scripted lacks a member its schema requires. Complete it: the schema is the channel's, in `protocol/specs/src/components/schemas` |
| ``a payload on <channel> is not that channel's: its `<member>` is malformed`` | The reply the test scripted holds a member its schema does not allow: text where it states a list, a fraction where it states an integer, a value its enumeration does not list, an id not of its pattern, a number below its least, or a member a closed object does not name. Write it as the schema states it |
| A global such as `describe` is not defined | The workspace's config does not merge the shared one, which sets `globals: true` |

`transport.requestLog` lists every request a `FaultyTransport` saw, in order, with the action its schedule applied.

## End-to-end tests

The suite at [`images/e2e/`](https://github.com/xynolog/images/tree/main/e2e) runs Playwright against a real stack. It exists for what no in-process test can see: timing on the event stream, races between a page's lifecycle and the bus, tear-down on navigation, a session rebuilt across sign-out and sign-in, and annotations that persist across a reload.

It is deliberately small. A spec earns its place by guarding a path that has broken before and that a unit or integration test cannot catch.

- **Not in CI.** No workflow runs it. Run it against a stack you brought up, usually one built from your tree ([Local Development](LOCAL-DEVELOPMENT.md)).
- **Seeded.** Its global setup signs in through the SDK and uploads the fixtures the specs assume.
- **Real sign-in.** The fixture is handed to the stack's Keycloak and types the credentials into its page.
- **One worker, no retries, Chromium only.** A flake is diagnosed, not retried away.
- **Slow specs opt in.** `npm test` leaves out specs tagged `@slow`; `npm run test:slow` runs only those.
- **Wire-level assertions.** A spec asserts on the bus as well as on the page: that a `mark:create-request` was emitted and a `mark:create-ok` arrived with the same correlation id. A page can end up right for the wrong reason; the wire cannot.

It reads four variables: `E2E_EMAIL` and `E2E_PASSWORD`, which are required and have no default, and `E2E_BROWSER_URL` and `E2E_GATEWAY_URL`, which default to `http://localhost:3000` and `http://localhost:4000`.

```bash
cd e2e                                     # in a checkout of images
npm ci
npx playwright install chromium
npm test                                   # typechecks the specs, then runs them
npm test -- specs/02-open-resource.spec.ts # one spec
```

Use `npm test` rather than `npx playwright test`: its `pretest` typechecks the specs, and nothing else does.

Everything else is in the suite's own docs:

| Doc | What it covers |
|---|---|
| [README](https://github.com/xynolog/images/blob/main/e2e/README.md) | Running from a container, reaching the stack from inside one, and the full flow against a freshly built stack |
| [running.md](https://github.com/xynolog/images/blob/main/e2e/docs/running.md) | Invocation: one spec, headed, `--repeat-each` |
| [writing.md](https://github.com/xynolog/images/blob/main/e2e/docs/writing.md) | The spec template, fixture ordering, selectors |
| [bus-logging.md](https://github.com/xynolog/images/blob/main/e2e/docs/bus-logging.md) | The bus log, the `bus` capture fixture and its helpers |
| [debugging.md](https://github.com/xynolog/images/blob/main/e2e/docs/debugging.md) | Traces, pulling an error out of one, diagnostic specs |
| [containers.md](https://github.com/xynolog/images/blob/main/e2e/docs/containers.md) | Rebuilding the stack after a code change |
| [jaeger.md](https://github.com/xynolog/images/blob/main/e2e/docs/jaeger.md), [page-errors.md](https://github.com/xynolog/images/blob/main/e2e/docs/page-errors.md) | The fixtures that attach traces and uncaught page errors to a report |
| [live-monitoring.md](https://github.com/xynolog/images/blob/main/e2e/docs/live-monitoring.md) | Hunting a bug on a running stack without Playwright |
| [gotchas.md](https://github.com/xynolog/images/blob/main/e2e/docs/gotchas.md) | The sharp edges |

## Coverage

A repository that measures coverage measures its own code's and reports it to Codecov, under the flags its Codecov configuration names. No vitest config sets a threshold, so a coverage run fails exactly when the suite does.

`npm run test:coverage` writes a workspace's `coverage/` directory: `lcov.info`, `coverage-summary.json`, `cobertura-coverage.xml`, and an HTML report at `coverage/index.html`.

## Continuous integration

Each repository's `.github/workflows/ci.yml` runs on every pull request and on pushes to `main`, and in the merge queue where `main` has one. Its last job, `CI Gate`, waits for every other job, and a census holds that list to the workflow's jobs; it fails when any of them failed or was cancelled, and a job skipped by its own condition passes. `CI Gate` is the check the org's ruleset requires.

Where `main` has a merge queue, a pull request is merged through it, not by bringing it up to date with `main`. The queue makes a commit of `main` and every pull request queued ahead, runs `ci.yml` on it, and merges when `CI Gate` passes there; a pull request whose run fails leaves the queue, and `main` is unchanged.

Locally, run the suite for the code you changed. CI runs the whole matrix.

## Related

- [Local Development](LOCAL-DEVELOPMENT.md): building a stack from your tree to test against
- [Browser testing](https://github.com/xynolog/images/blob/main/browser/docs/TESTING.md), [react-ui testing](https://github.com/xynolog/sdk/blob/main/typescript/react-ui/docs/TESTING.md), [gateway testing](https://github.com/xynolog/images/blob/main/gateway/docs/TESTING.md): each part's own guide
- [The conformance suites](https://github.com/xynolog/protocol/blob/main/conformance/README.md): what they are and how the harness works
- [Testing with the SDK's doubles](../builder/react-ui/TESTING.md): for anyone building on the SDK
