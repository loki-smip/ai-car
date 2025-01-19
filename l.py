from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider


class CarControlApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Create a slider for controlling speed
        self.speed_slider = Slider(min=0, max=255, value=150, size_hint=(1, 0.1))
        self.layout.add_widget(self.speed_slider)

        # Create the grid layout for buttons
        control_layout = GridLayout(cols=3, rows=3, size_hint=(1, 1), padding=10)

        # Create empty widgets for the outer cells
        control_layout.add_widget(Widget())  # Empty space
        control_layout.add_widget(Button(text="Forward", on_press=self.move_forward))
        control_layout.add_widget(Widget())  # Empty space

        control_layout.add_widget(Button(text="Left", on_press=self.move_left))
        control_layout.add_widget(Button(text="Stop", on_press=self.stop_car))  # Stop button in the middle
        control_layout.add_widget(Button(text="Right", on_press=self.move_right))

        control_layout.add_widget(Widget())  # Empty space
        control_layout.add_widget(Button(text="Backward", on_press=self.move_backward))
        control_layout.add_widget(Widget())  # Empty space

        # Add the control layout (buttons) to the main layout
        self.layout.add_widget(control_layout)

        return self.layout

    # Define car movement functions
    def move_forward(self, instance):
        print("Move Forward")

    def move_left(self, instance):
        print("Move Left")

    def move_right(self, instance):
        print("Move Right")

    def move_backward(self, instance):
        print("Move Backward")

    def stop_car(self, instance):
        print("Stop")


if __name__ == '__main__':
    CarControlApp().run()
