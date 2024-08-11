#!pip install dlib
#!pip install opencv-contrib-python
import os

import dlib, cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects

# Agg 백엔드 설정
matplotlib.use('Agg')  

print(os.getcwd())

detector = dlib.get_frontal_face_detector()   # 얼굴 존재 여부 탐지 모델
print("::: 랜드마크 로딩")
sp = dlib.shape_predictor('utils/shape_predictor_68_face_landmarks.dat')  # 얼굴의 68개 랜드마크 찾기(2차원 값: x축, y 축)
print("::: 얼굴 인코딩 모델 로딩")
facerec = dlib.face_recognition_model_v1('utils/dlib_face_recognition_resnet_model_v1.dat') # 얼굴 인코딩 (128요소 벡터)변환


# 1. 함수 기능 
#      이미지 경로를 주면 비교가 잘되는 이미지를 리턴함
# 2. 파라메터 
#      imag_path ---- 이미지 경로
# 3. 리턴값 
#      img_gray ----- 비교용 파일 
#      img_rgb ------ RGB로만 변환만한 파일
def imageProcess(imag_path):
    img = cv2.imread(imag_path)
    
    if img is None:
        print(imag_path, " 이미지 파일을 찾을 수 없습니다.")
        return None, None

    ## 1. 비교용 파일 처리
    # 흑백변환
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 이미지 대비 조정
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    img_gray = clahe.apply(img_gray)
    # 알파, 베타 조정
    img_gray = cv2.convertScaleAbs(img_gray, alpha=2, beta=0) # 알파값이랑 베타값 조정

    ## 2. 출력용 파일 처리
    # 출력용 컬러파일
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # 컬러 처리

    return img_gray, img_rgb  # 비교용 파일 gray 와 , RGB로 변환만한 파일

# 1. 함수 기능 
#      주어진 이미지에서 얼굴찾기
# 2. 파라메터 
#      img ---- 얼굴이미지 , 이 프로젝트에서는 imageProcess를 통해서 처리된것을 쓴다
# 3. 리턴값 
#      rects ----- N개의, 얼굴사각형 좌표
#      shapes ---- N개의, 68개 점을 가진 dlib.full_object_detection 오브젝트
#      shpaes_np - N개의, 68개의 점을 가진 배열
def find_faces(img):
    dets = detector(img, 1)  # 얼굴 존재 여부 찾기

    # detector가 얼굴 못 찾은 경우
    if len(dets) == 0:
        return np.empty(0), np.empty(0), np.empty(0)

    # 얼굴 좌표와 랜드마크 찾기
    rects = []  # 얼굴좌표 변수 초기화  
    shapes = [] # 얼굴배열
    shapes_np = np.zeros((len(dets), 68, 2), dtype=int)  # 랜드마크 초기화 (2차원으로 구현되므로 68x2가 필요함)

    # 얼굴 찾은 개수 만큼 루프(좌표 입력: 좌우상하)
    for k, d in enumerate(dets): #k는 인덱스이고, d는 dlib.rectangle 객체
        #dlib.rectangle 객체에서 4개의 좌표를 뽑아 rect에 담음
        rect = ((d.left(), d.top()), (d.right(), d.bottom()))
        rects.append(rect)
        
        # shape 는 dlib.full_object_detection
        shape = sp(img, d)  # 얼굴 d 에서 68개 랜드마크 찾기
        
        # 68개의 점을 가진 shape(dlib.full_object_detection)을 넘파이 배열로 
        for i in range(0, 68):
            shapes_np[k][i] = (shape.part(i).x, shape.part(i).y)  # 68개 랜드마크를 2차원 값으로 표현

        shapes.append(shape)

    return rects,  shapes,  shapes_np

# 1. 함수 기능 
#      128개의 요소를 가진 벡터를 리턴함    
# 2. 파라메터 
#      img ---- rgb로 변환한 이미지
#      shapes - dlib.full_object_detection)
# 3. 리턴값 
#      np.array(face_descriptors) , 
def encode_faces(img, shapes):
    face_descriptors = []
    for shape in shapes:
        # 넘파이 배열
        face_descriptor = facerec.compute_face_descriptor(img, shape)   # 얼굴 인코딩 (128요소 벡터)변환
        face_descriptors.append(np.array(face_descriptor))

    # 인식한 얼굴 인코딩 값 저장
    return np.array(face_descriptors)



# 1. 함수 기능 
#      얼굴 이미지를 찾고 찾은 이미지에 박스로 그려서 저장함
# 2. 파라메터
#      event_image_path --- 사람들이 들어 있는 이미지
#      img_paths ---------- 찾고 싶은 사람"들"의 이미지 
#      result_image_path -- 찾은 얼굴을 마킹한 이미지
# 3. 리턴값 
#      return --- attendance 찾은 사람들의 학번을 리턴하는 배열

def findAll(event_image_path, img_paths, result_image_path):
    
    print("::: start findAll Function!!!")
    print("::: result file ====>",result_image_path)
    descs = {}
    attendance = [];
    for key, value in img_paths.items():
        descs[key]=None

    print("::: descs " , descs)

    for name, img_path in img_paths.items():
        img_gray, img_rgb = imageProcess(img_path)

        # RGB에서 얼굴 읽고 shape으로 받아오고, 이름에 맞게 저장
        rects, img_shapes, shapes_np = find_faces(img_gray) #이미지 그레이로 비교
        descs[name] = encode_faces(img_rgb, img_shapes)[0]
        # 중간 확인: 얼굴 검출 및 랜드마크 시각화
#        plt.imshow(img_rgb)

        ax = plt.gca()
        for rect in rects:
            rect_patch = patches.Rectangle(rect[0], rect[1][0] - rect[0][0], rect[1][1] - rect[0][1], linewidth=1, edgecolor='w', facecolor='none')
            ax.add_patch(rect_patch)
        for shape in shapes_np:
            for (x, y) in shape:
                circle = patches.Circle((x, y), radius=2, edgecolor='y', facecolor='b')
                ax.add_patch(circle)
        plt.title(name)
        plt.axis('off')
#        plt.show()                
#        np.save('./descs.npy', descs)

    img_gray, img_rgb = imageProcess(event_image_path)
    rects, shapes, _ = find_faces(img_gray) #이미지 그레이로 비교
    descriptors = encode_faces(img_rgb, shapes)
    fig, ax = plt.subplots(1, figsize=(20, 20))
##
    ax.imshow(img_rgb)

    for i, desc in enumerate(descriptors):
        found = False 
        
        # 받은 이미지(desc)의 개수 만큼 이터레이션을 돌린다 
        for name, saved_desc in descs.items(): 
            # 128개 요소의 벡터 사이의 유클리디안 거리 이용 , 거리가 가까워야함!
            dist = np.linalg.norm([desc] - saved_desc, axis=1)
            similarity = cosine_similarity(desc, saved_desc)
            
            print(dist, similarity);
            
            if dist < 0.6:    # threshold , 0.6보다 가까울때
#            if dist > 0.9:    # threshold , 0.6보다 가까울때
                found = True  # 찾았다!
                print(name, "찾았다!")
                attendance.append(name)
                
                text = ax.text(rects[i][0][0], rects[i][0][1], name,
                        color='b', fontsize=30, fontweight='bold')
                text.set_path_effects([path_effects.Stroke(linewidth=10, foreground='red'), path_effects.Normal()])
                rect = patches.Rectangle(rects[i][0],
                                    rects[i][1][1] - rects[i][0][1],
                                    rects[i][1][0] - rects[i][0][0],
                                    linewidth=2, edgecolor='w', facecolor='none')
                ax.add_patch(rect)
                break

        if not found:
            print('unknown')
            ax.text(rects[i][0][0], rects[i][0][1], 'unknown',
                    color='r', fontsize=20, fontweight='bold')
            rect = patches.Rectangle(rects[i][0],
                                rects[i][1][1] - rects[i][0][1],
                                rects[i][1][0] - rects[i][0][0],
                                linewidth=2, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

    plt.axis('off')
    plt.savefig(result_image_path)

    return attendance

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)