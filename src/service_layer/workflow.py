from adapters.repository import AbstractRepository
from domain.anomaly_detection import run_anomaly_detection, run_feature_extraction
from domain.diagnosis import run_diagnosis, run_root_cause_analysis
from domain.model import DiagnosisReport


class InvalidMachineId(Exception):
    pass


def is_valid_machine_id(machine_id, machine_id_list):
    return machine_id in machine_id_list


def diagnose(machine_id: str, repo: AbstractRepository) -> DiagnosisReport:
    machine_id_list = repo.list()
    if not is_valid_machine_id(machine_id, machine_id_list):
        raise InvalidMachineId(f"Invalid machine id {machine_id}")
    machine = repo.prepare_machine(machine_id)
    snapshot = repo.get_sensor_snapshot(machine)
    feature = run_feature_extraction(snapshot)
    anomaly_score = run_anomaly_detection(snapshot)
    machine_status = run_diagnosis(anomaly_score, machine)
    report = run_root_cause_analysis(machine_status, feature, anomaly_score)
    return report
