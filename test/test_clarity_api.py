import os
import sys

import pytest
from conftest import reason

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    import clarity_api
except ImportError:
    skip = True
else:
    skip = False


reason = "do not run on MacOS or windows OR dependency is not installed OR " + reason


clarity_url = "https://www.clarity.ms"
# get token from env vars
token = os.environ.get("CLARITY_TOKEN", default="NA")
# create client
client = clarity_api.Api(url=clarity_url, token=token, verify=False)


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_get_data():
    numOfDays = 3
    dimension1 = "OS"
    data = client.get_data_export(number_of_days=numOfDays, dimension_1=dimension1)
    assert data.numOfDays == numOfDays
    assert data.dimension1 == dimension1


if __name__ == "__main__":
    test_get_data()
