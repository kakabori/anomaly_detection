from datetime import datetime, timedelta

from adapters.repository import AbstractRecordRepository, AbstractSensorRepository
from domain.detection import run_anomaly_detection
from domain.diagnosis import run_diagnosis, run_root_cause_analysis
from domain.diagnosis_precondition import (
    check_operating_condition,
    check_sensor_validity,
)
from domain.model import DiagnosisReport, DiagnosisResult
from domain.ports import AnomalyDetector, FeatureExtractor


class InvalidMachineId(Exception):
    pass


def is_valid_machine_id(machine_id, machine_id_list):
    return machine_id in machine_id_list


def diagnose(
    machine_id: str,
    sensor_repo: AbstractSensorRepository,
    record_repo: AbstractRecordRepository,
    detector: AnomalyDetector,
    extractor: FeatureExtractor,
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
    diagnosis_records = run_anomaly_detection(
        machine.machine_id,
        detector,
        extractor,
        snapshots,
    )

    # 異常判定
    machine_status = run_diagnosis(diagnosis_records, machine)

    # DBに結果を格納
    # save(diagnosis_records, machine_status)

    if machine_status == "NORMAL":
        return DiagnosisReport(machine_status=machine_status)

    # ---- ここから Step 2 ----
    # トレンド分析: 過去数か月分のDiagnosisRecordを取ってくる
    t1 = datetime.now()
    t0 = t1 - timedelta(days=90)
    trend = record_repo.retrieve_record(machine, (t0, t1))

    report = run_root_cause_analysis(trend)
    return report
