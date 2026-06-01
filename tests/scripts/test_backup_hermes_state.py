import tarfile

from scripts.backup_hermes_state import _redact, create_backup


def test_redact_common_secret_shapes():
    text = "TOKEN=abc123456 AIRTABLE_API_KEY: keyvalue123 sk-abcdefghijklmnopqrstuvwxyz github_pat_1234567890abcdefghijklmnopqrstuvwxyz"
    redacted = _redact(text)
    assert "abc123456" not in redacted
    assert "keyvalue123" not in redacted
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "github_pat_1234567890" not in redacted


def test_create_backup_sanitizes_config_and_excludes_env(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("hello", encoding="utf-8")
    (repo / "scripts").mkdir()
    (repo / "scripts" / "safe.py").write_text("TOKEN=abc123456\n", encoding="utf-8")
    (repo / ".env").write_text("TOKEN=should_not_copy\n", encoding="utf-8")

    home = tmp_path / "home"
    (home / "cron").mkdir(parents=True)
    (home / "cron" / "jobs.json").write_text("[]", encoding="utf-8")

    monkeypatch.setattr("scripts.backup_hermes_state.HERMES_HOME", home)
    result = create_backup(repo, push=False)
    assert result["success"] is True
    tar_path = result["tarball"]
    with tarfile.open(tar_path, "r:gz") as tar:
        names = tar.getnames()
        assert not any(name.endswith(".env") for name in names)
        script_member = next(name for name in names if name.endswith("repo/scripts/safe.py"))
        content = tar.extractfile(script_member).read().decode()
        assert "abc123456" not in content
        assert "REDACTED" in content
