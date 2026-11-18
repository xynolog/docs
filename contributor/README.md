# Contributing to Xynolog

Start with [CONTRIBUTING.md](https://github.com/xynolog/.github/blob/main/CONTRIBUTING.md) for branches, pull requests and review.
The [architecture](../architecture/README.md) explains the system; the
[protocol](https://github.com/xynolog/protocol/blob/main/README.md) defines what its implementations agree on.

## Where the code lives

Each part of Xynolog is a repository of its own, with its own CI ending in `CI Gate`. Those that build have a `Makefile` whose `make help` lists its targets; their language toolchains run in containers.

| Repository | What it holds |
|---|---|
| [protocol](https://github.com/xynolog/protocol) | The specs, the contract every implementation honours, and the conformance suites |
| [sdk](https://github.com/xynolog/sdk) | The SDKs in nine languages, and the artifact bundle images, cli and desktop build against |
| [images](https://github.com/xynolog/images) | The Browser and the seven service images |
| [cli](https://github.com/xynolog/cli) | The `xynolog` launcher |
| [desktop](https://github.com/xynolog/desktop) | Xynolog Desktop |
| [build-tools](https://github.com/xynolog/build-tools) | The scripts the other repositories share |
| [docs](https://github.com/xynolog/docs) | These docs |

## Find the details

| Guide | What it covers |
|---|---|
| [Local Development](LOCAL-DEVELOPMENT.md) | Building images and the launcher from your trees, and running a stack on them |
| [Local build commands](https://github.com/xynolog/images/blob/main/LOCAL-BUILD.md) | The images repository's build targets |
| [Testing](TESTING.md) | Suites, test doubles and CI gates |
| [Adding a job](ADDING-A-JOB.md) | Spec, SDK, service and test changes for a new job kind |
| [Dependencies](DEPENDENCIES.md) | Dependency updates, advisories and vulnerability fixes |
| [Documentation](DOCUMENTATION.md) | Editing builder docs and SDK examples |
| [Release](RELEASE.md) | What each repository publishes, and the gates an image passes |
