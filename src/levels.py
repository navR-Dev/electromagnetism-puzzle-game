import os
import json
import time
import platform

LEVEL_COUNT = 30
PROGRESS_FILE = "progress.json"

LEVELS = {
    "1": {
        "id": 1,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 100, 20, 200), (400, 200, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "2": {
        "id": 2,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 200, 300, 20), (500, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "3": {
        "id": 3,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (300, 100, 20, 300), (200, 400, 400, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "4": {
        "id": 4,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (150, 150, 20, 300), (600, 200, 150, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "5": {
        "id": 5,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (250, 100, 300, 20), (300, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "6": {
        "id": 6,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 100, 20, 400), (600, 200, 100, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "7": {
        "id": 7,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 200, 400, 20), (400, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "8": {
        "id": 8,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (300, 100, 20, 300), (500, 300, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "9": {
        "id": 9,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (150, 200, 300, 20), (400, 400, 20, 150)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "10": {
        "id": 10,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 100, 20, 300), (300, 300, 300, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "11": {
        "id": 11,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 150, 400, 20), (500, 200, 20, 300)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "12": {
        "id": 12,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (300, 100, 20, 400), (400, 400, 300, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "13": {
        "id": 13,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 200, 300, 20), (300, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "14": {
        "id": 14,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 100, 20, 300), (600, 200, 100, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "15": {
        "id": 15,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (250, 150, 300, 20), (400, 300, 20, 250)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "16": {
        "id": 16,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (150, 200, 20, 300), (500, 100, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "17": {
        "id": 17,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 100, 400, 20), (300, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "18": {
        "id": 18,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 200, 20, 300), (600, 300, 150, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "19": {
        "id": 19,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (300, 100, 300, 20), (400, 400, 20, 150)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "20": {
        "id": 20,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 200, 20, 300), (500, 100, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "21": {
        "id": 21,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 150, 400, 20), (400, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "22": {
        "id": 22,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (300, 100, 20, 400), (500, 200, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "23": {
        "id": 23,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 200, 300, 20), (400, 400, 20, 150)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "24": {
        "id": 24,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 100, 20, 300), (600, 200, 100, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "25": {
        "id": 25,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (250, 150, 300, 20), (300, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "26": {
        "id": 26,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (150, 200, 20, 300), (500, 100, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "27": {
        "id": 27,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 100, 400, 20), (400, 300, 20, 200)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "28": {
        "id": 28,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (100, 200, 20, 300), (600, 300, 150, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "29": {
        "id": 29,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": 50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (300, 100, 300, 20), (400, 400, 20, 150)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    },
    "30": {
        "id": 30,
        "goal_area": (600, 450),
        "start_pos": (50, 50),
        "game_charge_val": -50,
        "walls": [
            (0, 0, 800, 20), (0, 580, 800, 20), (0, 0, 20, 600), (780, 0, 20, 600),
            (200, 200, 20, 300), (500, 100, 200, 20)
        ],
        "completed": False,
        "time_taken": None,
        "start_time": None
    }
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