import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests

# ESP32 IP and URL for controlling the car (update IP if necessary)
ESP32_IP = "esp32-car.local"  # Use your ESP32's IP or hostname
ESP32_URL = f"http://{ESP32_IP}/control"  # Endpoint for car control

# Constants
MAX_SPEED = 255  # Maximum speed of the car
MIN_DISTANCE = 50  # Minimum distance (in pixels) to stop
MAX_DISTANCE = 300  # Maximum distance (in pixels) for full speed

# Function to send commands to the ESP32
def send_car_command(command, speed):
    try:
        # Construct the URL with command and speed
        url = f"{ESP32_URL}?cmd={command}&speed={int(speed)}"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Sent command: {command}, Speed: {speed}")
        else:
            print(f"Failed to send command: {response.text}")
    except Exception as e:
        print(f"Error sending command: {e}")

# QR code tracking function
def track_qr_codes(frame):
    decoded_objects = decode(frame)
    car_qr, target_qr = None, None

    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        if "car" in data:
            car_qr = obj
        elif "target" in data:
            target_qr = obj

    return car_qr, target_qr

# Function to calculate speed based on distance
def calculate_speed(distance):
    # Map distance to speed using a linear scale
    if distance <= MIN_DISTANCE:
        return 0  # Stop
    elif distance >= MAX_DISTANCE:
        return MAX_SPEED  # Full speed
    else:
        # Linearly scale speed between MIN_DISTANCE and MAX_DISTANCE
        return ((distance - MIN_DISTANCE) / (MAX_DISTANCE - MIN_DISTANCE)) * MAX_SPEED

# Main function to process the camera feed
def process_camera_feed():
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    if not cap.isOpened():
        print("Unable to access the camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Detect QR codes
        car_qr, target_qr = track_qr_codes(frame)

        if car_qr and target_qr:
            # Calculate center points and distance
            car_center = car_qr.rect
            target_center = target_qr.rect
            distance = np.sqrt((car_center[0] - target_center[0]) ** 2 + (car_center[1] - target_center[1]) ** 2)

            # Calculate speed based on distance
            speed = calculate_speed(distance)

            # Draw QR code bounding boxes
            for qr_code, label, color in [(car_qr, "Car", (0, 255, 0)), (target_qr, "Target", (0, 0, 255))]:
                points = qr_code.polygon
                if len(points) == 4:
                    pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, color, 3)
                    center = qr_code.rect
                    cv2.putText(frame, label, (center[0], center[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Display distance and speed
            cv2.putText(frame, f"Distance: {distance:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            cv2.putText(frame, f"Speed: {speed:.0f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            # Determine movement
            if speed > 0:
                if target_center[0] < car_center[0] - 50:
                    send_car_command("left", speed)  # Turn left
                elif target_center[0] > car_center[0] + 50:
                    send_car_command("right", speed)  # Turn right
                else:
                    send_car_command("forward", speed)  # Move forward
            else:
                send_car_command("stop", 0)  # Stop

        # Show the processed frame
        cv2.imshow("Car Control Feed", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            send_car_command("stop", 0)  # Stop the car before exiting
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_camera_feed()
