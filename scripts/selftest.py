#!/usr/bin/env python3
"""Exercise the portable checker using disposable projects and deliberate defects."""
import importlib.util
import json
import shutil
import tempfile
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("skillset_checker", Path(__file__).with_name("check.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def put(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def skill(root, name, body, implicit=False):
    put(root, f"skills/{name}/SKILL.md", f'---\nname: {name}\ndescription: "요청한 작업을 수행할 때 사용한다."\ndisable-model-invocation: {str(not implicit).lower()}\n---\n\n# {name}\n\n{body}\n')
    put(root, f"skills/{name}/agents/openai.yaml", 'interface:\n' +
        f'  display_name: "{name}"\n' +
        '  short_description: "요청한 작업을 끝까지 수행하고 결과를 확인하는 도구입니다"\n' +
        f'  default_prompt: "${name}를 사용해 요청한 작업을 수행해 주세요."\n' +
        f'policy:\n  allow_implicit_invocation: {str(implicit).lower()}\n')


def fixture(root):
    config = {"schema_version": 1, "language": "ko", "entry_policy": {"demo-mode": True}}
    put(root, "skillset.json", json.dumps(config))
    skill(root, "demo-mode", '`playbooks/create.md`\n\n`../tool/SKILL.md`\n\n- **먼저 확인** (`principle-check`). 중요한 판단 전에 적용한다.', True)
    skill(root, "tool", '`principle-check`를 적용한다.\n\n[기준](references/detail.md)')
    skill(root, "principle-check", '**Why:** 판단 근거가 필요하다.\n\n**Pattern:** 실제 근거를 확인한다.\n\n**Stop:** 근거가 없으면 미확인으로 둔다.')
    put(root, "skills/tool/references/detail.md", '# 기준\n\n[도구](../SKILL.md)\n\n```md\n[무시할 템플릿](../../missing.md)\n```\n')
    put(root, "skills/demo-mode/playbooks/create.md", '### 새로 만들기\n\n1. `../tool/SKILL.md`를 읽고 작업한다.\n2. `principle-check`를 적용한다.\n')
    put(root, "README.md", '# 예시\n\n<!-- skillset:summary:start -->\n<!-- skillset:summary:end -->\n')
    put(root, "DESIGN.md", '# 설계\n\n<!-- skillset:policy:start -->\n<!-- skillset:policy:end -->\n\n## 확인하지 못한 것\n\n| 항목 | 상태 | 닫을 조건 |\n| --- | --- | --- |\n| 앱 실행 | unverified | 실제 앱에서 새 세션 실행 |\n')
    put(root, ".github/workflows/check.yml", 'name: check\non: [push, pull_request]\njobs:\n  check:\n    runs-on: ubuntu-latest\n    steps:\n      - run: python3 scripts/check.py .\n')
    return config


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skillset-selftest-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = fixture(self.root)
        self.assertEqual([], checker.Checker(self.root).run(True).errors)

    def save_config(self):
        put(self.root, "skillset.json", json.dumps(self.config))

    def replace(self, path, before, after):
        target = self.root / path
        text = target.read_text()
        self.assertIn(before, text)
        target.write_text(text.replace(before, after))

    def errors(self):
        return checker.Checker(self.root).run().errors

    def assert_error(self, code):
        errors = self.errors()
        self.assertTrue(any(item.startswith(code + ":") for item in errors), errors)

    def test_normal_and_fenced_template(self):
        self.assertEqual([], self.errors())
        result = checker.Checker(self.root).run()
        self.assertEqual({"skills": 3, "modes": 1, "playbooks": 1, "leaves": 1, "principles": 1}, result.counts)
        self.assertEqual([], result.warnings)

    def test_missing_sibling_reference(self):
        self.replace("skills/demo-mode/playbooks/create.md", "../tool/", "../absent/")
        self.assert_error("REF_MISSING")

    def test_playbook_reference_uses_skill_root(self):
        put(self.root, "skills/demo-mode/playbooks/create.md", '### 작업\n\n1. `../tool/SKILL.md`를 읽는다.\n')
        self.assertEqual([], self.errors())

    def test_plain_read_uses_skill_root_and_ignores_fences(self):
        put(self.root, "skills/demo-mode/playbooks/create.md", "### 작업\n\n1. Read ../tool/SKILL.md.\n\n```md\nRead ../../outside.md\n```\n")
        self.assertEqual([], self.errors())

    def test_missing_plain_read(self):
        put(self.root, "skills/demo-mode/playbooks/create.md", "### 작업\n\n1. Read ../absent/SKILL.md\n")
        self.assert_error("REF_MISSING")

    def test_plain_read_escape(self):
        for target in ("../../README.md", "/etc/passwd"):
            with self.subTest(target=target):
                put(self.root, "skills/demo-mode/playbooks/create.md", f"### 작업\n\n1. Read {target}\n")
                self.assert_error("REF_ESCAPE")

    def test_markdown_reference_uses_document_directory(self):
        self.replace("skills/tool/references/detail.md", "../SKILL.md", "../../SKILL.md")
        self.assert_error("REF_MISSING")

    def test_outside_link(self):
        self.replace("skills/tool/SKILL.md", "references/detail.md", "../../README.md")
        self.assert_error("REF_ESCAPE")

    def test_absolute_link(self):
        self.replace("skills/tool/SKILL.md", "references/detail.md", "/etc/passwd")
        self.assert_error("REF_ESCAPE")

    def test_outside_symlink(self):
        path = self.root / "skills/tool/references/detail.md"
        path.unlink()
        path.symlink_to(self.root / "README.md")
        self.assert_error("REF_ESCAPE")

    def test_existing_shared_folder_is_not_a_distribution_unit(self):
        put(self.root, "skills/shared/config.json", "{}")
        with (self.root / "skills/tool/SKILL.md").open("a") as handle:
            handle.write("\n`../shared/config.json`\n")
        self.assert_error("REF_UNPACKAGED")

    def test_wrong_metadata_and_leaf_policy(self):
        self.replace("skills/tool/agents/openai.yaml", 'display_name: "tool"', 'display_name: "wrong"')
        self.replace("skills/tool/agents/openai.yaml", "allow_implicit_invocation: false", "allow_implicit_invocation: true")
        self.assert_error("AGENT_NAME")
        self.assert_error("POLICY")

    def test_implicit_mode_policy(self):
        self.replace("skills/demo-mode/SKILL.md", "disable-model-invocation: false", "disable-model-invocation: true")
        self.assert_error("POLICY")

    def test_unsupported_yaml_is_rejected(self):
        self.replace("skills/tool/SKILL.md", 'description: "요청한 작업을 수행할 때 사용한다."', 'description: >\n  여러 줄 문자열')
        self.assert_error("FRONTMATTER")

    def test_duplicate_yaml_key(self):
        self.replace("skills/tool/SKILL.md", "name: tool", "name: tool\nname: other")
        self.assert_error("FRONTMATTER")

    def test_json_quoted_special_characters(self):
        self.replace("skills/tool/SKILL.md", 'description: "요청한 작업을 수행할 때 사용한다."', 'description: ' + json.dumps('작업: "문자열" # 문자와 줄바꿈\\n도 확인한다.', ensure_ascii=False))
        self.assertEqual([], self.errors())

    def test_unsupported_agent_mapping(self):
        self.replace("skills/tool/agents/openai.yaml", '  display_name: "tool"', '  display_name:\n    nested: "tool"')
        self.assert_error("AGENT_YAML")

    def test_mode_policy_key_mismatch(self):
        self.config["entry_policy"] = {"unknown-mode": True}
        self.save_config()
        self.assert_error("POLICY_MODES")

    def test_unindexed_playbook(self):
        put(self.root, "skills/demo-mode/playbooks/extra.md", "### 추가\n\n1. 읽는다.\n")
        self.assert_error("PLAYBOOK_INDEX")

    def test_playbook_has_steps(self):
        put(self.root, "skills/demo-mode/playbooks/create.md", "### 작업\n\n단계가 없다.\n")
        self.assert_error("PLAYBOOK_FORMAT")

    def test_principle_index_and_warning(self):
        self.replace("skills/demo-mode/SKILL.md", '- **먼저 확인** (`principle-check`). 중요한 판단 전에 적용한다.', "")
        self.assert_error("PRINCIPLE_INDEX")

    def test_each_mode_needs_a_valid_principle_index(self):
        skill(self.root, "second-mode", "`playbooks/change.md`")
        put(self.root, "skills/second-mode/playbooks/change.md", "### 수정\n\n1. Read ../tool/SKILL.md\n")
        self.config["entry_policy"]["second-mode"] = False
        self.save_config()
        self.assert_error("PRINCIPLE_INDEX")
        principle_body = "**Why:** 다른 판단이다.\n\n**Pattern:** 따로 확인한다.\n\n**Stop:** 근거가 없으면 멈춘다."
        skill(self.root, "principle-other", principle_body)
        with (self.root / "skills/second-mode/SKILL.md").open("a") as handle:
            handle.write("\n- **별도 판단** (`principle-other`). 다른 작업에 적용한다.\n")
        result = checker.Checker(self.root).run(True)
        self.assertEqual([], result.errors)

    def test_shared_principle_index_sentences_must_match(self):
        skill(self.root, "second-mode", "`playbooks/change.md`\n\n- **먼저 확인** (`principle-check`). 원래 문장과 다른 설명이다.")
        put(self.root, "skills/second-mode/playbooks/change.md", "### 수정\n\n1. Read ../tool/SKILL.md\n")
        self.config["entry_policy"]["second-mode"] = False
        self.save_config()
        self.assert_error("PRINCIPLE_INDEX")

    def test_principle_unused_is_only_warning(self):
        self.replace("skills/tool/SKILL.md", '`principle-check`를 적용한다.', "직접 작업한다.")
        self.replace("skills/demo-mode/playbooks/create.md", '2. `principle-check`를 적용한다.', "2. 확인한다.")
        result = checker.Checker(self.root).run()
        self.assertEqual([], result.errors)
        self.assertTrue(any(w.startswith("PRINCIPLE_UNUSED:") for w in result.warnings))

    def test_readme_does_not_rescue_orphan(self):
        skill(self.root, "orphan", "독립된 도구다.")
        with (self.root / "README.md").open("a") as handle:
            handle.write('\n`skills/orphan/SKILL.md`\n')
        checker.Checker(self.root).run(True)
        self.assert_error("ORPHAN")

    def test_adapter_pointer_position(self):
        self.config["adapters"] = [{"skill": "tool", "consumers": ["demo-mode"]}]
        self.save_config()
        self.assert_error("ADAPTER_POINTER")
        self.replace("skills/demo-mode/SKILL.md", "# demo-mode\n", "# demo-mode\n\nRead ../tool/SKILL.md\n")
        self.assertEqual([], self.errors())

    def test_portability_exceptions_and_transition(self):
        path = "skills/tool/references/detail.md"
        self.config["portability"] = {"paths": ["skills/**/references/*.md"], "forbidden": ["기준"], "exceptions": {}, "transitions": {}}
        self.save_config()
        self.assert_error("PORTABILITY")
        self.config["portability"]["exceptions"] = {path: ["기준"]}
        self.save_config()
        self.assertEqual([], self.errors())
        self.config["portability"]["exceptions"] = {}
        self.config["portability"]["transitions"] = {path: {"reason": "이전 중", "close_when": "adapter로 이동"}}
        self.save_config()
        self.assertEqual([], self.errors())
        self.config["portability"]["transitions"][path]["close_when"] = ""
        self.save_config()
        self.assert_error("PORTABILITY_CONFIG")

    def test_stale_migration_is_not_pruned(self):
        self.config["migration"] = {"rewritten": ["skills/tool"], "pending": [{"id": "old-1", "path": "skills/tool/SKILL.md"}]}
        self.save_config()
        before = (self.root / "skillset.json").read_bytes()
        self.assert_error("MIGRATION_STALE")
        self.assertEqual(before, (self.root / "skillset.json").read_bytes())

    def test_copy_drift_and_escape(self):
        put(self.root, "source.txt", "same")
        put(self.root, "copy.txt", "same")
        self.config["copies"] = [{"source": "source.txt", "target": "copy.txt"}]
        self.save_config()
        self.assertEqual([], self.errors())
        put(self.root, "copy.txt", "different")
        self.assert_error("COPY_DRIFT")
        self.config["copies"][0]["source"] = "../outside.txt"
        self.save_config()
        self.assert_error("COPY_CONFIG")

    def test_commands_are_literal_not_executed(self):
        command = "touch SHOULD_NOT_EXIST"
        put(self.root, "command.md", command)
        put(self.root, "snapshot.txt", command)
        self.config["command_snapshots"] = [{"reference": "command.md", "snapshot": "snapshot.txt", "commands": [command]}]
        self.save_config()
        self.assertEqual([], self.errors())
        self.assertFalse((self.root / "SHOULD_NOT_EXIST").exists())
        put(self.root, "snapshot.txt", "wrong command")
        self.assert_error("COMMAND_SNAPSHOT")

    def test_unknown_requires_closing_condition(self):
        self.replace("DESIGN.md", "실제 앱에서 새 세션 실행", "")
        self.assert_error("UNKNOWN_QUEUE")

    def test_docs_drift_and_marker_refusal(self):
        self.replace("README.md", "mode 1개", "mode 99개")
        self.assert_error("DOC_DRIFT")
        self.assertEqual([], checker.Checker(self.root).run(True).errors)
        before = (self.root / "DESIGN.md").read_bytes()
        self.replace("README.md", "<!-- skillset:summary:end -->", "<!-- skillset:summary:start -->")
        result = checker.Checker(self.root).run(True)
        self.assertTrue(any(e.startswith("DOC_MARKERS:") for e in result.errors))
        self.assertEqual(before, (self.root / "DESIGN.md").read_bytes())

    def test_guide_cited_path(self):
        put(self.root, "docs/guide/start.md", "# 시작\n\n`skills/absent/SKILL.md`\n")
        self.assert_error("REF_MISSING")

    def test_future_examples_are_not_runtime(self):
        put(self.root, "examples/future/plan.md", "`skills/future-mode/SKILL.md`\n[계획](future.md)\n")
        self.assertEqual([], self.errors())

    def test_ci_required(self):
        self.replace(".github/workflows/check.yml", "push, pull_request", "push")
        self.assert_error("CI")

    def test_ci_must_execute_checker_not_echo_it(self):
        self.replace(".github/workflows/check.yml", "run: python3 scripts/check.py .", "run: echo 'python3 scripts/check.py .'")
        self.assert_error("CI")

    def test_ci_literal_block_runs_checker(self):
        self.replace(".github/workflows/check.yml", "run: python3 scripts/check.py .", "run: |\n          # python3 scripts/check.py .\n          python3 scripts/check.py .")
        self.assertEqual([], self.errors())
        self.replace(".github/workflows/check.yml", "          python3 scripts/check.py .", "          echo done")
        self.assert_error("CI")

    def test_bad_manifest_does_not_raise(self):
        self.config["portability"] = []
        self.config["adapters"] = None
        self.config["copies"] = "wrong"
        self.config["migration"] = {"pending": [None]}
        self.config["command_snapshots"] = [{}]
        self.save_config()
        for code in ("PORTABILITY_CONFIG", "ADAPTER_CONFIG", "COPY_CONFIG", "MIGRATION_CONFIG", "SNAPSHOT_CONFIG"):
            self.assert_error(code)

    def test_inline_marker_explanation_is_not_a_duplicate_block(self):
        with (self.root / "DESIGN.md").open("a") as handle:
            handle.write('\n문서는 `<!-- skillset:policy:start -->` 마커를 쓴다.\n')
        self.assertEqual([], self.errors())

    def test_reference_style_link_is_checked(self):
        with (self.root / "skills/tool/SKILL.md").open("a") as handle:
            handle.write('\n[기준][rule]\n\n[rule]: references/absent.md\n')
        self.assert_error("REF_MISSING")

    def test_malformed_url_is_reported(self):
        self.replace("skills/tool/SKILL.md", "references/detail.md", "https://[bad")
        self.assert_error("REF_SYNTAX")

    def test_ci_comment_does_not_count_as_event(self):
        self.replace(".github/workflows/check.yml", "on: [push, pull_request]", "on: [push]\n# pull_request")
        self.assert_error("CI")

    def test_engine_and_tests_copy_to_generated_scripts(self):
        generated = self.root / "generated/scripts"
        generated.mkdir(parents=True)
        for filename in ("check.py", "selftest.py"):
            shutil.copy2(Path(__file__).with_name(filename), generated / filename)
        self.assertEqual((generated / "check.py").read_bytes(), Path(__file__).with_name("check.py").read_bytes())


@unittest.skipUnless(Path(__file__).with_name("install_smoke.py").is_file(), "installer not copied to this generated project")
class InstallSmokeTests(unittest.TestCase):
    def setUp(self):
        module_spec = importlib.util.spec_from_file_location("install_smoke", Path(__file__).with_name("install_smoke.py"))
        self.smoke = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(self.smoke)
        self.temp = tempfile.TemporaryDirectory(prefix="install-smoke-selftest-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        fixture(self.source)
        self.dest = self.root / "destination"

    def test_refuse_nonempty_destination(self):
        put(self.dest, "important.txt", "keep")
        with self.assertRaisesRegex(ValueError, "new or empty"):
            self.smoke.prepare_destination(self.source, self.dest)
        self.assertEqual("keep", (self.dest / "important.txt").read_text())

    def test_refuse_destination_symlink_and_source_overlap(self):
        target = self.root / "target"
        target.mkdir()
        self.dest.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.smoke.prepare_destination(self.source, self.dest)
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.smoke.prepare_destination(self.source, self.source / "nested")
        self.assertFalse((self.source / "nested").exists())

    def test_refuse_source_link_instead_of_copied_skills(self):
        agents = self.dest / ".agents"
        agents.mkdir(parents=True)
        (agents / "skills").symlink_to(self.source / "skills", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "real copied directory"):
            self.smoke.inspect_install(self.source, self.dest)

    def test_refuse_individual_source_skill_link(self):
        installed = self.dest / ".agents/skills"
        installed.mkdir(parents=True)
        for path in (self.source / "skills").iterdir():
            (installed / path.name).symlink_to(path, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "real copied directory"):
            self.smoke.inspect_install(self.source, self.dest)

    def test_installed_plain_read_is_opened(self):
        put(self.source, "skills/demo-mode/playbooks/create.md", "### 작업\n\n1. Read ../absent/SKILL.md\n")
        shutil.copytree(self.source / "skills", self.dest / ".agents/skills")
        links = self.dest / ".claude/skills"
        links.mkdir(parents=True)
        for path in (self.dest / ".agents/skills").iterdir():
            (links / path.name).symlink_to(path, target_is_directory=True)
        with self.assertRaises(FileNotFoundError):
            self.smoke.inspect_install(self.source, self.dest)
        for root in (self.source, self.dest / ".agents"):
            put(root, "skills/demo-mode/playbooks/create.md", "### 작업\n\n1. Read ../tool/SKILL.md\n")
        evidence = self.smoke.inspect_install(self.source, self.dest)
        self.assertEqual(2, evidence["opened_playbooks"])

    def test_inspect_simulated_install_and_detect_mutation(self):
        # No installer or external command runs in this fixture.
        shutil.copytree(self.source / "skills", self.dest / ".agents/skills")
        links = self.dest / ".claude/skills"
        links.mkdir(parents=True)
        for path in (self.dest / ".agents/skills").iterdir():
            (links / path.name).symlink_to(path, target_is_directory=True)
        evidence = self.smoke.inspect_install(self.source, self.dest)
        self.assertEqual(3, evidence["skill_count"])
        self.assertEqual(2, evidence["opened_playbooks"])
        self.assertGreater(evidence["opened_references"], 0)
        put(self.dest, ".agents/skills/tool/references/detail.md", "changed")
        with self.assertRaisesRegex(ValueError, "resources differ"):
            self.smoke.inspect_install(self.source, self.dest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
