from time import sleep

import requests
import json

# url = "https://developer.orkescloud.com/api/token"
# headers = {
#     "Content-Type": "application/json"
# }
# data = {
#     "keyId": "47hs2be26735-4ee7-11f0-a795-d685533af8e3",
#     "keySecret": "kosQVUbCtvFarR8AmaG8RWomGLtm67ulTJWMUlLZIxoMkEXk"
# }
#
# response = requests.post(url, headers=headers, data=json.dumps(data))
#
# print(response.status_code)
# token = response.json()['token']

token = 'eyJhbGciOiJIUzUxMiJ9.eyJvcmtlc19rZXkiOiI0N2hzMmJlMjY3MzUtNGVlNy0xMWYwLWE3OTUtZDY4NTUzM2FmOGUzIiwib3JrZXNfY29uZHVjdG9yX3Rva2VuIjp0cnVlLCJzdWIiOiJhcHA6ZjM0ZjYyNmItZDFhZC00YWYxLThjZDEtODQwNDQ0ZmRhNGQwIiwiaWF0IjoxNzUwNTQyMzc1fQ.J7IqR03wDl7SOfd2DSsdxKMNXk0FPMkDiPGUEHLbYJbsbgj3IQIR5pkISO75R3Ixx4R5YuWI76SL803yKSUwtw'

import requests
import json

url = "https://developer.orkescloud.com/api/workflow"
headers = {
    "x-authorization": f"{token}",
    "Content-Type": "application/json"
}
data = {
    "name": "GitTranslate_v3",
    "version": 1,
    "input": {
        "github_url": "https://github.com/streamlit/streamlit",
        "lang": "english"
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))
workflow_id = response.text

url = f"https://developer.orkescloud.com/api/workflow/{workflow_id}?summarize=true"

headers = {
    "x-authorization": f"{token}",
    "Content-Type": "application/json"
}

while True:
    response = requests.get(url, headers=headers)

    # print(response.status_code)
    # print(response.json())
    status = response.json()["status"]
    if status == "COMPLETED":
        print("Workflow completed successfully.")
        print("Output:", response.json()['output']['data'])
        break
    elif status == "FAILED":
        print("Workflow failed.")
        break
    else:
        print(f"Workflow is still running... {workflow_id}")
