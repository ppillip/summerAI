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
sp = dlib.shape_predictor('./work/shape_predictor_68_face_landmarks.dat')  # 얼굴의 68개 랜드마크 찾기(2차원 값: x축, y 축)
print("::: 얼굴 인코딩 모델 로딩")
facerec = dlib.face_recognition_model_v1('./work/dlib_face_recognition_resnet_model_v1.dat') # 얼굴 인코딩 (128요소 벡터)변환



# 이미지 경로를 주면 비교가 잘되는 img_gray (비교용)와 img_rgb(출력용) 두개를 리턴함
def imageProcess(imag_path):
    img = cv2.imread(imag_path)
    print(imag_path)
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

    return img_gray, img_rgb


def find_faces(img):
    dets = detector(img, 1)  # 얼굴 존재 여부 찾기

    # 얼굴 못 찾은 경우
    if len(dets) == 0:
        return np.empty(0), np.empty(0), np.empty(0)

    # 얼굴 좌표와 랜드마크 찾기
    rects, shapes = [], [] #얼굴좌표, 랜드마크 초기화
    shapes_np = np.zeros((len(dets), 68, 2), dtype=int)  # 랜드마크는 2차원으로 구현되므로 68x2가 필요함.

    # 얼굴 찾은 개수 만큼 루프(좌표 입력: 좌우상하)
    for k, d in enumerate(dets):
        rect = ((d.left(), d.top()), (d.right(), d.bottom()))
        rects.append(rect)
        shape = sp(img, d)  # 얼굴에서 68개 랜드마크 찾기

     # convert dlib shape to numpy array
        for i in range(0, 68):
            shapes_np[k][i] = (shape.part(i).x, shape.part(i).y)  # 68개 랜드마크를 2차원 값으로 표현
        shapes.append(shape)

    return rects, shapes, shapes_np


def encode_faces(img, shapes):
    face_descriptors = []
    for shape in shapes:
        face_descriptor = facerec.compute_face_descriptor(img, shape)   # 얼굴 인코딩 (128요소 벡터)변환
        face_descriptors.append(np.array(face_descriptor))

    # 인식한 얼굴 인코딩 값 저장
    return np.array(face_descriptors)




def findAll(event_image_path, img_paths, result_image_path):
    
    print("::: start findAll Function!!!")
    print("::: result file ====>",result_image_path)
    descs = {}       

    for key, value in img_paths.items():
        descs[key]=None

    print("::: descs " , descs)

    for name, img_path in img_paths.items():
        #img_bgr = cv2.imread(img_path)
        #img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        img_gray, img_rgb = imageProcess(img_path)

        print(name)
        # RGB에서 얼굴 읽고 shape으로 받아오고, 이름에 맞게 저장
        rects, img_shapes, shapes_np = find_faces(img_gray) #이미지 그레이로 비교

        descs[name] = encode_faces(img_rgb, img_shapes)[0]

        # 중간 확인: 얼굴 검출 및 랜드마크 시각화
##
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
##
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
        for name, saved_desc in descs.items():
            dist = np.linalg.norm([desc] - saved_desc, axis=1)   # 128개 요소의 벡터 사이의 유클리디안 거리 이용

            if dist < 0.6:    # threshold
                found = True
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

    return True