from datetime import datetime, timedelta

import pytest

from domain.model import SensorSnapshot


def test_length_mismatch_message():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples + 1)],
    }
    with pytest.raises(ValueError, match="長さ不一致"):
        SensorSnapshot(time=time, data=data)


def test_missing_key_message():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
    }
    with pytest.raises(ValueError, match="キーが不足"):
        SensorSnapshot(time=time, data=data)


def test_non_monotonically_increasing_message():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    time[0], time[1] = time[1], time[0]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples + 1)],
    }
    with pytest.raises(ValueError, match="単調増加でない"):
        SensorSnapshot(time=time, data=data)
