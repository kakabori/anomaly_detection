import math
from datetime import datetime, timedelta

from domain.diagnosis_precondition import (
    check_operating_condition,
    check_sensor_validity,
)
from domain.model import DiagnosisConfig, DiagnosisUnavailable, SensorSnapshot


def make_sensor_snapshot(n_samples: int = 10):
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples)],
    }
    return SensorSnapshot(time=time, data=data)


def test_temperature_within_range():
    snapshot = make_sensor_snapshot(10)
    sensor_check = check_sensor_validity(snapshot)
    assert sensor_check is None


def test_temperature_too_high():
    snapshot = make_sensor_snapshot(10)
    snapshot.data["temperature"][0] = 150.1
    sensor_check = check_sensor_validity(snapshot)
    assert isinstance(sensor_check, DiagnosisUnavailable)
    assert sensor_check.reason == "sensor_out_of_range"
    assert (
        sensor_check.evidence.anomalous_features["temperature"]
        == "温度がセンサー仕様範囲外"
    )

    snapshot.data["temperature"][0] = -50.1
    sensor_check = check_sensor_validity(snapshot)
    assert isinstance(sensor_check, DiagnosisUnavailable)
    assert sensor_check.reason == "sensor_out_of_range"
    assert (
        sensor_check.evidence.anomalous_features["temperature"]
        == "温度がセンサー仕様範囲外"
    )


def test_too_many_missing_values():
    snapshot = make_sensor_snapshot(10)
    snapshot.data["vibration"][0] = math.nan
    snapshot.data["vibration"][1] = math.nan
    snapshot.data["vibration"][2] = math.nan
    sensor_check = check_sensor_validity(snapshot)
    assert isinstance(sensor_check, DiagnosisUnavailable)
    assert sensor_check.reason == "missing_rate_too_high"
    assert (
        sensor_check.evidence.anomalous_features["vibration"]
        == "欠損率が上限を超えている"
    )


def test_temperature_in_allowed_range():
    config = DiagnosisConfig(24, 1.0, (-5, 4))
    snapshot = make_sensor_snapshot(10)
    condition_check = check_operating_condition(config, snapshot)
    assert condition_check is None


def test_operating_temperature_out_of_range():
    config = DiagnosisConfig(24, 1.0, (-5, 3.9))
    snapshot = make_sensor_snapshot(10)
    condition_check = check_operating_condition(config, snapshot)
    assert isinstance(condition_check, DiagnosisUnavailable)
    assert condition_check.reason == "temperature_out_of_range"
    assert (
        condition_check.evidence.anomalous_features["temperature"]
        == "operating temperature[9] is above operating range"
    )

    config = DiagnosisConfig(24, 1.0, (-4.9, 4))
    condition_check = check_operating_condition(config, snapshot)
    assert isinstance(condition_check, DiagnosisUnavailable)
    assert condition_check.reason == "temperature_out_of_range"
    assert (
        condition_check.evidence.anomalous_features["temperature"]
        == "operating temperature[0] is below operating range"
    )
