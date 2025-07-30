import sys
import pytest
from argparse import ArgumentParser
from cv_cli import cli
from unittest.mock import MagicMock
from types import SimpleNamespace

@pytest.mark.parametrize("argv, expected", [
    (["resume", "build", "-p", "custom.yaml", "-t", "custom"], {"command": "build", "profile": "custom.yaml", "template": "custom"}),
    (["resume", "profiles", "new", "profile1", "-s", "src1"], {"profiles_command": "new", "src": "src1"}),
    (["resume", "profiles", "edit", "profile1", "-e", "vim"], {"profiles_command": "edit", "editor": "vim"}),
    (["resume", "profiles", "del", "profile1"], {"profiles_command": "del", "name": "profile1"}),
    (["resume", "profiles", "init", "myrepo", "-p"], {"profiles_command": "init", "name": "myrepo", "public": True}),
    (["resume", "profiles", "sync"], {"profiles_command": "sync"}),
    (["resume", "profiles", "clone", "https://github.com/test/repo", "-f"], {"profiles_command": "clone", "remote": "https://github.com/test/repo", "force": True}),
    (["resume", "templates", "new", "template1", "-s", "src1"], {"templates_command": "new", "src": "src1"}),
    (["resume", "templates", "edit", "template1", "-e", "nano"], {"templates_command": "edit", "editor": "nano"}),
    (["resume", "templates", "del", "template1"], {"templates_command": "del", "name": "template1"}),
    (["resume", "templates", "init", "myrepo", "-p"], {"templates_command": "init", "name": "myrepo", "public": True}),
    (["resume", "templates", "clone", "https://github.com/test/repo", "template1", "-f"], {"templates_command": "clone", "remote": "https://github.com/test/repo", "name": "template1", "force": True}),
])
def test_get_args(monkeypatch, argv, expected):
    monkeypatch.setattr(sys, "argv", argv)
    args = cli.get_args()

    for key, val in expected.items():
        assert getattr(args, key) == val

@pytest.mark.parametrize("runner, command_key, command_name, target_func, extra_args", [
    (cli.run_profiles, "profiles_command", "new", "new_template", {"name": "test", "src": None}),
    (cli.run_profiles, "profiles_command", "edit", "edit_template", {"name": "test", "editor": "vim"}),
    (cli.run_profiles, "profiles_command", "del", "del_template", {"name": "test"}),
    (cli.run_profiles, "profiles_command", "init", "init_template", {"name": "test", "public": True}),
    (cli.run_profiles, "profiles_command", "sync", "sync_template", {}),
    (cli.run_profiles, "profiles_command", "clone", "clone_template", {"remote": "url", "force": True}),

    (cli.run_templates, "templates_command", "new", "new_template", {"name": "test", "src": None}),
    (cli.run_templates, "templates_command", "edit", "edit_template", {"name": "test", "editor": "nano"}),
    (cli.run_templates, "templates_command", "del", "del_template", {"name": "test"}),
    (cli.run_templates, "templates_command", "init", "init_template", {"name": "test", "public": True}),  # Note: typo in your code
    (cli.run_templates, "templates_command", "sync", "sync_template", {"name": "test"}),
    (cli.run_templates, "templates_command", "clone", "clone_template", {"remote": "url", "name": "test", "force": True}),
])
def test_branches(monkeypatch, runner, command_key, command_name, target_func, extra_args):
    mock_func = MagicMock()
    monkeypatch.setattr(cli, target_func, mock_func)
    args = {command_key: command_name}
    args.update(extra_args)
    runner(SimpleNamespace(**args))
    mock_func.assert_called_once()


def test_main(monkeypatch, capsys):
    mock_templates = MagicMock()
    mock_profiles = MagicMock()
    mock_compile = MagicMock()

    args = SimpleNamespace(command="build", profile="p", template="t", output="o")
    monkeypatch.setattr(cli, "get_args", lambda: args)
    monkeypatch.setattr(cli, "compile_pdf", mock_compile)
    cli.main()
    mock_compile.assert_called_once_with(profile="p", template="t", output_name="o")

    args = SimpleNamespace(command="profiles")
    monkeypatch.setattr(cli, "get_args", lambda: args)    
    monkeypatch.setattr(cli, "run_profiles", mock_profiles)
    cli.main()
    mock_profiles.assert_called_once_with(args)

    args = SimpleNamespace(command="templates")
    monkeypatch.setattr(cli, "get_args", lambda: args)    
    monkeypatch.setattr(cli, "run_templates", mock_templates)
    cli.main()
    mock_templates.assert_called_once_with(args)
