import math

from domain.model import DiagnosisConfig, DiagnosisUnavailable, Evidence, SensorSnapshot


def check_sensor_validity(
    snapshot: list[SensorSnapshot],
) -> DiagnosisUnavailable | None:
    # 欠損率の上限
    for sensor_name, sensor_value in snapshot.data.items():
        ratio = sum(math.isnan(v) for v in sensor_value) / len(sensor_value)
        if ratio > 0.2:
            return DiagnosisUnavailable(
                reason="missing_rate_too_high",
                evidence=Evidence({sensor_name: "欠損率が上限を超えている"}),
            )

    # 温度のハードウェア仕様範囲
    for value in snapshot.data["temperature"]:
        if value < -50 or value > 150:
            return DiagnosisUnavailable(
                reason="sensor_out_of_range",
                evidence=Evidence({"temperature": "温度がセンサー仕様範囲外"}),
            )


def check_operating_condition(
    config: DiagnosisConfig, snapshot: list[SensorSnapshot]
) -> DiagnosisUnavailable | None:
    # 例えば、temperatureのセンサー値が上限を超えている場合は異常検知の実行すらできないといった条件を定義する
    for i, value in enumerate(snapshot.data["temperature"]):
        if value < config.temperature_operating_range[0]:
            return DiagnosisUnavailable(
                reason="temperature_out_of_range",
                evidence=Evidence(
                    anomalous_features={
                        "temperature": f"operating temperature[{i}] is below operating range"
                    }
                ),
            )
        if value > config.temperature_operating_range[1]:
            return DiagnosisUnavailable(
                reason="temperature_out_of_range",
                evidence=Evidence(
                    anomalous_features={
                        "temperature": f"operating temperature[{i}] is above operating range"
                    }
                ),
            )
    return None


if __name__ == "__main__":
    from datetime import datetime, timedelta

    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples)],
    }
    data["temperature"][0] = 150.1
    snapshot = SensorSnapshot(time=time, data=data)
    sensor_check = check_sensor_validity(snapshot)
    print(sensor_check)
