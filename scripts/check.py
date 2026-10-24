#!/usr/bin/env python3
"""Portable skillset checker. No commands in skillset.json are executed.

Schema v1: language, entry_policy; optional adapters[{skill, consumers}],
portability{paths: globs, forbidden: literals, exceptions: {path: [literals]},
transitions: {path: {reason, close_when}}}, migration{rewritten: [path],
pending: [{id,path}]}, copies[{source,target}], and
command_snapshots[{reference,snapshot,commands: [literal]}]. Paths are root-relative.
YAML subset: JSON-quoted strings, booleans, simple bare strings, and one mapping
level (metadata in frontmatter; interface/policy in openai.yaml). No full YAML.
"""
import argparse
import json
import re
import shlex
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

NAME = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
INDEX = re.compile(r"^- \*\*(.+?)\*\* \(`(principle-[a-z0-9-]+)`\)\.\s*(.+)$", re.M)
HANGUL = re.compile(r"[가-힣]")
COMMAND = "python3 scripts/check.py ."


def unfenced(text):
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not line[match.end():].strip():
                fence = None
        elif fence is None:
            lines.append(line)
    return "\n".join(lines)


def scalar(value):
    if value.startswith('"'):
        result = json.loads(value)
        if not isinstance(result, str):
            raise ValueError("quoted value must be a string")
        return result
    if value in ("true", "false"):
        return value == "true"
    if re.fullmatch(r"[A-Za-z0-9_./$-]+", value) and value not in ("null", "Null", "NULL", "yes", "no", "on", "off"):
        return value
    raise ValueError("unsupported YAML scalar; use a JSON double-quoted string")


def yaml_subset(text, sections):
    result, section = {}, None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"( {0}| {2})([A-Za-z_][A-Za-z0-9_-]*):(?: (.+))?", line)
        if not match:
            raise ValueError(f"line {number}: unsupported YAML syntax")
        indent, key, value = match.groups()
        if indent:
            if section is None or value is None:
                raise ValueError(f"line {number}: invalid nested mapping")
            dest = result[section]
        else:
            section = None
            dest = result
        if key in dest:
            raise ValueError(f"line {number}: duplicate key {key}")
        if value is None:
            if indent or key not in sections:
                raise ValueError(f"line {number}: unsupported mapping {key}")
            result[key], section = {}, key
        else:
            dest[key] = scalar(value)
    return result


def frontmatter(text):
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("missing or malformed frontmatter")
    fields = yaml_subset(match.group(1), {"metadata"})
    if not re.search(r'^description: "', match.group(1), re.M):
        raise ValueError("description must use a JSON double-quoted string")
    return fields, text[match.end():]


def runtime_documents(skills):
    docs = []
    for folder in sorted(skills.iterdir()) if skills.is_dir() else []:
        if not folder.is_dir() or not (folder / "SKILL.md").is_file():
            continue
        docs.append((folder / "SKILL.md", folder))
        for subdir in ("playbooks", "references"):
            docs.extend((p, folder) for p in sorted((folder / subdir).rglob("*.md")) if p.is_file())
    return docs


def references(text, doc, owner=None):
    """Yield (literal, base). Inline paths and plain Read paths use the skill root."""
    clean = unfenced(text)
    for match in re.finditer(r"\]\((<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\)", clean):
        yield match.group(1).strip("<>"), doc.parent
    for match in re.finditer(r'^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)', clean, re.M):
        yield match.group(1).strip("<>"), doc.parent
    if owner:
        for token in re.findall(r"\bRead[ \t]+((?:\.\.?/|/|~/|[A-Za-z]:\\)[^\s`<>]+)", clean):
            yield token.rstrip(".,;:)]}"), owner
        for token in re.findall(r"`([^`\n]+)`", clean):
            if re.fullmatch(r"(?:\.\.?/|playbooks/|references/|scripts/|assets/)[^\s`]+", token):
                yield token, owner
            elif re.match(r"(?:/|~/|[A-Za-z]:\\)", token) and not re.search(r"\s", token):
                yield token, owner
    else:
        for token in re.findall(r"`((?:\./)?skills/[^`\s]+/SKILL\.md)`", clean):
            yield token, None


def ci_commands(text):
    """Read single-line run values and literal run blocks, without executing shell."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^( *)(?:- +)?run: *(.*?) *$", line)
        if not match:
            continue
        value = match.group(2)
        if value in ("|", "|-", "|+"):
            indentation = None
            for continuation in lines[index + 1:]:
                if not continuation.strip():
                    continue
                spaces = len(continuation) - len(continuation.lstrip(" "))
                if indentation is None:
                    indentation = spaces
                if spaces <= len(match.group(1)) or spaces < indentation:
                    break
                yield continuation.strip()
        elif value.startswith('"'):
            try:
                command = json.loads(value)
                if isinstance(command, str):
                    yield command
            except ValueError:
                continue
        elif value.startswith("'") and value.endswith("'"):
            yield value[1:-1].replace("''", "'")
        else:
            yield value


def invokes_checker(command):
    try:
        tokens = shlex.split(command, comments=True)
    except ValueError:
        return False
    return tokens in (["python3", "scripts/check.py", "."], ["python3", "scripts/check.py", ".", "--check"])


class Checker:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.skills = self.root / "skills"
        self.errors = []
        self.warnings = []
        self.counts = {}

    def issue(self, code, path, message, warning=False):
        try:
            shown = Path(path).relative_to(self.root)
        except ValueError:
            shown = path
        (self.warnings if warning else self.errors).append(f"{code}: {shown}: {message}")

    def read(self, path):
        try:
            if not path.resolve().is_relative_to(self.root):
                raise ValueError("path escapes repository")
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            self.issue("READ", path, str(exc))
            return ""

    def path(self, token, base=None, boundary=None):
        base, boundary = base or self.root, boundary or self.root
        if not isinstance(token, str) or not token or token.startswith(("/", "~")) or "\\" in token:
            raise ValueError(f"invalid relative path {token!r}")
        candidate = base / token
        if not candidate.resolve().is_relative_to(boundary.resolve()):
            raise ValueError(f"path escapes allowed root: {token}")
        return candidate

    def manifest(self):
        path = self.root / "skillset.json"
        try:
            value = json.loads(self.read(path))
            if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
                raise ValueError("schema_version must be 1")
            if not isinstance(value.get("language"), str) or not value["language"]:
                raise ValueError("language must be a nonempty string")
            policy = value.get("entry_policy")
            if not isinstance(policy, dict) or not all(NAME.fullmatch(k) and type(v) is bool for k, v in policy.items()):
                raise ValueError("entry_policy must map mode names to booleans")
            return value
        except (ValueError, TypeError) as exc:
            self.issue("CONFIG", path, str(exc))
            return None

    def check_reference(self, token, base, doc, runtime=False):
        try:
            parsed = urlsplit(token)
        except ValueError as exc:
            self.issue("REF_SYNTAX", doc, str(exc))
            return None
        if parsed.scheme in ("https", "http", "mailto", "data") or token.startswith("#"):
            return None
        if parsed.scheme or token.startswith("//"):
            self.issue("REF_ESCAPE", doc, f"unsupported or absolute local reference: {token}")
            return None
        try:
            path = self.path(unquote(parsed.path), base, self.skills if runtime else self.root)
            if runtime and path.exists():
                parts = path.resolve().relative_to(self.skills.resolve()).parts
                if not parts or not (self.skills / parts[0] / "SKILL.md").is_file():
                    self.issue("REF_UNPACKAGED", doc, f"reference is outside a distributable skill folder: {token}")
                    return None
            if not path.exists():
                self.issue("REF_MISSING", doc, f"reference does not exist: {token}")
            elif path.is_file():
                path.open("rb").close()
            return path
        except (OSError, ValueError, RuntimeError) as exc:
            self.issue("REF_ESCAPE", doc, str(exc))
            return None

    def check_skill(self, name, modes, config):
        folder = self.skills / name
        path = folder / "SKILL.md"
        text = self.read(path)
        try:
            fields, body = frontmatter(text)
        except ValueError as exc:
            self.issue("FRONTMATTER", path, str(exc))
            fields, body = {}, text
        if fields.get("name") != name or not NAME.fullmatch(name):
            self.issue("NAME", path, "frontmatter name must equal kebab-case folder name")
        desc = fields.get("description")
        if not isinstance(desc, str) or not 1 <= len(desc) <= 1024 or any(c in desc for c in "<>"):
            self.issue("DESCRIPTION", path, "description must be 1..1024 characters without angle brackets")
        elif config["language"] == "ko" and not HANGUL.search(desc):
            self.issue("LANGUAGE", path, "Korean description must contain Hangul")
        expected = config["entry_policy"].get(name, False) if name in modes else False
        if type(fields.get("disable-model-invocation")) is not bool or fields.get("disable-model-invocation") != (not expected):
            self.issue("POLICY", path, f"disable-model-invocation must be {str(not expected).lower()}")
        metadata = fields.get("metadata", {})
        if isinstance(metadata, dict) and metadata.get("internal") is True:
            self.issue("INTERNAL", path, "internal verification skills belong outside distributed skills/")
        if name.startswith("principle-"):
            for marker in ("**Why:**", "**Pattern:**", "**Stop:**"):
                if marker not in body:
                    self.issue("PRINCIPLE_BODY", path, f"missing {marker}")
        yaml_path = folder / "agents/openai.yaml"
        try:
            agent = yaml_subset(self.read(yaml_path), {"interface", "policy"})
            interface, policy = agent.get("interface", {}), agent.get("policy", {})
            if not isinstance(interface, dict) or not isinstance(policy, dict):
                raise ValueError("interface and policy must be mappings")
            if interface.get("display_name") != name:
                self.issue("AGENT_NAME", yaml_path, "display_name must equal folder name")
            short = interface.get("short_description")
            if not isinstance(short, str) or not 25 <= len(short) <= 64:
                self.issue("AGENT_SHORT", yaml_path, "short_description must be 25..64 characters")
            prompt = interface.get("default_prompt")
            if not isinstance(prompt, str) or not re.search(r"\$" + re.escape(name) + r"(?![a-z0-9-])", prompt):
                self.issue("AGENT_PROMPT", yaml_path, f"default_prompt must mention ${name}")
            elif config["language"] == "ko" and not HANGUL.search(prompt):
                self.issue("LANGUAGE", yaml_path, "Korean default_prompt must contain Hangul")
            if type(policy.get("allow_implicit_invocation")) is not bool or policy.get("allow_implicit_invocation") != expected:
                self.issue("POLICY", yaml_path, f"allow_implicit_invocation must be {str(expected).lower()}")
        except ValueError as exc:
            self.issue("AGENT_YAML", yaml_path, str(exc))
        return text

    def check_runtime(self, names, modes, texts):
        referenced, used_principles, index = set(), set(), {}
        for doc, owner in runtime_documents(self.skills):
            if not doc.resolve().is_relative_to(self.skills.resolve()):
                self.issue("REF_ESCAPE", doc, "runtime document escapes skills/")
                continue
            text = self.read(doc)
            clean = unfenced(text)
            for token, base in references(text, doc, owner):
                target = self.check_reference(token, base, doc, True)
                if target:
                    try:
                        target_name = target.resolve().relative_to(self.skills.resolve()).parts[0]
                        if target_name != owner.name:
                            referenced.add(target_name)
                    except (ValueError, IndexError):
                        pass
            for name in re.findall(r"(?:`|\*\*)([a-z][a-z0-9-]+)(?:`|\*\*)", clean):
                if name in names and name != owner.name:
                    referenced.add(name)
                elif name.startswith("principle-") and name not in names:
                    self.issue("UNKNOWN_PRINCIPLE", doc, name)
            without_index = INDEX.sub("", clean)
            for name in names:
                if name.startswith("principle-") and owner.name != name and re.search(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])", without_index):
                    used_principles.add(name)
            if doc.parent.name == "playbooks":
                if not text.startswith("### ") or not re.search(r"^1\.\s+\S", clean, re.M):
                    self.issue("PLAYBOOK_FORMAT", doc, "playbook must begin with ### and contain numbered steps")
        total_playbooks = 0
        principles = {n for n in names if n.startswith("principle-")}
        for mode in modes:
            path = self.skills / mode / "SKILL.md"
            actual = {p.name for p in (self.skills / mode / "playbooks").glob("*.md")}
            declared = set(re.findall(r"`playbooks/([^`/]+\.md)`", unfenced(texts[mode])))
            total_playbooks += len(actual)
            if not actual or actual != declared:
                self.issue("PLAYBOOK_INDEX", path, f"files/index differ: unlisted={sorted(actual-declared)}, missing={sorted(declared-actual)}")
            seen = set()
            for title, name, sentence in INDEX.findall(unfenced(texts[mode])):
                if name in seen:
                    self.issue("PRINCIPLE_INDEX", path, f"duplicate principle {name}")
                seen.add(name)
                line = f"{title}|{sentence.strip()}"
                if name in index and index[name] != line:
                    self.issue("PRINCIPLE_INDEX", path, f"index sentence differs for {name}")
                index[name] = line
            if principles and not seen.intersection(principles):
                self.issue("PRINCIPLE_INDEX", path, "mode needs at least one valid principle index entry")
        if set(index) != principles:
            self.issue("PRINCIPLE_INDEX", self.skills, f"index/leaf differ: unlisted={sorted(principles-set(index))}, missing={sorted(set(index)-principles)}")
        for name in sorted(set(names) - set(modes)):
            if name not in referenced:
                self.issue("ORPHAN", self.skills / name / "SKILL.md", "no other runtime document references this skill")
        for name in sorted(principles - used_principles):
            self.issue("PRINCIPLE_UNUSED", self.skills / name / "SKILL.md", "no use outside mode principle index", warning=True)
        self.counts = {"skills": len(names), "modes": len(modes), "playbooks": total_playbooks, "leaves": len(names)-len(modes)-len(principles), "principles": len(principles)}

    def config_path(self, value, must_exist=True):
        path = self.path(value)
        if must_exist and not path.exists():
            raise ValueError(f"registered path missing: {value}")
        return path

    def conditional(self, config, names):
        def strings(value):
            if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
                raise ValueError("expected a list of nonempty strings")
            return value

        def records(key):
            value = config.get(key, [])
            if not isinstance(value, list) or not all(isinstance(x, dict) for x in value):
                raise ValueError(f"{key} must be a list of objects")
            return value

        try:
            for adapter in records("adapters"):
                name = adapter["skill"]
                if name not in names:
                    raise ValueError(f"unknown adapter {name!r}")
                for consumer in strings(adapter["consumers"]):
                    if consumer not in names:
                        raise ValueError(f"unknown adapter consumer {consumer}")
                    path = self.skills / consumer / "SKILL.md"
                    _, body = frontmatter(self.read(path))
                    lines = body.strip().splitlines()
                    after = next((line.strip() for line in lines[1:] if line.strip()), "") if lines and lines[0].startswith("# ") else ""
                    if f"Read ../{name}/SKILL.md" not in after:
                        self.issue("ADAPTER_POINTER", path, f"first text after title must contain Read ../{name}/SKILL.md")
        except (KeyError, TypeError, ValueError) as exc:
            self.issue("ADAPTER_CONFIG", self.root / "skillset.json", str(exc))
        try:
            lint = config.get("portability", {})
            if not isinstance(lint, dict):
                raise ValueError("portability must be an object")
            forbidden = strings(lint.get("forbidden", []))
            exceptions, transitions = lint.get("exceptions", {}), lint.get("transitions", {})
            if not isinstance(exceptions, dict) or not isinstance(transitions, dict):
                raise ValueError("exceptions and transitions must be path maps")
            for path, terms in exceptions.items():
                self.config_path(path)
                if set(strings(terms)) - set(forbidden):
                    raise ValueError(f"exception uses unregistered terms: {path}")
            for path, transition in transitions.items():
                self.config_path(path)
                if not isinstance(transition, dict) or not all(isinstance(transition.get(k), str) and transition[k].strip() for k in ("reason", "close_when")):
                    raise ValueError(f"transition needs reason and close_when: {path}")
            files = set()
            for pattern in strings(lint.get("paths", [])):
                self.path(pattern)
                if ".." in Path(pattern).parts:
                    raise ValueError(f"glob may not contain ..: {pattern}")
                files.update(p for p in self.root.glob(pattern) if p.is_file())
            for path in sorted(files):
                relative = path.relative_to(self.root).as_posix()
                content = self.read(path)
                for term in forbidden:
                    if term in content and term not in exceptions.get(relative, []) and relative not in transitions:
                        self.issue("PORTABILITY", path, f"forbidden literal: {term}")
        except (TypeError, ValueError, OSError) as exc:
            self.issue("PORTABILITY_CONFIG", self.root / "skillset.json", str(exc))
        try:
            migration = config.get("migration", {})
            if not isinstance(migration, dict):
                raise ValueError("migration must be an object")
            rewritten = [self.config_path(p) for p in strings(migration.get("rewritten", []))]
            pending = migration.get("pending", [])
            if not isinstance(pending, list):
                raise ValueError("pending must be a list")
            ids = set()
            for item in pending:
                if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip() or item["id"] in ids:
                    raise ValueError("pending entries need unique nonempty ids")
                ids.add(item["id"])
                path = self.config_path(item["path"], must_exist=False)
                if any(path == done or path.is_relative_to(done) for done in rewritten):
                    self.issue("MIGRATION_STALE", self.root / "skillset.json", f"pending {item['id']} is covered by rewritten path {item['path']}")
        except (KeyError, TypeError, ValueError) as exc:
            self.issue("MIGRATION_CONFIG", self.root / "skillset.json", str(exc))
        for key in ("copies", "command_snapshots"):
            try:
                for item in records(key):
                    if key == "copies":
                        source, target = self.config_path(item["source"]), self.config_path(item["target"])
                        if source.read_bytes() != target.read_bytes():
                            self.issue("COPY_DRIFT", target, f"differs from {item['source']}")
                    else:
                        ref, snapshot = self.config_path(item["reference"]), self.config_path(item["snapshot"])
                        text, saved = self.read(ref), self.read(snapshot)
                        for command in strings(item["commands"]):
                            if command not in text or command not in saved:
                                self.issue("COMMAND_SNAPSHOT", ref, f"literal missing in reference or snapshot: {command}")
            except (KeyError, TypeError, ValueError, OSError) as exc:
                self.issue("COPY_CONFIG" if key == "copies" else "SNAPSHOT_CONFIG", self.root / "skillset.json", str(exc))

    def document_blocks(self, config, write):
        c = self.counts
        summary = f"mode {c['modes']}개, playbook {c['playbooks']}개, skill {c['leaves']}개, principle {c['principles']}개 (설치 단위 {c['skills']}개).\n\n검사: `{COMMAND}`"
        rows = ["| mode | 자연어 자동 호출 |", "| --- | --- |"]
        rows.extend(f"| `{mode}` | `{str(implicit).lower()}` |" for mode, implicit in sorted(config["entry_policy"].items()))
        rows.append("\nleaf skill과 principle의 자동 호출은 `false`다.")
        edits = []
        for name, block, value in (("README.md", "summary", summary), ("DESIGN.md", "policy", "\n".join(rows))):
            path = self.root / name
            text = self.read(path)
            start, end = f"<!-- skillset:{block}:start -->", f"<!-- skillset:{block}:end -->"
            starts = list(re.finditer(r"^" + re.escape(start) + r"$", text, re.M))
            ends = list(re.finditer(r"^" + re.escape(end) + r"$", text, re.M))
            if len(starts) != 1 or len(ends) != 1 or starts[0].start() > ends[0].start():
                self.issue("DOC_MARKERS", path, f"need exactly one ordered {block} marker pair")
                continue
            expected = text[:starts[0].end()] + "\n" + value + "\n" + text[ends[0].start():]
            if text != expected:
                if write and not path.is_symlink():
                    edits.append((path, expected))
                else:
                    self.issue("DOC_DRIFT", path, "generated block differs; run --write-docs")
        if write and not any(e.startswith("DOC_MARKERS:") for e in self.errors):
            for path, value in edits:
                path.write_text(value, encoding="utf-8")

    def docs(self):
        design = self.root / "DESIGN.md"
        text = self.read(design)
        section = re.search(r"^## 확인하지 못한 것\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if not section:
            self.issue("UNKNOWN_QUEUE", design, "missing 확인하지 못한 것 section")
        else:
            rows = [line for line in section.group(1).splitlines() if line.strip().startswith("|")]
            if not rows and not re.search(r"없음|None", section.group(1)):
                self.issue("UNKNOWN_QUEUE", design, "declare none or provide a table with closing conditions")
            elif rows:
                cells = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in rows]
                if "닫을 조건" not in cells[0]:
                    self.issue("UNKNOWN_QUEUE", design, "table needs 닫을 조건 column")
                else:
                    column = cells[0].index("닫을 조건")
                    data = [row for row in cells[1:] if not all(re.fullmatch(r":?-+:?", cell.replace(" ", "")) for cell in row)]
                    if not data:
                        self.issue("UNKNOWN_QUEUE", design, "table needs an explicit none row or an item")
                    for row in data:
                        if len(row) <= column or not row[column] or row[column] in ("-", "TBD", "TODO"):
                            self.issue("UNKNOWN_QUEUE", design, f"closing condition is empty: {row[0]}")
        docs = [self.root / "README.md", design] + sorted((self.root / "docs" / "guide").rglob("*.md"))
        for doc in docs:
            content = self.read(doc)
            for token, base in references(content, doc):
                self.check_reference(token, base, doc)
        owned = docs + [doc for doc, _ in runtime_documents(self.skills)]
        for doc in owned:
            if re.search("[—–]", self.read(doc)):
                self.issue("LONG_DASH", doc, "replace long dash with ordinary punctuation")
        workflow = self.root / ".github/workflows/check.yml"
        content = self.read(workflow)
        events = set()
        inline = re.search(r"^on: *\[([^]\n]+)\] *$", content, re.M)
        block = re.search(r"^on: *\n((?:[ \t].*(?:\n|$)|\n)+)", content, re.M)
        if inline:
            events = {event.strip() for event in inline.group(1).split(",")}
        elif block:
            events = set(re.findall(r"^  ([a-z_]+):", block.group(1), re.M))
        if not {"push", "pull_request"} <= events or not any(invokes_checker(command) for command in ci_commands(content)):
            self.issue("CI", workflow, f"workflow must run {COMMAND} on push and pull_request")

    def run(self, write_docs=False):
        config = self.manifest()
        if config is None:
            return self
        names = sorted(folder.name for folder in self.skills.iterdir() if folder.is_dir() and (folder / "SKILL.md").is_file()) if self.skills.is_dir() else []
        modes = [name for name in names if (self.skills / name / "playbooks").is_dir()]
        if not names or not modes:
            self.issue("STRUCTURE", self.skills, "need at least one skill and one mode")
        if set(config["entry_policy"]) != set(modes):
            self.issue("POLICY_MODES", self.root / "skillset.json", "entry_policy keys must equal mode folders")
        texts = {name: self.check_skill(name, modes, config) for name in names}
        self.check_runtime(names, modes, texts)
        self.conditional(config, names)
        self.document_blocks(config, write_docs)
        self.docs()
        return self


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--write-docs", action="store_true")
    parser.add_argument("--check", action="store_true", help="explicit spelling of default read-only checks")
    args = parser.parse_args()
    if args.write_docs and args.check:
        parser.error("--check and --write-docs cannot be combined")
    result = Checker(args.root).run(args.write_docs)
    for warning in result.warnings:
        print("warning: " + warning)
    for error in result.errors:
        print("error: " + error)
    if result.errors:
        print(f"failed: {len(result.errors)} errors, {len(result.warnings)} warnings")
        return 1
    print("ok: " + ", ".join(f"{value} {key}" for key, value in result.counts.items()) + f", {len(result.warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
