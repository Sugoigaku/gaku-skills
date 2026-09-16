"""Run a synthetic, read-only native skill smoke test; do not grade semantics."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "behavior"
NAMES = ("topic-plan", "false-quote", "enrichment", "session-delivery")


def bundle_digest(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def cli_command():
    executable = shutil.which("copilot")
    if executable is None:
        raise RuntimeError("Copilot CLI is unavailable; no packages were installed.")
    path = Path(executable)
    if path.suffix.lower() in {".cmd", ".bat"}:
        loader = path.parent / "node_modules" / "@github" / "copilot" / "npm-loader.js"
        sibling_node = path.parent / "node.exe"
        node = str(sibling_node) if sibling_node.is_file() else shutil.which("node")
        if node is None or not loader.is_file():
            raise RuntimeError("The Windows CLI shim has no supported direct Node entry point.")
        return [node, str(loader)]
    return [executable]


def summarize_events(output, fixture, return_code):
    invocations = set()
    completed = set()
    tools = []
    messages = []
    malformed = 0
    failed_tools = 0
    reported_exit_code = None
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line.lstrip("\ufeff"))
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(event, dict) and event.get("type") == "result":
            code = event.get("exitCode")
            if type(code) is not int or reported_exit_code is not None:
                malformed += 1
            else:
                reported_exit_code = code
            continue
        if not isinstance(event, dict) or not isinstance(event.get("data"), dict):
            malformed += 1
            continue
        data = event["data"]
        kind = event.get("type")
        if kind == "tool.execution_start":
            name = data.get("toolName")
            tools.append(name if isinstance(name, str) else "<unknown>")
            arguments = data.get("arguments")
            call_id = data.get("toolCallId")
            if (
                name == "skill" and isinstance(arguments, dict)
                and arguments.get("skill") == "case-session-to-wiki"
                and isinstance(call_id, str)
            ):
                invocations.add(call_id)
        elif kind == "tool.execution_complete":
            if data.get("success") is False:
                failed_tools += 1
            if data.get("success") is True:
                call_id = data.get("toolCallId")
                if isinstance(call_id, str):
                    completed.add(call_id)
        elif kind == "assistant.message":
            text = data.get("content")
            if isinstance(text, str) and text.strip():
                messages.append(text)
    unexpected = sorted(set(tools) - {"skill", "view"})
    transport_passed = (
        return_code == 0 and bool(invocations & completed)
        and bool(messages) and not unexpected and malformed == 0 and failed_tools == 0
        and reported_exit_code in (None, 0)
    )
    return {
        "schema_version": 1,
        "fixture": fixture,
        "cli_return_code": return_code,
        "reported_exit_code": reported_exit_code,
        "native_skill_invoked": bool(invocations & completed),
        "tools_used": tools,
        "unexpected_tools": unexpected,
        "malformed_output_lines": malformed,
        "failed_tool_calls": failed_tools,
        "transport_status": "passed" if transport_passed else "failed",
        "semantic_result": "not-reviewed",
        "assistant_messages": messages,
        "limitations": [
            "Synthetic prompt only; no real session or case data.",
            "Read-only tool restrictions; not a full write-path integration test.",
            "A successful invocation is not a semantic pass or release approval.",
        ],
    }


def run_fixture(name):
    bundle = ROOT / ".github" / "skills" / "case-session-to-wiki"
    before = bundle_digest(bundle)
    prompt = (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
    args = cli_command() + [
        "-C", str(ROOT),
        "--available-tools", "skill", "view",
        "--allow-tool", "skill", "view",
        "--disable-builtin-mcps", "--no-remote", "--no-remote-export",
        "--no-auto-update", "--log-level", "none",
        "--output-format", "json", "--stream", "off", "-p", prompt,
    ]
    config = Path.home() / ".copilot" / "mcp-config.json"
    if config.exists():
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        servers = data.get("mcpServers", {})
        if not isinstance(servers, dict):
            raise RuntimeError("MCP configuration has an unsupported shape.")
        for server_name in servers:
            args.extend(["--disable-mcp-server", server_name])
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8",
        errors="strict", timeout=300, check=False,
    )
    report = summarize_events(result.stdout, name, result.returncode)
    after = bundle_digest(bundle)
    report["skill_bundle_sha256"] = before
    report["bundle_unchanged_during_run"] = before == after
    report["model_configuration"] = "Inherited CLI default; no override."
    if before != after:
        report["transport_status"] = "failed"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", choices=NAMES, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("The output already exists; select a new output path.")
    if not args.output.parent.is_dir():
        parser.error("The output directory does not exist.")
    try:
        result = run_fixture(args.fixture)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        print(json.dumps({
            "transport_status": "failed",
            "error": "Cannot complete the synthetic test; check CLI access, input/configuration, and output path.",
        }))
        return 1
    print(json.dumps({
        "transport_status": result["transport_status"],
        "native_skill_invoked": result["native_skill_invoked"],
        "semantic_result": result["semantic_result"],
    }))
    return 0 if result["transport_status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
