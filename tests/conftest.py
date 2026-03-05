"""Shared fixtures for odb_read tests."""

import pytest

from odb_read.services.analysis import AnalysisService


@pytest.fixture
def analysis():
    """Provide a fresh AnalysisService instance for each test."""
    return AnalysisService()
