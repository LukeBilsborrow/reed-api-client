# ReedJobs

ReedJobs is a Python library for interacting with the Reed API. It supports both sync and async operations, and provides full typing for easier integration. The library allows you to search for jobs, retrieve job details, and manage API responses with minimal effort.

This library covers only the Jobseeker API.

## Features

- Sync/Async support
- Fully typed for better development experience
- Response handling and object mapping for seamless data integration
- Complete coverage of the Jobseeker API
- Guaranteed access to raw API responses and requests

## Installation

To install ReedJobs, simply use pip:

```bash
pip install reedjobs
```

## Requirements

- Python 3.8+
- httpx==0.27.2
- pydantic==2.9.2

## Usage

To use the ReedJobs client, you need to have an API token from Reed. You can get one for free from [here](https://www.reed.co.uk/developers/Jobseeker)

### Example

```python
import os
from reedjobs import ReedApiClient, UseSync, UseAsync

api_token = os.getenv("REED_API_KEY")  
# Ensure your API key is set
client = ReedApiClient(api_token)

# Perform a job search
search_params = {
    "location_name": "London",
    "results_to_take": 10
}
search_results = client.job_search(params=search_params)

# search_results = client.job_search(params=search_params, sync_type=UseSync)

# search_results = await client.job_search(params=search_params, sync_type=UseAsync)


# Retrieve job details
job_id = search_results.jobs[0].jobId
job_details = client.job_detail(job_id)
```


## License

ReedJobs is licensed under the MIT License. See `LICENSE` for more information.
