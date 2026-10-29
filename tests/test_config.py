import textwrap

import pytest

from shared.config import load_config


def test_load_config(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        textwrap.dedent(
            """
            compose_root: /stacks
            update:
              poll_interval_sec: 5
              timeout_sec: 20
            telegram:
              enabled: true
              bot_token: "x"
              chat_ids: [1, 2]
            services:
              - name: nextcloud
                compose_file: nc/compose.yaml
            """
        ),
        encoding="utf-8",
    )
    config = load_config(str(path))
    assert config.update.poll_interval_sec == 5
    assert config.update.timeout_sec == 20
    assert config.telegram.chat_ids == (1, 2)
    assert config.services["nextcloud"].compose_file == "nc/compose.yaml"


def test_missing_config(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "nope.yaml"))
