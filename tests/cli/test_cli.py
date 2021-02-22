import pytest
from subprocess import Popen, PIPE
from liesl.files.labrecorder.cli_wrapper import LabRecorderCLI
import time
from liesl.cli.lsl_api import Ini, default_lsl_api_cfg
import signal
from sys import platform


def test_cli_main_help():
    p = Popen(["liesl", "-h"], stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    assert "liesl [-h]" in o.decode()


def test_cli_xdf(xdf_file):
    assert xdf_file.exists()
    p = Popen(
        ["liesl", "xdf", str(xdf_file), "--timeout", "inf"],
        stdout=PIPE,
        stderr=PIPE,
    )
    o, e = p.communicate()
    assert f"Loading {xdf_file}" in o.decode()
    assert "Liesl-Mock-EEG" in o.decode()
    assert "Liesl-Mock-Marker" in o.decode()


@pytest.mark.skipif(
    platform.startswith("win"), reason="Popen bug on GH Actions"
)
def test_cli_xdf_at_most(xdf_file):
    p = Popen(
        ["liesl", "xdf", xdf_file, "--at-most", "2"], stdout=PIPE, stderr=PIPE
    )
    o, e = p.communicate()
    assert f"Loading {xdf_file}" in o.decode()


def test_cli_config_default(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    assert (tmpdir / "lsl_api.cfg").exists() == False
    p = Popen(
        ["liesl", "config", "local", "--default"], stdout=PIPE, stderr=PIPE
    )
    o, e = p.communicate()
    assert str(tmpdir) in o.decode()
    assert (tmpdir / "lsl_api.cfg").exists()

    ini = Ini(level="local")
    output = ini.as_dict()
    for key in default_lsl_api_cfg.keys():
        assert default_lsl_api_cfg[key] == output[key]


def test_cli_config_sessionid(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    assert (tmpdir / "lsl_api.cfg").exists() == False
    ini = Ini(level="local")
    assert ini.path.exists() == False
    p = Popen(
        ["liesl", "config", "local", "--sessionid", "test",],
        stdout=PIPE,
        stderr=PIPE,
    )
    o, e = p.communicate()
    assert (tmpdir / "lsl_api.cfg").exists() == True
    ini = ini.as_dict()
    assert ini["lab"]["SessionID"] == "test"


def test_cli_config_knownpeers(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    assert (tmpdir / "lsl_api.cfg").exists() == False
    ini = Ini(level="local")
    assert ini.path.exists() == False
    p = Popen(
        ["liesl", "config", "local", "--knownpeers", "127.0.0.1",],
        stdout=PIPE,
        stderr=PIPE,
    )
    o, e = p.communicate()
    assert (tmpdir / "lsl_api.cfg").exists() == True
    ini = ini.as_dict()
    assert ini["lab"]["KnownPeers"] == "{127.0.0.1}"


@pytest.mark.ascii
def test_cli_show_ascii():
    m = Popen(["liesl", "mock"], stdout=PIPE, stderr=PIPE,)
    time.sleep(5)
    p = Popen(["liesl", "show"], stdout=PIPE, stderr=PIPE,)
    time.sleep(5)
    p.kill()
    m.kill()
    o, e = p.communicate()
    assert "|" in o.decode()
