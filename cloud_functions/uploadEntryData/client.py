import requests, json, os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

TOKEN_CONTENT = ""
# 设置 Google 服务账号
USE_GCP_AJ = False
if USE_GCP_AJ:
    credentials = service_account.Credentials.from_service_account_file('/Users/wangrui/llmapi-385907-8a7ad32fecb8.json')
    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
    auth_req = Request()
    scoped_credentials.refresh(auth_req)
    TOKEN_CONTENT = scoped_credentials.token


headers = {
    'Authorization': f'Bearer {TOKEN_CONTENT}',
    'Content-Type': 'application/json'
}
print(headers)

def upload_data(url, data, collection_name=None):
    payload = {
        'collection_name': collection_name,
        'payload': data
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.text

def get_metadata(url):
    response = requests.get(url, headers=headers)
    return response.text

# 示例数据和函数 URL
data_single = {"entry_type":"intent", "user_query":"I want to record a resume of mine", "intent":"create_resume"}
function_url = os.getenv('FUNCTION_URL')

if __name__ == '__main__':
    if not function_url:
        print('请设置 FUNCTION_URL 环境变量')
    if os.environ.get('GET_REQUEST', None):
        print(get_metadata(function_url))
    else:
        print(upload_data(function_url, data_single, 'feedback'))