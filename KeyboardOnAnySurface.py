from time import sleep
import cv2
import numpy as np

# Constants
CANNY_THRESHOLD1 = 100
CANNY_THRESHOLD2 = 200

# Define skin color range in HSV for finger detection
LOWER_SKIN = np.array([0, 40, 70], dtype=np.uint8)
UPPER_SKIN = np.array([20, 255, 255], dtype=np.uint8)

KEY_MAP = {
    (0, 0): "Esc", (0, 1): "F1", (0, 2): "F2", (0, 3): "F3", (0, 4): "F4", (0, 5): "F5", (0, 6): "F6", (0, 7): "F7",
    (0, 8): "F8", (0, 9): "F9", (0, 10): "F10", (0, 11): "F11", (0, 12): "F12", (0, 13): "Delete",
    (1, 0): "~`", (1, 1): "1", (1, 2): "2", (1, 3): "3", (1, 4): "4", (1, 5): "5", (1, 6): "6", (1, 7): "7",
    (1, 8): "8", (1, 9): "9", (1, 10): "0", (1, 11): "-", (1, 12): "=", (1, 13): "Backspace",
    (2, 0): "Tab", (2, 1): "Q", (2, 2): "W", (2, 3): "E", (2, 4): "R", (2, 5): "T", (2, 6): "Y", (2, 7): "U",
    (2, 8): "I", (2, 9): "O", (2, 10): "P", (2, 11): "[", (2, 12): "]", (2, 13): "\\|",
    (3, 0): "Caps Lock", (3, 1): "A", (3, 2): "S", (3, 3): "D", (3, 4): "F", (3, 5): "G", (3, 6): "H", (3, 7): "J",
    (3, 8): "K", (3, 9): "L", (3, 10): ";", (3, 11): "'", (3, 12): "Enter",
    (4, 0): "Shift", (4, 1): "Z", (4, 2): "X", (4, 3): "C", (4, 4): "V", (4, 5): "B", (4, 6): "N", (4, 7): "M",
    (4, 8): ",", (4, 9): ".", (4, 10): "/", (4, 11): "Shift",
    (5, 0): "Ctrl", (5, 1): "Fn", (5, 3): "Alt", (5, 4): "Space", (5, 5): "Alt", (5, 6): "Ctrl", (5, 7): "Home", (5, 8): "PgUp", (5, 9): "PgDn", (5, 10): "End"
}

rectangles = []
key_assignments = {}

def find_rectangles_and_centers(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = []

    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            x, y, w, h = cv2.boundingRect(approx)
            center_x = x + w // 2
            center_y = y + h // 2
            if w > 10 and h > 10:
                rectangles.append(((center_x, center_y), approx, (x, y, w, h)))

    filtered_rectangles = []
    for i, (center, vertices, (x, y, w, h)) in enumerate(rectangles):
        is_inside = False
        for j, (_, _, (x2, y2, w2, h2)) in enumerate(rectangles):
            if i != j and (x > x2 and y > y2 and x + w < x2 + w2 and y + h < y2 + h2):
                is_inside = True
                break
        if not is_inside:
            filtered_rectangles.append((center, vertices))

    return filtered_rectangles

def detect_fingers(frame):
    """
    Detects the tips of fingers even if the entire finger is not visible.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)
    
    # Apply morphological transformations to reduce noise and fill holes
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours of the hand or finger tips
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    fingertips = []

    for contour in contours:
        # Ignore very small contours
        if cv2.contourArea(contour) < 500:  
            continue

        # Find the top-most point (fingertip) in the contour
        topmost = tuple(contour[contour[:, :, 1].argmin()][0])
        fingertips.append(topmost)

        # Visualize fingertip detection
        cv2.circle(frame, topmost, 10, (0, 255, 0), -1)  # Green circle at fingertip

    return fingertips

def assign_keys_to_rectangles(rectangles):
    if not rectangles:
        return {}

    centers = np.array([center for center, _ in rectangles])
    x_coords = centers[:, 0]
    y_coords = centers[:, 1]
    tolerance_y = 30
    unique_y = []
    y_clusters = {}
    sorted_y = np.sort(y_coords)
    current_cluster = [sorted_y[0]]
    current_mean = sorted_y[0]

    for y in sorted_y[1:]:
        if abs(y - current_mean) <= tolerance_y:
            current_cluster.append(y)
            current_mean = np.mean(current_cluster)
        else:
            unique_y.append(current_mean)
            y_clusters[current_mean] = current_cluster
            current_cluster = [y]
            current_mean = y
    unique_y.append(current_mean)
    y_clusters[current_mean] = current_cluster

    unique_y.sort()
    key_assignments = {}
    tolerance_x = 30

    for row_idx, row_y in enumerate(unique_y):
        row_centers = [(center, vertices) for (center, vertices) in rectangles 
                      if abs(center[1] - row_y) <= tolerance_y]
        row_centers.sort(key=lambda x: x[0][0])
        x_positions = []
        current_x = row_centers[0][0][0]
        x_cluster = [row_centers[0]]

        for center, vertices in row_centers[1:]:
            if abs(center[0] - current_x) <= tolerance_x:
                x_cluster.append((center, vertices))
            else:
                x_positions.append((current_x, x_cluster))
                x_cluster = [(center, vertices)]
                current_x = center[0]
        x_positions.append((current_x, x_cluster))

        for col_idx, (_, cluster) in enumerate(x_positions):
            if (row_idx, col_idx) in KEY_MAP:
                for center, _ in cluster:
                    key_assignments[center] = KEY_MAP[(row_idx, col_idx)]

    return key_assignments

import time

# Add a dictionary to track hover frames for keys
hover_tracking = {}  # {key: {'hover_frames': int, 'hovering': bool}}

def process_frame(frame, first=True):
    global rectangles, key_assignments, hover_tracking

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    edges = cv2.Canny(blurred, CANNY_THRESHOLD1, CANNY_THRESHOLD2)

    if first:
        rectangles = find_rectangles_and_centers(edges)
        key_assignments = assign_keys_to_rectangles(rectangles)

    fingertips = detect_fingers(frame)

    # Track keys being hovered over
    current_hovered_keys = set()

    for fingertip in fingertips:
        for center, vertices in rectangles:
            x, y, w, h = cv2.boundingRect(vertices)
            if x <= fingertip[0] <= x + w and y <= fingertip[1] <= y + h:
                key = key_assignments.get(center, 'Unknown')
                if key != 'Unknown':
                    current_hovered_keys.add(key)

                    # Start or increment the hover frame count
                    if key not in hover_tracking:
                        hover_tracking[key] = {'hover_frames': 1, 'hovering': True}
                    else:
                        hover_tracking[key]['hover_frames'] += 1
                break

    # Frame threshold for detecting a "press"
    HOVER_THRESHOLD_FRAMES = 8  # Number of frames

    # Check hover frames and print keys only if hovered for threshold frames
    pressed_keys = set()

    for key, data in hover_tracking.items():
        if key in current_hovered_keys:
            if data['hover_frames'] >= HOVER_THRESHOLD_FRAMES:
                if key not in pressed_keys:
                    print(f"Finger hovered over key: {key}")
                    pressed_keys.add(key)
                    data['hover_frames'] = 0  # Reset hover frames after registering a "press"
        else:
            # Reset hover tracking if the finger is no longer on the key
            data['hover_frames'] = 0

    # Update hover_tracking status
    for key in list(hover_tracking.keys()):
        if key not in current_hovered_keys:
            hover_tracking[key]['hovering'] = False
            hover_tracking[key]['hover_frames'] = 0

    # Draw rectangles and centroids for visualization
    for center, vertices in rectangles:
        x, y, w, h = cv2.boundingRect(vertices)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Rectangle

        # Draw centroid as a circle
        cv2.circle(frame, center, 5, (0, 255, 0), -1)

        # Display centroid coordinates
        #text = f"({center[0]}, {center[1]})"
        #cv2.putText(frame, text, (center[0] - 20, center[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Get the key assigned to this rectangle
        key_name = key_assignments.get(center, "Unknown")

        # Display the key text near the centroid
        cv2.putText(frame, key_name, (center[0] - 20, center[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    return frame



def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        first = True if i == 0 else False 
        frame = process_frame(frame, first)
        i += 1
        sleep(0.1)

        cv2.imshow('Processed Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_file = r"C:\Users\zohaa\OneDrive\Desktop\vid.mp4"

    process_video(video_file)