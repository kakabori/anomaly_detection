from datetime import datetime, timedelta

import adapters.anomaly_detection as anomaly
from adapters.repository import AbstractRecordRepository, AbstractSensorRepository
from domain.detection import run_anomaly_detection
from domain.diagnosis import create_diagnosis_report, run_diagnosis
from domain.diagnosis_precondition import (
    check_operating_condition,
    check_sensor_validity,
)
from domain.model import DiagnosisResult


class InvalidMachineId(Exception):
    pass


def is_valid_machine_id(machine_id, machine_id_list):
    return machine_id in machine_id_list


def diagnose(
    machine_id: str,
    sensor_repo: AbstractSensorRepository,
    record_repo: AbstractRecordRepository,
) -> DiagnosisResult:
    # window_widthは1Recordの長さ
    # 現実的には特徴量抽出ウィンドウ幅はanomaly_detectionの精度に影響するので
    # anomaly_detectionのpolicyの管理下になると思われる
    #
    # diagnosis_window_width は異常スコアの集まりのサイズを決める
    # 集まりの統計量から正常/異常の判定結果を求めるので、判定結果のノイズに影響する
    # 判定結果はトレンド分析のトリガーになるので、この窓が短すぎるとfalse positiveな
    # トレンド分析イベントが頻発しかねないことには留意必要

    machine_id_list = sensor_repo.list()
    if not is_valid_machine_id(machine_id, machine_id_list):
        raise InvalidMachineId(f"Invalid machine id {machine_id}")
    machine = sensor_repo.prepare_machine(machine_id)

    # TODO: machineと各オブジェクトを関連付けるrepositoryを実装する
    detector = anomaly.PandasDetector()
    extractor = anomaly.PandasExtractor(timedelta(hours=1))

    snapshots = sensor_repo.get_sensor_snapshot(machine)

    # センサー故障チェック
    sensor_check = check_sensor_validity(snapshots)
    if sensor_check:
        return sensor_check

    # そもそも機械の異常検知を実行できる状態かの判定
    condition_check = check_operating_condition(machine.diagnosis_config, snapshots)
    if condition_check:
        return condition_check

    # 特徴量抽出→異常兆候スコアリング→診断レコード生成
    latest_records = run_anomaly_detection(
        machine.machine_id,
        detector,
        extractor,
        snapshots,
    )

    # 異常判定
    machine_status = run_diagnosis(latest_records, machine)

    # DBに結果を格納
    record_repo.push_record(latest_records)

    # ---- ここから Step 2 ----
    # 過去数か月分のDiagnosisRecordを取ってくる
    now = datetime.now()
    t0 = now - timedelta(days=90)
    diagnosis_records = record_repo.retrieve_record(machine, (t0, now))

    report = create_diagnosis_report(machine_status, diagnosis_records, now)
    return report


# if __name__ == "__main__":
#     machine_id = "001"
#     sensor_repo =


#     def diagnose(
#     machine_id: str,
#     sensor_repo: AbstractSensorRepository,
#     record_repo: AbstractRecordRepository,
#     detector: AnomalyDetector,
#     extractor: FeatureExtractor,
# )
