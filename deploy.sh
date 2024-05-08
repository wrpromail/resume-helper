#!/bin/bash

# 如果任何环境变量为空,则打印提示信息
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ] || [ -z "$OPENAI_API_KEY" ] || [ -z "$MISTRAL_API_KEY" ]; then
  echo "Please set the required environment variables and try again."
  exit 1
else
  python3 -m modal deploy main.py
fi