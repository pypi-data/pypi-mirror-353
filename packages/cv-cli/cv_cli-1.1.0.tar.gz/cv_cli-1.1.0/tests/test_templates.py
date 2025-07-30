import pytest
from unittest.mock import patch
from pathlib import Path

from cv_cli.templates import new_template, edit_template, del_template, init_template, sync_template, clone_template

@pytest.fixture
def tmp_templates_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("cv_cli.constants.TEMPLATES_DIR", tmp_path)
    monkeypatch.setattr("cv_cli.templates.TEMPLATES_DIR", tmp_path)
    yield tmp_path

def test_new_template_creates(tmp_templates_dir):
    template_name = "test"
    new_template(template_name, None)
    template_path = tmp_templates_dir / template_name
    assert template_path.exists()

def test_new_template_with_src(tmp_templates_dir):
    src_name = "src"
    src_path = tmp_templates_dir / src_name
    src_path.mkdir()
    (src_path / "test.tex").write_text("test")
    template_name = "test"
    
    new_template(template_name, src_name)
    template_path = tmp_templates_dir / template_name
    assert (template_path / "test.tex").read_text() == "test"

def test_new_template_with_src_invalid(tmp_templates_dir, capsys):
    src_name = "src"
    template_name = "test"
    new_template(template_name, src_name)
    captured = capsys.readouterr()
    assert "not exist" in captured.out

def test_new_template_exists(tmp_templates_dir, capsys):
    template_path = "test"
    template_path = tmp_templates_dir / template_path
    template_path.mkdir()

    new_template(template_path, None)
    captured = capsys.readouterr()
    assert "already exists" in captured.out

def test_edit_template_call(tmp_templates_dir):
    template_name = "test"
    template_path = tmp_templates_dir / template_name
    template_path.mkdir()

    with patch("cv_cli.templates.edit_file") as mock:
        edit_template(template_name, "code")
        mock.assert_called_once_with(template_path, "code")

def test_edit_template_invalid(tmp_templates_dir, capsys):
    edit_template("invalid", "code")
    captured = capsys.readouterr()
    assert "not exist" in captured.out

def test_del_template_deletes(tmp_templates_dir):
    template_name = "test"
    template_path = tmp_templates_dir / template_name
    template_path.mkdir()
    del_template(template_name)
    assert not template_path.exists()

def test_del_template_invalid(tmp_templates_dir, capsys):
    del_template("invalid")
    captured = capsys.readouterr()
    assert "not exist" in captured.out

def test_init_templates_calls(tmp_templates_dir):
    with patch("cv_cli.templates.git_init") as mock:
        init_template("test", True)
        mock.assert_called_once_with(tmp_templates_dir / "test", "test", True)

def test_sync_templates_calls(tmp_templates_dir):
    with patch("cv_cli.templates.git_sync") as mock:
        sync_template("test")
        mock.assert_called_once()

def test_clone_templates_calls(tmp_templates_dir):
    with patch("cv_cli.templates.git_clone") as mock:
        clone_template("test.com", "template", True)
        mock.assert_called_once_with("test.com", tmp_templates_dir / "template", True)
