import os
import json
import time
import platform

LEVEL_COUNT = 30
PROGRESS_FILE = "progress.json"

LEVELS = {
    "1": {
        "id": 1,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": 50,
        "walls": [
            [0, 0, 800, 20],  # Top
            [0, 580, 800, 20],  # Bottom
            [0, 0, 20, 600],  # Left
            [780, 0, 20, 600],  # Right
            [200, 100, 400, 20],  # Horizontal barrier
            [300, 200, 20, 300],  # Vertical wall to force charge placement
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "2": {
        "id": 2,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": -50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 100, 600, 20],  # Top barrier
            [100, 480, 600, 20],  # Bottom barrier
            [350, 120, 20, 360],  # Central vertical wall with gap
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "3": {
        "id": 3,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": 50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 200, 20, 300],  # Left vertical
            [200, 100, 500, 20],  # Top horizontal
            [680, 120, 20, 360],  # Right vertical
            [200, 480, 480, 20],  # Bottom horizontal
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "4": {
        "id": 4,
        "goal_area": [400, 300],
        "start_pos": [50, 50],
        "game_charge_val": -50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 100, 600, 20],  # Top
            [100, 480, 600, 20],  # Bottom
            [350, 120, 20, 100],  # Top vertical
            [350, 380, 20, 100],  # Bottom vertical
            [300, 280, 100, 20],  # Central horizontal barrier
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "5": {
        "id": 5,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": 50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [200, 100, 20, 400],  # Left vertical
            [580, 100, 20, 400],  # Right vertical
            [220, 300, 360, 20],  # Central horizontal
            [300, 200, 20, 100],  # Upper vertical stub
            [500, 320, 20, 100],  # Lower vertical stub
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "6": {
        "id": 6,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": -50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 100, 20, 400],  # Left vertical
            [680, 100, 20, 400],  # Right vertical
            [120, 250, 560, 20],  # Central horizontal
            [300, 100, 20, 150],  # Upper left vertical
            [500, 270, 20, 230],  # Lower right vertical
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "7": {
        "id": 7,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": 50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [200, 100, 400, 20],  # Top horizontal
            [200, 480, 400, 20],  # Bottom horizontal
            [300, 120, 20, 360],  # Left vertical
            [500, 120, 20, 360],  # Right vertical
            [350, 250, 100, 20],  # Central horizontal
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "8": {
        "id": 8,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": -50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 100, 600, 20],  # Top horizontal
            [100, 480, 600, 20],  # Bottom horizontal
            [350, 120, 20, 360],  # Central vertical
            [200, 250, 150, 20],  # Left horizontal
            [400, 330, 150, 20],  # Right horizontal
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "9": {
        "id": 9,
        "goal_area": [750, 550],
        "start_pos": [50, 50],
        "game_charge_val": 50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 200, 20, 300],  # Left vertical
            [680, 200, 20, 300],  # Right vertical
            [120, 100, 560, 20],  # Top horizontal
            [120, 480, 560, 20],  # Bottom horizontal
            [300, 200, 200, 20],  # Central horizontal
            [400, 300, 20, 180],  # Central vertical
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "10": {
        "id": 10,
        "goal_area": [400, 300],
        "start_pos": [50, 50],
        "game_charge_val": -50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [100, 100, 300, 20],  # Top left
            [500, 100, 200, 20],  # Top right
            [100, 480, 300, 20],  # Bottom left
            [500, 480, 200, 20],  # Bottom right
            [200, 120, 20, 360],  # Left vertical
            [600, 120, 20, 360],  # Right vertical
            [300, 250, 200, 20],  # Central horizontal
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
}

# Placeholder levels 11-30 to maintain compatibility
for i in range(11, 31):
    LEVELS[str(i)] = {
        "id": i,
        "goal_area": [750 - (i-1)*5, 550 - (i-1)*3],
        "start_pos": [50 + (i-11)*2, 50 + (i-11)*2],
        "game_charge_val": 50 if i % 2 == 1 else -50,
        "walls": [
            [0, 0, 800, 20],
            [0, 580, 800, 20],
            [0, 0, 20, 600],
            [780, 0, 20, 600],
            [200 + (i-11)*10, 100, 20, 80],
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    }

def load_progress():
    if platform.system() != "Emscripten" and os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            for level_id, d in data.items():
                if level_id in LEVELS:
                    LEVELS[level_id]["completed"] = d.get("completed", False)
                    LEVELS[level_id]["time_taken"] = d.get("time_taken", None)

def save_progress():
    if platform.system() != "Emscripten":
        data = {
            level_id: {
                "completed": level["completed"],
                "time_taken": level["time_taken"]
            } for level_id, level in LEVELS.items()
        }
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f, indent=2)

def start_level_timer(level_id):
    level = LEVELS[str(level_id)]
    level["start_time"] = time.time()

def end_level_timer(level_id):
    level = LEVELS[str(level_id)]
    if level["start_time"] is not None:
        level["time_taken"] = round(time.time() - level["start_time"], 2)
        level["completed"] = True
        level["start_time"] = None
        save_progress()

def reset_level(level_id):
    level = LEVELS[str(level_id)]
    level["start_time"] = time.time()
    return level

def get_level(level_id):
    return LEVELS.get(str(level_id))

def get_completed_count():
    return sum(1 for lvl in LEVELS.values() if lvl["completed"])

def reset_all_progress():
    for lvl in LEVELS.values():
        lvl["completed"] = False
        lvl["time_taken"] = None
        lvl["start_time"] = None
    save_progress()