import pytest
from sentinel_simplecli.cli import parse_requirements_from_text, parse_requirements, load_trakignore

def test_parse_requirements_from_text():
    req_text = "requests==2.25.1\nflask==1.1.2\n"
    result = parse_requirements_from_text(req_text)
    assert result == [("requests", "2.25.1"), ("flask", "1.1.2")]

def test_parse_requirements(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests==2.25.1\n# comment\nflask==1.1.2\n")
    result = parse_requirements(str(req_file))
    assert result == [("requests", "2.25.1"), ("flask", "1.1.2")]

def test_load_trakignore(tmp_path, monkeypatch):
    trak_file = tmp_path / ".trakignore"
    trak_file.write_text("GHSA-1234\nGHSA-5678\n")
    monkeypatch.chdir(tmp_path)
    ignore_set = load_trakignore()
    assert ignore_set == {"GHSA-1234", "GHSA-5678"}
