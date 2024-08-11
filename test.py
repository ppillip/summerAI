
from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt

# 사용자의 얼굴 이미지를 로드합니다.
target_img_path = "/Users/ppillip/Projects/summerAI/public/images/member/M00002.jpg"
target_img = cv2.imread(target_img_path)

# 단체 사진을 로드합니다.
group_img_path = "/Users/ppillip/Projects/summerAI/public/images/event/2024-08-20.jpeg"
group_img = cv2.imread(group_img_path)

# OpenCV를 사용하여 단체 사진에서 얼굴을 감지합니다.
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
gray_img = cv2.cvtColor(group_img, cv2.COLOR_BGR2GRAY)
faces = detector.detectMultiScale(gray_img, scaleFactor=1.3, minNeighbors=5)

# 감지된 얼굴 중에서 사용자의 얼굴과 가장 일치하는 얼굴을 찾습니다.
best_match = None
best_score = float("inf")
for (x, y, w, h) in faces:
    face_img = group_img[y:y+h, x:x+w]
    try:
        result = DeepFace.verify(
                            face_img, 
                            target_img, 
                            model_name='Facenet'
                            )
        if result["verified"]:
            score = result["distance"]
            if score < best_score:
                best_match = (x, y, w, h)
                best_score = score
    except Exception as e:
        print(f"Error processing face: {e}")
        continue

# 일치하는 얼굴을 표시합니다.
if best_match:
    (x, y, w, h) = best_match
    cv2.rectangle(group_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    plt.imshow(cv2.cvtColor(group_img, cv2.COLOR_BGR2RGB))
    plt.title("Best Match Found")
    plt.show()
else:
    print("No matching face found.")
