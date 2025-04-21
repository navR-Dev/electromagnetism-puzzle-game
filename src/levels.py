import os
import json
import time

LEVEL_COUNT = 30
PROGRESS_FILE = "progress.json"

LEVELS = [
    {
        "id": i + 1,
        "charges": [(100 + (i % 5) * 100, 100 + (i % 4) * 80)],
        "charge_vals": [50 if i % 2 == 0 else -50],
        "loops": [(400 + (i % 3) * 50, 300 + (i % 2) * 70)] if i % 3 == 0 else [],
        "goal_area": (600, 450, 50, 50),
        "start_time": None,
        "completed": False,
        "time_taken": None
    }
    for i in range(LEVEL_COUNT)
]

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            for i, d in enumerate(data):
                LEVELS[i]["completed"] = d.get("completed", False)
                LEVELS[i]["time_taken"] = d.get("time_taken", None)

def save_progress():
    data = [
        {
            "completed": level["completed"],
            "time_taken": level["time_taken"]
        } for level in LEVELS
    ]
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def start_level_timer(level_id):
    level = LEVELS[level_id - 1]
    level["start_time"] = time.time()

def end_level_timer(level_id):
    level = LEVELS[level_id - 1]
    if level["start_time"] is not None:
        level["time_taken"] = round(time.time() - level["start_time"], 2)
        level["completed"] = True
        level["start_time"] = None
        save_progress()

def reset_level(level_id):
    level = LEVELS[level_id - 1]
    level["start_time"] = time.time()
    # You can also reset charges/loops here if needed
    return level

def is_goal_reached(player_pos, goal_area):
    px, py = player_pos
    gx, gy, gw, gh = goal_area
    return gx <= px <= gx + gw and gy <= py <= gy + gh

def get_level(level_id):
    return LEVELS[level_id - 1] if 1 <= level_id <= LEVEL_COUNT else None

def get_completed_count():
    return sum(1 for lvl in LEVELS if lvl["completed"])

def reset_all_progress():
    for lvl in LEVELS:
        lvl["completed"] = False
        lvl["time_taken"] = None
        lvl["start_time"] = None
    save_progress()
