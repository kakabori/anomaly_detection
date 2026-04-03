from domain.model import DiagnosisConfig, DiagnosisUnavailable, Evidence, SensorSnapshot


def check_sensor_validity(snapshot: SensorSnapshot) -> DiagnosisUnavailable | None:
    for value in snapshot.data["temperature"]:
        if value < -50 or value > 150:
            return DiagnosisUnavailable(
                reason="sensor_out_of_range",
                evidence=Evidence(
                    anomalous_features={"temperature": "温度がセンサー仕様範囲外"}
                ),
            )


def check_operating_condition(
    config: DiagnosisConfig, snapshot: SensorSnapshot
) -> DiagnosisUnavailable | None:
    # 例えば、temperatureのセンサー値が上限を超えている場合は異常検知の実行すらできないといった条件を定義する
    for i, value in enumerate(snapshot.data["temperature"]):
        if value < config.temperature_operating_range[0]:
            return DiagnosisUnavailable(
                reason="temperature_out_of_range",
                evidence=Evidence(
                    anomalous_features={
                        "temperature": f"temperature[{i}] is below operating range"
                    }
                ),
            )
        if value > config.temperature_operating_range[1]:
            return DiagnosisUnavailable(
                reason="temperature_out_of_range",
                evidence=Evidence(
                    anomalous_features={
                        "temperature": f"temperature[{i}] is above operating range"
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
