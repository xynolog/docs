# Where a stack runs

Every Xynolog service runs as a Linux container. What differs from place to place is who starts the containers.

## With the launcher

The [`xynolog` launcher](https://github.com/xynolog/cli/blob/main/README.md) runs a stack on these systems, for `arm64` and `amd64`:

| System | Container runtime | Notes |
|---|---|---|
| macOS | Apple `container`, Docker Desktop or Podman | [Running knowledge bases on your computer](../LOCAL-XYNOLOG.md) |
| Linux | Docker or Podman | [Running knowledge bases on your computer](../LOCAL-XYNOLOG.md) |
| Windows | Docker Desktop, on its WSL2 backend | [Xynolog on Windows](WINDOWS.md): inside WSL2, or as `xynolog.exe` |
| GitHub Codespaces | Docker, inside the codespace | `xynolog start --runtime codespace`, from any of the above: [Knowledge Bases](../../KNOWLEDGE-BASES.md) |

`--runtime` names the runtime for one command, and `xynolog settings runtime` sets it for the machine.

## On a platform of your own

Kubernetes, OpenShift, a cloud's container service, or machines on your own premises: the launcher is not involved, and the deployment is yours to write. [Deploying Xynolog](../administration/DEPLOYMENT.md#your-own-platform) states what each image needs and what the platform must provide.
