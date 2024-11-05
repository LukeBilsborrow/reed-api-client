import asyncio
import os

import dotenv
import pytest

import _model
import client
import utils

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
    result = _client.job_search(sync_type=client.UseSync,
                                params={
                                    "location_name": "London",
                                    "results_to_take": 1
                                })

    assert isinstance(result, _model.JobSearchResponse)


@pytest.mark.asyncio
async def test_job_search_async():
    _client = client.ReedApiClient(TOKEN)
    result = _client.job_search(sync_type=client.UseAsync,
                                params={
                                    "location_name": "London",
                                    "results_to_take": 1
                                })
    result = await result
    print(result)

    assert isinstance(result, _model.JobSearchResponse)


def test_job_detail():
    _client = client.ReedApiClient(TOKEN)
    sample_job_id = _client.job_search(sync_type=client.UseSync,
                                       params={
                                           "location_name": "London",
                                           "results_to_take": 1
                                       }).jobs[0].jobId
    result = _client.job_detail(sample_job_id, sync_type=client.UseSync)

    assert isinstance(result, _model.JobDetailResponse) and result.job is not None


@pytest.mark.asyncio
async def test_job_detail_async():
    _client = client.ReedApiClient(TOKEN)

    sample_job = await _client.job_search(
        params={
            "location_name": "London",
            "results_to_take": 1
        },
        sync_type=client.UseAsync,
    )
    sample_job_id = sample_job.jobs[0].jobId
    result = _client.job_detail(sample_job_id, sync_type=client.UseAsync)
    result = await result
    print(result)

    assert isinstance(result, _model.JobDetailResponse) and result.job is not None


@pytest.mark.asyncio
async def test_job_search_async_is_non_blocking():
    _client = client.ReedApiClient(TOKEN)

    # Start two async job searches simultaneously
    task1 = _client.job_search(sync_type=client.UseAsync,
                               params={
                                   "location_name": "London",
                                   "results_to_take": 1
                               })
    task2 = _client.job_search(sync_type=client.UseAsync,
                               params={
                                   "location_name": "Bristol",
                                   "results_to_take": 1
                               })

    # Wait for both tasks to complete
    result1, result2 = await asyncio.gather(task1, task2)

    # Assert both results are of the correct type
    assert isinstance(result1, _model.JobSearchResponse)
    assert isinstance(result2, _model.JobSearchResponse)


def test_job_search_recognises_location():
    _client = client.ReedApiClient(TOKEN)
    result = _client.job_search(sync_type=client.UseSync,
                                params={
                                    "location_name": "London",
                                    "results_to_take": 1
                                })
    second_result = _client.job_search(sync_type=client.UseSync,
                                       params={
                                           "location_name": "Bristol",
                                           "results_to_take": 1
                                       })

    assert result.jobs[0].jobId != second_result.jobs[0].jobId
