import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from cv_cli.git import get_repo_url, git_init, git_clone, git_pull, git_push, git_sync

def test_get_repo_url(monkeypatch):
    EXPECTED_URL = "https://github.com/test/repo.git"
    mock = MagicMock(return_value=MagicMock(returncode=0, stdout=EXPECTED_URL))
    monkeypatch.setattr("cv_cli.git.run", mock)
    actual_url = get_repo_url("test/repo")
    assert actual_url == EXPECTED_URL

def test_get_repo_url_fail(monkeypatch):
    mock = MagicMock(return_value=MagicMock(returncode=1))
    monkeypatch.setattr("cv_cli.git.run", mock)

    with pytest.raises(FileNotFoundError):
        get_repo_url("test/repo.git")
    
def test_git_init(monkeypatch, tmp_path):
    URL = "https://github.com/test/repo.git"
    mock = MagicMock()
    mock_get_url = MagicMock(return_value=URL)

    monkeypatch.setattr("cv_cli.git.run", mock)
    monkeypatch.setattr("cv_cli.git.get_repo_url", mock_get_url)
    monkeypatch.setattr("cv_cli.git.git_sync", MagicMock())

    git_init(tmp_path, "repo", True)
    assert tmp_path.exists()
    mock.assert_any_call(["git", "init"], cwd=tmp_path, check=True)
    mock.assert_any_call(["git", "remote", "add", "origin", URL], cwd=tmp_path, check=True)

def test_git_init_no_repo(monkeypatch, tmp_path):
    mock_run = MagicMock()
    monkeypatch.setattr("cv_cli.git.run", mock_run)
    monkeypatch.setattr("cv_cli.git.get_repo_url", MagicMock(side_effect=FileNotFoundError))
    monkeypatch.setattr("cv_cli.git.git_sync", MagicMock())

    git_init(tmp_path, "test/repo", public=False)
    mock_run.assert_any_call(["git", "init"], cwd=tmp_path, check=True)

def test_git_clone(monkeypatch, tmp_path):
    URL = "https://github.com/test/repo.git"
    mock = MagicMock()
    mock_rm = MagicMock()
    monkeypatch.setattr("cv_cli.git.run", mock)
    monkeypatch.setattr("cv_cli.git.rmtree", mock_rm)

    git_clone(URL, tmp_path, force=True)
    mock.assert_any_call(["git", "clone", URL, tmp_path], check=True)

def test_git_pull(monkeypatch, tmp_path):
    mock = MagicMock()
    monkeypatch.setattr("cv_cli.git.run", mock)

    git_pull(tmp_path)
    mock.assert_any_call(["git", "branch", "-M", "main"], cwd=tmp_path, check=True)
    mock.assert_any_call(["git", "pull", "origin", "main"], cwd=tmp_path, check=True)

def test_git_push(monkeypatch, tmp_path):
    mock = MagicMock()
    monkeypatch.setattr("cv_cli.git.run", mock)

    git_push(tmp_path)
    mock.assert_any_call(["git", "branch", "-M", "main"], cwd=tmp_path, check=True)
    mock.assert_any_call(["git", "add", "."], cwd=tmp_path, check=True)
    mock.assert_any_call(["git", "commit", "-m", "sync: auto sync"], cwd=tmp_path, check=True)
    mock.assert_any_call(["git", "push", "-u", "origin", "main"], cwd=tmp_path, check=True)

def test_git_sync(monkeypatch, tmp_path):
    mock_push = MagicMock()
    mock_pull = MagicMock()
    monkeypatch.setattr("cv_cli.git.git_push", mock_push)
    monkeypatch.setattr("cv_cli.git.git_pull", mock_pull)

    git_sync(tmp_path)
    mock_push.assert_called_once_with(tmp_path)
    mock_pull.assert_called_once_with(tmp_path)
