import os
import cv2
import face_recognition
import numpy as np
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup

class FaceRecognitionApp(App):
    def build(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(RegisterScreen(name='register'))
        return sm
    
    def load_known_faces(self):
        if not os.path.exists('faces'):
            os.makedirs('faces')
        
        for filename in os.listdir('faces'):
            if filename.endswith('.jpg'):
                path = os.path.join('faces', filename)
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(path)
                encoding = face_recognition.face_encodings(image)[0]
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Camera preview
        self.image = Image()
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=0.2)
        register_btn = Button(text='Register New Face')
        register_btn.bind(on_press=self.switch_to_register)
        
        button_layout.add_widget(register_btn)
        
        layout.add_widget(self.image)
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
        
        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/30.0)
    
    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Convert frame to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            app = App.get_running_app()
            
            # Loop through each face
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(app.known_face_encodings, face_encoding)
                name = "Unknown"
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = app.known_face_names[first_match_index]
                
                # Draw rectangle and name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            
            # Convert frame to texture for Kivy
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture
    
    def switch_to_register(self, instance):
        self.manager.current = 'register'
    
    def on_leave(self):
        self.capture.release()

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Name input
        self.name_input = TextInput(
            multiline=False,
            hint_text='Enter name',
            size_hint_y=None,
            height=50
        )
        
        # Camera preview
        self.image = Image()
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=0.2)
        back_btn = Button(text='Back')
        capture_btn = Button(text='Capture')
        
        back_btn.bind(on_press=self.go_back)
        capture_btn.bind(on_press=self.capture_face)
        
        button_layout.add_widget(back_btn)
        button_layout.add_widget(capture_btn)
        
        layout.add_widget(self.name_input)
        layout.add_widget(self.image)
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
        
        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/30.0)
    
    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Convert frame to texture for Kivy
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture
            self.last_frame = frame
    
    def capture_face(self, instance):
        if not hasattr(self, 'last_frame'):
            return
        
        name = self.name_input.text.strip()
        if not name:
            self.show_error('Please enter a name')
            return
        
        # Detect faces in frame
        rgb_frame = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            self.show_error('No face detected')
            return
        
        if len(face_locations) > 1:
            self.show_error('Multiple faces detected')
            return
        
        # Save face image
        if not os.path.exists('faces'):
            os.makedirs('faces')
        
        filename = f'faces/{name}.jpg'
        cv2.imwrite(filename, self.last_frame)
        
        # Update known faces
        app = App.get_running_app()
        image = face_recognition.load_image_file(filename)
        encoding = face_recognition.face_encodings(image)[0]
        app.known_face_encodings.append(encoding)
        app.known_face_names.append(name)
        
        self.show_success('Face registered successfully!')
        self.name_input.text = ''
    
    def show_error(self, message):
        popup = Popup(title='Error',
                     content=Label(text=message),
                     size_hint=(None, None), size=(400, 200))
        popup.open()
    
    def show_success(self, message):
        popup = Popup(title='Success',
                     content=Label(text=message),
                     size_hint=(None, None), size=(400, 200))
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def on_leave(self):
        self.capture.release()

if __name__ == '__main__':
    FaceRecognitionApp().run()
