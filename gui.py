import tkinter as tk
from tkinter import messagebox
import pickle, os

# Load model and vectorizer
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
    return "FAKE" if prediction == 0 else "REAL"

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Fake News Detection System")
root.geometry("600x400")
root.config(bg="#001f3f")

# Title
tk.Label(root, text="📰 Fake News Detection", font=("Helvetica", 18, "bold"), bg="#001f3f", fg="white").pack(pady=10)

# Input Frame
frame = tk.Frame(root, bg="#001f3f")
frame.pack(pady=10)

tk.Label(frame, text="Title:", bg="#001f3f", fg="white").grid(row=0, column=0, sticky="w", pady=5)
title_entry = tk.Entry(frame, width=50)
title_entry.grid(row=0, column=1, pady=5)

tk.Label(frame, text="Author:", bg="#001f3f", fg="white").grid(row=1, column=0, sticky="w", pady=5)
author_entry = tk.Entry(frame, width=50)
author_entry.grid(row=1, column=1, pady=5)

tk.Label(frame, text="News Text:", bg="#001f3f", fg="white").grid(row=2, column=0, sticky="nw", pady=5)
text_entry = tk.Text(frame, width=50, height=8)
text_entry.grid(row=2, column=1, pady=5)

# Result Label
result_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#001f3f", fg="yellow")
result_label.pack(pady=10)

# Prediction Function
def on_predict():
    title = title_entry.get()
    author = author_entry.get()
    text = text_entry.get("1.0", tk.END).strip()
    if not title or not author or not text:
        messagebox.showwarning("Input Error", "Please fill all fields!")
        return
    result = predict_news(title, author, text)
    result_label.config(text=f"Prediction: {result}", fg="lime" if result=="REAL" else "red")

# Buttons
btn_frame = tk.Frame(root, bg="#001f3f")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Predict", command=on_predict, bg="orange", fg="black", width=12).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Exit", command=root.quit, bg="red", fg="white", width=12).grid(row=0, column=1, padx=5)

root.mainloop()
