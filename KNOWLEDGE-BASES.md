# Knowledge Bases

Xynolog runs from a **knowledge-base repo** — a separate, small repository
holding your documents, configuration, and startup scripts — not from the
platform's source: [sdk](https://github.com/xynolog/sdk), which builds the SDK
packages, and [images](https://github.com/xynolog/images), which publishes the
container images.

Every KB repo shares the same shape under `.xynolog/`: its project file
(`config.yaml`), the documents describing its stack (`stack/`, one Inference
document per way of serving its models), and the event log. The stack is run
by the host-installed [`xynolog` launcher](https://github.com/xynolog/cli)
(a single static binary), which *pulls* the published, attested
`ghcr.io/xynolog/xynolog-*` images the documents name and mounts into
each one the configuration it writes from them — KB repos build no images of
their own (see [Container Images](operator/administration/IMAGES.md)).

On this page: the [demo knowledge bases](#demo-kbs), which arrive with content, and
[how to run one](#running-one); the [community](#community) ones;
[starting from scratch](#starting-from-scratch); and running any of them
[in a GitHub Codespace](#in-a-github-codespace).

## Demo KBs

Each ships a small corpus and a layered set of skills (ingest → mark →
canonicalize → wire-edges → compose-aggregates) that demonstrate the SDK in a
particular domain. The value is the *skills*, not the data — the skills are
corpus-generic and work on any corpus dropped into the same directory layout.

| Knowledge Base | Domain | Clone |
|---|---|---|
| **[semiont-gutenberg-kb](https://github.com/xynoplex/semiont-gutenberg-kb)** | Public-domain literature from Project Gutenberg | `git clone https://github.com/xynoplex/semiont-gutenberg-kb.git` |
| **[semiont-arxiv-kb](https://github.com/xynoplex/semiont-arxiv-kb)** | Research papers from arXiv | `git clone https://github.com/xynoplex/semiont-arxiv-kb.git` |
| **[semiont-legal-kb](https://github.com/xynoplex/semiont-legal-kb)** | Synthetic legal documents — contracts, attorney correspondence, internal memos | `git clone https://github.com/xynoplex/semiont-legal-kb.git` |
| **[semiont-caselaw-kb](https://github.com/xynoplex/semiont-caselaw-kb)** | U.S. case law — Supreme Court opinions and state appellate cases | `git clone https://github.com/xynoplex/semiont-caselaw-kb.git` |
| **[semiont-clinical-evidence-kb](https://github.com/xynoplex/semiont-clinical-evidence-kb)** | Synthetic clinical evidence — trials, observational studies, treatment guidelines, drug-safety reports | `git clone https://github.com/xynoplex/semiont-clinical-evidence-kb.git` |
| **[semiont-newsroom-kb](https://github.com/xynoplex/semiont-newsroom-kb)** | Synthetic investigative-journalism documents — interview transcripts, FOIA responses, public statements | `git clone https://github.com/xynoplex/semiont-newsroom-kb.git` |
| **[semiont-household-kb](https://github.com/xynoplex/semiont-household-kb)** | Synthetic home-property records — service receipts, contractor emails, manuals, mortgage / insurance, HOA notices | `git clone https://github.com/xynoplex/semiont-household-kb.git` |

### Running one

Install the launcher first: steps 0 to 2 of the [Quick Start](builder/QUICK-START.md),
which also say where an Anthropic key goes. Then clone a knowledge base and start it.
One command starts the whole stack, including the Xynolog browser at http://localhost:3000:

```bash
brew install xynolog/xynolog/xynolog   # once
git clone https://github.com/xynoplex/semiont-gutenberg-kb.git
cd semiont-gutenberg-kb
xynolog start
xynolog useradd --email admin@example.com   # prompts for the password
```

A demo knowledge base arrives with its identity and its stack's documents already
set, so there is no `xynolog init` to run, and with content, so there is nothing to
ingest before you read and annotate. A plain `xynolog start` runs its local Ollama
Inference document, which needs no key. `xynolog start --config anthropic` runs on
your Anthropic key instead.

A new stack has no users, which is what `useradd` is for. Then open the browser,
pick the knowledge base in its Knowledge Bases panel and sign in: steps 5 and 6
of the Quick Start.

`xynolog logs` follows the stack, `xynolog status` health-checks it, and
`xynolog stop` tears it down, the Browser with it. The Browser is the viewer of
every KB rather than a member of one stack: every start ensures it, and
`xynolog stop --service browser` stops it alone. Its Knowledge Bases panel
discovers launcher-managed stacks automatically.

See [Running knowledge bases on your computer](operator/LOCAL-XYNOLOG.md) for the full local guide:
choosing a config, the ports, and where things are kept.

## Community

| Knowledge Base | Domain | Clone |
|---|---|---|
| **[synthetic-family](https://github.com/pingel-org/synthetic-family)** | Synthetic family history and genealogy | `git clone https://github.com/pingel-org/synthetic-family.git` |

Built a knowledge base others could learn from? Open an
[issue](https://github.com/xynolog/docs/issues) to get
it listed here.

## Starting from scratch

**`xynolog init`** births a new KB in place — no clone required. It writes
the permanent did:web identity into `.xynolog/config.yaml` at birth (from
`--domain` or your git origin), writes the stack's documents into
`.xynolog/stack/` from `--inference` / `--model` / `--embedding` choices (or
copies the template's with `--from-template`), and refuses rather than
writing documents that cannot start:

```bash
xynolog init --yes --inference anthropic --embedding ollama:nomic-embed-text
```

Or clone the empty template:

| Template | Description | Clone |
|---|---|---|
| **[kb-template](https://github.com/xynolog/kb-template)** | Empty template — start here for a new project | `git clone https://github.com/xynolog/kb-template.git` |

The template holds the `.xynolog/` folder `xynolog init` writes, and a
`.devcontainer/` that runs its stack in a codespace.

## In a GitHub Codespace

Run a knowledge base on GitHub's machine instead of yours. The same launcher places
a KB stack in a **GitHub Codespace**. One command does several things:
- creates the codespace, or resumes it;
- waits for the stack, which the codespace's own launcher runs;
- forwards the KB and its sign-in service (Keycloak) to local ports;
- starts the browser on this machine, when it has a container runtime.

```bash
xynolog start --runtime codespace --repo xynolog/kb-template
```

Each codespace KB gets its own pair of local ports: the KB on 4000 (or the
lowest free port above it), and Keycloak on 8080 (or the lowest free port
above it, which the launcher moves the codespace's Keycloak to match). So one
local browser works — and signs in to — several cloud KBs at once via its
Knowledge Bases panel. The summary names the codespace and both ports;
`xynolog status` and `gh codespace list` show it too.

**A new codespace KB has no users.** Create the first account the way the
start summary says; it prompts for the password, and the account is made by
the launcher inside the codespace:

```bash
xynolog useradd --repo xynolog/kb-template --email you@example.com
```

Then sign in from the browser: the first sign-in asks for your name.

`xynolog stop --repo <owner/name>` stops the codespace and both forwards.
Compute stops billing; storage bills until GitHub deletes the codespace 30
days after it stopped. `--delete` destroys it now. Every `--repo` command
finds the repo's codespace even when this machine has no record of it — a
codespace whose setup failed during `start` included — so
`xynolog stop --repo <owner/name> --delete` is always the way to remove one.
Prerequisites (the `gh` CLI and an `ANTHROPIC_API_KEY` Codespaces user secret)
are in each KB's README; the raw `gh` recipe is kept there too as the
no-launcher path.
