from __future__ import annotations
from typing import AsyncIterable
# built-in modules
import time, random, string, os, json, uuid, datetime
from datetime import timezone

# cloud service modules
import fastapi_poe as fp

# third-party tool modules
import requests
from pdfminer.high_level import extract_text
import modal
from modal import Image, Stub, asgi_app
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from google.cloud import translate_v2 as translate
from google.cloud import storage
from google.cloud import vision 
from google.oauth2.service_account import Credentials
from firebase_admin import credentials, firestore, initialize_app

GOOGLE_SERVICE_ACCOUNT_JSON_ENV = "SERVICE_ACCOUNT_JSON"
LOCAL_SERVICE_ACCOUNT_JSON_PATH = "GOOGLE_APPLICATION_CREDENTIALS"
DEFAULT_STORAGE_BUCKET = "poebot"
MODAL_SERVICE_NAME = 'resume-helper'
DEBUG_MODE = True if os.environ.get('DEBUG', None) else False


def read_gcp_cred():
    gcp_cred = None
    fs_cred = None
    ACCOUNT_JSON_CONTENT = os.environ.get(GOOGLE_SERVICE_ACCOUNT_JSON_ENV, None)
    if not ACCOUNT_JSON_CONTENT:
        file_path = os.environ.get(LOCAL_SERVICE_ACCOUNT_JSON_PATH)
        if DEBUG_MODE:
            print(f"Service Account JSON Path: {file_path}")
        gcp_cred = Credentials.from_service_account_file(file_path)
        fs_cred = credentials.Certificate(file_path)
        return gcp_cred, fs_cred
    service_account_info = json.loads(ACCOUNT_JSON_CONTENT)
    if DEBUG_MODE:
        print(f"Service Account JSON: {ACCOUNT_JSON_CONTENT}")
        print(f"Service Account Info: {service_account_info}")
    gcp_cred = Credentials.from_service_account_info(service_account_info)
    fs_cred = credentials.Certificate(service_account_info)
    return gcp_cred, fs_cred

gcp_cred, fs_cred = read_gcp_cred()
if gcp_cred is not None:
    print(f"Google Cloud Credentials: {gcp_cred}")

# 机器人所使用的一些API服务密钥是通过 modal 平台管理的，而其环境变量是用户定义的

staging_app = initialize_app(credential=fs_cred, name='myfs')
db = firestore.client(app=staging_app)

def create_user_info(user_id, resume_register=None, voice_enabled=None, language=None):
    now = datetime.datetime.now(tz=timezone.utc)
    print(f"Creating user info for user {user_id}")
    user_ref = db.collection('user_info').document(user_id)
    update_data = {}
    if resume_register is not None:
        update_data['resume_register'] = resume_register
    if voice_enabled is not None:
        update_data['voice_enabled'] = voice_enabled
    if language:
        update_data['language'] = language
    if update_data:
        update_data['created_at'] = now
        update_data['updated_at'] = now
        print("set user info")
        print("update_data: ", update_data)
        rst = user_ref.set(update_data)
        return rst
    return None 

def update_user_info(user_id, resume_register=None, voice_enabled=None, language=None):
    now = datetime.datetime.now(tz=timezone.utc)
    user_ref = db.collection('user_info').document(user_id)
    update_data = {}
    if resume_register:
        update_data['resume_register'] = resume_register
    if voice_enabled:
        update_data['voice_enabled'] = voice_enabled
    if language:
        update_data['language'] = language
    if update_data:
        update_data['updated_at'] = now
        rst = user_ref.update(update_data)
        return rst
    return None 

def get_user_info(user_id):
    user_ref = db.collection('user_info').document(user_id)
    user_info = user_ref.get()
    return user_info.to_dict()


def create_basic_resume(user_id, resume_raw_content, resume_llm_processed_content ,resume_tags):
    if not user_id or user_id == '':
        return None
    
    doc_id = str(uuid.uuid4())
    resume_ref = db.collection('basic_resume').document(doc_id)
    timestamp_now = datetime.datetime.now(tz=timezone.utc)
    update_data = {}
    if resume_raw_content:
        update_data['resume_raw_content'] = resume_raw_content
    if resume_llm_processed_content:
        update_data['resume_llm_processed_content'] = resume_llm_processed_content
    if resume_tags:
        update_data['resume_tags'] = resume_tags
    if update_data:
        update_data['user_id'] = user_id
        update_data['created_at'] = timestamp_now
        update_data['updated_at'] = timestamp_now
        rst = resume_ref.set(update_data)
        return rst
    return None

# 暂时还不支持基本简历的更新
def update_basic_resume(user_id, resume_id, resume_content, resume_tags):
    resume_ref = db.collection('basic_resume').document(resume_id)
    update_data = {'user_id': user_id, 'updated_at': datetime.datetime.now(tz=timezone.utc)}
    if resume_content:
        update_data['resume_content'] = resume_content
    if resume_tags:
        update_data['resume_tags'] = resume_tags
    rst = resume_ref.update(update_data)
    return rst

def get_basic_resume(user_id, resume_id=None):
    col = db.collection('basic_resume')
    if resume_id:
        resume_ref = col.document(resume_id)
        resume = resume_ref.get()
        if resume.exists and resume.to_dict().get('user_id') == user_id:
            return resume.to_dict()
    # 当使用 firestore 的索引时，需要先在 GCP 控制台进行创建
    query = col.where('user_id','==', user_id).order_by('created_at').limit(1)
    results = query.stream()
    for result in results:
        return result.to_dict()
    return None

def create_job_description(user_id, text_content, source, tags):
    doc_id = str(uuid.uuid4())
    jd_ref = db.collection('job_description').document(doc_id)
    timestamp_now = datetime.datetime.now(tz=timezone.utc)
    update_data = {}
    if text_content:
        update_data['text_content'] = text_content
    if source:
        update_data['source'] = source
    if tags:
        update_data['tags'] = tags
    if update_data:
        update_data['user_id'] = user_id
        update_data['created_at'] = timestamp_now
        update_data['updated_at'] = timestamp_now
        rst = jd_ref.set(update_data)
        return doc_id, rst
    return "", None

def create_compare_entry(resume_id, jd_id, compare_result, user_id=None):
    doc_id = str(uuid.uuid4())
    compare_ref = db.collection('compare_result').document(doc_id)
    timestamp_now = datetime.datetime.now(tz=timezone.utc)
    update_data = {}
    update_data['resume_id'] = resume_id
    update_data['jd_id'] = jd_id
    update_data['compare_result'] = compare_result
    if user_id:
        update_data['user_id'] = user_id
    update_data['created_at'] = timestamp_now
    update_data['updated_at'] = timestamp_now
    rst = compare_ref.set(update_data)
    return doc_id, rst


# 项目声明部分
# todo: 应用名称、依赖等内容需要改为配置化并进行版本管理
# 将需要的依赖在这里声明，modal 等 serverless 平台为你构建服务需要的运行环境镜像
REQUIREMENTS = ["fastapi-poe==0.0.36", "requests==2.31.0", "google-cloud-storage",
                "langchain-openai", "langchain","google-cloud-translate",
                "google-cloud-vision","pdfminer.six", "firebase-admin"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
# 这里是对 app 的命名， modal 上的监控面板通过该名称区分不同的API服务
stub = Stub(MODAL_SERVICE_NAME)
# modal 还允许声明挂载的卷，但是如果使用云服务，在需要固定化数据时也应考虑保存至云存储上，方便使用其他 IaC 工具进行迁移

# utils 
def generate_random_file_name():
    current_time = time.strftime("%Y%m%d")
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    file_name = f"{current_time}_{random_string}.txt"
    return file_name

# 文件输入处理逻辑
def process_plain_text_file(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return "read plain text file failed"
    # 模拟对文本的处理，这里可以是任何逻辑，如果是计算密集型，甚至可以考虑异步下发任务进行处理
    content = response.content.decode('utf-8')
    content = content.replace("", "")
    temp_file_name = generate_random_file_name()
    with open(f"{temp_file_name}", "wb") as f:
        f.write(content.encode())
    os.remove(temp_file_name)
    return content

# langchain parser 实现案例
class ResumeCompare(BaseModel):
    Reqs: str = Field(description="精简的岗位要求的技能")
    Pros: str = Field(description="简历拥有者过往经验相较岗位的优势")
    Cons: str = Field(description="简历拥有者过往经验相较岗位的劣势")
    Suggestions: str = Field(description="对于简历拥有者而言应该如何准备该岗位的面试")

parser = JsonOutputParser(pydantic_object=ResumeCompare)
compare_template="""
我给你发送某人的简历内容与某岗位描述.
{format_instructions}
###简历内容:{resume}
###职位描述:{jd}
"""
prompt = PromptTemplate(
    template=compare_template,
    input_variables=["resume", "jd"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

model = ChatOpenAI(temperature=0.2)
compare_chain = prompt | model | parser

def compare_resume_and_jd(resume_content, jd_content):
    rst = compare_chain.invoke({"resume": resume_content, "jd": jd_content})
    return rst

# 文本输入处理逻辑
# 调用 llm 对于法语句子产生特定的处理
french_process_prompt = """
请使用中文逐字逐词给我讲解下面的法语内容，如果有重要的语法点或惯用语也请说明，最后仿造两个类似的法语句子。{target}"""

resume_summary_prompt = """
以下内容是一个简历的文本内容，请忽略与个人优势、介绍、工作经历、项目经历以外无关的部分，比如电话号码和邮箱，然后梳理这个简历，不要遗漏任何技能点或者工作内容。{target}"""

def openai_invoke(template: str, fill_content: str):
    llm = ChatOpenAI(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system","You are french language teacher."),
        ("user", "{input}")
    ])
    chain = prompt | llm
    response = chain.invoke({"input":template.format(target=fill_content)})
    return response.content

# 调用 google translate 对于英文句子产生特定的处理
def sentence_translate_process(text: str):
    translate_client = translate.Client(credentials=gcp_cred)
    translation = translate_client.translate(text, target_language="zh-CN")
    return translation["translatedText"]

def upload_file_to_gcp_storage(url, suffix, bucket_name=DEFAULT_STORAGE_BUCKET):
    file_name = download_files(url, suffix, 0)
    if not file_name:
        return None 
    sc = storage.Client(credentials=gcp_cred)
    bucket = sc.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    os.remove(file_name)
    return blob.public_url
    
# take care of max_size param, unit is 256 not 1024
def download_files(url: str, suffix: str, max_size: int = 1024 * 256 * 4 * 5):
    print(f"Downloading file from {url}")
    response = requests.head(url)
    total_length = int(response.headers.get('content-length', 0))
    if max_size > 0 and total_length > max_size:
        print(f"file size is too large, max size is 1MB, file size is {total_length}")
        return None

    # 文件大小合适，开始下载
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # 使用uuid生成随机文件名
        random_filename = f"{uuid.uuid4()}{suffix}"
        with open(random_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded and saved as {random_filename}")
        return random_filename
    else:
        print("Failed to download the file.")
        return None

def process_pdf_file(url: str):
    file_path = download_files(url,'.pdf')
    if file_path is None:
        print(f"Failed to download the file for url {url}")
        return None
    text = extract_text(file_path)
    if text is not None:
        print("process_pdf_file content length", len(text))
    content = '\n'.join([line for line in text.splitlines() if line.strip()])
    os.remove(file_path)
    return content

def detect_text_from_url(url):
    client = vision.ImageAnnotatorClient(credentials=gcp_cred)
    image = vision.Image()
    image.source.image_uri = url
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    return None

# 临时的文字意图处理，后续需要考虑使用特定的模型、api服务或规则引擎解决
def plain_text_intent(text: str):
    # 创建简历
    if text.lower().startswith("[resume]"):
        return 1
    # 创建岗位描述
    if text.lower().startswith("[jd]"):
        return 2
    if text.lower().startswith("[test]"):
        return 9
    # 其他内容
    return 0


def compare_jd(user_id, jd_content, jd_source_type):
    user_resume = get_basic_resume(user_id)
    if not user_resume:
        return False, f"未找到用户简历信息 {user_id}"
    user_resume = user_resume.get('resume_raw_content')
    compare_result = compare_resume_and_jd(user_resume, jd_content)

    if not compare_result or compare_result == "":
        return False, "简历与岗位描述对比失败"
    jd_id, _ = create_job_description(user_id, jd_content, jd_source_type, ["jd"])
    compare_id, _ = create_compare_entry(user_id, jd_id, compare_result, user_id)
    return True, f"简历与岗位描述对比结果已生成，结果ID: {compare_id} ， 内容:{compare_result}，更多相关信息也会后台自动生成"

def check_user_status(user_id):
    user_basic_info_exists = False
    user_basic_resume_exists = False
    
    print(f"User ID: {user_id}")
    user_info = get_user_info(user_id)
    print(f"User Info: {user_info}")
    if user_info:
        user_basic_info_exists = True
        user_basic_resume_exists = user_info.get('resume_register')
        print(f"User {user_id} has registered user info")    
    else:
        print(f"User {user_id} has not registered user info")
        rst = create_user_info(user_id, resume_register=False, voice_enabled=False, language='en')
        if not rst:
            print(f"Failed to create user info for user {user_id}")
    return user_basic_info_exists, user_basic_resume_exists


class MyBot(fp.PoeBot):
    # feedback content sample
    # Feedback request with context json {"version":"1.1","type":"report_feedback","message_id":"m-000000xy92mwd91u86o5mn906klq5977","user_id":"u-000000xy92lqwx4nhina157rjs6s75re","conversation_id":"c-000000xy92mwd91sbt5dy11hu5vlqu4o","feedback_type":"dislike"}
    # Feedback request json {"version":"1.1","type":"report_feedback","message_id":"m-000000xy92mwd91u86o5mn906klq5977","user_id":"u-000000xy92lqwx4nhina157rjs6s75re","conversation_id":"c-000000xy92mwd91sbt5dy11hu5vlqu4o","feedback_type":"dislike"}

    #async def on_feedback_with_context(self, feedback_request: fp.ReportFeedbackRequest, context: fp.RequestContext) -> None:
    #    print("Feedback request with context json {}".format(feedback_request.model_dump_json()))
    #    return await super().on_feedback_with_context(feedback_request, context)
    
    async def on_feedback(self, feedback_request: fp.ReportFeedbackRequest) -> None:
        json_content = feedback_request.model_dump_json()
        print(f"Feedback request json {json_content}")
        return await super().on_feedback(feedback_request)

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        user_id = str(request.user_id)
        # 用户信息是否存在，用户基础简历是否存在
        _, user_basic_resume_exists = check_user_status(user_id)        
        is_file_captured = False

        # request.query 是一个数组，允许获取用户输入的上下文
        last_query = request.query[-1]
        # 处理用户的附件输入
        if len(last_query.attachments) > 0:
            is_file_captured = True
            for attachment in last_query.attachments:
                print(f"Attachment Content-Type: {attachment.content_type}")
                match attachment.content_type:
                    case "text/html":
                        storage_blob_url = upload_file_to_gcp_storage(attachment.url, '.html')
                        if not storage_blob_url:
                            yield fp.PartialResponse(text="获取 html 文件失败")
                            continue
                        else:
                            yield fp.PartialResponse(text=f"已上传文件到GCP存储 {storage_blob_url}")
                            continue
                    case "text/plain":
                        file_content = process_plain_text_file(attachment.url)
                        if len(file_content) < 50:
                            yield fp.PartialResponse(text=f"文本内容过短{file_content}")
                            continue
                        if not user_basic_resume_exists:
                            llm_processed_content = openai_invoke(resume_summary_prompt, file_content)
                            create_basic_resume(user_id, file_content, llm_processed_content, ["resume"])
                            update_user_info(user_id, resume_register=True)
                            yield fp.PartialResponse(text=f"已创建简历，简历内容也通过LLM进行了梳理{llm_processed_content}")
                            continue
                        else:
                            # compare_succ 失败时，可以进行埋点
                            _, compare_rst = compare_jd(user_id, file_content, "text/plain")
                            yield fp.PartialResponse(text=compare_rst)
                    case "application/pdf":
                        # yield fp.PartialResponse(text=process_pdf_file(attachment.url))
                        
                        pdf_file_content = process_pdf_file(attachment.url)
                        pdf_full_content = "".join(pdf_file_content)

                        # todo 这里需要校验 pdf_full_content 是否是简历内容
                        if len(pdf_full_content) < 50:
                            yield fp.PartialResponse(text="No enough resume content detected from the pdf file")
                            continue
                        if not user_basic_resume_exists:
                            llm_processed_content = openai_invoke(resume_summary_prompt, pdf_full_content)
                            create_basic_resume(user_id, pdf_full_content, llm_processed_content, ["resume"])
                            # todo 这里存在事务问题，如果创建简历成功，但是更新用户信息失败，会导致用户信息和简历不一致
                            update_user_info(user_id, resume_register=True)
                            yield fp.PartialResponse(text=f"Resume content has been registered, and processed by LLM model {llm_processed_content}")
                            continue
                        yield fp.PartialResponse(text='resume exists, not need to process again')
                        continue
                    case "image/jpeg":
                        image_content = detect_text_from_url(attachment.url)
                        if len(image_content) < 20:
                            yield fp.PartialResponse(text=f"No enough text detected from the image {image_content}")
                            continue
                        if not user_basic_resume_exists:
                            yield fp.PartialResponse(text="你还没有创建简历，请先使用 文本[RESUME]上传简历或pdf方式上传个人简历")
                            continue
                        else:
                            # 以下部分内容出现多次，后续需封装成函数
                            _, compare_rst = compare_jd(user_id, image_content, "image/jpeg")
                            yield fp.PartialResponse(text=compare_rst)
                            continue
                    case _:
                        yield fp.PartialResponse(text=f"Attachment type: {attachment.content_type} is not supported right now")  

        # 处理用户的文本输入
        last_message = last_query.content
        user_intent = plain_text_intent(last_message)
        print(f"User request_id {request.message_id} Intent: {user_intent}")

        if user_intent == 9:
            yield fp.PartialResponse(text="# Title one \n## Title Two \n### Title Three \n**Bold Character**")
            return

        # 用户还没有创建简历
        if user_intent == 0:
            # 只传递了文件，没有传递文本
            if is_file_captured:
                return
            yield fp.PartialResponse(text=f"未识别命令，echoserver返回 {last_message}")
            return
        else:
            if len(last_message) < 50:
                yield fp.PartialResponse(text="无论是录入简历还是岗位描述，内容都太少了，需要更多的信息（dev:文本判断逻辑还未上线）")
                return

        if not user_basic_resume_exists:
            match user_intent:
                case 1:
                    # 通过文本创建简历
                    llm_processed_content = openai_invoke(resume_summary_prompt, pdf_full_content)
                    create_basic_resume(user_id, pdf_full_content, llm_processed_content, ["resume"])
                    # todo 这里存在事务问题，如果创建简历成功，但是更新用户信息失败，会导致用户信息和简历不一致
                    update_user_info(user_id, resume_register=True)
                    yield fp.PartialResponse(text=f"已创建简历，简历内容也通过LLM进行了梳理 {llm_processed_content}")
                case 2:
                    yield fp.PartialResponse(text="你还没有创建简历，请先使用 文本[RESUME]上传简历或pdf方式上传个人简历")
                    return 
        else:
            match user_intent:
                case 1:
                    yield fp.PartialResponse(text="你已经创建了简历，目前暂不支持创建多份简历或删除简历，请联系管理员")
                case 2:
                    _, compare_rst = compare_jd(user_id, last_message, "text")
                    yield fp.PartialResponse(text=compare_rst)

    
    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        print("Settings request: ", setting.model_dump())
        return fp.SettingsResponse(allow_attachments=True, server_bot_dependencies={"GPT-3.5-Turbo": 1})

# 全局注入业务需要使用的 secrets，这里 secret 的名称就是你在 modal 等 serverless 平台上注册的 secret 名称
@stub.function(secrets=[modal.Secret.from_name("my-googlecloud-secret"), modal.Secret.from_name("my-openai-secret")], image=image)
@asgi_app()
def fastapi_app():
    bot = MyBot()
    # todo: allow_without_key should be set to False in production
    app = fp.make_app(bot, allow_without_key=True)
    return app