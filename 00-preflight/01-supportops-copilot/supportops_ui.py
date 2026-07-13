# ===========================
# login.py
# PART 1
# ===========================

import customtkinter as ctk
from tkinter import messagebox
import csv
import os
import hashlib
import re
from PIL import Image

# -----------------------------
# APPEARANCE
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WIDTH = 1200
HEIGHT = 720

CSV_FILE = "users.csv"

# -----------------------------
# COLORS (iOS 26 Liquid Glass)
# -----------------------------
BG = "#060606"
CARD = "#161616"
CARD2 = "#202020"

ACCENT = "#E5E5E5"

TEXT = "#FFFFFF"
SUBTEXT = "#A4A4A4"

ENTRY = "#1E1E1E"
ENTRY_BORDER = "#2C2C2C"

BTN = "#F5F5F5"
BTN_HOVER = "#CFCFCF"

SUCCESS = "#00D26A"
ERROR = "#FF4D67"

FONT = "SF Pro Display"


# -----------------------------
# CSV
# -----------------------------
def create_database():

    if not os.path.exists(CSV_FILE):

        with open(CSV_FILE, "w", newline="", encoding="utf8") as f:

            writer = csv.writer(f)

            writer.writerow([
                "Name",
                "Email",
                "Password"
            ])


create_database()


# -----------------------------
# PASSWORD HASH
# -----------------------------
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# -----------------------------
# EMAIL VALIDATION
# -----------------------------
def valid_email(email):

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    return re.match(pattern, email)


# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
def valid_password(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    return True


# -----------------------------
# USER EXISTS
# -----------------------------
def user_exists(email):

    with open(
            CSV_FILE,
            "r",
            encoding="utf8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            if row["Email"].lower() == email.lower():

                return True

    return False


# -----------------------------
# SAVE USER
# -----------------------------
def save_user(
        name,
        email,
        password
):

    with open(
            CSV_FILE,
            "a",
            newline="",
            encoding="utf8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            name,
            email,
            hash_password(password)
        ])


# -----------------------------
# LOGIN
# -----------------------------
def login_user(
        email,
        password
):

    password = hash_password(password)

    with open(
            CSV_FILE,
            "r",
            encoding="utf8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            if (
                    row["Email"].lower() == email.lower()
                    and
                    row["Password"] == password
            ):

                return row["Name"]

    return None


# -----------------------------
# APP
# -----------------------------
class AuthApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.geometry(f"{WIDTH}x{HEIGHT}")

        self.title("Liquid Glass Authentication")

        self.configure(
            fg_color=BG
        )

        self.resizable(False, False)

        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.container.pack(
            fill="both",
            expand=True
        )

        self.show_signup()

# -----------------------------
# CLEAR
# -----------------------------
    def clear(self):

        for widget in self.container.winfo_children():

            widget.destroy()

# -----------------------------
# GLASS CARD
# -----------------------------
    def glass_card(self):

        card = ctk.CTkFrame(

            self.container,

            width=470,

            height=590,

            fg_color=CARD,

            corner_radius=35,

            border_width=1,

            border_color="#2F2F2F"

        )

        card.place(

            relx=.5,

            rely=.5,

            anchor="center"

        )

        return card


# -----------------------------
# ENTRY
# -----------------------------
    def create_entry(

            self,

            parent,

            placeholder,

            show=""

    ):

        entry = ctk.CTkEntry(

            parent,

            width=350,

            height=52,

            corner_radius=18,

            fg_color=ENTRY,

            border_color=ENTRY_BORDER,

            text_color=TEXT,

            placeholder_text=placeholder,

            placeholder_text_color=SUBTEXT,

            font=(FONT, 15),

            show=show

        )

        return entry


# -----------------------------
# BUTTON
# -----------------------------
    def create_button(

            self,

            parent,

            text,

            command

    ):

        button = ctk.CTkButton(

            parent,

            text=text,

            width=350,

            height=52,

            font=(FONT,16,"bold"),

            corner_radius=26,

            fg_color=BTN,

            hover_color=BTN_HOVER,

            text_color="black",

            command=command,

            cursor="hand2"

        )

        return button


# -----------------------------
# LABEL
# -----------------------------
    def title(

            self,

            parent,

            text

    ):

        label = ctk.CTkLabel(

            parent,

            text=text,

            text_color=TEXT,

            font=(FONT,34,"bold")

        )

        return label


# -----------------------------
# SUBTITLE
# -----------------------------
    def subtitle(

            self,

            parent,

            text

    ):

        label = ctk.CTkLabel(

            parent,

            text=text,

            text_color=SUBTEXT,

            font=(FONT,15)

        )

        return label
    # -----------------------------
# SIGN UP PAGE
# -----------------------------
    def show_signup(self):

        self.clear()

        card = self.glass_card()

        title = self.title(
            card,
            "Create Account"
        )
        title.pack(
            pady=(35, 5)
        )

        subtitle = self.subtitle(
            card,
            "Create your account to continue"
        )
        subtitle.pack(
            pady=(0, 25)
        )

        # -------------------------
        # NAME
        # -------------------------
        self.signup_name = self.create_entry(
            card,
            "Full Name"
        )
        self.signup_name.pack(pady=8)

        # -------------------------
        # EMAIL
        # -------------------------
        self.signup_email = self.create_entry(
            card,
            "Email Address"
        )
        self.signup_email.pack(pady=8)

        # -------------------------
        # PASSWORD
        # -------------------------
        self.signup_password = self.create_entry(
            card,
            "Password",
            show="●"
        )
        self.signup_password.pack(pady=8)

        # -------------------------
        # CONFIRM PASSWORD
        # -------------------------
        self.signup_confirm = self.create_entry(
            card,
            "Confirm Password",
            show="●"
        )
        self.signup_confirm.pack(pady=8)

        # -------------------------
        # ERROR LABEL
        # -------------------------
        self.signup_status = ctk.CTkLabel(
            card,
            text="",
            text_color=ERROR,
            font=(FONT, 13)
        )
        self.signup_status.pack(
            pady=(8, 0)
        )

        # -------------------------
        # BUTTON
        # -------------------------
        signup_btn = self.create_button(
            card,
            "Create Account",
            self.signup
        )
        signup_btn.pack(
            pady=(15, 18)
        )

        # -------------------------
        # FOOTER
        # -------------------------
        footer = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        footer.pack()

        lbl = ctk.CTkLabel(
            footer,
            text="Already have an account?",
            text_color=SUBTEXT,
            font=(FONT, 14)
        )
        lbl.pack(side="left")

        signin = ctk.CTkLabel(
            footer,
            text=" Sign In",
            text_color=ACCENT,
            font=(FONT, 14, "bold"),
            cursor="hand2"
        )
        signin.pack(side="left")

        signin.bind(
            "<Button-1>",
            lambda e: self.show_signin()
        )

        signin.bind(
            "<Enter>",
            lambda e: signin.configure(
                text_color="white"
            )
        )

        signin.bind(
            "<Leave>",
            lambda e: signin.configure(
                text_color=ACCENT
            )
        )

# -----------------------------
# SIGNUP FUNCTION
# -----------------------------
    def signup(self):

        name = self.signup_name.get().strip()

        email = self.signup_email.get().strip()

        password = self.signup_password.get()

        confirm = self.signup_confirm.get()

        if name == "":

            self.signup_status.configure(
                text="Enter your name."
            )
            return

        if len(name) < 3:

            self.signup_status.configure(
                text="Name must contain at least 3 characters."
            )
            return

        if not valid_email(email):

            self.signup_status.configure(
                text="Invalid email address."
            )
            return

        if user_exists(email):

            self.signup_status.configure(
                text="Email already exists."
            )
            return

        if not valid_password(password):

            self.signup_status.configure(
                text="Password must contain 8 characters, uppercase, lowercase and number."
            )
            return

        if password != confirm:

            self.signup_status.configure(
                text="Passwords do not match."
            )
            return

        save_user(
            name,
            email,
            password
        )

        messagebox.showinfo(
            "Success",
            "Account created successfully!"
        )

        self.current_user = name

        messagebox.showinfo(
            "Success",
            "Account created successfully.\nYou are now signed in."
        )

        self.show_home()
        # -----------------------------
# SIGN IN PAGE
# -----------------------------
    def show_signin(self):

        self.clear()

        card = self.glass_card()

        title = self.title(
            card,
            "Welcome Back"
        )
        title.pack(
            pady=(40, 5)
        )

        subtitle = self.subtitle(
            card,
            "Sign in to continue"
        )
        subtitle.pack(
            pady=(0, 30)
        )

        # -------------------------
        # EMAIL
        # -------------------------
        self.login_email = self.create_entry(
            card,
            "Email Address"
        )
        self.login_email.pack(
            pady=10
        )

        # -------------------------
        # PASSWORD
        # -------------------------
        self.login_password = self.create_entry(
            card,
            "Password",
            show="●"
        )
        self.login_password.pack(
            pady=10
        )

        # -------------------------
        # STATUS LABEL
        # -------------------------
        self.login_status = ctk.CTkLabel(
            card,
            text="",
            text_color=ERROR,
            font=(FONT, 13)
        )
        self.login_status.pack(
            pady=(10, 0)
        )

        # -------------------------
        # SIGN IN BUTTON
        # -------------------------
        signin_btn = self.create_button(
            card,
            "Sign In",
            self.signin
        )
        signin_btn.pack(
            pady=(20, 18)
        )

        # -------------------------
        # FOOTER
        # -------------------------
        footer = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        footer.pack()

        lbl = ctk.CTkLabel(
            footer,
            text="Don't have an account?",
            text_color=SUBTEXT,
            font=(FONT, 14)
        )
        lbl.pack(side="left")

        signup = ctk.CTkLabel(
            footer,
            text=" Sign Up",
            text_color=ACCENT,
            font=(FONT, 14, "bold"),
            cursor="hand2"
        )
        signup.pack(side="left")

        signup.bind(
            "<Button-1>",
            lambda e: self.show_signup()
        )

        signup.bind(
            "<Enter>",
            lambda e: signup.configure(
                text_color="white"
            )
        )

        signup.bind(
            "<Leave>",
            lambda e: signup.configure(
                text_color=ACCENT
            )
        )

        # -------------------------
        # ENTER KEY SUPPORT
        # -------------------------
        self.login_password.bind(
            "<Return>",
            lambda e: self.signin()
        )

# -----------------------------
# SIGN IN FUNCTION
# -----------------------------
    def signin(self):

        email = self.login_email.get().strip()

        password = self.login_password.get()

        if email == "":
            self.login_status.configure(
                text="Please enter your email."
            )
            return

        if not valid_email(email):
            self.login_status.configure(
                text="Invalid email address."
            )
            return

        if password == "":
            self.login_status.configure(
                text="Please enter your password."
            )
            return

        user = login_user(
            email,
            password
        )

        if user is None:

            self.login_status.configure(
                text="Incorrect email or password."
            )
            return

        self.current_user = user

        self.show_home()
        # -----------------------------
# HOME PAGE
# -----------------------------
    def show_home(self):

        self.clear()

        # Background Frame
        bg = ctk.CTkFrame(
            self.container,
            fg_color=BG
        )
        bg.pack(
            fill="both",
            expand=True
        )

        # -------------------------
        # Glass Card
        # -------------------------
        card = ctk.CTkFrame(
            bg,
            width=520,
            height=340,
            fg_color=CARD,
            corner_radius=35,
            border_width=1,
            border_color="#303030"
        )

        card.place(
            relx=.5,
            rely=.5,
            anchor="center"
        )

        # -------------------------
        # Welcome
        # -------------------------
        title = ctk.CTkLabel(
            card,
            text="Welcome 👋",
            text_color=TEXT,
            font=(FONT, 32, "bold")
        )
        title.pack(
            pady=(45, 8)
        )

        user = ctk.CTkLabel(
            card,
            text=self.current_user,
            text_color=ACCENT,
            font=(FONT, 22)
        )
        user.pack()

        msg = ctk.CTkLabel(
            card,
            text="You have successfully signed in.",
            text_color=SUBTEXT,
            font=(FONT, 15)
        )
        msg.pack(
            pady=(10, 35)
        )

        # -------------------------
        # Logout Button
        # -------------------------
        logout = self.create_button(
            card,
            "Logout",
            self.show_signin
        )

        logout.pack()

        # -------------------------
        # Footer
        # -------------------------
        footer = ctk.CTkLabel(
            bg,
            text="Designed with iOS 26 Liquid Glass Theme",
            text_color="#666666",
            font=(FONT, 12)
        )

        footer.pack(
            side="bottom",
            pady=20
        )


# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":

    app = AuthApp()

    app.mainloop()