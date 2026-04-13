from dataclasses import asdict

from flask import Flask, jsonify, request

import adapters.repository as repository
import service_layer.workflow as workflow
from domain.model import DiagnosisReport, DiagnosisUnavailable

app = Flask(__name__)


@app.route("/diagnose", methods=["POST"])
def diagnose_endpoint():
    machine_id = request.json["machineid"]
    sensor_repo = repository.SensorDBRepository()
    record_repo = repository.RecordDBRepository()

    try:
        result = workflow.diagnose(machine_id, sensor_repo, record_repo)
    except workflow.InvalidMachineId as e:
        return jsonify({"error": str(e)}), 400

    if isinstance(result, DiagnosisReport):
        return jsonify({"status": "OK", "result": asdict(result)}), 200
    elif isinstance(result, DiagnosisUnavailable):
        return jsonify({"status": "FAIL", "error": asdict(result)}), 200
    else:
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    sensor_repo = repository.SensorDBRepository()
    record_repo = repository.RecordDBRepository()
    machine_id = "001"
    result = workflow.diagnose(machine_id, sensor_repo, record_repo)
    print(f"Diagnosing machine {machine_id}...")
    if isinstance(result, DiagnosisReport):
        print(result.machine_status)
        for key, value in result.anomalous_features:
            print(f"{key}: {value}")
    elif isinstance(result, DiagnosisUnavailable):
        print(result.reason)
        print(result.evidence)

    machine_id = "002"
    result = workflow.diagnose(machine_id, sensor_repo, record_repo)
    print(f"Diagnosing machine {machine_id}...")
    if isinstance(result, DiagnosisReport):
        print(result.machine_status)
        for key, value in result.anomalous_features:
            print(f"{key}: {value}")
    elif isinstance(result, DiagnosisUnavailable):
        print(result.reason)
        print(result.evidence)
