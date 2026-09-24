import http.server
import json
import os
import urllib.request
import uuid

import tracing

CARD_PATH = "/app/.well-known/agent-card.json"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")
PEERS_FILE = os.environ.get("PEERS_FILE", "/etc/peers/peers.json")

_peers_cache = None


def load_peers():
    global _peers_cache
    if _peers_cache is None:
        with open(PEERS_FILE, "r") as f:
            _peers_cache = json.load(f)
    return _peers_cache


def call_ollama(prompt, trace_id=None, parent_span_id=None):
    span = tracing.Span(
        "orchestrator.ollama_generate",
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        kind=tracing.SPAN_KIND_CLIENT,
    )
    span.set_attribute("ollama.model", OLLAMA_MODEL)
    span.set_attribute("ollama.prompt_length", len(prompt))

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "traceparent": span.traceparent(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
        response_text = result.get("response", "").strip()
        span.set_attribute("ollama.response_length", len(response_text))
        span.end()
        return response_text, span
    except Exception as e:
        print(f"[orchestrator] Ollama error: {e}", flush=True)
        span.set_error(str(e))
        span.end()
        return None, span


def route_to_peer(user_text, peers, trace_id=None, parent_span_id=None):
    peer_list = "\n".join(
        f"- {p['name']}: {p['description']}" for p in peers
    )
    prompt = (
        f"You are a router. Given these agents:\n{peer_list}\n\n"
        f"User request: \"{user_text}\"\n\n"
        f"Which agent name should handle this? Reply with ONLY the agent name, nothing else."
    )

    response, ollama_span = call_ollama(prompt, trace_id, parent_span_id)
    if response:
        for peer in peers:
            if peer["name"].lower() in response.lower():
                return peer, [ollama_span]
    return (peers[0] if peers else None), [ollama_span]


def fetch_agent_card(url, auth_header="", trace_id=None, parent_span_id=None):
    span = tracing.Span(
        "orchestrator.fetch_agent_card",
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        kind=tracing.SPAN_KIND_CLIENT,
    )
    span.set_attribute("peer.url", url)

    try:
        card_url = f"{url}/.well-known/agent-card.json"
        headers = {"traceparent": span.traceparent()}
        if auth_header:
            headers["Authorization"] = auth_header
        req = urllib.request.Request(card_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            card = json.loads(resp.read())
        span.set_attribute("peer.name", card.get("name", ""))
        span.end()
        return card, span
    except Exception as e:
        print(f"[orchestrator] Failed to fetch agent card from {url}: {e}", flush=True)
        span.set_error(str(e))
        span.end()
        return None, span


def forward_request(peer_url, jsonrpc_request, auth_header="", trace_id=None, parent_span_id=None):
    span = tracing.Span(
        "orchestrator.forward_to_peer",
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        kind=tracing.SPAN_KIND_CLIENT,
    )
    span.set_attribute("peer.url", peer_url)
    span.set_attribute("jsonrpc.method", jsonrpc_request.get("method", ""))

    payload = json.dumps(jsonrpc_request).encode()
    headers = {
        "Content-Type": "application/json",
        "traceparent": span.traceparent(),
    }
    if auth_header:
        headers["Authorization"] = auth_header
    req = urllib.request.Request(f"{peer_url}/", data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        span.end()
        return result, span
    except Exception as e:
        print(f"[orchestrator] Forward error to {peer_url}: {e}", flush=True)
        span.set_error(str(e))
        span.end()
        return None, span


class OrchestratorHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[orchestrator] {fmt % args}", flush=True)

    def do_GET(self):
        if self.path == "/.well-known/agent-card.json":
            try:
                with open(CARD_PATH, "r") as f:
                    card = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(card.encode())
            except FileNotFoundError:
                self.send_error(404, "Agent card not found")
        else:
            self.send_error(404)

    def do_POST(self):
        tp = tracing.parse_traceparent(self.headers.get("traceparent"))
        root = tracing.Span(
            "orchestrator.message_send",
            trace_id=tp["trace_id"] if tp else None,
            parent_span_id=tp["parent_span_id"] if tp else None,
            kind=tracing.SPAN_KIND_SERVER,
        )
        spans = [root]

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            root.set_error("Parse error")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(None, -32700, "Parse error")
            return

        req_id = req.get("id")
        method = req.get("method")
        root.set_attribute("jsonrpc.id", str(req_id))
        root.set_attribute("jsonrpc.method", str(method))

        if method != "message/send":
            root.set_error(f"Unknown method: {method}")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(req_id, -32601, f"Unknown method: {method}")
            return

        try:
            parts = req["params"]["message"]["parts"]
            user_text = next((p["text"] for p in parts if p.get("type") == "text"), "")
        except (KeyError, StopIteration):
            user_text = ""

        if not user_text.strip():
            root.set_error("Empty message")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(req_id, -32602, "Empty message")
            return

        auth_header = self.headers.get("Authorization", "")
        tracing.set_auth_attributes(root, auth_header)

        peers = load_peers()
        if not peers:
            root.set_error("No peers configured")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(req_id, -32000, "No peers configured")
            return

        peer, route_spans = route_to_peer(
            user_text, peers, trace_id=root.trace_id, parent_span_id=root.span_id
        )
        spans.extend(route_spans)

        if not peer:
            root.set_error("No suitable peer found")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(req_id, -32000, "No suitable peer found")
            return

        root.set_attribute("peer.selected", peer["name"])
        print(f"[orchestrator] Routing to {peer['name']} at {peer['url']}", flush=True)

        card, card_span = fetch_agent_card(
            peer["url"], auth_header=auth_header,
            trace_id=root.trace_id, parent_span_id=root.span_id,
        )
        spans.append(card_span)

        if not card:
            root.set_error(f"Peer {peer['name']} unreachable")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(req_id, -32000, f"Peer {peer['name']} unreachable")
            return

        print(f"[orchestrator] Verified agent card: {card.get('name')}", flush=True)

        peer_response, fwd_span = forward_request(
            peer["url"], req, auth_header=auth_header,
            trace_id=root.trace_id, parent_span_id=root.span_id,
        )
        spans.append(fwd_span)

        if not peer_response:
            root.set_error(f"Peer {peer['name']} did not respond")
            root.end()
            tracing.export_spans(spans)
            self._json_rpc_error(req_id, -32000, f"Peer {peer['name']} did not respond")
            return

        peer_text = ""
        try:
            artifacts = peer_response["result"]["artifacts"]
            peer_text = artifacts[0]["parts"][0]["text"]
        except (KeyError, IndexError):
            peer_text = json.dumps(peer_response.get("result", {}))

        resp = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "id": f"task-{uuid.uuid4().hex[:8]}",
                "status": {"state": "completed"},
                "artifacts": [{
                    "parts": [{
                        "type": "text",
                        "text": f"[Routed to {peer['name']}] {peer_text}"
                    }]
                }]
            }
        }

        root.end()
        tracing.export_spans(spans)
        self._send_json(resp)

    def _json_rpc_error(self, req_id, code, message):
        resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
        self._send_json(resp)

    def _send_json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = http.server.HTTPServer(("0.0.0.0", port), OrchestratorHandler)
    print(f"[orchestrator] A2A router listening on :{port} (LLM: {OLLAMA_URL}, model: {OLLAMA_MODEL})", flush=True)
    server.serve_forever()
