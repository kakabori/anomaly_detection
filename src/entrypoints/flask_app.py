from dataclasses import asdict

from flask import Flask, jsonify, request

import adapters.repository as repository
import service_layer.workflow as workflow
from domain.model import DiagnosisReport, DiagnosisUnavailable

app = Flask(__name__)


@app.route("/diagnose", methods=["POST"])
def diagnose_endpoint():
    repo = repository.MyDatabaseRepository()
    machine_id = request.json["machineid"]
    try:
        report = workflow.diagnose(machine_id, repo)
    except workflow.InvalidMachineId as e:
        return jsonify({"message": str(e)}), 400

    return jsonify(asdict(report)), 201


if __name__ == "__main__":
    repo = repository.MyDatabaseRepository()
    machine_id = "001"
    result = workflow.diagnose(machine_id, repo)
    print(f"Diagnosing machine {machine_id}...")
    if isinstance(result, DiagnosisReport):
        print(result.machine_status)
        print(result.next_action)
    elif isinstance(result, DiagnosisUnavailable):
        print(result.reason)
        print(result.evidence)

    machine_id = "002"
    result = workflow.diagnose(machine_id, repo)
    print(f"Diagnosing machine {machine_id}...")
    if isinstance(result, DiagnosisReport):
        print(result.machine_status)
        print(result.next_action)
    elif isinstance(result, DiagnosisUnavailable):
        print(result.reason)
        print(result.evidence)
