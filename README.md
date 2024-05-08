# resume-helper

### deploy modal service on self pc
when deploy serverless service on modal, the code need running on local env.
#### windows (powershell)
$env:GOOGLE_APPLICATION_CREDENTIALS='D:\xxx.json'
$env:OPENAI_API_KEY='sk-xxx'
$env:MISTRAL_API_KEY='...'
python3 -m modal deploy main.py