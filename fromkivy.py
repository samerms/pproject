from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import json
import os
import re
from PyPDF2 import PdfReader

# ניהול נתוני משתמשים
class UserManager:
    FILE_NAME = "users.json"

    @staticmethod
    def load_users():
        if os.path.exists(UserManager.FILE_NAME):
            with open(UserManager.FILE_NAME, "r") as file:
                return json.load(file)
        return {}

    @staticmethod
    def save_users(users):
        with open(UserManager.FILE_NAME, "w") as file:
            json.dump(users, file)

# פונקציה למציאת תאריכים בקובץ PDF
def extract_date_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # חיפוש דפוסי תאריכים נפוצים
        date_patterns = [
            r"\b\d{4}-\d{2}-\d{2}\b",  # פורמט YYYY-MM-DD
            r"\b\d{2}/\d{2}/\d{4}\b",  # פורמט DD/MM/YYYY
            r"\b\d{2}-\d{2}-\d{4}\b",  # פורמט DD-MM-YYYY
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return "No date found"
    except Exception as e:
        return f"Error reading PDF: {e}"

# בניית ממשק KV
KV = '''
ScreenManager:
    LoginScreen:
    SignupScreen:
    MainScreen:

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(20)
        padding: dp(20)
        MDLabel:
            text: "Welcome to the App"
            halign: "center"
            theme_text_color: "Primary"
            font_style: "H4"

        MDTextField:
            id: login_username
            hint_text: "Enter your username"
            icon_right: "account"
            size_hint_x: None
            width: 300
            pos_hint: {"center_x": 0.5}

        MDTextField:
            id: login_password
            hint_text: "Enter your password"
            password: True
            icon_right: "key"
            size_hint_x: None
            width: 300
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            on_release: root.login(login_username.text, login_password.text)

        MDRaisedButton:
            text: "Sign Up"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "signup"

<SignupScreen>:
    name: "signup"
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(20)
        padding: dp(20)
        MDLabel:
            text: "Create an Account"
            halign: "center"
            theme_text_color: "Primary"
            font_style: "H4"

        MDTextField:
            id: signup_username
            hint_text: "Choose a username"
            icon_right: "account"
            size_hint_x: None
            width: 300
            pos_hint: {"center_x": 0.5}

        MDTextField:
            id: signup_password
            hint_text: "Choose a password"
            password: True
            icon_right: "key"
            size_hint_x: None
            width: 300
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "Sign Up"
            pos_hint: {"center_x": 0.5}
            on_release: root.signup(signup_username.text, signup_password.text)

        MDRaisedButton:
            text: "Back to Login"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "login"

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(20)
        padding: dp(20)
        MDLabel:
            text: "Welcome to the Main Page!"
            halign: "center"
            theme_text_color: "Primary"
            font_style: "H4"

        MDRaisedButton:
            text: "Select PDF and Extract Date"
            pos_hint: {"center_x": 0.5}
            on_release: app.extract_date_from_pdf_dialog()

        MDRaisedButton:
            text: "Logout"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "login"
'''

# מחלקות למסכים
class LoginScreen(Screen):
    def login(self, username, password):
        users = UserManager.load_users()
        if username in users and users[username] == password:
            self.manager.current = "main"
        else:
            self.show_message("Login Error", "Invalid username or password!")

    def show_message(self, title, message):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

class SignupScreen(Screen):
    def signup(self, username, password):
        if not username or not password:
            self.show_message("Error", "Please fill out all fields!")
            return

        users = UserManager.load_users()

        if username in users:
            self.show_message("Error", "Username already exists!")
        else:
            users[username] = password
            UserManager.save_users(users)
            self.show_message("Success", "Account created successfully!")
            self.manager.current = "login"

    def show_message(self, title, message):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

class MainScreen(Screen):
    pass

class PharmacyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def extract_date_from_pdf_dialog(self):
        # שימוש ב-Tkinter לבחירת קובץ
        Tk().withdraw()  # מסתיר את החלון הראשי של Tkinter
        file_path = askopenfilename(title="Select PDF file", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            dialog = MDDialog(
                title="Error",
                text="No file selected.",
                buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()
            return

        # קריאת תאריך מהקובץ
        date = extract_date_from_pdf(file_path)
        dialog = MDDialog(
            title="Extracted Date",
            text=f"Date found: {date}" if date else "No date found.",
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

if __name__ == "__main__":
    PharmacyApp().run()
