#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
#  Rossoctl + SPIRE Signing Demo — Full Setup
#
#  Recreates the blog-post environment:
#    1. Gets the custom Keycloak image (from registry or builds locally)
#    2. Creates a kind cluster and makes images available
#    3. Installs the platform with SPIRE via rossoctl installer
#    4. Enables signature verification on the operator (audit mode)
#    5. Gets the agentcard-signer, deploys the weather-agent demo
#
#  When the local registry is running (scripts/registry.sh start) and
#  images have been pushed (scripts/registry.sh push), this script pulls
#  from it instead of building.
#
#  Options:
#    --force-build              Build images even if registry is available
#    --skip-cluster-recreate    Reuse existing cluster (faster iteration)
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KAGENTI_DIR="${KAGENTI_DIR:-$HOME/kagenti}"
KAGENTI_OPERATOR_DIR="${KAGENTI_OPERATOR_DIR:-$HOME/kagenti-operator}"
CLUSTER_NAME="${CLUSTER_NAME:-rossoctl}"
TRUST_DOMAIN="localtest.me"

REGISTRY_NAME="kagenti-registry"
REGISTRY_PORT="${REGISTRY_PORT:-5000}"
REGISTRY_HOST="localhost:${REGISTRY_PORT}"

FORCE_BUILD=false
SKIP_CLUSTER_RECREATE=false

export KIND_EXPERIMENTAL_PROVIDER=podman
export CONTAINER_ENGINE=podman

# ---------------------------------------------------------------------------
#  Args
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force-build) FORCE_BUILD=true; shift ;;
        --skip-cluster-recreate) SKIP_CLUSTER_RECREATE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------
info()  { printf '\033[0;34m→\033[0m %s\n' "$*"; }
ok()    { printf '\033[0;32m✓\033[0m %s\n' "$*"; }
warn()  { printf '\033[0;33m!\033[0m %s\n' "$*"; }
err()   { printf '\033[0;31m✗\033[0m %s\n' "$*" >&2; }
die()   { err "$@"; exit 1; }

load_image_to_kind() {
    local image="$1"
    local sanitized="${image//\//_}"; sanitized="${sanitized//:/_}"
    local tmp="/tmp/${sanitized}.tar"
    info "Loading $image into kind cluster..."
    podman save "$image" -o "$tmp"
    podman cp "$tmp" "${CLUSTER_NAME}-control-plane:/tmp/image.tar"
    podman exec "${CLUSTER_NAME}-control-plane" \
        ctr -n k8s.io images import /tmp/image.tar
    rm -f "$tmp"
    ok "Image loaded: $image"
}

registry_available() {
    ! $FORCE_BUILD && \
    podman inspect "$REGISTRY_NAME" --format '{{.State.Running}}' 2>/dev/null | grep -q true && \
    curl -sf "http://${REGISTRY_HOST}/v2/" >/dev/null 2>&1
}

registry_has_image() {
    local repo="$1" tag="${2:-latest}"
    curl -sf "http://${REGISTRY_HOST}/v2/${repo}/manifests/${tag}" \
        -H "Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json" \
        >/dev/null 2>&1
}

USE_REGISTRY=false

# ---------------------------------------------------------------------------
#  Preflight
# ---------------------------------------------------------------------------
info "Checking prerequisites..."
for cmd in podman helm kubectl kind; do
    command -v "$cmd" >/dev/null || die "$cmd not found in PATH"
done
ok "All tools found"

[ -d "$KAGENTI_DIR" ] || die "kagenti repo not found at $KAGENTI_DIR — clone https://github.com/kagenti/kagenti.git"

if registry_available; then
    USE_REGISTRY=true
    ok "Local registry detected at $REGISTRY_HOST"
else
    if $FORCE_BUILD; then
        info "Force-build mode — skipping registry"
    else
        info "No local registry — will build images locally"
    fi
fi

# ---------------------------------------------------------------------------
#  Step 0: inotify limits
# ---------------------------------------------------------------------------
info "Checking inotify limits..."
watches=$(cat /proc/sys/fs/inotify/max_user_watches)
instances=$(cat /proc/sys/fs/inotify/max_user_instances)
if [ "$watches" -lt 524288 ] || [ "$instances" -lt 512 ]; then
    info "Setting inotify limits (requires sudo)..."
    sudo sysctl -w fs.inotify.max_user_watches=524288 \
                   fs.inotify.max_user_instances=512
    ok "inotify limits set"
else
    ok "inotify limits already sufficient (watches=$watches, instances=$instances)"
fi

# ---------------------------------------------------------------------------
#  Step 1: Get keycloak-agentic image
# ---------------------------------------------------------------------------
if $USE_REGISTRY && registry_has_image "keycloak-agentic"; then
    KEYCLOAK_REPO="localhost:${REGISTRY_PORT}/keycloak-agentic"
    ok "keycloak-agentic found in registry — will pull from $REGISTRY_HOST"
else
    KEYCLOAK_REPO="localhost/keycloak-agentic"
    info "Building keycloak-agentic image..."
    podman build -t keycloak-agentic:latest "$PROJECT_DIR/keycloak-spi/"
    ok "keycloak-agentic:latest built"
fi

# ---------------------------------------------------------------------------
#  Step 2: Create keycloak-values.yaml
# ---------------------------------------------------------------------------
KEYCLOAK_VALUES="$PROJECT_DIR/keycloak-values.yaml"
cat > "$KEYCLOAK_VALUES" <<YAML
keycloak:
  image:
    repository: ${KEYCLOAK_REPO}
    tag: latest
    pullPolicy: IfNotPresent
  extraEnvVars:
    - name: KC_FEATURES
      value: "client-auth-federated:v1,spiffe:v1,token-exchange:v1,token-exchange-standard:v2,kubernetes-service-accounts:v1"
YAML
ok "keycloak-values.yaml written (repo: $KEYCLOAK_REPO)"

# ---------------------------------------------------------------------------
#  Step 3: Create kind cluster
# ---------------------------------------------------------------------------
if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
    if $SKIP_CLUSTER_RECREATE; then
        ok "Cluster '$CLUSTER_NAME' already exists — reusing it"
    else
        info "Cluster '$CLUSTER_NAME' already exists — deleting..."
        kind delete cluster --name "$CLUSTER_NAME"
        info "Creating kind cluster '$CLUSTER_NAME'..."
        kind create cluster --name "$CLUSTER_NAME" \
            --config "$KAGENTI_DIR/scripts/kind/kind-config-registry.yaml"
        ok "Kind cluster created"
    fi
else
    info "Creating kind cluster '$CLUSTER_NAME'..."
    kind create cluster --name "$CLUSTER_NAME" \
        --config "$KAGENTI_DIR/scripts/kind/kind-config-registry.yaml"
    ok "Kind cluster created"
fi

# ---------------------------------------------------------------------------
#  Step 4: Make images available in kind
# ---------------------------------------------------------------------------
if $USE_REGISTRY; then
    info "Connecting registry to kind cluster..."
    source "$SCRIPT_DIR/registry.sh" --source-only
    connect_to_kind
else
    load_image_to_kind "localhost/keycloak-agentic:latest"
fi

# ---------------------------------------------------------------------------
#  Step 4b: Build operator image before platform install
#           (ghcr.io chart images may be inaccessible; use local build)
# ---------------------------------------------------------------------------
if [ ! -d "$KAGENTI_OPERATOR_DIR" ]; then
    info "Cloning kagenti-operator..."
    git clone https://github.com/kagenti/kagenti-operator.git "$KAGENTI_OPERATOR_DIR"
    ok "kagenti-operator cloned"
else
    ok "kagenti-operator already at $KAGENTI_OPERATOR_DIR"
fi

if $USE_REGISTRY && registry_has_image "rossoctl-operator"; then
    OPERATOR_IMG="localhost:${REGISTRY_PORT}/rossoctl-operator:latest"
    ok "rossoctl-operator found in registry"
else
    OPERATOR_IMG="localhost/rossoctl-operator:latest"
    info "Building rossoctl-operator from source..."
    podman build -t rossoctl-operator:latest "$KAGENTI_OPERATOR_DIR/operator/"
    ok "rossoctl-operator built"
    load_image_to_kind "localhost/rossoctl-operator:latest"
fi

if $USE_REGISTRY && registry_has_image "authbridge"; then
    AUTHBRIDGE_IMG="localhost:${REGISTRY_PORT}/authbridge:latest"
    ok "authbridge found in registry"
else
    AUTHBRIDGE_IMG="localhost/authbridge:otel"
    if podman image exists "$AUTHBRIDGE_IMG" 2>/dev/null; then
        ok "Using local authbridge:otel image"
        load_image_to_kind "$AUTHBRIDGE_IMG"
    else
        die "No authbridge image available. Build from cortex or run 'registry.sh push'"
    fi
fi

OPERATOR_VALUES="$PROJECT_DIR/operator-values.yaml"
cat > "$OPERATOR_VALUES" <<YAML
operator-chart:
  controllerManager:
    container:
      image:
        repository: ${OPERATOR_IMG%:*}
        tag: ${OPERATOR_IMG##*:}
        pullPolicy: IfNotPresent
  defaults:
    images:
      authbridge: ${AUTHBRIDGE_IMG}
      pullPolicy: IfNotPresent
    proxy:
      transparentPort: 8083
YAML
ok "operator-values.yaml written (operator: $OPERATOR_IMG, authbridge: $AUTHBRIDGE_IMG)"

# ---------------------------------------------------------------------------
#  Step 5: Install platform with SPIRE (skip cluster creation)
# ---------------------------------------------------------------------------
info "Installing rossoctl platform with SPIRE..."
# Clean up stale Helm releases from interrupted prior runs
for rel in rossoctl-deps rossoctl; do
    if helm status "$rel" -n rossoctl-system 2>/dev/null | grep -q 'pending-install'; then
        warn "Cleaning up stale $rel release (pending-install)..."
        helm uninstall "$rel" -n rossoctl-system --no-hooks 2>/dev/null || true
    fi
done
(cd "$KAGENTI_DIR" && bash scripts/kind/setup-rossoctl.sh \
    --skip-cluster \
    --with-spire \
    --rossoctl-deps-values "$KEYCLOAK_VALUES" \
    --rossoctl-values "$OPERATOR_VALUES")

# Ensure keycloak statefulset uses IfNotPresent (chart may override)
kubectl patch statefulset keycloak -n keycloak \
    --type='json' \
    -p='[{"op":"replace","path":"/spec/template/spec/containers/0/imagePullPolicy","value":"IfNotPresent"}]' \
    2>/dev/null || true

info "Waiting for Keycloak to be ready..."
kubectl wait --for=condition=ready pod/keycloak-0 -n keycloak --timeout=180s
ok "Platform installed"

# ---------------------------------------------------------------------------
#  Step 5b: Enable Phoenix tracing
# ---------------------------------------------------------------------------
info "Enabling Phoenix tracing..."
helm upgrade rossoctl-deps "$KAGENTI_DIR/charts/rossoctl-deps" \
    --namespace rossoctl-system \
    --reuse-values \
    -f "$PROJECT_DIR/phoenix-values.yaml"

kubectl wait --for=condition=available --timeout=120s \
    deployment/otel-collector -n rossoctl-system
kubectl rollout status statefulset/phoenix -n rossoctl-system --timeout=120s 2>/dev/null || true
ok "Phoenix tracing enabled"

# ---------------------------------------------------------------------------
#  Step 6: Enable signature verification (audit mode)
# ---------------------------------------------------------------------------
info "Enabling signature verification on operator (audit mode)..."
helm upgrade rossoctl "$KAGENTI_DIR/charts/rossoctl" \
    --namespace rossoctl-system \
    --reuse-values \
    --set operator-chart.signatureVerification.enabled=true \
    --set operator-chart.signatureVerification.spireTrustDomain="$TRUST_DOMAIN" \
    --set operator-chart.signatureVerification.spireTrustBundle.configMapNamespace=spire-system \
    --set operator-chart.signatureVerification.enforceNetworkPolicies=true \
    --set operator-chart.signatureVerification.auditMode=true \
    --set authBridge.clientAuthType=federated-jwt

kubectl rollout status deployment/rossoctl-controller-manager \
    -n rossoctl-system --timeout=60s
ok "Signature verification enabled (audit mode)"

# ---------------------------------------------------------------------------
#  Step 6b: Create demo-ui Keycloak client and Alice user
# ---------------------------------------------------------------------------
info "Waiting for Keycloak pod to be ready..."
kubectl wait --for=condition=ready pod/keycloak-0 -n keycloak --timeout=300s

# Keycloak's readiness probe checks /health/ready endpoint, so if pod is Ready, Keycloak is ready.
# Give it a few extra seconds to fully initialize the admin console.
info "Waiting for Keycloak admin console to initialize..."
sleep 10
ok "Keycloak is ready"

info "Creating demo-ui Keycloak client and Alice user..."

# Retry kcadm login in case Keycloak needs a moment after pod ready
RETRY=0
until kubectl exec -n keycloak keycloak-0 -- bash -c '
  /opt/keycloak/bin/kcadm.sh config credentials \
    --server http://localhost:8080 --realm master --user admin --password admin 2>&1
' | grep -q "Logging into" ; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge 6 ]; then
        die "kcadm.sh login failed after 30 seconds"
    fi
    info "Waiting for Keycloak admin API (attempt $RETRY/6)..."
    sleep 5
done

kubectl exec -n keycloak keycloak-0 -- bash -c '
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 --realm master --user admin --password admin

/opt/keycloak/bin/kcadm.sh create clients -r rossoctl \
  -s clientId=demo-ui \
  -s publicClient=true \
  -s standardFlowEnabled=true \
  -s directAccessGrantsEnabled=false \
  -s "redirectUris=[\"http://demo-ui.localtest.me:8080/*\"]" \
  -s "webOrigins=[\"http://demo-ui.localtest.me:8080\"]" \
  -s rootUrl=http://demo-ui.localtest.me:8080 \
  -s "attributes={\"pkce.code.challenge.method\":\"S256\"}" \
  2>/dev/null || true

/opt/keycloak/bin/kcadm.sh create users -r rossoctl \
  -s username=alice -s enabled=true \
  -s email=alice@demo.localtest.me \
  -s emailVerified=true \
  -s firstName=Alice -s lastName=Demo \
  2>/dev/null || true

ALICE_ID=$(/opt/keycloak/bin/kcadm.sh get users -r rossoctl -q username=alice \
  --fields id --format csv --noquotes)
/opt/keycloak/bin/kcadm.sh set-password -r rossoctl --userid "$ALICE_ID" --new-password alice
'
ok "Keycloak demo-ui client and Alice user created"

# ---------------------------------------------------------------------------
#  Step 7: Operator already built and deployed in Step 4b
# ---------------------------------------------------------------------------
ok "Operator image already set via Helm values (Step 4b)"

# ---------------------------------------------------------------------------
#  Step 8: Get agentcard-signer image
# ---------------------------------------------------------------------------
if $USE_REGISTRY && registry_has_image "agentcard-signer"; then
    SIGNER_IMG="localhost:${REGISTRY_PORT}/agentcard-signer:latest"
    ok "agentcard-signer found in registry — will pull from $REGISTRY_HOST"
else
    SIGNER_IMG="ghcr.io/rossoctl/operator/agentcard-signer:latest"
    info "Building agentcard-signer..."
    (cd "$KAGENTI_OPERATOR_DIR/operator" && \
        podman build -t "$SIGNER_IMG" -f cmd/agentcard-signer/Dockerfile .)
    ok "agentcard-signer built"
    load_image_to_kind "$SIGNER_IMG"
fi

# ---------------------------------------------------------------------------
#  Step 9: Deploy the SPIRE signing demo
# ---------------------------------------------------------------------------
DEMO_DIR="$KAGENTI_OPERATOR_DIR/operator/demos/agentcard-spire-signing"
info "Deploying SPIRE signing demo..."

kubectl apply -f "$DEMO_DIR/k8s/namespace.yaml"
kubectl label namespace agents rossoctl-enabled=true --overwrite 2>/dev/null || true
kubectl apply -f "$DEMO_DIR/k8s/clusterspiffeid.yaml"

# --- Deploy shared OTel tracing module ---
kubectl apply -f "$PROJECT_DIR/k8s/otel-tracing.yaml"

# --- 9-pre-a: Copy authbridge-config to agents namespace.
#     The operator's ClientRegistration controller reads authbridge-config from the
#     agent's namespace (not rossoctl-system). Without it, client registration stalls
#     and the spiffe-helper-config / keycloak credentials are never created.
info "Copying authbridge-config to agents namespace (with PLATFORM_CLIENT_IDS)..."
kubectl get configmap authbridge-config -n rossoctl-system -o json \
    | jq 'del(.metadata.namespace, .metadata.resourceVersion, .metadata.uid, .metadata.creationTimestamp, .metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"], .metadata.managedFields)' \
    | jq '.metadata.namespace = "agents" | .data.PLATFORM_CLIENT_IDS = "demo-ui"' \
    | kubectl apply -f -
ok "authbridge-config copied to agents namespace"

# --- 9-pre-a2: Copy authbridge-runtime-config with transparent proxy port fix.
#     operator's findFreePort assigns forward_proxy_addr=:8082 which collides with the
#     authbridge preset default transparent_proxy_addr=:8082. Override to :8083.
#     proxy.transparentPort=8083 in operator-values.yaml matches.
#     NOTE: no allowed_audiences override needed — PLATFORM_CLIENT_IDS=demo-ui (above)
#     causes the operator to attach per-agent audience scopes to demo-ui, so Alice's
#     tokens include agent SPIFFE IDs. The default jwt-validation audience (from
#     /shared/client-id.txt) matches both Alice's direct tokens and delegated tokens.
info "Copying authbridge-runtime-config to agents namespace (port fix)..."
kubectl get configmap authbridge-runtime-config -n rossoctl-system -o json \
    | jq 'del(.metadata.namespace, .metadata.resourceVersion, .metadata.uid, .metadata.creationTimestamp, .metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"], .metadata.managedFields, .metadata.labels["app.kubernetes.io/managed-by"], .metadata.labels["helm.sh/chart"], .metadata.labels["app.kubernetes.io/version"])' \
    | jq '.metadata.namespace = "agents"' \
    | python3 -c "
import sys, json, yaml
cm = json.load(sys.stdin)
config = yaml.safe_load(cm['data']['config.yaml']) or {}
listener = config.setdefault('listener', {})
listener['transparent_proxy_addr'] = ':8083'
cm['data']['config.yaml'] = yaml.dump(config, default_flow_style=False)
json.dump(cm, sys.stdout)
" \
    | kubectl apply -f -
ok "authbridge-runtime-config copied with transparent_proxy_addr=:8083"

# --- 9-pre-b: Deploy agents first (without rossoctl.io/type labels), then
#     AgentRuntime CRs. The operator requires the target Deployment to exist before
#     it reconciles an AgentRuntime CR. The operator then adds rossoctl.io/type labels,
#     creates prerequisites, and triggers the webhook to inject the AuthBridge sidecar.
#     A ValidatingAdmissionPolicy prevents setting rossoctl.io/type labels manually.
info "Creating authproxy-routes ConfigMap for token exchange..."
kubectl apply -f "$PROJECT_DIR/k8s/authproxy-routes.yaml"
ok "AuthBridge outbound routes configured"

# --- 9a: Deploy weather-agent (no rossoctl.io/type label — operator adds it) ---
info "Deploying weather-agent with A2A handler..."
kubectl apply -f "$PROJECT_DIR/k8s/weather-agent-server.yaml"

if $USE_REGISTRY && registry_has_image "agentcard-signer"; then
    info "Patching weather-agent to use registry signer image..."
    sed "s|image: ghcr.io/rossoctl/operator/agentcard-signer:latest|image: localhost:${REGISTRY_PORT}/agentcard-signer:latest|" \
        "$PROJECT_DIR/k8s/weather-agent-deployment.yaml" | kubectl apply -f -
else
    kubectl apply -f "$PROJECT_DIR/k8s/weather-agent-deployment.yaml"
fi
info "weather-agent Deployment created (operator will add labels and inject sidecar)"

# --- 9b: Deploy Ollama (in-cluster LLM) ---
info "Deploying Ollama..."
kubectl apply -f "$PROJECT_DIR/k8s/ollama-deployment.yaml"
info "Waiting for Ollama to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/ollama -n agents
ok "Ollama is running"

info "Pulling qwen2.5:0.5b model (this may take a few minutes)..."
OLLAMA_POD=$(kubectl get pods -n agents -l app.kubernetes.io/name=ollama \
    --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n agents "$OLLAMA_POD" -- ollama pull qwen2.5:0.5b
ok "Model qwen2.5:0.5b pulled"

# --- 9c: Deploy orchestrator agent (no rossoctl.io/type label — operator adds it) ---
if $USE_REGISTRY && registry_has_image "orchestrator-agent"; then
    ORCH_IMG="localhost:${REGISTRY_PORT}/orchestrator-agent:latest"
    ok "orchestrator-agent found in registry"
else
    ORCH_IMG="localhost/orchestrator-agent:latest"
    info "Building orchestrator-agent image..."
    podman build -t orchestrator-agent:latest "$PROJECT_DIR/orchestrator/"
    load_image_to_kind "localhost/orchestrator-agent:latest"
fi

info "Deploying orchestrator agent..."
if $USE_REGISTRY && registry_has_image "orchestrator-agent"; then
    sed -e "s|image: ghcr.io/rossoctl/operator/agentcard-signer:latest|image: localhost:${REGISTRY_PORT}/agentcard-signer:latest|" \
        -e "s|image: localhost:5000/orchestrator-agent:latest|image: ${ORCH_IMG}|" \
        "$PROJECT_DIR/k8s/orchestrator-deployment.yaml" | kubectl apply -f -
else
    sed "s|image: localhost:5000/orchestrator-agent:latest|image: ${ORCH_IMG}|" \
        "$PROJECT_DIR/k8s/orchestrator-deployment.yaml" | kubectl apply -f -
fi
info "orchestrator-agent Deployment created (operator will add labels and inject sidecar)"

# --- 9d: Now both Deployments exist — apply AgentRuntime CRs so operator can reconcile ---
info "Creating AgentRuntime CRs (operator needs Deployments to exist first)..."
kubectl apply -f "$PROJECT_DIR/k8s/agentruntime.yaml"

info "Waiting for operator to create AuthBridge prerequisites..."
for i in $(seq 1 90); do
    cm_ok="no"; sec_ok="no"
    kubectl get configmap spiffe-helper-config -n agents >/dev/null 2>&1 && cm_ok="yes"
    kubectl get secrets -n agents -o name 2>/dev/null | grep -q rossoctl-keycloak-client-credentials && sec_ok="yes"
    if [ "$cm_ok" = "yes" ] && [ "$sec_ok" = "yes" ]; then
        break
    fi
    sleep 2
done
if [ "$cm_ok" != "yes" ] || [ "$sec_ok" != "yes" ]; then
    die "AuthBridge prerequisites not ready after 3 minutes (spiffe-helper-config=$cm_ok, keycloak-secret=$sec_ok). Check operator logs."
fi
ok "AuthBridge prerequisites ready"

# --- 9e: Ensure pods are fresh after operator added labels + prerequisites ---
info "Restarting agent deployments to ensure AuthBridge sidecar is injected..."
kubectl rollout restart deployment/weather-agent -n agents
kubectl rollout restart deployment/orchestrator-agent -n agents

info "Waiting for weather-agent deployment..."
kubectl wait --for=condition=available --timeout=180s \
    deployment/weather-agent -n agents
ok "Weather agent running"

info "Waiting for orchestrator-agent deployment..."
kubectl wait --for=condition=available --timeout=180s \
    deployment/orchestrator-agent -n agents
ok "Orchestrator agent running"

# --- 9f: Wait for operator to auto-create and sync AgentCards ---
info "Waiting for AgentCards to be created and synced..."
for i in $(seq 1 60); do
    card_count=$(kubectl get agentcard -n agents --no-headers 2>/dev/null | wc -l)
    if [ "$card_count" -ge 2 ]; then
        all_synced="yes"
        while IFS= read -r card_name; do
            synced=$(kubectl get agentcard "$card_name" -n agents \
                -o jsonpath='{.status.conditions[?(@.type=="Synced")].status}' 2>/dev/null)
            [ "$synced" != "True" ] && all_synced="no"
        done < <(kubectl get agentcard -n agents -o jsonpath='{.items[*].metadata.name}' 2>/dev/null | tr ' ' '\n')
        [ "$all_synced" = "yes" ] && break
    fi
    sleep 2
done
ok "AgentCards synced ($(kubectl get agentcard -n agents --no-headers 2>/dev/null | wc -l) cards)"

# --- Deploy demo UI ---
info "Deploying demo UI..."
kubectl label namespace agents shared-gateway-access=true --overwrite 2>/dev/null || true
kubectl apply -f "$PROJECT_DIR/k8s/demo-ui.yaml"

info "Waiting for demo-ui deployment..."
kubectl wait --for=condition=available --timeout=60s \
    deployment/demo-ui -n agents
ok "Demo UI deployed"

ok "Demo deployed"

# ---------------------------------------------------------------------------
#  Step 10: Verify
# ---------------------------------------------------------------------------
echo ""
info "Running demo verification..."
(cd "$KAGENTI_OPERATOR_DIR/operator" && \
    bash "$DEMO_DIR/run-demo-commands.sh")

echo ""
echo "============================================"
ok "Setup complete!"
echo "============================================"
echo ""
echo "  Demo UI:   http://demo-ui.localtest.me:8080  (alice / alice)"
echo "  Phoenix:   http://phoenix.localtest.me:8080"
echo "  Keycloak:  http://keycloak.localtest.me:8080  (admin / admin)"
echo "  Tornjak:   http://spire-tornjak-ui.localtest.me:8080"
echo ""
echo "  Signature verification: audit mode (logs only, no blocking)"
echo "  AuthBridge:             proxy-sidecar (federated-jwt)"
echo "  Trust domain:           $TRUST_DOMAIN"
echo ""
if $USE_REGISTRY; then
    echo "  Images:    pulled from local registry ($REGISTRY_HOST)"
else
    echo "  Images:    built locally"
    echo "  Tip:       run 'scripts/registry.sh start && scripts/registry.sh push'"
    echo "             to cache images for faster cluster recreation"
fi
echo ""
echo "  To switch to strict enforcement:"
echo "    helm upgrade rossoctl $KAGENTI_DIR/charts/rossoctl \\"
echo "      --namespace rossoctl-system --reuse-values \\"
echo "      --set operator-chart.signatureVerification.auditMode=false"
echo ""
