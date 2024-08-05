from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from utils.find_users import findAll
import os
import uuid

load_dotenv()

app_path = os.getcwd()

print("::: 어플리케이션 패스 :",app_path)

#환경 변수 불러오기
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
uri = f"mongodb+srv://{db_username}:{db_password}@{db_host}/?retryWrites=true&w=majority&appName=Cluster0"

print(f"::: 디비URI [{uri}]")

client = MongoClient(uri)
print("::: 디비연결 성공")
mimi = client[db_name]
memberCollection = mimi["member"]
eventCollection = mimi["event"]

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>우리는 알바 B조 입니다.</h1>"+"Hello, Flask!"

# 사용자 리스트 입니다
@app.route('/api/member/list', methods=['GET'])
def get_member():
    data = []
    try:
        print("데이터 조회 시작")
        results = memberCollection.find({})
        for document in results:
            data.append(document)
                
    except Exception as e:
        raise Exception(
            "다음과 같은 에러가 발생하였습니다.: ", e)

    return jsonify(data)

# 사용자 추가
@app.route('/api/member/add', methods=['POST'])
def set_members():
    data = {"result":"ok"}
    print("여기는 들어오나요")
    test = request.form["test"]
    print(test)
    
    return jsonify(data)

#모임 리스트
@app.route('/api/event/list', methods=['GET'])
def get_events():
    data = []
    try:
        print("데이터 조회 시작")
        results = eventCollection.find({})
        for document in results:
            data.append(document)
                
    except Exception as e:
        raise Exception(
            "다음과 같은 에러가 발생하였습니다.: ", e)

    return jsonify(data)

#모임 요청
@app.route('/api/event/add', methods=['POST'])
def set_event():
    data = []
    
    #1. 미미 회원 리스트 조회 - 몽고디비 
    #2. 미미 회원 파일 읽어오기 - 파일 
    #3. 이벤트 이미지에서 사용자 찾기
    #4. 메일 전송 하기
    
    return jsonify(data)


# 랜덤 이미지 파일명 생성 함수
def generate_random_image_name(app_path, extension='.png'):
    random_filename = f"{uuid.uuid4()}{extension}"
    return os.path.join(app_path, 'work', random_filename)

@app.route('/api/findUser', methods=['GET'])
def findUser():
    data = {"result":"ok"}
    print("::: findUser")
    
    # 랜덤 이미지 파일명 생성
    random_result_image_path = generate_random_image_name(app_path)
    
    #찾아봅시다
    findAll(event_image_path=f"{app_path}/work/kingsman.png", 
            img_paths={
                        "Samuel" : f"{app_path}/work/사무엘잭슨.png",
                        "Egerton": f"{app_path}/work/테런에저턴.png",
                        "Colin"  : f"{app_path}/work/콜린퍼스.png"},
            result_image_path=random_result_image_path)
    
    # 생성된 랜덤 파일명 출력
    print(f"생성된 결과 이미지 경로: {random_result_image_path}")
    
    #1. 미미 회원 리스트 조회 - 몽고디비 
    #2. 미미 회원 파일 읽어오기 - 파일 
    #3. 이벤트 이미지에서 사용자 찾기
    #4. 메일 전송 하기
    #5. 테스트
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

