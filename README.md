# Microsoft Clarity API

![PyPI - Version](https://img.shields.io/pypi/v/clarity-api)
![PyPI - Downloads](https://img.shields.io/pypi/dd/clarity-api)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/clarity-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/clarity-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/clarity-api)
![PyPI - License](https://img.shields.io/pypi/l/clarity-api)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/clarity-api)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/clarity-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/clarity-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/clarity-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/clarity-api)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/clarity-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/clarity-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/clarity-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/clarity-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/clarity-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/clarity-api)

*Version: 0.0.2*

**Microsoft Clarity Data Export API**

This Python library allows you to work with the dashboard data. The data can be structured over a specified date range 
and can break down insights by up to three dimensions.

Find out more about the [Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api)

This repository is actively maintained - Contributions are welcome!

<details>
  <summary><b>Getting Started:</b></summary>

### Prerequisites
- An active Microsoft Clarity account. [Learn how to sign up for Clarity](https://clarity.microsoft.com).
- An API access token generated by the project's admin from the settings page.
- Python3.8+

### Obtaining Access Tokens
**Note**: Only project admins can manage access tokens.

1. Go to your Clarity project. Select `Settings` -> `Data Export` -> `Generate new API token`.
2. Provide a descriptive name for the token for easy identification.

## Parameters
- `numOfDays`: (1, 2, or 3) The number of days for the data export since the API call, relating to the last 24, 48, or 72 hours, respectively.
- `dimension1`: The first dimension to break down insights.
- `dimension2`: The second dimension to break down insights.
- `dimension3`: The third dimension to break down insights.

#### Dimension Options:
- Browser
- Device
- Country
- OS
- Source
- Medium
- Campaign
- Channel
- URL

</details>

<details>
  <summary><b>Usage:</b></summary>

```python
#!/usr/bin/python
# coding: utf-8
import clarity_api

# Use token generated from the steps above
token = "<TOKEN>"
url = "https://www.clarity.ms"
client = clarity_api.Api(url=url, token=token)

data = client.get_data_export(number_of_days=2, dimension_1="OS", dimension_2="Channel")
print("Pydantic Object:", data)
print("Raw Request Output:", data.raw_output)
print("JSON Request Output:", data.json_output)
print("Pydantic Object Model Dump:", data.model_dump())
print("Request Status Code:", data.status_code)
print("Request Error:", data.error)
```

</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

Install Python Package

```bash
python -m pip install clarity-api
```

</details>

<details>
  <summary><b>Tests:</b></summary>

pre-commit check
```bash
pre-commit run --all-files
```

pytest
```bash
pytest ./test/test_clarity_models.py
```
</details>


<details>
  <summary><b>Repository Owners:</b></summary>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)
</details>
