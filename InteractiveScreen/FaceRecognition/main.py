from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import cv2
import face_recognition
import os
import pyttsx3

data_path = "face_data/"
if not os.path.exists(data_path):
    os.makedirs(data_path)

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        self.image = Image()
        self.add_widget(self.image)
        Clock.schedule_interval(self.update, 1.0 / 30.0)
        self.name_input = TextInput(hint_text='Enter your name', size_hint=(0.8, 0.1), pos_hint={'center_x': 0.5, 'y': 0.1})
        self.add_widget(self.name_input)
        self.capture_button = Button(text='Capture & Save', size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5, 'y': 0.2})
        self.capture_button.bind(on_press=self.capture_image)
        self.add_widget(self.capture_button)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf = cv2.flip(frame, 0).tostring()
            self.image.texture = self.image.texture.create(size=(frame.shape[1], frame.shape[0]))
            self.image.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

    def capture_image(self, instance):
        ret, frame = self.capture.read()
        if ret and self.name_input.text:
            cv2.imwrite(os.path.join(data_path, f"{self.name_input.text}.jpg"), frame)
            print(f"Image saved as {self.name_input.text}.jpg")

class RecognitionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        self.image = Image()
        self.add_widget(self.image)
        Clock.schedule_interval(self.recognize_faces, 1.0 / 30.0)

    def recognize_faces(self, dt):
        ret, frame = self.capture.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            known_face_encodings = []
            known_face_names = []
            for file in os.listdir(data_path):
                img = face_recognition.load_image_file(os.path.join(data_path, file))
                encoding = face_recognition.face_encodings(img)[0]
                known_face_encodings.append(encoding)
                known_face_names.append(os.path.splitext(file)[0])

            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            for encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, encoding)
                name = "Unknown"
                if True in matches:
                    match_index = matches.index(True)
                    name = known_face_names[match_index]
                    self.speak(f"Attendance marked for {name}")
                    print(f"Recognized: {name}")

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

class FaceRecognitionApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(CameraScreen(name='camera'))
        sm.add_widget(RecognitionScreen(name='recognition'))
        return sm

if __name__ == '__main__':
    FaceRecognitionApp().run()
