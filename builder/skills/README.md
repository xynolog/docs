# Agent skills

A skill is a definition an AI coding assistant loads to do one job with Xynolog: a `SKILL.md` that says when the skill applies, what to ask the user, and the script to write. Each one here stands alone, so copy the directories you want into your assistant's skills directory (`.claude/skills/` for Claude Code), or into a knowledge base's own repository beside the skills written for its corpus.

The scripts are TypeScript on `@xynolog/sdk`, and every code fence in them is type-checked against the built SDK with the rest of the builder docs. [`xynolog-worker`](xynolog-worker/SKILL.md) shows its worker in Rust and in Python too, and each of those blocks is, word for word, a program its SDK's own tests compile and run. Its complete TypeScript worker is run as it stands too, by a test of sdk's `typescript/sdk`. See [the SDK guide](../Usage.md) for the calls they use.

## The layers

A knowledge base is built up in layers, each one made from the layers under it. The skills follow them:

| Layer | What it holds | Skill |
|---|---|---|
| 1. Primary material | The documents: the ground truth everything else points back to | [`xynolog-ingest`](xynolog-ingest/SKILL.md) |
| 2. Annotations | What someone marked in a document: a highlight, a comment, an assessment, a tag, a reference to an entity | [`xynolog-highlight`](xynolog-highlight/SKILL.md), [`xynolog-comment`](xynolog-comment/SKILL.md), [`xynolog-assess`](xynolog-assess/SKILL.md), [`xynolog-tag`](xynolog-tag/SKILL.md) |
| 3. Canonical nodes | One resource for each entity, which every mention of that entity is bound to | [`xynolog-wiki`](xynolog-wiki/SKILL.md) |
| 4. Edges | How the nodes relate: who is whose parent, which party is the counterparty | [`xynolog-relate`](xynolog-relate/SKILL.md) |
| 5. Aggregates | Resources composed from the layers below, written to be read: a report, a timeline, a memo | [`xynolog-aggregate`](xynolog-aggregate/SKILL.md) |

In verbs: [yield](https://github.com/xynolog/protocol/blob/main/contract/flows/YIELD.md) the documents, [mark](https://github.com/xynolog/protocol/blob/main/contract/flows/MARK.md) them, [gather](https://github.com/xynolog/protocol/blob/main/contract/flows/GATHER.md), [match](https://github.com/xynolog/protocol/blob/main/contract/flows/MATCH.md) and [bind](https://github.com/xynolog/protocol/blob/main/contract/flows/BIND.md) each mention to its node, and yield again what the knowledge base can now say. [Frame](https://github.com/xynolog/protocol/blob/main/contract/flows/FRAME.md) declares the vocabulary every layer uses.

## Running Xynolog, and scripts that stay up

| Skill | For |
|---|---|
| [`xynolog-local`](xynolog-local/SKILL.md) | Installing the launcher and running a knowledge base on your own machine |
| [`xynolog-session`](xynolog-session/SKILL.md) | A script that keeps running: token renewal, bus subscriptions, shutdown |
| [`xynolog-worker`](xynolog-worker/SKILL.md) | A daemon that claims jobs from the queue and reports their progress |
| [`xynolog-tour`](xynolog-tour/SKILL.md) | Driving a participant's Browser from a script: a guided tour of a knowledge base |
