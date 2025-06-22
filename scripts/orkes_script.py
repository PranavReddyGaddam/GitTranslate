# To set up the project, install the dependencies, and run the application, follow these steps:
#
# 1. Create a Conda environment with the latest version of Python:
#    conda create --name myenv python
#
# 2. Activate the environment:
#    conda activate myenv
#
# 3. Install the necessary dependencies:
#    pip install conductor-python
#
# 4. Run the Python script (replace script.py with your actual script name):
#    python script.py
import json
from functools import cache, lru_cache
from typing import List

from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.worker.worker_task import worker_task
import os
from scripts.fetch_repo_data import GitHubRepoFetcher  # Import the class

# Load environment variables from .env file
from dotenv import load_dotenv

from scripts.text2speech import get_audio_file

load_dotenv()

os.environ['CONDUCTOR_SERVER_URL'] = os.getenv('CONDUCTOR_SERVER_URL', 'https://developer.orkescloud.com/api')
os.environ['CONDUCTOR_AUTH_KEY'] = os.getenv('CONDUCTOR_AUTH_KEY')
os.environ['CONDUCTOR_AUTH_SECRET'] = os.getenv('CONDUCTOR_AUTH_SECRET')


@worker_task(task_definition_name='GithubDetails')
def task(github_url: str = None, lang: str = None, ):
    """
    Orkes worker task to fetch GitHub repository data.
    Takes a GitHub repo URL as input from the task.
    """
    github_repo_url = github_url
    print("processing task with github_repo_url:", github_repo_url, "language:", lang)
    if not github_repo_url:
        return {
            'status': 'FAILED',
            'error_message': 'github_repo_url not provided in task input'
        }

    try:
        fetcher = GitHubRepoFetcher()
        repo_data = fetcher.fetch_repo_data(github_repo_url)
        return {
            'status': 'COMPLETED',
            'data': repo_data
        }
    except Exception as e:
        return {
            'status': 'FAILED',
            'error_message': str(e)
        }


@worker_task(task_definition_name='text2speech')
def text2speech(summary: str = None, lang: str = None, ):
    """
    Orkes worker task to fetch GitHub repository data.
    Takes a GitHub repo URL as input from the task.
    """
    print('processing task with summary:', summary, "language:", lang)
    try:
        summary = json.loads(summary)
        print('Summary loaded:')
        s3link = get_audio_file(summary, lang)
    except Exception as e:
        print("Error processing summary:", e)
        return "Sorry I could not parse the summary. Please try again."

    print("processing task with summary:", summary)
    return s3link


api_config = Configuration()

task_handler = TaskHandler(configuration=api_config)
task_handler.start_processes() # starts polling for work
# task_handler.stop_processes() # stops polling for work