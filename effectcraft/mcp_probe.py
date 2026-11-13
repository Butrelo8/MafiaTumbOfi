"""Probe `effectcraft-cli mcp` over raw stdio JSON-RPC: initialize, tools/list, then the calls given as arguments.

  python3 -I effectcraft/mcp_probe.py <write_root> [tool '{"arg":..}' ...]
Prints the tool names and each call's result (truncated). Not registered in any .mcp.json: this only tests the server.
"""
import json, subprocess, sys, time

root = sys.argv[1]
p = subprocess.Popen(["effectcraft-cli", "mcp", "--automation-read-root", root, "--automation-write-root", root],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
n = 0


def rpc(method, params=None, notify=False):
    global n
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if not notify:
        n += 1
        msg["id"] = n
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    if notify:
        return None
    while True:
        line = p.stdout.readline()
        if not line:
            raise SystemExit("server closed: " + p.stderr.read()[-2000:])
        r = json.loads(line)
        if r.get("id") == n:
            return r


t = time.time()
r = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "probe", "version": "0"}})
print("initialize", json.dumps(r.get("result", r))[:400], "%.2fs" % (time.time() - t))
rpc("notifications/initialized", notify=True)
tools = rpc("tools/list")["result"]["tools"]
print("tools", len(tools), [x["name"] for x in tools])
args = sys.argv[2:]
for name, a in zip(args[::2], args[1::2]):
    t = time.time()
    r = rpc("tools/call", {"name": name, "arguments": json.loads(a)})
    print("call", name, "%.2fs" % (time.time() - t), json.dumps(r.get("result", r))[:1500])
p.stdin.close()
p.wait(timeout=10)
