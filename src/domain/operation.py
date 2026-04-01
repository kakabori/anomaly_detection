from typing import Optional

from domain.model import DiagnosisConfig, DiagnosisUnavailable, Evidence, SensorSnapshot


def check_operating_condition(
    config: DiagnosisConfig, snapshot: SensorSnapshot
) -> Optional[DiagnosisUnavailable]:
    # 例えば、temperatureのセンサー値が上限を超えている場合は異常検知の実行すらできないといった条件を定義する
    for i, value in enumerate(snapshot.data["temperature"]):
        if value < config.temperature_operating_range[0]:
            return DiagnosisUnavailable(
                reason="sensor_out_of_range",
                evidence=Evidence(
                    anomalous_features={
                        "temperature": f"temperature[{i}] is below operating range"
                    }
                ),
            )
        if value > config.temperature_operating_range[1]:
            return DiagnosisUnavailable(
                reason="sensor_out_of_range",
                evidence=Evidence(
                    anomalous_features={
                        "temperature": f"temperature[{i}] is above operating range"
                    }
                ),
            )
    return None
