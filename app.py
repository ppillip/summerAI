from flask import Flask, jsonify, render_template, request
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from utils.find_users import findAll
import os
import uuid

load_dotenv()

app_path = os.getcwd()

print("::: 어플리케이션 패스 :::",app_path)

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

app = Flask(__name__, template_folder='templates')

# 메인페이지 라우팅 설정
@app.route('/')
def home():
    return render_template('home.html')

# html template 라우팅 설정
# 브라우저 /view/requestSupport
# 실제파일 /templates/requestSupport.html 
@app.route('/view/<name>')
def view(name):
    return render_template(f'{name}.html')

# 사용자 리스트 입니다
@app.route('/api/member/list', methods=['GET','POST'])
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
# 파일 저장 경로 설정


# 사용자 추가
@app.route('/api/member/add', methods=['GET','POST'])
def set_members():
    if 'student_photo' not in request.files:
        return jsonify({"error": "파일이 없어요"}), 400
    
    file = request.files['student_photo']
    if file.filename == '':
        return jsonify({"error": "선택된 파일이 없습니다"}), 400

    if 'student_id' not in request.form or request.form['student_id']=="":
        return jsonify({"error": "학번은 필수입니다."}), 400
    
    if 'student_name' not in request.form or request.form['student_name']=="":
        return jsonify({"error": "이름은 필수입니다"}), 400
    
    if file:
        #파일 확장자만 가져와서 ID로 바꾼다.
        _, file_extension = os.path.splitext(file.filename)
        filename = request.form['student_id'] + file_extension
        print("::::::",filename)
        
        filepath = os.path.join("static/images/member", filename)
        file.save(filepath)
        
        student_id = request.form['student_id']
        name = request.form['student_name']
        
        # MongoDB에 데이터 저장
        member_data = {
            "_id": student_id,
            "name": name,
            "photo": filename
        }

        # Upsert 작업 수행 , 있으면 업데이트 없으면 인서트
        memberCollection.update_one(
            {"_id": student_id},  # 검색 조건
            {"$set": member_data},  # 업데이트할 데이터
            upsert=True  # upsert 옵션
        )
        
        return jsonify({"message": "미미 회원이 정상적으로 등록(변경) 되었어요"}), 201

#모임 리스트
@app.route('/api/event/list', methods=['GET','POST'])
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
    if 'event_id' not in request.form or request.form['event_id']=="":
        return jsonify({"error": "모임일자는 필수, '9999-12-31' 형식 "}), 400

    if 'desc' not in request.form or request.form['desc']=="":
        return jsonify({"error": "모임 설명을 넣어주세요"}), 400

    if 'image' not in request.files:
        return jsonify({"error": "파일이 없어요"}), 400

    event_id = request.form['event_id']
    desc = request.form['desc']        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "선택된 파일이 없습니다"}), 400
 
    if file:
        #파일 확장자만 가져와서 ID로 바꾼다.
        _, file_extension = os.path.splitext(file.filename)
        filename = event_id + file_extension
        new_filename = event_id + "-check" + file_extension
        print("::::::",filename, new_filename)
        
        filepath = os.path.join("static/images/event", filename)
        file.save(filepath)
        
        new_filepath = "static/images/event/" + new_filename

        #1. 미미 회원 리스트 조회
        print("데이터 조회 시작")
        results = memberCollection.find({})

        img_paths = {};
        for doc in results:
            img_paths[doc["_id"]] = "static/images/member/"+doc["photo"]

        print( filepath, img_paths, new_filepath )
         #2. 이미지 비교해서 찾기
        attendance = findAll(event_image_path=filepath, img_paths=img_paths, result_image_path=new_filepath)    
        
        
        # MongoDB에 데이터 저장
        event_data = {
            "_id": event_id,
            "desc": desc,
            "image": filename,            
            "image_check" : new_filename, 
            "attendance" : attendance
        }

        # Upsert 작업 수행 , 있으면 업데이트 없으면 인서트
        eventCollection.update_one(
            {"_id": event_id},  # 검색 조건
            {"$set": event_data},  # 업데이트할 데이터
            upsert=True  # upsert 옵션
        )        
    
    #4. 메일 전송 하기

    
    return jsonify(data)

# 랜덤 이미지 파일명 생성 함수
def generate_random_image_name(app_path, extension='.png'):
    random_filename = f"{uuid.uuid4()}{extension}"
    return os.path.join(app_path, 'work', random_filename)

@app.route('/api/findUser', methods=['GET','POST'])
def findUser():
    data = {"result":"ok"}
    print("::: findUser")
    
    # 랜덤 이미지 파일명 생성
    random_result_image_path = generate_random_image_name(app_path)
    
    #찾아봅시다
    attendance = findAll(event_image_path=f"{app_path}/work/kingsman.png", 
            img_paths={
                        "Samuel" : f"{app_path}/work/사무엘잭슨.png",
                        "Egerton": f"{app_path}/work/테런에저턴.png",
                        "Colin"  : f"{app_path}/work/콜린퍼스.png"
                      },
            result_image_path=random_result_image_path)
    
    # 생성된 랜덤 파일명 출력
    print( f"생성된 결과 이미지 경로: {random_result_image_path}" )
    
    #1. 미미 회원 리스트 조회 - 몽고디비 
    #2. 미미 회원 파일 읽어오기 - 파일 
    #3. 이벤트 이미지에서 사용자 찾기
    #4. 메일 전송 하기
    #5. 테스트
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=9000)
