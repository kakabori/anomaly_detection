from adapters.repository import AbstractRepository
from domain.anomaly_detection import run_anomaly_detection, run_feature_extraction
from domain.diagnosis import run_diagnosis, run_root_cause_analysis
from domain.diagnosis_precondition import (
    check_operating_condition,
    check_sensor_validity,
)
from domain.model import (
    DiagnosisResult,
)


class InvalidMachineId(Exception):
    pass


def is_valid_machine_id(machine_id, machine_id_list):
    return machine_id in machine_id_list


def diagnose(machine_id: str, repo: AbstractRepository) -> DiagnosisResult:
    machine_id_list = repo.list()
    if not is_valid_machine_id(machine_id, machine_id_list):
        raise InvalidMachineId(f"Invalid machine id {machine_id}")
    machine = repo.prepare_machine(machine_id)

    snapshot = repo.get_sensor_snapshot(machine)

    # センサー故障チェック
    sensor_check = check_sensor_validity(snapshot)
    if sensor_check:
        return sensor_check

    # そもそも機械の異常検知を実行できる状態かの判定
    condition_check = check_operating_condition(machine.diagnosis_config, snapshot)
    if condition_check:
        return condition_check

    feature = run_feature_extraction(snapshot)
    anomaly_score = run_anomaly_detection(snapshot)
    machine_status = run_diagnosis(anomaly_score, machine)
    report = run_root_cause_analysis(machine_status, feature, anomaly_score)
    return report
