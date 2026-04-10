from domain.model import DiagnosisRecord, SensorSnapshot
from domain.ports import AnomalyDetector, FeatureExtractor


def run_anomaly_detection(
    machine_id: str,
    detector: AnomalyDetector,
    extractor: FeatureExtractor,
    snapshots: list[SensorSnapshot],
):
    features, time, feature_names, frames = extractor.run(snapshots)
    anomaly_score = detector.run(features)

    # Recordに変換
    records = []

    # 列名からセンサ名のprefixを除去
    for i in range(len(frames)):
        frames[i].columns = feature_names[i]

    for i in range(len(time)):
        mydict = {}
        # 行ごとにdictに変換してからRecordを作る
        for df, snapshot in zip(frames, snapshots):
            row = df.iloc[i]
            mydict[snapshot.sensor_channel.name] = row.to_dict()

        records.append(
            DiagnosisRecord(
                date=time[i],
                machine_id=machine_id,
                features=mydict,
                anomaly_score=float(anomaly_score[i]),
            )
        )

    return records
