from pathlib import Path

from cihpc.collectors.flow123d import Flow123dCollector


def test():
    _current_dir: Path = Path(__file__).absolute().parent
    collector = Flow123dCollector(dict(), dict())

    reports = [collector.process_file(file) for file in _current_dir.glob("**/*.json")]
    assert reports[0][0]["index"]["frame"] == "whole-program"
    assert reports[0][0]["result"]["dur_ratio"] == 1.0
