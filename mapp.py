import cv2
import numpy as np
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from threading import Thread
from pyzbar.pyzbar import decode
from kivy.uix.screenmanager import ScreenManager, Screen


# Default values
ESP32_IP = "esp32-car.local"  # Default IP address, can be changed via the UI
ESP32_URL = f"http://{ESP32_IP}:80/control"  # URL endpoint for car control


# Function to send commands to the ESP32
def send_car_command(command, speed):
    try:
        url = f"{ESP32_URL}?cmd={command}&speed={speed}"
        response = requests.get(url)
        print(f"Sent command: {command}, Speed: {speed}")
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


# Calculate speed based on the distance between QR codes
def calculate_speed(distance):
    max_distance = 500  # Maximum detectable distance
    return int((255 * min(distance, max_distance)) / max_distance)


# Main Screen with control buttons
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")

        # Mode switcher (Manual vs Tracking)
        mode_switch_label = Label(text="Switch to Tracking Mode", size_hint=(1, 0.1))
        self.mode_switch = Switch(active=False, size_hint=(1, 0.1))
        self.mode_switch.bind(active=self.on_mode_switch)
        self.layout.add_widget(mode_switch_label)
        self.layout.add_widget(self.mode_switch)

        # Control buttons in a "+" shape for Manual Mode
        control_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.4))
        control_layout.add_widget(Button(text="Left", on_press=self.move_left))
        control_layout.add_widget(Button(text="Forward", on_press=self.move_forward))
        control_layout.add_widget(Button(text="Right", on_press=self.move_right))
        self.layout.add_widget(control_layout)

        control_layout2 = BoxLayout(orientation="horizontal", size_hint=(1, 0.4))
        control_layout2.add_widget(Button(text="Stop", on_press=self.stop_car))
        control_layout2.add_widget(Button(text="Backward", on_press=self.move_backward))
        self.layout.add_widget(control_layout2)

        # Empty space at the top-left, top-right, bottom-left, bottom-right for "+" shape
        empty_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.4))
        self.layout.add_widget(empty_layout)

        # Camera mode switch (to switch between front and back camera)
        self.camera_switch_button = Button(text="Switch to Back Camera", size_hint=(1, 0.1), on_press=self.switch_camera)
        self.layout.add_widget(self.camera_switch_button)

        # Speed slider
        self.speed_slider = Slider(min=0, max=255, value=150, size_hint=(1, 0.1))
        self.layout.add_widget(self.speed_slider)

        self.add_widget(self.layout)
        self.current_camera = "front"  # Track the current camera mode

    def on_mode_switch(self, instance, value):
        if value:
            self.manager.current = "tracking"
        else:
            self.manager.current = "manual"
            self.camera_switch_button.disabled = True  # Disable camera switch button in manual mode

    def move_forward(self, instance):
        speed = int(self.speed_slider.value)
        send_car_command("forward", speed)

    def move_left(self, instance):
        speed = int(self.speed_slider.value)
        send_car_command("left", speed)

    def move_right(self, instance):
        speed = int(self.speed_slider.value)
        send_car_command("right", speed)

    def move_backward(self, instance):
        speed = int(self.speed_slider.value)
        send_car_command("backward", speed)

    def stop_car(self, instance):
        send_car_command("stop", 0)

    def switch_camera(self, instance):
        """Switch between front and back camera"""
        if self.current_camera == "front":
            self.current_camera = "back"
            self.camera_switch_button.text = "Switch to Front Camera"
        else:
            self.current_camera = "front"
            self.camera_switch_button.text = "Switch to Back Camera"


# Tracking Screen with camera feed and QR code tracking
class TrackingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Camera feed
        self.camera_image = Image(size_hint=(1, 0.8))
        self.layout.add_widget(self.camera_image)

        # Add "Back to Manual" button
        back_button = Button(text="Back to Manual", size_hint=(1, 0.1), on_press=self.switch_to_manual)
        self.layout.add_widget(back_button)

        # Start camera processing in a separate thread
        self.camera_thread = Thread(target=self.process_camera_feed)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        self.add_widget(self.layout)

    def switch_to_manual(self, instance):
        self.manager.current = 'manual'

    def process_camera_feed(self):
        cap = cv2.VideoCapture(0)  # Use the default front camera
        if not cap.isOpened():
            print("Unable to access the camera.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame from the camera.")
                break

            # QR code tracking logic
            car_qr, target_qr = track_qr_codes(frame)
            if car_qr and target_qr:
                car_center = car_qr.rect
                target_center = target_qr.rect
                distance = np.sqrt((car_center[0] - target_center[0]) ** 2 + (car_center[1] - target_center[1]) ** 2)
                cv2.putText(frame, f"Distance: {distance:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Control the car based on distance
                speed = calculate_speed(distance)
                if distance > 100:
                    send_car_command("forward", speed)
                else:
                    send_car_command("stop", 0)
            else:
                send_car_command("stop", 0)

            # Convert the frame to texture for Kivy Image widget
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.camera_image.texture = texture

            # Sleep for a short time to prevent high CPU usage
            cv2.waitKey(1)

        cap.release()


# CarControlApp to manage screens
class CarControlApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.main_screen = MainScreen(name="manual")
        self.tracking_screen = TrackingScreen(name="tracking")

        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.tracking_screen)

        return self.screen_manager


if __name__ == '__main__':
    app = CarControlApp()
    app.run()
