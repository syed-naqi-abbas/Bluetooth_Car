import serial
import cv2
import mediapipe as mp

bluetooth = serial.Serial("COM8", 9600, timeout=1)  
print("Connected to Arduino via Bluetooth!")
def send_command(command):
    bluetooth.write(command.encode())

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Start Video Capture
cap = cv2.VideoCapture(0)


while cap.isOpened():
    command = "S"
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for a natural mirror effect
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip and base coordinates
            index_tip = hand_landmarks.landmark[8]   # Tip of the index finger
            index_base = hand_landmarks.landmark[5]  # Base of the index finger

            h, w, _ = frame.shape
            tip_x, tip_y = int(index_tip.x * w), int(index_tip.y * h)
            base_x, base_y = int(index_base.x * w), int(index_base.y * h)

            # Determine direction
            direction = ""
            if abs(tip_x - base_x) > abs(tip_y - base_y):  # More horizontal movement
                if tip_x > base_x:
                    direction = "RIGHT"
                    command = "R"
                else:
                    direction = "LEFT"
                    command = "L"
            else:  # More vertical movement
                if tip_y < base_y:
                    direction = "UP"
                    command = "F"
                else:
                    direction = "DOWN"
                    command = "B"

            # Display direction on screen
            cv2.putText(frame, f"Direction: {direction}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Finger Direction Detection", frame)

    send_command(command)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
