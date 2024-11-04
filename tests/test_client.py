import pytest
import _model
import client
import utils
import dotenv
import os

pytest_plugins = ("pytest_asyncio",)
dotenv.load_dotenv()
TOKEN = os.getenv("REED_API_KEY")


def test_client_default_url():
    _client = client.ReedApiClient(TOKEN)
    assert _client.base_url == utils.get_base_url(protocol="https")


def test_client_custom_url():
    _client = client.ReedApiClient(TOKEN, override_full_url="https://example.com")
    assert _client.base_url == "https://example.com"


def test_job_search():
    _client = client.ReedApiClient(TOKEN)
    result = _client.job_search(locationName="London", resultsToTake=1, use_async=False)

    assert type(result) == _model.JobSearchResponse


@pytest.mark.asyncio
async def test_job_search_async():
    _client = client.ReedApiClient(TOKEN)
    result = _client.job_search(locationName="London", resultsToTake=1, use_async=True)
    result = await result
    print(result)

    assert type(result) == _model.JobSearchResponse


def test_job_detail():
    _client = client.ReedApiClient(TOKEN)
    sample_job_id = _client.job_search(locationName="London", resultsToTake=1, use_async=False).jobs[0].jobId
    result = _client.job_detail(sample_job_id, use_async=False)

    assert type(result) == _model.JobDetailResult and result.job is not None
