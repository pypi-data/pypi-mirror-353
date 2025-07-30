import importlib
import sys
from types import ModuleType
from pathlib import Path
from unittest.mock import MagicMock

import pytest

FEATURE_FUNCTIONS = [
    "get_dataset",
    "train",
    "resume_train",
    "valid",
    "stream",
    "video_detect",
]


@pytest.fixture()
def cli_module(monkeypatch):
    """Import atar.cli with mocked dependencies."""
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root))
    dummy = ModuleType("dummy")
    dummy.roboflow_dataset = MagicMock()
    dummy.video_detect = MagicMock()
    dummy.stream = MagicMock()
    dummy.m_valid = MagicMock()
    dummy.m_train = MagicMock()
    dummy.r_train = MagicMock()

    deps = [
        "src.Utilities.roboFlowDataSet",
        "src.Utilities.vDetect",
        "src.Utilities.sDetect",
        "src.Utilities.modelValid",
        "src.Utilities.modelTrain",
        "src.Utilities.rTrain",
    ]
    for name in deps:
        monkeypatch.setitem(sys.modules, name, dummy)

    sys.modules.pop("atar.cli", None)
    sys.modules.pop("src.Utilities.features", None)

    cli = importlib.import_module("atar.cli")
    return cli


@pytest.mark.parametrize(
    "choice,func_name",
    [
        ("1", "get_dataset"),
        ("2", "train"),
        ("3", "resume_train"),
        ("4", "valid"),
        ("5", "stream"),
        ("6", "video_detect"),
    ],
)
def test_process_choice_valid(monkeypatch, cli_module, choice, func_name):
    mock_func = MagicMock()
    monkeypatch.setattr(cli_module.features, func_name, mock_func)
    result = cli_module.process_choice(choice)
    assert result is True
    mock_func.assert_called_once_with()


def test_process_choice_quit(monkeypatch, cli_module):
    mock_info = MagicMock()
    monkeypatch.setattr(cli_module.log.logger, "info", mock_info)
    result = cli_module.process_choice("7")
    assert result is False
    mock_info.assert_called_once()


def test_process_choice_invalid_option(monkeypatch, cli_module):
    mock_warning = MagicMock()
    monkeypatch.setattr(cli_module.log.logger, "warning", mock_warning)
    for func in FEATURE_FUNCTIONS:
        monkeypatch.setattr(cli_module.features, func, MagicMock())

    result = cli_module.process_choice("invalid")
    assert result is True
    mock_warning.assert_called_once()
    for func in [getattr(cli_module.features, name) for name in FEATURE_FUNCTIONS]:
        func.assert_not_called()
