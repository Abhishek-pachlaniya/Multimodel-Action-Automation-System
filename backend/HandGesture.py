import cv2
import mediapipe as mp
import pyautogui
import math
import time


# ------------------ Mediapipe & Screen Setup ------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
click_times = []
freeze_cursor = False
prev_x, prev_y = 0, 0
prev_screen_x, prev_screen_y = 0, 0
scroll_mode = False
pinch_active = False
last_click_time = 0
DOUBLE_CLICK_DELAY = 0.8
screenshot_cooldown = 4
last_screenshot_time = 0
click_text = ""
click_text_time = 0
TEXT_DURATION = 0.5

# Initializing hands object
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Get Screen Dimensions
screen_w, screen_h = pyautogui.size()
pyautogui.FAILSAFE = False
print("\n hand mouse control .")

# ------------------ Camera Setup ------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# ------------------ Main Loop ------------------
while True:
    ret, frame = cap.read()

    if not ret:
        print("Can't receive frame")
        break

    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame for hand detection
    result = hands.process(rgb_frame)

    # If hand detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # Draw the landmarks
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # --- Extract Finger Tips ---
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]

            # --- Detect full palm open ---
            index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
            middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
            ring_up = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
            pinky_up = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

            full_palm = index_up and middle_up and ring_up and pinky_up

            # --- Check which fingers are up ---
            fingers = [
                1 if hand_landmarks.landmark[tip].y <
                hand_landmarks.landmark[tip - 2].y else 0
                for tip in [8, 12, 16, 20]
            ]

            # -------- Stable Click Logic --------
            dist = math.hypot(
                thumb_tip.x - index_tip.x,
                thumb_tip.y - index_tip.y
            )
            current_time = time.time()

            if dist < 0.06 and not pinch_active:
                pinch_active = True

            elif dist >= 0.06 and pinch_active:
                pinch_active = False

                if current_time - last_click_time < DOUBLE_CLICK_DELAY:
                    pyautogui.doubleClick()
                    click_text = "Double Click"
                    click_text_time = time.time()
                    last_click_time = 0
                else:
                    pyautogui.click()
                    click_text = "Single Click"
                    click_text_time = time.time()
                    last_click_time = current_time

            # --- Screenshot (all fingers folded) ---
            if sum(fingers) == 0:
                current_time = time.time()
                if current_time - last_screenshot_time > screenshot_cooldown:
                    pyautogui.screenshot(f"screenshot_{int(current_time)}.png")
                    click_text = "Screenshot Taken"
                    click_text_time = time.time()
                    last_screenshot_time = current_time

            # --- Check index & middle finger up ---
            index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
            middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y

            index_middle_dist = math.hypot(
                hand_landmarks.landmark[8].x -
                hand_landmarks.landmark[12].x,
                hand_landmarks.landmark[8].y -
                hand_landmarks.landmark[12].y
            )

            # --- Move cursor ---
            if not freeze_cursor and not full_palm and index_up and middle_up and index_middle_dist > 0.05:

                curr_x = index_tip.x
                curr_y = index_tip.y

                dx = curr_x - prev_x
                dy = curr_y - prev_y

                if abs(dx) < 0.002:
                    dx = 0
                if abs(dy) < 0.002:
                    dy = 0

                speed = math.hypot(dx, dy)

                acceleration = 2 + min(speed * 10, 5)

                target_x = prev_screen_x + dx * screen_w * acceleration
                target_y = prev_screen_y + dy * screen_h * acceleration

                smooth_factor = 0.80

                screen_x = int(
                    prev_screen_x * smooth_factor +
                    target_x * (1 - smooth_factor)
                )
                screen_y = int(
                    prev_screen_y * smooth_factor +
                    target_y * (1 - smooth_factor)
                )

                screen_x = max(0, min(screen_w - 1, screen_x))
                screen_y = max(0, min(screen_h - 1, screen_y))

                pyautogui.moveTo(screen_x, screen_y, duration=0)

                prev_x, prev_y = curr_x, curr_y
                prev_screen_x, prev_screen_y = screen_x, screen_y

            # --- Scroll Mode ---
            if full_palm:

                center_zone_top = 0.45
                center_zone_bottom = 0.55

                if index_tip.y < center_zone_top:
                    intensity = (center_zone_top - index_tip.y)
                    scroll_amount = int(300 * intensity)
                    pyautogui.scroll(scroll_amount)

                elif index_tip.y > center_zone_bottom:
                    intensity = (index_tip.y - center_zone_bottom)
                    scroll_amount = int(300 * intensity)
                    pyautogui.scroll(-scroll_amount)

    # ---- Persistent Text Display ----
    if time.time() - click_text_time < TEXT_DURATION:
        cv2.putText(frame, click_text,
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 0), 2)
    cv2.imshow("Hand Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ------------------ Cleanup ------------------
cap.release()
cv2.destroyAllWindows()