import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import date

FILE_NAME = "attendance.csv"


def load_records():
    records = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", newline="", encoding="utf-8") as file:
            records = list(csv.DictReader(file))
    return records


def save_attendance():
    name = name_entry.get().strip()
    roll = roll_entry.get().strip()
    status = status_var.get()

    if not name or not roll:
        messagebox.showwarning("Missing Details", "Enter name and roll number.")
        return

    today = date.today().isoformat()
    records = load_records()

    for record in records:
        if record["Date"] == today and record["Roll Number"] == roll:
            messagebox.showwarning(
                "Already Marked", "Attendance is already marked today."
            )
            return

    file_exists = os.path.exists(FILE_NAME)
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["Date", "Roll Number", "Name", "Status"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "Date": today,
            "Roll Number": roll,
            "Name": name,
            "Status": status
        })

    name_entry.delete(0, tk.END)
    roll_entry.delete(0, tk.END)
    refresh_records()
    messagebox.showinfo("Success", "Attendance saved successfully!")


def refresh_records():
    for item in table.get_children():
        table.delete(item)

    for record in reversed(load_records()):
        table.insert("", tk.END, values=(
            record["Date"],
            record["Roll Number"],
            record["Name"],
            record["Status"]
        ))


root = tk.Tk()
root.title("Attendance Management System")
root.geometry("800x550")
root.configure(bg="#f1f5f9")

tk.Label(
    root, text="Attendance Management System",
    font=("Arial", 20, "bold"), bg="#f1f5f9", fg="#1e3a8a"
).pack(pady=15)

form = tk.Frame(root, bg="#f1f5f9")
form.pack(pady=10)

tk.Label(form, text="Student Name:", bg="#f1f5f9").grid(
    row=0, column=0, padx=8, pady=8, sticky="w"
)
name_entry = tk.Entry(form, width=28)
name_entry.grid(row=0, column=1, padx=8, pady=8)

tk.Label(form, text="Roll Number:", bg="#f1f5f9").grid(
    row=1, column=0, padx=8, pady=8, sticky="w"
)
roll_entry = tk.Entry(form, width=28)
roll_entry.grid(row=1, column=1, padx=8, pady=8)

tk.Label(form, text="Attendance:", bg="#f1f5f9").grid(
    row=2, column=0, padx=8, pady=8, sticky="w"
)
status_var = tk.StringVar(value="Present")
ttk.Combobox(
    form, textvariable=status_var, values=["Present", "Absent"],
    state="readonly", width=25
).grid(row=2, column=1, padx=8, pady=8)

tk.Button(
    root, text="Save Attendance", command=save_attendance,
    bg="#2563eb", fg="white", font=("Arial", 11, "bold"),
    padx=12, pady=6
).pack(pady=10)

tk.Label(
    root, text="Attendance Records",
    font=("Arial", 14, "bold"), bg="#f1f5f9"
).pack(pady=8)

columns = ("Date", "Roll Number", "Name", "Status")
table = ttk.Treeview(root, columns=columns, show="headings", height=10)

for column in columns:
    table.heading(column, text=column)
    table.column(column, width=170, anchor="center")

table.pack(padx=15, pady=10, fill="both", expand=True)
refresh_records()
root.mainloop()