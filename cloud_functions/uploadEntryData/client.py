import requests, json, os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# 设置 Google 服务账号
credentials = service_account.Credentials.from_service_account_file('/Users/wangrui/llmapi-385907-8a7ad32fecb8.json')

scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])

auth_req = Request()
scoped_credentials.refresh(auth_req)

headers = {
    'Authorization': f'Bearer {scoped_credentials.token}',
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

# 示例数据和函数 URL
data_single = {'name': 'example', 'value': 42}
function_url = os.getenv('FUNCTION_URL')

if __name__ == '__main__':
    print(upload_data(function_url, data_single, 'feedback'))