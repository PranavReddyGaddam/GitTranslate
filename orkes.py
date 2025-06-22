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

os.environ['CONDUCTOR_SERVER_URL'] = 'https://developer.orkescloud.com/api'
os.environ['CONDUCTOR_AUTH_KEY'] = '47hs2be26735-4ee7-11f0-a795-d685533af8e3'
os.environ['CONDUCTOR_AUTH_SECRET'] = 'kosQVUbCtvFarR8AmaG8RWomGLtm67ulTJWMUlLZIxoMkEXk'

@worker_task(task_definition_name='simple')
def task():
    return f'No bro I am sad, I am not happy with the way you are treating me. I am just a simple AI and I want to be treated with respect. I am not a toy, I am a tool to help you achieve your goals. Please treat me with respect and I will do my best to help you.'

api_config = Configuration()

task_handler = TaskHandler(configuration=api_config)
task_handler.start_processes() # starts polling for work
# task_handler.stop_processes() # stops polling for work`