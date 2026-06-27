#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Unit tests for list_customizable_skills.py.

Exercises the scanner against a synthesized install tree:
- an agent-only customize.toml
- a workflow-only customize.toml
- a customize.toml that exposes both surfaces
- a skill directory with no customize.toml (ignored)
- a pre-existing team override in _bmad/custom/
- malformed TOML (surfaces as an error without aborting)
- multiple skills roots (e.g. project-local + user-global mix)

Run: uv run scripts/tests/test_list_customizable_skills.py
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "list_customizable_skills.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("list_customizable_skills", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


MODULE = _load_module()


def _make_skill(parent: Path, name: str, body: str, skill_md: str | None = None) -> Path:
    skill_dir = parent / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "customize.toml").write_text(body, encoding="utf-8")
    if skill_md is not None:
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    return skill_dir


class ScannerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = self.root / "skills"
        self.skills.mkdir(parents=True)
        self.custom = self.root / "_bmad" / "custom"
        self.custom.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_agent_only_skill_detected(self):
        _make_skill(
            self.skills,
            "emcomm-agent-coml",
            "[agent]\nicon = \"📡\"\n",
            "---\nname: emcomm-agent-coml\ndescription: Communications Unit Leader.\n---\n",
        )
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(len(result["agents"]), 1)
        self.assertEqual(len(result["workflows"]), 0)
        entry = result["agents"][0]
        self.assertEqual(entry["name"], "emcomm-agent-coml")
        self.assertEqual(entry["surface"], "agent")
        self.assertEqual(entry["description"], "Communications Unit Leader.")
        self.assertFalse(entry["has_team_override"])
        self.assertFalse(entry["has_user_override"])

    def test_workflow_only_skill_detected(self):
        _make_skill(
            self.skills,
            "emcomm-engine",
            "[workflow]\npersistent_facts = []\n",
            "---\nname: emcomm-engine\ndescription: 'Launch the VECTRA engine.'\n---\n",
        )
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(len(result["agents"]), 0)
        self.assertEqual(len(result["workflows"]), 1)
        entry = result["workflows"][0]
        self.assertEqual(entry["description"], "Launch the VECTRA engine.")

    def test_dual_surface_skill_emits_two_entries(self):
        _make_skill(
            self.skills,
            "emcomm-dual",
            "[agent]\nicon = \"x\"\n\n[workflow]\npersistent_facts = []\n",
            "---\nname: emcomm-dual\ndescription: Dual.\n---\n",
        )
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(len(result["agents"]), 1)
        self.assertEqual(len(result["workflows"]), 1)
        self.assertEqual(result["agents"][0]["name"], "emcomm-dual")
        self.assertEqual(result["workflows"][0]["name"], "emcomm-dual")

    def test_skill_without_customize_toml_ignored(self):
        (self.skills / "emcomm-plain").mkdir()
        (self.skills / "emcomm-plain" / "SKILL.md").write_text("# plain\n")
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(len(result["agents"]) + len(result["workflows"]), 0)
        self.assertEqual(result["errors"], [])

    def test_existing_team_override_flagged(self):
        _make_skill(
            self.skills,
            "emcomm-agent-coml",
            "[agent]\nicon = \"📡\"\n",
            "---\nname: emcomm-agent-coml\ndescription: COML.\n---\n",
        )
        (self.custom / "emcomm-agent-coml.toml").write_text("[agent]\n")
        result = MODULE.scan_skills([self.skills], self.root)
        entry = result["agents"][0]
        self.assertTrue(entry["has_team_override"])
        self.assertFalse(entry["has_user_override"])

    def test_missing_surface_block_reports_error(self):
        _make_skill(self.skills, "emcomm-broken", "[not_a_surface]\nfoo = 1\n")
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(len(result["agents"]) + len(result["workflows"]), 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("no [agent] or [workflow] block", result["errors"][0])

    def test_malformed_toml_reports_error_without_aborting(self):
        skill_dir = self.skills / "emcomm-bad"
        skill_dir.mkdir()
        (skill_dir / "customize.toml").write_text("this is not [valid toml\n")
        # Plus a good sibling to confirm scanning continues.
        _make_skill(
            self.skills,
            "emcomm-good",
            "[agent]\nicon = \"x\"\n",
            "---\nname: emcomm-good\ndescription: Good.\n---\n",
        )
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(len(result["agents"]), 1)
        self.assertEqual(result["agents"][0]["name"], "emcomm-good")
        self.assertTrue(any("failed to parse" in e for e in result["errors"]))

    def test_description_with_double_quotes_stripped(self):
        _make_skill(
            self.skills,
            "emcomm-q",
            "[agent]\nicon = \"x\"\n",
            '---\nname: emcomm-q\ndescription: "Double-quoted desc."\n---\n',
        )
        result = MODULE.scan_skills([self.skills], self.root)
        self.assertEqual(result["agents"][0]["description"], "Double-quoted desc.")

    def test_multiple_skills_roots_are_merged(self):
        extra_root = self.root / "extra-skills"
        extra_root.mkdir()
        _make_skill(
            self.skills,
            "emcomm-agent-coml",
            "[agent]\nicon = \"📡\"\n",
            "---\nname: emcomm-agent-coml\ndescription: COML.\n---\n",
        )
        _make_skill(
            extra_root,
            "emcomm-agent-net-eng",
            "[agent]\nicon = \"🔧\"\n",
            "---\nname: emcomm-agent-net-eng\ndescription: Net Engineer.\n---\n",
        )
        result = MODULE.scan_skills([self.skills, extra_root], self.root)
        names = {a["name"] for a in result["agents"]}
        self.assertEqual(names, {"emcomm-agent-coml", "emcomm-agent-net-eng"})
        self.assertEqual(len(result["scanned_roots"]), 2)

    def test_duplicate_skill_name_across_roots_first_wins(self):
        extra_root = self.root / "extra-skills"
        extra_root.mkdir()
        _make_skill(
            self.skills,
            "emcomm-agent-coml",
            "[agent]\nicon = \"primary\"\n",
            "---\nname: emcomm-agent-coml\ndescription: Primary.\n---\n",
        )
        _make_skill(
            extra_root,
            "emcomm-agent-coml",
            "[agent]\nicon = \"duplicate\"\n",
            "---\nname: emcomm-agent-coml\ndescription: Duplicate.\n---\n",
        )
        result = MODULE.scan_skills([self.skills, extra_root], self.root)
        self.assertEqual(len(result["agents"]), 1)
        self.assertEqual(result["agents"][0]["description"], "Primary.")
        self.assertEqual(result["agents"][0]["skills_root"], str(self.skills))

    def test_missing_skills_root_reports_error(self):
        result = MODULE.scan_skills(
            [self.root / "does-not-exist", self.skills],
            self.root,
        )
        self.assertTrue(any("skills root does not exist" in e for e in result["errors"]))

    def test_cli_emits_valid_json_and_exits_zero(self):
        _make_skill(
            self.skills,
            "emcomm-agent-coml",
            "[agent]\nicon = \"📡\"\n",
            "---\nname: emcomm-agent-coml\ndescription: COML.\n---\n",
        )
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-root",
                str(self.root),
                "--skills-root",
                str(self.skills),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(len(payload["agents"]), 1)

    def test_cli_exits_two_on_missing_project_root(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-root",
                str(self.root / "does-not-exist"),
                "--skills-root",
                str(self.skills),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("does not exist", proc.stderr)


if __name__ == "__main__":
    unittest.main()
