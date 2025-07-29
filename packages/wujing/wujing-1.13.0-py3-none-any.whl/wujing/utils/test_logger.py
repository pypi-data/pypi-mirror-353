import pytest
from loguru import logger

from wujing.utils.logger import configure_logger


@pytest.fixture(autouse=True)
def reset_logger():
    yield
    logger.remove()


def test_configure_logger_stdout(capsys):
    configure_logger(sink="stdout")
    logger.info("Test message to stdout")
    logger.stop()
    captured = capsys.readouterr()
    assert "Test message to stdout" in captured.out


def test_configure_logger_file(tmp_path):
    log_file = tmp_path / "test.log"
    configure_logger(log_file_name=str(log_file), sink="file")
    logger.info("Test message to file")

    logger.stop()
    with open(log_file, "r") as f:
        content = f.read()
        assert "Test message to file" in content
