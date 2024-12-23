import cv2
import mediapipe as mp
import numpy as np
import sys
import datetime
import json

#json檔
#path = 'output.txt'
path = 'output.json'
f = open(path, 'w')
data = {
    "take": False,
    "time": "2024-12-20 21:37:47.456536+08:00",
}
json.dump(data, f, indent = 2)
f.flush()
path_r = 'input.json'
counter = -1 #紀錄比對到第幾個element
med_counter = 0 #防止跳動造成誤判
Op = False
Op_w = False
time = []

# 初始化 Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 設定吃藥時間
def set_time_med(path):
    file = open(path, 'r')
    fr = json.load(file)
    global time
    global counter
    counter = -1
    time = []
    row1 = []
    row2 = []
    try:
        for i in range(len(fr["times"])):
            if i % 2 == 0:
                row1.append(fr["times"][i])
            else:
                row2.append(fr["times"][i])
        row1.append(999)
        row2.append(999)
        time.append(row1)
        time.append(row2)
        #print(time)
    except Exception as e:
        print(f"Error0: {e}")
    file.close()

# 偵測拿藥的姿勢
def get_medicine_pose(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4] #4號點

    index_mcp = hand_landmarks.landmark[5] #5號點
    index_pip = hand_landmarks.landmark[6] #6號點
    index_dip = hand_landmarks.landmark[7] #7號點
    index_tip = hand_landmarks.landmark[8] #8號點

    middle_pip = hand_landmarks.landmark[10] #10號點
    middle_dip = hand_landmarks.landmark[11] #11號點
    middle_tip = hand_landmarks.landmark[12] #12號點

    ring_mcp = hand_landmarks.landmark[13] #13號點
    ring_pip = hand_landmarks.landmark[14] #14號點
    ring_dip = hand_landmarks.landmark[15] #15號點
    ring_tip = hand_landmarks.landmark[16] #16號點

    pinky_mcp = hand_landmarks.landmark[17] #17號點
    pinky_pip = hand_landmarks.landmark[18] #18號點
    pinky_dip = hand_landmarks.landmark[19] #19號點
    pinky_tip = hand_landmarks.landmark[20] #20號點

    # 確認拇指和其他手指之間的距離與角度
    thumb_index_dist = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2) ** 0.5

    index_mp_dist = ((index_mcp.x - index_pip.x)**2 + (index_mcp.y - index_pip.y)**2) ** 0.5 #distance between 5 and 6
    index_pd_dist = ((index_pip.x - index_dip.x)**2 + (index_pip.y - index_dip.y)**2) ** 0.5 #distance between 6 and 7
    index_dt_dist = ((index_dip.x - index_tip.x)**2 + (index_dip.y - index_tip.y)**2) ** 0.5 #distance between 7 and 8
    index_md_dist = ((index_mcp.x - index_dip.x)**2 + (index_mcp.y - index_dip.y)**2) ** 0.5 #distance between 5 and 7
    index_pt_dist = ((index_pip.x - index_tip.x)**2 + (index_pip.y - index_tip.y)**2) ** 0.5 #distance between 6 and 8

    middle_pd_dist = ((middle_pip.x - middle_dip.x)**2 + (middle_pip.y - middle_dip.y)**2) ** 0.5
    #middle_dtip_dist = ((middle_dip.x - middle_tip.x)**2 + (middle_dip.y - middle_tip.y)**2) ** 0.5

    ring_mp_dist = ((ring_mcp.x - ring_pip.x)**2 + (ring_mcp.y - ring_pip.y)**2) ** 0.5 #distance between 13 and 14
    ring_pd_dist = ((ring_pip.x - ring_dip.x)**2 + (ring_pip.y - ring_dip.y)**2) ** 0.5 #distance between 14 and 15
    ring_dt_dist = ((ring_dip.x - ring_tip.x)**2 + (ring_dip.y - ring_tip.y)**2) ** 0.5 #distance between 15 and 16
    ring_md_dist = ((ring_mcp.x - ring_dip.x)**2 + (ring_mcp.y - ring_dip.y)**2) ** 0.5 #distance between 13 and 15
    ring_pt_dist = ((ring_pip.x - ring_tip.x)**2 + (ring_pip.y - ring_tip.y)**2) ** 0.5 #distance between 14 and 16

    pinky_mp_dist = ((pinky_mcp.x - pinky_pip.x)**2 + (pinky_mcp.y - pinky_pip.y)**2) ** 0.5 #distance between 17 and 18
    pinky_pd_dist = ((pinky_pip.x - pinky_dip.x)**2 + (pinky_pip.y - pinky_dip.y)**2) ** 0.5 #distance between 18 and 19
    pinky_dt_dist = ((pinky_dip.x - pinky_tip.x)**2 + (pinky_dip.y - pinky_tip.y)**2) ** 0.5 #distance between 19 and 20
    pinky_md_dist = ((pinky_mcp.x - pinky_dip.x)**2 + (pinky_mcp.y - pinky_dip.y)**2) ** 0.5 #distance between 17 and 19
    pinky_pt_dist = ((pinky_pip.x - pinky_tip.x)**2 + (pinky_pip.y - pinky_tip.y)**2) ** 0.5 #distance between 18 and 20

    index_angle0 = (index_mp_dist ** 2 + index_pd_dist ** 2 - index_md_dist ** 2) / (2 * index_mp_dist * index_pd_dist) #angle 6
    index_angle1 = (index_pd_dist ** 2 + index_dt_dist ** 2 - index_pt_dist ** 2) / (2 * index_pd_dist * index_dt_dist) #angle 7
    ring_angle0 = (ring_mp_dist ** 2 + ring_pd_dist ** 2 - ring_md_dist ** 2) / (2 * ring_mp_dist * ring_pd_dist) #angle 14
    ring_angle1 = (ring_pd_dist ** 2 + ring_dt_dist ** 2 - ring_pt_dist ** 2) / (2 * ring_pd_dist * ring_dt_dist) #angle 15
    pinky_angle0 = (pinky_mp_dist ** 2 + pinky_pd_dist ** 2 - pinky_md_dist ** 2) / (2 * pinky_mp_dist * pinky_pd_dist) #angle 18
    pinky_angle1 = (pinky_pd_dist ** 2 + pinky_dt_dist ** 2 - pinky_pt_dist ** 2) / (2 * pinky_pd_dist * pinky_dt_dist) #angle 19

    direction = index_tip.y > index_mcp.y
    
    get_medicine = thumb_index_dist < 0.1 and index_angle0 < 0 and index_angle1 < 0 and middle_pd_dist < 0.1 and ring_pd_dist < 0.1 and \
                    pinky_pd_dist < 0.1 and ring_angle0 > 0 and ring_angle1 < 0 and pinky_angle0 > 0 and pinky_angle1 < 0 and direction

    return get_medicine

set_time_med(path_r)

# 開啟攝影機
cap = cv2.VideoCapture(0)
#cv2.namedWindow('Hidden Window', cv2.WINDOW_NORMAL)
#cv2.setWindowProperty('Hidden Window', cv2.WND_PROP_VISIBLE, 0)
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        # 更新時間
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
        sec = now.second
        #print("now = " + str(now))

        if sec == 0:
            counter = 0
            med_counter = 0
            Op_w = False

        if counter == -1:
            counter = 0
            Op_w = False
            try:
                for i in range(len(time[0])):
                    if  sec > time[1][i]:
                        counter += 1
            except Exception as e:
                print(f"Error1: {e}")

        # 記錄(未)服藥時間
        '''
        if sec > time[1][counter] and counter + 1 < len(time[0]):
            if Op and med_counter >= 5:
                lines = 'Get Medicine ' + str(now) + '\n'
                f.writelines(lines)
                Op = False
            elif ~Op:
                lines = 'Did Not Get Medicine ' + str(now) + '\n'
                f.writelines(lines)
            counter += 1
            med_counter = 0
        '''
        # 記錄未服藥時間
        if sec > time[1][counter]:
            if med_counter < 5:
                try:
                    f = open(path, 'r')
                    data = json.load(f)
                    f = open(path, 'w')
                except Exception as e:
                    print(f"Error2: {e}")
                data["take"] = False
                data["time"] = str(now)
                json.dump(data, f, indent = 2)
                f.flush()
            counter += 1
            med_counter = 0
            Op_w = False

        # 記錄服藥時間
        if med_counter >= 5 and not Op_w:
            try:
                f = open(path, 'r')
                data = json.load(f)
                f = open(path, 'w')
            except Exception as e:
                print(f"Error2: {e}")
            data["take"] = True
            data["time"] = str(now)
            json.dump(data, f, indent = 2)
            f.flush()
            Op = False
            Op_w = True

        ret, frame = cap.read()
        if not ret:
            sys.exit('ERROR: Unable to read from webcam. Please verify your webcam settings.')

        # 轉換影像到 RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)

        # 轉換回 BGR 顯示
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 偵測手部位置
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 繪製手部結構
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 檢查是否符合條件
                if get_medicine_pose(hand_landmarks):
                    cv2.putText(image, "Get Medicine!", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    if Op:
                        med_counter += 1
                    Op = True
                else:
                    cv2.putText(image, "Not Get Medicine", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    if med_counter <= 4:
                        med_counter = 0
        else:
            cv2.putText(image, "Hands Not Detected!", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            if med_counter <= 4:
                med_counter = 0
                    
        cv2.putText(image, "Time:" + str(sec), (470, 470),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
        
        if sec < time[0][counter] and counter + 1 < len(time[0]):
            Op = False

        # 顯示影像
        cv2.imshow('MediaPipe Hand Detection', image)

        if cv2.waitKey(5) & 0xFF == 114:  # 按下r鍵(小寫)修改時間 #這個先不要理他
            set_time_med(path_r)
            lines = 'Time Modified ' + str(now) + '\n'
            f.writelines(lines)
            Op = False
        elif cv2.waitKey(5) & 0xFF == 27:  # 按下 ESC 鍵退出
            break

f.close()
cap.release()
cv2.destroyAllWindows()
