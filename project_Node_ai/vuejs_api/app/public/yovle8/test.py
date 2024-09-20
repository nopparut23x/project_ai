import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # pretrained YOLOv8n model
# model = YOLO('cards.pt')  # pretrained YOLOv8n model
cap = cv2.VideoCapture(0)
count = 0
track = {}
while True:
  ok, frame = cap.read()
  if not ok:
    break
  h, w, _ = frame.shape  # (480, 640, 3)
  cx = int(w / 2)
#  results = model(frame, conf=0.7, classes=[20, 70], verbose=False)  # return a list of Results objects
  results = model.track(frame, conf=0.5, verbose=False, classes=[0], persist=True)  # return a list of Results objects
  # persist  ต้องเป็น true เพื่อนับ track
  result = results[0]
  img = result.plot()
  # cv2.imshow('camera', frame)
  cv2.line(img, (cx, 0), (cx, h), (0, 0, 255), 2)
  cv2.putText(img, "Count={0}".format(count), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)
  cv2.imshow('detect', img)
  for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    for idx in range(len(result.boxes.cls)):
      classId = int(result.boxes.cls[idx])
      box = result.boxes.xyxy[idx]
      score = float(result.boxes.conf[idx])
      trackId = None
      # print(result.boxes)
      if result.boxes.id is None:
        print("sorry")
        continue
      trackId = str(int(result.boxes.id[idx]))
      if not trackId in track:
        track[trackId] = { "left": int(box[0]), "right": int(box[2]) }
      else:
        x_cur_left = int(box[0])
        x_cur_right = int(box[2])
        x_prev = track[trackId]
        track[trackId] = {"left": x_cur_left, "right": x_cur_right}
        if x_prev["left"] < cx and x_cur_left >= cx:
          count += 1
        if x_prev["right"] > cx and x_cur_right <= cx:
          count -= 1

      # print('classId=', classId, 'box=', box, 'score=', score)
  
  key = cv2.waitKey(1)
  if key & 0xff == 27:
    break

cap.release()
cv2.destroyAllWindows()