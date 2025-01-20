import pygame
import requests
import time

# === Constants ===
ESP32_IP = "http://esp32-car.local"  # Replace with your ESP32's IP address
FORWARD_URL = f"{ESP32_IP}/forward"
BACKWARD_URL = f"{ESP32_IP}/reverse"
LEFT_URL = f"{ESP32_IP}/left"
RIGHT_URL = f"{ESP32_IP}/right"
STOP_URL = f"{ESP32_IP}/stop"
SPEED_URL = f"{ESP32_IP}/setSpeed"

# === Initialize Pygame ===
pygame.init()

# === Set up the Xbox Controller ===
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# === Define button mappings ===
BUTTON_X = 0  # Button X
BUTTON_Y = 1  # Button Y
BUTTON_B = 2  # Button B
BUTTON_A = 3  # Button A

# === Movement Control ===
def send_command(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Command {url} sent successfully!")
        else:
            print(f"Failed to send command {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# === Speed Control ===
def send_speed(value):
    try:
        response = requests.get(f"{SPEED_URL}?value={value}")
        if response.status_code == 200:
            print(f"Speed set to {value}")
        else:
            print(f"Failed to set speed")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# === Main Loop ===
try:
    previous_command = None  # Variable to track the last movement command
    stopped = True  # Variable to track if the car is currently stopped

    while True:
        # === Event Handling ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # === Joystick Axes (Left Joystick for movement) ===
        x_axis = joystick.get_axis(0)  # Left Joystick X (right/left)
        y_axis = joystick.get_axis(1)  # Left Joystick Y (forward/backward)

        # === Movement Control based on joystick position ===
        if abs(x_axis) > 0.5 or abs(y_axis) > 0.5:  # Joystick is being moved
            if y_axis < -0.5:  # Move Forward
                if previous_command != FORWARD_URL:
                    send_command(FORWARD_URL)
                    previous_command = FORWARD_URL
            elif y_axis > 0.5:  # Move Backward
                if previous_command != BACKWARD_URL:
                    send_command(BACKWARD_URL)
                    previous_command = BACKWARD_URL
            elif x_axis < -0.5:  # Turn Left
                if previous_command != LEFT_URL:
                    send_command(LEFT_URL)
                    previous_command = LEFT_URL
            elif x_axis > 0.5:  # Turn Right
                if previous_command != RIGHT_URL:
                    send_command(RIGHT_URL)
                    previous_command = RIGHT_URL
            stopped = False  # Movement detected, car is not stopped
        else:  # Joystick is at rest
            if not stopped:
                send_command(STOP_URL)  # Send stop command once
                stopped = True  # Set car to stopped state
                previous_command = STOP_URL  # Track stop command to prevent repeat

        # === Button Presses (XYBA) for Speed Control ===
        if joystick.get_button(BUTTON_X):  # Button X to set speed to 100
            send_speed(255)
        elif joystick.get_button(BUTTON_Y):  # Button Y to set speed to 80
            send_speed(80)
        elif joystick.get_button(BUTTON_B):  # Button B to set speed to 50
            send_speed(50)
        elif joystick.get_button(BUTTON_A):  # Button A to set speed to 0 (Stop)
            send_speed(0)

        time.sleep(0.01)  # Shorter delay for faster response

except KeyboardInterrupt:
    pygame.quit()
    print("Exiting...")
