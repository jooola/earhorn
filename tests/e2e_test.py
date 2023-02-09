import os
import sys
from datetime import datetime
from glob import glob
from pathlib import Path
from signal import SIGINT
from subprocess import Popen
from time import sleep

import httpx
from testcontainers.compose import DockerCompose  # type: ignore

here = Path(__file__).parent


def test_cli(tmp_path: Path):
    os.chdir(tmp_path)

    now = datetime.now()
    archive_path = tmp_path / "archive"
    archive_path.mkdir()

    with DockerCompose(here, compose_file_name="e2e-stack.yml", pull=True):
        with Popen(
            [sys.executable, "-m", "earhorn.main"],
            env={
                "LOG_LEVEL": "debug",
                "STATS_URL": "http://localhost:32814/admin/stats.xml",
                "STATS_USER": "admin",
                "STATS_PASSWORD": "hackme",
                "STREAM_URL": "http://localhost:32814/main.ogg",
                "ARCHIVE_PATH": str(archive_path),
                "ARCHIVE_COPY_STREAM": "true",
            },
        ) as process:
            sleep(8)

            resp = httpx.get("http://localhost:9950")
            resp.raise_for_status()
            prometheus = resp.content.decode(encoding="utf-8")

            sleep(4)
            process.send_signal(SIGINT)
            process.wait(timeout=30)

    assert process.returncode == 0

    segment_dir = archive_path / f"{now.year}" / f"{now.month:02d}" / f"{now.day:02d}"
    assert segment_dir.is_dir()
    assert len(glob(f"{segment_dir}/*.ogg")) == 1

    assert "icecast_sources 1.0" in prometheus
    assert "earhorn_stats_scraping_count 1.0" in prometheus
    assert 'earhorn_stream_status{earhorn_stream_status="up"} 1.0' in prometheus
    assert 'earhorn_stream_silence{earhorn_stream_silence="up"} 0.0' in prometheus
