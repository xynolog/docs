# Dependencies

How Xynolog's dependencies are kept current, how a vulnerable one is fixed, and how the SDK's packages depend on each other.

## Dependabot

Each repository's `.github/dependabot.yml` names the ecosystems Dependabot updates there, and every Dependabot pull request is labelled `dependencies`. The [sdk's README](https://github.com/xynolog/sdk/blob/main/README.md#development) lists the manifests it covers, and which it cannot.

## Advisories

sdk, images, cli and desktop check every lockfile they track, and each one CI resolves where they commit none, against the OSV database with [`advisories.py`](https://github.com/xynolog/build-tools/blob/main/advisories.py) from build-tools. A finding fails the run unless the repository's `advisories.toml` ignores it with the reason it cannot reach what the repository ships, and an ignore that matches no finding fails it too, so none outlives what it was about.

## Reviewing a dependency pull request

**Do not merge part of a group.** A group keeps packages that must move together on one version, such as a bundler and its per-platform native binaries (`@rolldown/binding-*`, `lightningcss-*`). Moving one without the others fails CI with `cannot find module *.linux-x64-gnu.node`.

## Fixing a vulnerable dependency

**Move the consumer forward rather than pinning around it.** Bump the package that pulls in the vulnerable one, regenerate the lockfile, accept the drift, and validate with a real `npm ci`. An `overrides` entry is the last resort, for when no consumer has a release that carries the fix.

**Before retiring an override, check every copy.** A hoisted version that looks clean is not evidence that the override is dead. npm hoists one copy to the root, but a dependency that pins an exact version keeps a nested copy of its own, and the override may be the only thing lifting it:

```bash
jq -r '.packages | to_entries[]
  | select(.key | test("node_modules/<pkg>$"))
  | "\(.value.version)  \(.key)"' package-lock.json
```

If any nested copy is below the advisory's patched version, the override is still doing its job. When you do move a dependency for an advisory, target the newest fixed release, not the first one that cleared it: patched versions routinely draw advisories of their own.

## Lockfiles

**Regenerate a lockfile with its package manager, never by hand.** A lockfile records each workspace's version in several linked places, and only the package manager rewrites them consistently. Run it in the container the repository's `Makefile` uses, as its toolchains run there.

## How the SDK's packages depend on each other

**In source, a dependency on another `@xynolog/*` package is `"*"`.** That always resolves to the workspace's own copy, and it can never go stale. A concrete version would: once it stopped matching the workspace's version, npm would install the *published* copy nested under the consumer, and the consumer would build against old code with no error.

**At publish, `"*"` is rewritten to the exact release version.** Every package is published at every version, so an exact pin always finds its sibling, and a published tarball can never pull a mismatched internal version. One function does the rewrite, `stampInternalDeps` in [`typescript/scripts/stamp-internal-deps.mjs`](https://github.com/xynolog/sdk/blob/main/typescript/scripts/stamp-internal-deps.mjs).

**Every import must be declared.** The workspace hoists, so a package can import something it never declared and work there, then fail for anyone who installs it from npm.

## Licences

The service images pass a licence policy before they are published. For the Python images it reads the image's bill of materials, which lists every package installed from PyPI; for the Rust images, [`scripts/check-image-crates.mjs`](https://github.com/xynolog/images/blob/main/scripts/check-image-crates.mjs) reads the crates each binary links. [`.github/licenses/exceptions.txt`](https://github.com/xynolog/images/blob/main/.github/licenses/exceptions.txt) records what a person read where the scanner could not say: the licence of a package that states none, and a licence a package states under a name SPDX does not have. It answers for nothing the scanner did name, and what it supplies is held to the same allowlist.

## Related

- [Release](RELEASE.md): what is published, and the gates an image passes first
- [Testing](TESTING.md#continuous-integration): what CI checks
- [Container Images](../operator/administration/IMAGES.md): verifying a published image
