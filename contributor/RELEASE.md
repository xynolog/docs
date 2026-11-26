# Releasing

Each repository releases on its own, by its own workflow:

| Repository | What it publishes | Published by |
|---|---|---|
| [sdk](https://github.com/xynolog/sdk/blob/main/CONTRIBUTING.md#releasing) | One verified bundle of the nine SDKs' packages, on a GitHub Release | `release-artifacts.yml`, on the `v*` tag `scripts/tag-release.sh` pushes |
| [images](https://github.com/xynolog/images) | The eight images, to `ghcr.io/xynolog` | [`publish-service-images.yml`](https://github.com/xynolog/images/blob/main/.github/workflows/publish-service-images.yml) and [`publish-browser.yml`](https://github.com/xynolog/images/blob/main/.github/workflows/publish-browser.yml), dispatched with a version |
| [cli](https://github.com/xynolog/cli/blob/main/README.md#releasing) | The `xynolog` launcher's archives for macOS, Linux and Windows, its `.deb` and `.rpm` packages, checksums and SBOMs, on a GitHub Release | `release.yml`, on a `v*` tag |
| desktop | Xynolog Desktop's installers, on a GitHub Release | `release.yml`, on a `v*` tag |
| [homebrew-xynolog](https://github.com/xynolog/homebrew-xynolog) | The `xynolog` formula, which builds the launcher from the cli commit it names | a pull request that moves the formula |

## Container images

Each service image passes these gates before it is pushed, in order. They fail one at a time, so fixing one can reveal the next:

1. **The image is what it should be.** The Rust images are checked to carry no source and to start as documented ([`check-gateway-image.sh`](https://github.com/xynolog/images/blob/main/scripts/check-gateway-image.sh), [`check-document-image.sh`](https://github.com/xynolog/images/blob/main/scripts/check-document-image.sh) for the dispatcher's and the Archivist's). The worker's, the weaver's, the smelter's and the librarian's images are checked to carry every library they can be configured for (each model provider's, each graph database's client), no installer and no Node, and to refuse by name without their document; the smelter's is checked to carry the `tesseract` program with its English data too, and to read a scanned page with no network ([`check-python-image.sh`](https://github.com/xynolog/images/blob/main/scripts/check-python-image.sh)).
2. **Vulnerabilities and secrets.** Trivy scans for `HIGH` and `CRITICAL` findings and fails on any vulnerability that has a fix, and on any secret. A file the secret scan misreads is skipped only by an allow rule in [`.github/trivy-secret.yaml`](https://github.com/xynolog/images/blob/main/.github/trivy-secret.yaml), which says why nothing in it is a secret. A vulnerability whose fix no dependent admits yet is passed only by an entry in [`.github/trivyignore.yaml`](https://github.com/xynolog/images/blob/main/.github/trivyignore.yaml), which names the package, says why the flaw does not reach the image's code, and expires.
3. **Licences.** See [Dependencies](DEPENDENCIES.md#licences).

Then the image is pushed with its version, `sha-<commit>` and, when `tag_latest` is set, `latest`, and its build provenance and bill of materials are attested.

`tag_latest` defaults to false on both image workflows, so rebuilding an older version does not move `latest` onto it:

```bash
gh workflow run publish-service-images.yml --repo xynolog/images --ref v<version> --field version=<version> --field tag_latest=true
gh workflow run publish-browser.yml --repo xynolog/images --ref v<version> --field version=<version> --field dry_run=true
```

An image workflow builds the ref it is dispatched on, so `--ref v<version>` is what makes an image the release's; without it the run builds the default branch.

What an operator sees of all this is in [Container Images](../operator/administration/IMAGES.md).

## Related

- [`LOCAL-BUILD.md`](https://github.com/xynolog/images/blob/main/LOCAL-BUILD.md): building the images on your machine
- [Dependencies](DEPENDENCIES.md): advisories, licences, and how the SDK's packages depend on each other
- [Container Images](../operator/administration/IMAGES.md): tags, and verifying an image
