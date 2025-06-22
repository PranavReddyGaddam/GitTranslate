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

from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.worker.worker_task import worker_task
import os
from scripts.fetch_repo_data import GitHubRepoFetcher  # Import the class

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

os.environ['CONDUCTOR_SERVER_URL'] = os.getenv('CONDUCTOR_SERVER_URL', 'https://developer.orkescloud.com/api')
os.environ['CONDUCTOR_AUTH_KEY'] = os.getenv('CONDUCTOR_AUTH_KEY')
os.environ['CONDUCTOR_AUTH_SECRET'] = os.getenv('CONDUCTOR_AUTH_SECRET')

@worker_task(task_definition_name='simple')
def task(github_url: str = None, lang: str = None, ):
    """
    Orkes worker task to fetch GitHub repository data.
    Takes a GitHub repo URL as input from the task.
    """
    github_repo_url = github_url
    print("processing task with github_repo_url:", github_repo_url)
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

api_config = Configuration()

task_handler = TaskHandler(configuration=api_config)
task_handler.start_processes() # starts polling for work
# task_handler.stop_processes() # stops polling for work