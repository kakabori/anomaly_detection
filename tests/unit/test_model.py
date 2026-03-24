from datetime import datetime, timedelta

import pytest

from domain.model import SensorSnapshot


def test_length_mismatch_message():
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [i for i in range(n_samples)],
        "temperature": [i - 5 for i in range(n_samples + 1)],
    }
    with pytest.raises(ValueError, match="長さが time と一致しません"):
        SensorSnapshot(time=time, data=data)
