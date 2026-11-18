# Local development

To try a change in a running stack, build the images from a checkout of [xynolog/images](https://github.com/xynolog/images) and the launcher from a checkout of [xynolog/cli](https://github.com/xynolog/cli), and run a knowledge base on them. What you test is what ships.

## What you need

- **Host tools**: GNU Make 3.81 or newer, Bash, Git, curl, and Apple `container`, Docker or Podman. Language toolchains run in containers.
- **The checkouts**, side by side, each cloned with `--recurse-submodules`: `images` and `cli`, and `sdk` beside them, which both build against unless given a bundle.
- **A knowledge base to run against.** Clone [`kb-template`](https://github.com/xynolog/kb-template), or see [Knowledge Bases](../KNOWLEDGE-BASES.md) for others.

## The loop

```bash
# 1. In images: build all eight images, tagged ghcr.io/xynolog/xynolog-<name>:local
make build

# 2. In cli: build the launcher, as dist/xynolog
make

# 3. In the knowledge base: run the stack on what you built. Name the :local
#    images in .xynolog/stack/*.yaml (ghcr.io/xynolog/xynolog-gateway:local,
#    and so on for each service), and the Browser's and the worker's in their
#    own documents
cd /path/to/your-kb
perl -pi -e 's#(xynolog-browser):\S+#$1:local#' "$(/path/to/cli/dist/xynolog settings browser --path)"
perl -pi -e 's#(xynolog-worker):\S+#$1:local#' "$(/path/to/cli/dist/xynolog settings worker --path)"
/path/to/cli/dist/xynolog start
/path/to/cli/dist/xynolog useradd --email you@example.com

# 4. Change code, rebuild what changed, and start again

# 5. When you are done
/path/to/cli/dist/xynolog stop
```

Two things make the stack use your build:

- **The `:local` images, named.** A knowledge base's documents in `.xynolog/stack/` name the image each service runs, and the launcher pulls none tagged `:local`. Write `ghcr.io/xynolog/xynolog-<service>:local` for each `image` of a Xynolog service there, and the Browser's and the worker's, which are shared, as the image in each one's own document, the file `xynolog settings browser --path` or `xynolog settings worker --path` prints; `:latest` there returns it to the published one. A document still naming `:latest` runs the published image, and your change is not in it.
- **The launcher you just built**, not one installed with Homebrew. A launcher from an earlier release may not match images built from your tree.

`make help` in each checkout lists its targets, and images' [LOCAL-BUILD.md](https://github.com/xynolog/images/blob/main/LOCAL-BUILD.md) covers the image builds, one image at a time among them.

## Working on one part, without a stack

Most changes do not need a running stack. Each repository builds and tests on its own: `make help` lists how, and [Testing](TESTING.md) has every suite.

## Looking at a running stack

The launcher's verbs work the same on a stack built from source:

```bash
xynolog status                     # each service's state and health
xynolog logs --service worker      # follow one service
xynolog start --service worker     # restart one after rebuilding its image
```

In the Browser's console, `window.__XYNOLOG_BUS_LOG__ = true` logs one line for every bus event that page sends and receives, which is often the fastest way to see what a change did: see [Bus logging](https://github.com/xynolog/images/blob/main/e2e/docs/bus-logging.md). Every service's traces are at `http://localhost:16686` ([Observability](../operator/administration/OBSERVABILITY.md)).

## Related

- [LOCAL-BUILD.md](https://github.com/xynolog/images/blob/main/LOCAL-BUILD.md): the images repository's build targets
- [The launcher's development notes](https://github.com/xynolog/cli/blob/main/README.md#development): building and testing the launcher
- [Testing](TESTING.md): the suites and how to run them
- [The service catalog](../operator/services/OVERVIEW.md): what is running, and on which ports
- [Running knowledge bases on your computer](../operator/LOCAL-XYNOLOG.md): the launcher from an operator's side
- [Troubleshooting](../operator/administration/TROUBLESHOOTING.md): when a start fails or a service is unhealthy
