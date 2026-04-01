from datetime import datetime, timedelta

import pytest

from domain.model import SensorSnapshot, TemperatureOutOfRange


def test_length_mismatch_message():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples + 1)],
    }
    with pytest.raises(AssertionError, match="長さ不一致"):
        SensorSnapshot(time=time, data=data)


def test_missing_key_message():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
    }
    with pytest.raises(AssertionError, match="キーが不足"):
        SensorSnapshot(time=time, data=data)


def test_temperature_too_high():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples)],
    }
    data["temperature"][0] = 150.1
    with pytest.raises(TemperatureOutOfRange, match="温度が仕様範囲外"):
        SensorSnapshot(time=time, data=data)
    data["temperature"][0] = -50.1
    with pytest.raises(TemperatureOutOfRange, match="温度が仕様範囲外"):
        SensorSnapshot(time=time, data=data)
