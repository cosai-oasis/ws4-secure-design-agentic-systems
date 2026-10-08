#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
#  Local OCI Registry for kind + podman
#
#  The registry lives on its own network (kagenti-registry-net) so it
#  survives kind cluster teardown/recreation.  When a kind cluster exists,
#  the registry is bridged to the "kind" network so nodes can pull via
#  podman DNS (kagenti-registry:5000).  Port 5000 is mapped to the VM
#  so you can push from the host.
#
#  Usage:
#    registry.sh start   — start the registry
#    registry.sh stop    — stop and remove the registry container
#    registry.sh status  — connectivity check + image list
#    registry.sh push    — build and push project images
#    registry.sh list    — list images in the registry
#    registry.sh connect — bridge registry to the kind network
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KAGENTI_OPERATOR_DIR="${KAGENTI_OPERATOR_DIR:-$HOME/kagenti-operator}"

REGISTRY_NAME="kagenti-registry"
REGISTRY_NETWORK="kagenti-registry-net"
REGISTRY_IMAGE="ghcr.io/distribution/distribution:3.0.0"
REGISTRY_PORT="${REGISTRY_PORT:-5000}"
REGISTRY_HOST="localhost:${REGISTRY_PORT}"
REGISTRY_INTERNAL="${REGISTRY_NAME}:${REGISTRY_PORT}"
CLUSTER_NAME="${CLUSTER_NAME:-rossoctl}"
KIND_NETWORK="kind"

export KIND_EXPERIMENTAL_PROVIDER=podman
export CONTAINER_ENGINE=podman

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------
info()  { printf '\033[0;34m→\033[0m %s\n' "$*"; }
ok()    { printf '\033[0;32m✓\033[0m %s\n' "$*"; }
warn()  { printf '\033[0;33m!\033[0m %s\n' "$*"; }
err()   { printf '\033[0;31m✗\033[0m %s\n' "$*" >&2; }
die()   { err "$@"; exit 1; }

registry_running() {
    podman inspect "$REGISTRY_NAME" --format '{{.State.Running}}' 2>/dev/null | grep -q true
}

registry_responding() {
    curl -sf "http://${REGISTRY_HOST}/v2/" >/dev/null 2>&1
}

cluster_exists() {
    podman inspect "${CLUSTER_NAME}-control-plane" --format '{{.State.Running}}' 2>/dev/null | grep -q true
}

registry_on_kind_network() {
    podman inspect "$REGISTRY_NAME" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' 2>/dev/null | grep -q "$KIND_NETWORK"
}

# ---------------------------------------------------------------------------
#  connect — bridge registry to the kind network + configure containerd
# ---------------------------------------------------------------------------
connect_to_kind() {
    if ! registry_running; then
        warn "Registry not running — nothing to connect"
        return 0
    fi
    if ! cluster_exists; then
        warn "Kind cluster '$CLUSTER_NAME' not running — skipping"
        return 0
    fi

    if ! podman network exists "$KIND_NETWORK" 2>/dev/null; then
        warn "'$KIND_NETWORK' network does not exist"
        return 1
    fi

    if ! registry_on_kind_network; then
        info "Connecting registry to '$KIND_NETWORK' network..."
        podman network connect "$KIND_NETWORK" "$REGISTRY_NAME"
        ok "Registry connected to '$KIND_NETWORK' network"
    else
        ok "Registry already on '$KIND_NETWORK' network"
    fi

    configure_kind_node
}

configure_kind_node() {
    local node="${CLUSTER_NAME}-control-plane"
    if ! cluster_exists; then
        warn "Kind cluster '$CLUSTER_NAME' not running — skipping containerd config"
        return 0
    fi

    info "Configuring containerd on $node for registry..."
    podman exec "$node" sh -c "
        mkdir -p /etc/containerd/certs.d/localhost:${REGISTRY_PORT}
        cat > /etc/containerd/certs.d/localhost:${REGISTRY_PORT}/hosts.toml <<TOML
server = \"http://${REGISTRY_INTERNAL}\"

[host.\"http://${REGISTRY_INTERNAL}\"]
  capabilities = [\"pull\", \"resolve\"]
  skip_verify = true
TOML
    "
    ok "containerd hosts.toml configured on $node"
}

# ---------------------------------------------------------------------------
#  start
# ---------------------------------------------------------------------------
cmd_start() {
    if registry_running; then
        ok "Registry '$REGISTRY_NAME' already running on port $REGISTRY_PORT"
        connect_to_kind
        return 0
    fi

    # clean up stopped container if it exists
    podman rm -f "$REGISTRY_NAME" 2>/dev/null || true

    # create the registry's own network (survives kind teardown)
    if ! podman network exists "$REGISTRY_NETWORK" 2>/dev/null; then
        info "Creating registry network '$REGISTRY_NETWORK'..."
        podman network create "$REGISTRY_NETWORK"
    fi

    info "Starting registry on port $REGISTRY_PORT..."
    podman run -d \
        --name "$REGISTRY_NAME" \
        --network "$REGISTRY_NETWORK" \
        --publish "${REGISTRY_PORT}:5000" \
        --restart always \
        "$REGISTRY_IMAGE"

    info "Waiting for registry to be ready..."
    for i in $(seq 1 20); do
        if registry_responding; then
            ok "Registry running at http://${REGISTRY_HOST}"
            connect_to_kind
            echo ""
            echo "  Push images:  podman push --tls-verify=false localhost:${REGISTRY_PORT}/<image>:<tag>"
            echo "  Or run:       scripts/registry.sh push"
            echo ""
            return 0
        fi
        sleep 1
    done
    die "Registry did not become ready within 20 seconds"
}

# ---------------------------------------------------------------------------
#  stop
# ---------------------------------------------------------------------------
cmd_stop() {
    if ! podman container exists "$REGISTRY_NAME" 2>/dev/null; then
        ok "Registry '$REGISTRY_NAME' is not running"
        return 0
    fi
    info "Stopping and removing registry..."
    podman rm -f "$REGISTRY_NAME"
    ok "Registry stopped (images are gone — push again after restart)"
}

# ---------------------------------------------------------------------------
#  status
# ---------------------------------------------------------------------------
cmd_status() {
    echo "=== Registry Status ==="
    echo ""

    if ! podman container exists "$REGISTRY_NAME" 2>/dev/null; then
        err "Registry container '$REGISTRY_NAME' does not exist"
        echo "  Run: scripts/registry.sh start"
        return 1
    fi

    local state
    state=$(podman inspect "$REGISTRY_NAME" --format '{{.State.Status}}' 2>/dev/null)
    echo "  Container:  $REGISTRY_NAME ($state)"

    local networks
    networks=$(podman inspect "$REGISTRY_NAME" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' 2>/dev/null)
    echo "  Networks:   $networks"

    if [ "$state" != "running" ]; then
        err "Registry is not running"
        return 1
    fi

    if registry_responding; then
        ok "Host connectivity:  http://${REGISTRY_HOST}/v2/ reachable"
    else
        err "Host connectivity:  http://${REGISTRY_HOST}/v2/ unreachable"
    fi

    if cluster_exists; then
        if registry_on_kind_network; then
            ok "Kind network:  connected"
        else
            warn "Kind network:  not connected"
            echo "  Run: scripts/registry.sh connect"
        fi

        if podman exec "${CLUSTER_NAME}-control-plane" \
            curl -sf "http://${REGISTRY_INTERNAL}/v2/" >/dev/null 2>&1; then
            ok "Kind node connectivity:  http://${REGISTRY_INTERNAL}/v2/ reachable"
        else
            err "Kind node connectivity:  http://${REGISTRY_INTERNAL}/v2/ unreachable"
            echo "  Run: scripts/registry.sh connect"
        fi

        if podman exec "${CLUSTER_NAME}-control-plane" \
            test -f "/etc/containerd/certs.d/localhost:${REGISTRY_PORT}/hosts.toml" 2>/dev/null; then
            ok "containerd hosts.toml:  configured"
        else
            warn "containerd hosts.toml:  missing"
            echo "  Run: scripts/registry.sh connect"
        fi
    else
        warn "Kind cluster '$CLUSTER_NAME' not running — cannot test node connectivity"
    fi

    echo ""
    cmd_list
}

# ---------------------------------------------------------------------------
#  push
# ---------------------------------------------------------------------------
cmd_push() {
    registry_running || die "Registry is not running — run 'registry.sh start' first"
    registry_responding || die "Registry is not responding at http://${REGISTRY_HOST}"

    echo "=== Building and pushing project images ==="
    echo ""

    # keycloak-agentic
    info "Building keycloak-agentic..."
    podman build -t keycloak-agentic:latest "$PROJECT_DIR/keycloak-spi/"
    podman tag localhost/keycloak-agentic:latest "localhost:${REGISTRY_PORT}/keycloak-agentic:latest"
    info "Pushing keycloak-agentic..."
    podman push --tls-verify=false "localhost:${REGISTRY_PORT}/keycloak-agentic:latest"
    ok "keycloak-agentic:latest pushed"

    # agentcard-signer
    local signer_ctx="$KAGENTI_OPERATOR_DIR/operator"
    if [ ! -d "$signer_ctx" ]; then
        warn "operator not found at $signer_ctx — skipping agentcard-signer"
        echo "  Clone it:  git clone https://github.com/kagenti/kagenti-operator.git $KAGENTI_OPERATOR_DIR"
    else
        info "Building agentcard-signer..."
        (cd "$signer_ctx" && podman build -t agentcard-signer:latest -f cmd/agentcard-signer/Dockerfile .)
        podman tag localhost/agentcard-signer:latest "localhost:${REGISTRY_PORT}/agentcard-signer:latest"
        info "Pushing agentcard-signer..."
        podman push --tls-verify=false "localhost:${REGISTRY_PORT}/agentcard-signer:latest"
        ok "agentcard-signer:latest pushed"
    fi

    # rossoctl-operator (rebuilt from source for SPIRE socket fix)
    local operator_ctx="${KAGENTI_OPERATOR_DIR:-$HOME/kagenti-operator}/operator"
    if [ -d "$operator_ctx" ]; then
        info "Building rossoctl-operator..."
        podman build -t rossoctl-operator:latest "$operator_ctx/"
        podman tag localhost/rossoctl-operator:latest "localhost:${REGISTRY_PORT}/rossoctl-operator:latest"
        info "Pushing rossoctl-operator..."
        podman push --tls-verify=false "localhost:${REGISTRY_PORT}/rossoctl-operator:latest"
        ok "rossoctl-operator:latest pushed"
    else
        warn "rossoctl-operator not found at $operator_ctx — skipping"
    fi

    # authbridge (from cortex, needed for AuthBridge sidecar injection)
    local extensions_dir="${KAGENTI_EXTENSIONS_DIR:-$HOME/kagenti-extensions}"
    if [ -d "$extensions_dir/authbridge" ]; then
        info "Building authbridge..."
        (cd "$extensions_dir/authbridge" && podman build -t authbridge:latest -f cmd/authbridge-proxy/Dockerfile .)
        podman tag localhost/authbridge:latest "localhost:${REGISTRY_PORT}/authbridge:latest"
        info "Pushing authbridge..."
        podman push --tls-verify=false "localhost:${REGISTRY_PORT}/authbridge:latest"
        ok "authbridge:latest pushed"
    elif podman image exists localhost/authbridge:otel 2>/dev/null; then
        info "cortex repo not found — pushing existing authbridge:otel image"
        podman tag localhost/authbridge:otel "localhost:${REGISTRY_PORT}/authbridge:latest"
        podman push --tls-verify=false "localhost:${REGISTRY_PORT}/authbridge:latest"
        ok "authbridge:latest pushed (from local otel build)"
    else
        warn "No authbridge image found — skipping"
        echo "  Clone it:  git clone https://github.com/kagenti/kagenti-extensions.git $extensions_dir"
    fi

    # orchestrator-agent
    info "Building orchestrator-agent..."
    podman build -t orchestrator-agent:latest "$PROJECT_DIR/orchestrator/"
    podman tag localhost/orchestrator-agent:latest "localhost:${REGISTRY_PORT}/orchestrator-agent:latest"
    info "Pushing orchestrator-agent..."
    podman push --tls-verify=false "localhost:${REGISTRY_PORT}/orchestrator-agent:latest"
    ok "orchestrator-agent:latest pushed"

    echo ""
    cmd_list
}

# ---------------------------------------------------------------------------
#  list
# ---------------------------------------------------------------------------
cmd_list() {
    if ! registry_responding; then
        err "Registry not responding at http://${REGISTRY_HOST}"
        return 1
    fi

    echo "=== Registry Images ==="
    echo ""

    local repos
    repos=$(curl -sf "http://${REGISTRY_HOST}/v2/_catalog" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('repositories', []):
    print(r)
" 2>/dev/null)

    if [ -z "$repos" ]; then
        echo "  (empty — no images pushed yet)"
        return 0
    fi

    while IFS= read -r repo; do
        local tags
        tags=$(curl -sf "http://${REGISTRY_HOST}/v2/${repo}/tags/list" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(', '.join(data.get('tags', []) or ['(none)']))
" 2>/dev/null)
        echo "  localhost:${REGISTRY_PORT}/${repo}:${tags}"
    done <<< "$repos"
    echo ""
}

# ---------------------------------------------------------------------------
#  Dispatch
# ---------------------------------------------------------------------------

# Allow sourcing for connect_to_kind / configure_kind_node
if [[ "${1:-}" == "--source-only" ]]; then
    return 0 2>/dev/null || exit 0
fi

case "${1:-help}" in
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    status)  cmd_status ;;
    push)    cmd_push ;;
    list)    cmd_list ;;
    connect) connect_to_kind ;;
    *)
        echo "Usage: $(basename "$0") {start|stop|status|push|list|connect}"
        echo ""
        echo "  start    Start the local registry"
        echo "  stop     Stop and remove the registry"
        echo "  status   Show registry state and connectivity"
        echo "  push     Build and push project images"
        echo "  list     List images in the registry"
        echo "  connect  Bridge registry to kind network + configure containerd"
        exit 1
        ;;
esac
