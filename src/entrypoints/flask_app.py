from dataclasses import asdict

from flask import Flask, jsonify, request

import adapters.repository as repository
import service_layer.workflow as workflow

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
    report = workflow.diagnose(machine_id, repo)
    print(report.machine_status)
    print(report.next_action)
