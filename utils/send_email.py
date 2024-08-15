import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from dotenv import load_dotenv

load_dotenv("/Users/ppillip/Projects/summerAI/.env")
# SMTP 정보 설정
smtp_info = {
     "smtp_server": os.getenv('SMTP_SERVER'),
     "smtp_user_id": os.getenv('SMTP_USER_ID'),
     "smtp_user_pw": os.getenv('SMTP_USER_PW'),
     "smtp_port": os.getenv('SMTP_PORT')
}

# smtp_info = {
#     "smtp_server": "smtp.naver.com",
#     "smtp_user_id": "ppillip@naver.com",
#     "smtp_user_pw": "Dnflemf7727!",
#     "smtp_port": 587
# }

print(smtp_info)




# 이메일 전송 함수
def send_email(smtp_info, msg):
    with smtplib.SMTP(smtp_info["smtp_server"], smtp_info["smtp_port"]) as server:
        server.starttls()  # TLS 보안 연결
        server.login(smtp_info["smtp_user_id"], smtp_info["smtp_user_pw"])  # 로그인
        # 로그인된 서버에 이메일 전송
        response = server.sendmail(msg['From'], msg['To'], msg.as_string())
        if not response:
            print('이메일을 성공적으로 보냈습니다.')
        else:
            print(response)

# MIME 멀티파트 메시지 생성 함수
def make_multimsg(msg_dict):
    multi = MIMEMultipart(_subtype='mixed')
    for key, value in msg_dict.items():
        if key == 'text':
            with open(value['filename'], encoding='utf-8') as fp:
                msg = MIMEText(fp.read(), _subtype=value['subtype'])
        elif key == 'image':
            with open(value['filename'], 'rb') as fp:
                msg = MIMEImage(fp.read(), _subtype=value['subtype'])
        elif key == 'audio':
            with open(value['filename'], 'rb') as fp:
                msg = MIMEAudio(fp.read(), _subtype=value['subtype'])
        else:
            with open(value['filename'], 'rb') as fp:
                msg = MIMEBase(value['maintype'], _subtype=value['subtype'])
                msg.set_payload(fp.read())
                encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(value['filename']))
        multi.attach(msg)
    return multi



def send_email_4_support(title, content, receiver, filename):    
    # 이메일 내용 설정
    # title = '미미모임 지원금주세효'
    # content = '미미 모임 지원금 주세효오오~'
    # receiver = 'ppillip@gmail.com'  #'myungkim@sogang.ac.kr'  #교수님 메일주소로 바꿀것
    # filename = '/Users/ppillip/Projects/summerAI/public/images/event/2024-02-05-check.jpeg'
    
    msg = MIMEText(_text = content, _charset = 'utf-8')

    # 첨부파일 지정
    msg_dict = {
        'image': {'maintype': 'image', 'subtype': 'jpeg', 'filename': filename},
    }

    # 첨부파일 추가
    multi = make_multimsg(msg_dict)  # msg_dict 안의 파일을 첨부함
    multi['Subject'] = title
    multi['From'] = smtp_info['smtp_user_id']  # 올바른 키 사용
    multi['To'] = receiver
    multi.attach(msg)

    # 이메일 전송
    send_email(smtp_info, multi)    
