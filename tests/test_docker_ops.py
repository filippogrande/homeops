from api.docker_ops import health_of, parse_ps


def test_parse_ps_skips_bad_lines():
    stdout = '{"Name": "a", "State": "running"}\nnot json\n{"Name": "b", "State": "running"}\n'
    assert len(parse_ps(stdout)) == 2


def test_parse_ps_accepts_array():
    stdout = '[{"Name": "a", "State": "running"}]'
    assert len(parse_ps(stdout)) == 1


def test_health_of_healthy_without_healthcheck():
    assert health_of([{"State": "running", "Health": ""}]) == "healthy"


def test_health_of_starting():
    assert health_of([{"State": "running", "Health": "starting"}]) == "starting"


def test_health_of_unhealthy_exited():
    assert health_of([{"State": "exited", "Health": ""}]) == "unhealthy"


def test_health_of_missing():
    assert health_of([]) == "missing"
