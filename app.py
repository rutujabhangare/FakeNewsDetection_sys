import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pickle, os
from PIL import Image, ImageTk
from datetime import datetime

# ---------------- ML Model ----------------
model_path = os.path.join(os.getcwd(), "model.pkl")
vectorizer_path = os.path.join(os.getcwd(), "vectorizer.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)
with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

def predict_news(title, author, text):
    if not text.strip():
        return "Invalid input"
    combined = f"{title} {author} {text}"
    transformed_text = vectorizer.transform([combined])
    prediction = model.predict(transformed_text)[0]
    return "FAKE" if prediction == 1 else "REAL"

# ---------------- Database Setup ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            author TEXT,
            text TEXT,
            result TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- Pages ----------------
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        bg_img = Image.open("news_background.jpg").resize((900, 600))
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        tk.Label(self, image=self.bg_photo).place(relwidth=1, relheight=1)

        login_frame = tk.Frame(self, bg="#001f3f")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="Login", bg="#001f3f", fg="white", font=("Helvetica", 16)).pack(pady=10)
        tk.Label(login_frame, text="Username", bg="#001f3f", fg="white").pack()
        self.username_entry = tk.Entry(login_frame)
        self.username_entry.pack()
        tk.Label(login_frame, text="Password", bg="#001f3f", fg="white").pack()
        self.password_entry = tk.Entry(login_frame, show="*")
        self.password_entry.pack()

        tk.Button(login_frame, text="Login", command=self.login).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            messagebox.showinfo("Login Success", f"Welcome {username}!")
            self.destroy()
            dashboard = DashboardPage(self.controller.container, self.controller, username)
            dashboard.pack(fill="both", expand=True)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username

        bg_img = Image.open("dashboard_bg.jpg").resize((900, 600))
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        tk.Label(self, image=self.bg_photo).place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(self, text=f"Welcome, {username}!", font=("Helvetica", 16), bg="#001f3f", fg="white").pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)
        tk.Label(form_frame, text="Title").grid(row=0, column=0)
        self.title_entry = tk.Entry(form_frame, width=50)
        self.title_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Author").grid(row=1, column=0)
        self.author_entry = tk.Entry(form_frame, width=50)
        self.author_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="News Text").grid(row=2, column=0)
        self.news_entry = tk.Text(form_frame, width=50, height=10)
        self.news_entry.grid(row=2, column=1)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Predict", command=self.predict).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="View History", command=self.view_history).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="User Analytics", command=self.show_analytics).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Logout", command=self.logout).grid(row=0, column=3, padx=5)

        self.result_label = tk.Label(self, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=10)

    def predict(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        text = self.news_entry.get("1.0", tk.END).strip()
        if not title or not author or not text:
            messagebox.showwarning("Input Error", "Please fill in all fields!")
            return
        result = predict_news(title, author, text)
        self.result_label.config(text=f"Prediction: {result}")

        # Save in DB
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (username, title, author, text, result, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                       (self.username, title, author, text, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def view_history(self):
        self.destroy()
        history = HistoryPage(self.controller.container, self.controller, self.username)
        history.pack(fill="both", expand=True)

    def show_analytics(self):
        self.destroy()
        analytics = AnalyticsPage(self.controller.container, self.controller, self.username)
        analytics.pack(fill="both", expand=True)

    def logout(self):
        self.destroy()
        login = LoginPage(self.controller.container, self.controller)
        login.pack(fill="both", expand=True)

class HistoryPage(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username

        tk.Label(self, text=f"{username}'s History", font=("Helvetica", 16)).pack(pady=10)
        tk.Button(self, text="⬅ Back", command=self.go_back).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("Title", "Author", "Result", "Timestamp"), show="headings")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Result", text="Result")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.column("Title", width=150)
        self.tree.column("Author", width=100)
        self.tree.column("Result", width=80)
        self.tree.column("Timestamp", width=150)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.load_history()

    def load_history(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, result, timestamp FROM history WHERE username=? ORDER BY timestamp DESC",
                       (self.username,))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def go_back(self):
        self.destroy()
        dashboard = DashboardPage(self.controller.container, self.controller, self.username)
        dashboard.pack(fill="both", expand=True)

class AnalyticsPage(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username

        tk.Label(self, text=f"{username}'s Analytics", font=("Helvetica", 16)).pack(pady=10)

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM history WHERE username=?", (username,))
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM history WHERE username=? AND result='FAKE'", (username,))
        fake = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM history WHERE username=? AND result='REAL'", (username,))
        real = cursor.fetchone()[0]
        conn.close()

        tk.Label(self, text=f"Total Predictions: {total}").pack()
        tk.Label(self, text=f"Fake News: {fake}").pack()
        tk.Label(self, text=f"Real News: {real}").pack()
        tk.Button(self, text="⬅ Back", command=self.go_back).pack(pady=10)

    def go_back(self):
        self.destroy()
        dashboard = DashboardPage(self.controller.container, self.controller, self.username)
        dashboard.pack(fill="both", expand=True)

# ---------------- Main App ----------------
class FakeNewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fake News Detection System")
        self.geometry("900x600")
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.show_login()

    def show_login(self):
        login_page = LoginPage(self.container, self)
        login_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = FakeNewsApp()
    app.mainloop()
