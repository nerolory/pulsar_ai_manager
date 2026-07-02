"""Tests for local model downloader helpers."""

import pytest

from app.model_downloader import get_model_path, is_model_downloaded, get_model_gguf_path


def test_invalid_model_id_rejected():
    with pytest.raises(ValueError):
        get_model_path("../escape")


def test_missing_model_not_downloaded():
    assert is_model_downloaded("nonexistent-model-id-xyz") is False
    assert get_model_gguf_path("nonexistent-model-id-xyz") is None
