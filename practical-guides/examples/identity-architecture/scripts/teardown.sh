#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
#  Teardown — delete the kind cluster, keep the registry
# ---------------------------------------------------------------------------

CLUSTER_NAME="${CLUSTER_NAME:-rossoctl}"

export KIND_EXPERIMENTAL_PROVIDER=podman

info()  { printf '\033[0;34m→\033[0m %s\n' "$*"; }
ok()    { printf '\033[0;32m✓\033[0m %s\n' "$*"; }

if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
    info "Deleting kind cluster '$CLUSTER_NAME'..."
    kind delete cluster --name "$CLUSTER_NAME"
    ok "Cluster deleted"
else
    ok "Cluster '$CLUSTER_NAME' does not exist"
fi

# Check if registry is still alive
if podman inspect kagenti-registry --format '{{.State.Running}}' 2>/dev/null | grep -q true; then
    ok "Registry is still running (images preserved)"
    echo ""
    echo "  To recreate the cluster:  scripts/setup.sh"
    echo "  To also remove registry:  scripts/registry.sh stop"
else
    echo ""
    echo "  To recreate the cluster:  scripts/setup.sh"
fi
echo ""
