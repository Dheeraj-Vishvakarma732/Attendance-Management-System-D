import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "attendance.json"

load_dotenv(BASE_DIR / ".env")
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY) if API_KEY else None

SAMPLE_DATA = {
    "days": ["2026-10-01", "2026-10-02", "2026-10-03",
             "2026-10-06", "2026-10-07"],
    "students": [
        {"name": "Asha", "rollno": "101", "attendance": {
            "2026-10-01": "P", "2026-10-02": "P",
            "2026-10-03": "P", "2026-10-06": "P",
            "2026-10-07": "P"}},
        {"name": "Ravi", "rollno": "102", "attendance": {
            "2026-10-01": "A", "2026-10-02": "P",
            "2026-10-03": "P", "2026-10-06": "P",
            "2026-10-07": "A"}},
        {"name": "Neha", "rollno": "103", "attendance": {
            "2026-10-01": "P", "2026-10-02": "P",
            "2026-10-03": "P", "2026-10-06": "P",
            "2026-10-07": "P"}},
        {"name": "Amit", "rollno": "104", "attendance": {
            "2026-10-01": "A", "2026-10-02": "A",
            "2026-10-03": "P", "2026-10-06": "P",
            "2026-10-07": "A"}},
        {"name": "Priya", "rollno": "105", "attendance": {
            "2026-10-01": "P", "2026-10-02": "A",
            "2026-10-03": "P", "2026-10-06": "P",
            "2026-10-07": "P"}}
    ]
}


def load_data():
    if not DATA_FILE.exists():
        save_data(SAMPLE_DATA)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for student in data["students"]:
        recorded = [
            value for value in student["attendance"].values()
            if value in ("P", "A")
        ]
        student["total_days"] = len(recorded)
        student["days_present"] = recorded.count("P")
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def refresh_table():
    for item in table.get_children():
        table.delete(item)

    data = load_data()
    for student in data["students"]:
        total = student["total_days"]
        present = student["days_present"]
        percentage = (present / total * 100) if total else 0
        table.insert("", "end", values=(
            student["rollno"], student["name"],
            present, total, f"{percentage:.1f}%"
        ))


def mark_attendance():
    roll = roll_entry.get().strip()
    status = status_var.get()
    today = date_entry.get().strip()

    data = load_data()
    student = next(
        (s for s in data["students"] if s["rollno"] == roll), None
    )

    if not student:
        messagebox.showerror("Error", "Roll number nahi mila.")
        return

    if not today:
        messagebox.showerror("Error", "Date enter karo.")
        return

    if today not in data["days"]:
        data["days"].append(today)
        for s in data["students"]:
            s["attendance"].setdefault(today, None)

    student["attendance"][today] = status
    save_data(data)
    refresh_table()
    messagebox.showinfo("Success", "Attendance JSON mein save ho gayi.")


def ask_openai():
    if client is None:
        messagebox.showwarning(
            "API key missing",
            ".env file mein OPENAI_API_KEY set karo."
        )
        return

    question = question_entry.get().strip()
    if not question:
        messagebox.showwarning("Question", "Apna sawaal likho.")
        return

    data = load_data()
    summary = []
    for s in data["students"]:
        total = s["total_days"]
        present = s["days_present"]
        pct = (present / total * 100) if total else 0
        summary.append(
            f"{s['name']} (roll {s['rollno']}): "
            f"{present}/{total} days present, {pct:.1f}%"
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful student attendance assistant. "
                        "Answer using only this attendance data:\n"
                        + "\n".join(summary)
                    )
                },
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        messagebox.showinfo("OpenAI Answer", answer)
    except Exception as e:
        messagebox.showerror("OpenAI Error", str(e))


root = tk.Tk()
root.title("Attendance Management System")
root.geometry("760x600")

tk.Label(
    root, text="Attendance Management System",
    font=("Arial", 19, "bold")
).pack(pady=12)

form = tk.Frame(root)
form.pack(pady=8)

tk.Label(form, text="Roll Number:").grid(row=0, column=0, padx=6, pady=6)
roll_entry = tk.Entry(form)
roll_entry.grid(row=0, column=1, padx=6, pady=6)

tk.Label(form, text="Date (YYYY-MM-DD):").grid(
    row=1, column=0, padx=6, pady=6
)
date_entry = tk.Entry(form)
date_entry.insert(0, date.today().isoformat())
date_entry.grid(row=1, column=1, padx=6, pady=6)

tk.Label(form, text="Status:").grid(row=2, column=0, padx=6, pady=6)
status_var = tk.StringVar(value="P")
ttk.Combobox(
    form, textvariable=status_var,
    values=["P", "A"], state="readonly", width=17
).grid(row=2, column=1, padx=6, pady=6)

tk.Button(
    root, text="Save Attendance", command=mark_attendance
).pack(pady=8)

columns = ("Roll No", "Name", "Present", "Total Days", "Percentage")
table = ttk.Treeview(root, columns=columns, show="headings", height=7)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=130, anchor="center")

table.pack(padx=12, pady=10, fill="x")

tk.Label(root, text="Ask OpenAI about attendance").pack(pady=5)
question_entry = tk.Entry(root, width=65)
question_entry.pack(pady=5)

tk.Button(
    root, text="Ask OpenAI", command=ask_openai
).pack(pady=8)

refresh_table()
root.mainloop()