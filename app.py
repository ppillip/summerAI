from flask import Flask, jsonify,send_from_directory, request
from utils.collections import memberCollection, eventCollection
from utils.send_email import send_email_4_support
from dotenv import load_dotenv
from utils.find_users import findAll
import os
import uuid


app_path = os.getcwd()
print("::: 어플리케이션 패스 :::",app_path)
app = Flask(__name__, static_folder='public', static_url_path='/')

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
        
        filepath = os.path.join("public/images/member", filename)
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
        
        filepath = os.path.join("public/images/event", filename)
        file.save(filepath)
        
        new_filepath = "public/images/event/" + new_filename

        #1. 미미 회원 리스트 조회
        print("데이터 조회 시작")
        results = memberCollection.find({})

        img_paths = {};
        for doc in results:
            img_paths[doc["_id"]] = "public/images/member/"+doc["photo"]

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
        
        print("이거를.... ",  attendance)
        
        title = f'{event_id} 미미모임 지원금 요청드립니다.'
        content = '미미 모임 지원금 주세효오오~'
        receiver = 'ppillip@gmail.com'  #'myungkim@sogang.ac.kr'  #교수님 메일주소로 바꿀것
        filename = new_filepath #'/Users/ppillip/Projects/summerAI/public/images/event/2024-02-05-check.jpeg'
        send_email_4_support(title,content,receiver,filename)
    
    return jsonify(attendance)

# 랜덤 이미지 파일명 생성 함수
def generate_random_image_name(app_path, extension='.png'):
    random_filename = f"{uuid.uuid4()}{extension}"
    return os.path.join(app_path, 'work', random_filename)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9000)
