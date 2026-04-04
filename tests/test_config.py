import pytest
from pathlib import Path


def test_config_model():
    from evokb.config import MODEL

    assert MODEL == "ollama/llama3.2"


def test_config_check_interval():
    from evokb.config import CHECK_INTERVAL

    assert CHECK_INTERVAL == 8


def test_config_raw_dir():
    from evokb.config import RAW_DIR

    assert RAW_DIR == Path("raw")


def test_config_wiki_dir():
    from evokb.config import WIKI_DIR

    assert WIKI_DIR == Path("wiki")


def test_config_clusters_dir():
    from evokb.config import CLUSTERS_DIR

    assert CLUSTERS_DIR == Path("clusters")


def test_config_program_md():
    from evokb.config import PROGRAM_MD

    assert PROGRAM_MD == Path("program.md")
