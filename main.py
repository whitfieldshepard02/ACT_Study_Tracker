import customtkinter as ctk
import json, os
from datetime import date, datetime, timedelta
import calendar
import matplotlib.pyplot as plt

DATA_FILE = "act_data.json"

# ---------------------------
# Data Layer
# ---------------------------
def default_data():
    return {
        "tasks": {},
        "streak": 0,
        "last_completed": None,
        "act_date": None
    }

def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return default_data()

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ---------------------------
# State
# ---------------------------
current_year = date.today().year
current_month = date.today().month
selected_date = str(date.today())

# ---------------------------
# Logic
# ---------------------------
def get_tasks(day):
    return data["tasks"].get(day, [])

def add_task(task_type="task"):
    name = task_entry.get()
    if not name:
        return

    task = {
        "name": name,
        "done": False,
        "type": task_type
    }

    if task_type == "test":
        try:
            task["score"] = int(score_entry.get())
        except:
            task["score"] = None

    data["tasks"].setdefault(selected_date, [])
    data["tasks"][selected_date].append(task)

    task_entry.delete(0, "end")
    score_entry.delete(0, "end")
    save_data()
    refresh_tasks()

def toggle_task(i):
    tasks = get_tasks(selected_date)
    tasks[i]["done"] = not tasks[i]["done"]
    update_streak()
    save_data()
    refresh_tasks()

def update_streak():
    today = str(date.today())
    tasks = get_tasks(today)

    if tasks and all(t["done"] for t in tasks):
        if data["last_completed"] == str(date.today() - timedelta(days=1)):
            data["streak"] += 1
        elif data["last_completed"] != today:
            data["streak"] = 1
        data["last_completed"] = today

def set_act_day():
    data["act_date"] = selected_date
    save_data()
    update_act_label()
    draw_calendar()

def get_days_until_act():
    if not data["act_date"]:
        return None
    act = datetime.strptime(data["act_date"], "%Y-%m-%d").date()
    return (act - date.today()).days

def plot_scores():
    scores = []
    dates = []

    for d, tasks in data["tasks"].items():
        for t in tasks:
            if t["type"] == "test" and t.get("score") is not None:
                dates.append(d)
                scores.append(t["score"])

    if not scores:
        return

    plt.figure()
    plt.plot(dates, scores, marker='o')
    plt.xticks(rotation=45)
    plt.title("Practice ACT Scores")
    plt.tight_layout()
    plt.show()

# ---------------------------
# UI Setup
# ---------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1000x650")
app.title("ACT Tracker Pro")

# Layout
left = ctk.CTkFrame(app, width=300)
left.pack(side="left", fill="y", padx=10, pady=10)

right = ctk.CTkFrame(app)
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ---------------------------
# Calendar Header
# ---------------------------
header = ctk.CTkFrame(left)
header.pack(fill="x")

month_label = ctk.CTkLabel(header, text="", font=("Arial", 18))
month_label.pack(pady=5)

def change_month(delta):
    global current_month, current_year
    current_month += delta

    if current_month > 12:
        current_month = 1
        current_year += 1
    elif current_month < 1:
        current_month = 12
        current_year -= 1

    draw_calendar()

ctk.CTkButton(header, text="<", width=40, command=lambda: change_month(-1)).pack(side="left")
ctk.CTkButton(header, text=">", width=40, command=lambda: change_month(1)).pack(side="right")

# ---------------------------
# Calendar Grid
# ---------------------------
calendar_frame = ctk.CTkFrame(left)
calendar_frame.pack(fill="both", expand=True)

def select_day(day):
    global selected_date
    selected_date = f"{current_year}-{current_month:02d}-{day:02d}"
    refresh_tasks()
    update_act_label()

def draw_calendar():
    for widget in calendar_frame.winfo_children():
        widget.destroy()

    month_label.configure(text=f"{calendar.month_name[current_month]} {current_year}")

    for i, d in enumerate(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]):
        ctk.CTkLabel(calendar_frame, text=d).grid(row=0, column=i)

    cal = calendar.monthcalendar(current_year, current_month)

    for r, week in enumerate(cal, start=1):
        for c, day in enumerate(week):
            if day == 0:
                continue

            date_str = f"{current_year}-{current_month:02d}-{day:02d}"

            btn = ctk.CTkButton(
                calendar_frame,
                text=str(day),
                width=40,
                command=lambda d=day: select_day(d)
            )

            today = date.today()

            if data.get("act_date") == date_str:
                btn.configure(fg_color="red")

            elif (day == today.day and
                  current_month == today.month and
                  current_year == today.year):
                btn.configure(fg_color="green")

            btn.grid(row=r, column=c, padx=3, pady=3)

draw_calendar()

# ---------------------------
# Task Panel
# ---------------------------
ctk.CTkLabel(right, text="Tasks", font=("Arial", 20)).pack(pady=10)

task_entry = ctk.CTkEntry(right, placeholder_text="Task or 'Practice ACT'")
task_entry.pack(pady=5)

score_entry = ctk.CTkEntry(right, placeholder_text="Score (only for practice ACT)")
score_entry.pack(pady=5)

ctk.CTkButton(right, text="Add Task", command=lambda: add_task("task")).pack(pady=3)
ctk.CTkButton(right, text="Add Practice ACT", command=lambda: add_task("test")).pack(pady=3)

ctk.CTkButton(right, text="Set as ACT Day", fg_color="red", command=set_act_day).pack(pady=5)

act_label = ctk.CTkLabel(right, text="")
act_label.pack()

def update_act_label():
    if data["act_date"]:
        countdown = get_days_until_act()
        act_label.configure(text=f"ACT Day: {data['act_date']} ({countdown} days left)")
    else:
        act_label.configure(text="No ACT Day set")

update_act_label()

# Task List
task_frame = ctk.CTkFrame(right)
task_frame.pack(fill="both", expand=True, pady=10)

def refresh_tasks():
    for w in task_frame.winfo_children():
        w.destroy()

    tasks = get_tasks(selected_date)

    for i, t in enumerate(tasks):
        label = t["name"]

        if t["type"] == "test" and t.get("score") is not None:
            label += f" (Score: {t['score']})"

        cb = ctk.CTkCheckBox(
            task_frame,
            text=label,
            command=lambda i=i: toggle_task(i)
        )

        if t["done"]:
            cb.select()

        cb.pack(anchor="w", padx=10, pady=5)

refresh_tasks()

# ---------------------------
# Analytics
# ---------------------------
ctk.CTkButton(right, text="View Score Graph", command=plot_scores).pack(pady=5)

streak_label = ctk.CTkLabel(right, text=f"🔥 Streak: {data['streak']}")
streak_label.pack(pady=10)

# ---------------------------
# Run
# ---------------------------
app.mainloop()