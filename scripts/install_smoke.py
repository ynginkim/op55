#!/usr/bin/env python3
"""Install into a new disposable project; inspect bytes, links and runtime paths.

This command needs network access to npx. It never installs globally, deletes a
folder, or runs commands from the source manifest. Keep the destination as evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("skillset_checker", Path(__file__).with_name("check.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def prepare_destination(source, destination):
    source = source.resolve(strict=True)
    if not (source / "skills").is_dir():
        raise ValueError("SOURCE must contain skills/")
    if destination.is_symlink():
        raise ValueError("destination may not be a symlink")
    destination = destination.resolve()
    if destination == source or destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("source and destination must not overlap")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("destination must be a new or empty directory")
    destination.mkdir(parents=True, exist_ok=True)
    return source, destination


def inventory(folder):
    files = {}
    for path in sorted(folder.rglob("*")):
        if "__pycache__" in path.parts or path.name == ".DS_Store":
            continue
        if not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError(f"resource escapes package: {path.relative_to(folder)}")
        if path.is_file():
            files[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def inspect_install(source, destination):
    source_skills = source / "skills"
    installed = destination / ".agents/skills"
    claude = destination / ".claude/skills"
    if any(path.is_symlink() for path in (destination / ".agents", installed)) or not installed.is_dir():
        raise ValueError("installed .agents/skills must be a real copied directory")
    if not installed.resolve().is_relative_to(destination.resolve()) or installed.resolve().is_relative_to(source.resolve()):
        raise ValueError("installed resources must be separate from source and inside destination")
    expected = sorted(p.name for p in source_skills.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    actual = sorted(p.name for p in installed.iterdir() if (p / "SKILL.md").is_file()) if installed.is_dir() else []
    if expected != actual:
        raise ValueError(f"installed skill names differ: expected={expected}, actual={actual}")
    checked_references, checked_playbooks = 0, 0
    resource_hashes = {}
    for name in expected:
        if (installed / name).is_symlink():
            raise ValueError(f"installed skill must be a real copied directory: {name}")
        original = inventory(source_skills / name)
        copied = inventory(installed / name)
        if original != copied:
            differences = sorted(key for key in set(original) | set(copied) if original.get(key) != copied.get(key))
            raise ValueError(f"installed resources differ for {name}: {differences}")
        resource_hashes[name] = copied
        link = claude / name
        if not link.is_symlink() or link.resolve() != (installed / name).resolve():
            raise ValueError(f"Claude skill must link to the installed agent skill: {name}")
    for skill_root in (installed, claude):
        for doc, owner in checker.runtime_documents(skill_root):
            doc.read_bytes()
            if doc.parent.name == "playbooks":
                checked_playbooks += 1
            for token, base in checker.references(doc.read_text(encoding="utf-8"), doc, owner):
                parsed = urlsplit(token)
                if parsed.scheme in ("http", "https", "mailto", "data") or token.startswith("#"):
                    continue
                if parsed.scheme or token.startswith(("/", "~")):
                    raise ValueError(f"nonportable installed reference: {token}")
                target = (base / unquote(parsed.path)).resolve()
                if not target.is_relative_to(installed.resolve()):
                    raise ValueError(f"installed reference escapes .agents/skills: {token}")
                parts = target.relative_to(installed.resolve()).parts
                if target.exists() and (not parts or parts[0] not in expected):
                    raise ValueError(f"unpackaged installed reference: {token}")
                if target.is_dir():
                    list(target.iterdir())
                else:
                    target.read_bytes()
                checked_references += 1
    return {"skill_count": len(expected), "skill_names": expected, "opened_references": checked_references,
            "opened_playbooks": checked_playbooks, "installed_resource_sha256": resource_hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--dest", type=Path, required=True)
    args = parser.parse_args()
    try:
        source, destination = prepare_destination(args.source, args.dest)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    evidence = {"source": str(source), "destination": str(destination), "status": "failed"}
    try:
        validation = checker.Checker(source).run()
        if validation.errors:
            raise ValueError("source structural checks failed:\n" + "\n".join(validation.errors))
        before = inventory(source / "skills")
        subprocess.run(["git", "init", "--quiet", str(destination)], cwd=destination, check=True, capture_output=True, text=True)
        evidence["npx_version"] = subprocess.run(["npx", "--version"], cwd=destination, check=True, capture_output=True, text=True).stdout.strip()
        command = ["npx", "--yes", "skills", "add", str(source), "-a", "claude-code", "-a", "codex", "-y"]
        evidence["command"] = command
        result = subprocess.run(command, cwd=destination, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (destination / "installer.log").write_text(result.stdout, encoding="utf-8")
        evidence["installer_exit_code"] = result.returncode
        if result.returncode:
            raise ValueError(f"installer failed ({result.returncode}); see {destination / 'installer.log'}")
        evidence.update(inspect_install(source, destination))
        evidence["source_resources_unchanged"] = before == inventory(source / "skills")
        if not evidence["source_resources_unchanged"]:
            raise ValueError("source skill resources changed during installation")
        evidence["status"] = "passed"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        evidence["error"] = str(exc)
    target = destination / "install-smoke.json"
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if evidence["status"] != "passed":
        print(f"error: {evidence['error']}\nevidence: {target}", file=sys.stderr)
        return 1
    print(f"ok: installed {evidence['skill_count']} skills; opened {evidence['opened_playbooks']} playbooks and {evidence['opened_references']} references through both harness paths\nevidence: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
