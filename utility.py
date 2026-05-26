#!/usr/bin/env python3
import json
import time
import utility
from typing import List
from pathlib import Path
from random import choice
from random import randint
from enum import Enum, auto
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent

# --------------------
# Special handler for main.swf injection
# --------------------

def build_swf_params() -> dict:
    player_data = utility.read_player_data()
    return {
        "json": json.dumps({
            "member": player_data["member"],
            "token":  player_data.get("token", ""),
            "medals": player_data.get("medals", []),
        }),
        "v":             "2.0",
        "api_host_name": "/api/",
        "page":          "SITE_PDW",
        "lang":          utility.player_language+".",
    }

# --------------------
# Helper data
# --------------------

language = {
    1: "ja",
    2: "en",
    3: "fr",
    4: "it",
    5: "de",
    7: "es",
    8: "ko"
}

with open(ROOT_DIR / "json_data" / "items.json", encoding="UTF-8") as f:
    item_info = json.load(f)

with open(ROOT_DIR / "json_data" / "pokemon.json", encoding="UTF-8") as f:
    pokemon_info = json.load(f)

with open(ROOT_DIR / "json_data" / "dream_islands.json", encoding="UTF-8") as f:
    area_info = json.load(f)

with open(ROOT_DIR / "json_data" / "berries.json", encoding="UTF-8") as f:
    berry_data = json.load(f)

# --------------------
# Helper functions
# --------------------

class PlayerStatus(Enum):
    AWAKE = 0
    SLEEPING = auto()
    DREAMING = auto()
    WAKE_READY = auto()

def generate_otoken():
    player_data = read_player_data()
    return f"{randint(1, 99)}dwt{player_data['member']['world_id']}{int(time.time()):x}.{randint(10000000, 99999999)}"

def date_to_unix(datetime_string: str):
    return datetime.strptime(datetime_string, "%Y-%m-%d").timestamp()

def get_random_pokemon(restriction_list: list[int] | None = None) -> dict[str: str|None]:
    """Retrieves a random Pokémon's data from `pokemon.json`.

    Args:
        restriction_list: An optional list of National Dex numbers to restrict
            the pool of possible Pokémon. If None, all Pokémon are eligible.

    Returns:
        A dictionary containing the randomly selected Pokémon's data.
        National Dex number is included as 'pokemon_no'.
    """

    if restriction_list is None:
        pkmn_options = [i for i in list(pokemon_info)]
    else:
        pkmn_options = [i for i in list(pokemon_info) if int(i.split("-")[0]) in restriction_list]

    pkmn = choice(pkmn_options)
    natdex = pkmn.split("-")[0]

    return {**pokemon_info[pkmn], "pokemon_no": natdex}

# --------------------
# Save data manager classes
# --------------------

class ChestManager:
    """Manages the player's Treasure Chest.

    Attributes:
        data: A dictionary containing the loaded chest inventory data.
    """

    def __init__(self, data_path):
        self._path = data_path
        with open(self._path, encoding="UTF-8") as f:
            self.data = json.load(f)

    def localize_names(self):
        for item in self.data["list"]:
            item_desc = lookup_str("item_descriptions", item["pokeitem_id"])

            item["pokeitem"] = lookup_str("item", item["pokeitem_id"])

            item["field_line1"] = item_desc[0]
            item["field_line2"] = item_desc[1]
            item["field_line3"] = item_desc[2]

        self.save()

    def save(self):
        with open(self._path, "w", encoding="UTF-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def fetch_item_by_id(self, item_id):
        return next((item for item in self.data["list"] if item["pokeitem_id"] == item_id), None)

    def add_item(self, item_id, count):
        current_date = datetime.now().strftime("%Y-%m-%d")

        chest_item = self.fetch_item_by_id(item_id)

        if chest_item:
            chest_item["item_cnt"] += count
            chest_item["date"] = current_date

        else:
            curr_item_info = item_info[str(item_id)]
            self.data["cnt"] += 1

            item_desc = lookup_str("item_descriptions", item_id)
            new_item = {
                "pokeitem_id": item_id,
                "pokeitem": lookup_str("item", item_id),
                "item_cnt": count,
                "bunrui_no": curr_item_info["first_sort"],
                "b_hozon_sentou": curr_item_info["second_sort"],
                "date": current_date,
                "field_line1": item_desc[0],
                "field_line2": item_desc[1],
                "field_line3": item_desc[2]
            }
            self.data["list"].append(new_item)

        self.save()

    def remove_item(self, item_id, count):
        current_date = datetime.now().strftime("%Y-%m-%d")
        chest_item = self.fetch_item_by_id(item_id)

        chest_item["item_cnt"] -= count
        chest_item["date"] = current_date

        if chest_item["item_cnt"] <= 0:
            item_index = self.data["list"].index(chest_item)
            del self.data["list"][item_index]
            self.data["cnt"] -= 1

        self.save()


class CropManager:
    """Manages the player's Berry garden.

    Attributes:
        data: A dictionary containing the loaded Berry plot data.
    """

    def __init__(self, data_path):
        self._path = data_path
        with open(self._path, encoding="UTF-8") as f:
            self.data = json.load(f)

    def localize_names(self):
        for crop in self.data["croft_list"]:
            if "pokeitem_id" not in crop:
                continue

            berry_desc = lookup_str("item_descriptions", crop["pokeitem_id"])

            crop["kinomi"] = lookup_str("item", crop["pokeitem_id"])

            crop["desc1"] = berry_desc[0]
            crop["desc2"] = berry_desc[1]
            crop["desc3"] = berry_desc[2]

        self.save()

    def save(self):
        with open(self._path, "w", encoding="UTF-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def fetch_plot_by_id(self, my_croft_id):
        return next((p for p in self.data["croft_list"] if p["my_croft_id"] == my_croft_id), None)

    def water_plot(self, my_croft_id):
        plot = self.fetch_plot_by_id(my_croft_id)
        plot["dirt_hp"] = 100

        self.save()

    def sow(self, my_croft_id, pokeitem_id):
        plot = self.fetch_plot_by_id(my_croft_id)

        current_time = round(time.time())

        berry_id = pokeitem_id - 148

        berry_desc = lookup_str("item_descriptions", pokeitem_id)
        plot.update({
            "my_croft_id": my_croft_id,
            "pokeitem_id": pokeitem_id,
            "kinomi": item_info[pokeitem_id]["item_name"],
            "kinomi_id": berry_id,
            "dirt_hp": 100,
            "desc1": berry_desc[0],
            "desc2": berry_desc[1],
            "desc3": berry_desc[2],
            "kinomi_state": 0,
            "x": plot["x"],
            "y": plot["y"],
            "server": {"planted_time": current_time, "last_update_time": current_time, "yield": berry_data[berry_id]["max_yield"]}
        })

        self.save()

    def harvest(self, my_croft_id):
        plot = self.fetch_plot_by_id(my_croft_id)
        plot_index = self.data["croft_list"].index(plot)

        harvest_data = {
            "kinomi_id": plot["kinomi_id"],
            "kinomi": plot["kinomi"],
            "pokeitem_id": plot["pokeitem_id"],
            "count": plot["server"]["yield"]
        }

        self.data["croft_list"][plot_index] = {"my_croft_id": my_croft_id, "x": plot["x"], "y": plot["y"]}

        self.save()

        return harvest_data

    def process_berry_growth(self):
        current_time = round(time.time())

        for plant in self.data["croft_list"]:
            if "dirt_hp" not in plant:
                continue

            curr_berry_data = berry_data[str(plant["kinomi_id"])]

            hours_since_planted = (current_time - plant["server"]["planted_time"]) // 3600
            hours_since_update = (current_time - plant["server"]["last_update_time"]) // 3600

            hours_at_last_update = hours_since_planted - hours_since_update

            single_stage_time = curr_berry_data["grow_time"] / 4

            for hour in range(1, hours_since_update + 1):
                total_hours = hours_at_last_update + hour
                plant["kinomi_state"] = min(total_hours // single_stage_time, 4)

                if plant["dirt_hp"] == 0: #remove 1/5th of the berry's max, but no lower than 2 berries
                    plant["server"]["yield"] = max(plant["server"]["yield"] - (curr_berry_data["max_yield"] * 0.2), 2)
                else:
                    plant["dirt_hp"] -= curr_berry_data["drain_rate"]

            if plant["dirt_hp"] < 0:
                plant["dirt_hp"] = 0

            plant["server"]["last_update_time"] = current_time

        self.save()

# --------------------
# Save data
# --------------------

def read_player_data():
    with open(ROOT_DIR / "save_data" / "player_data.json", encoding="UTF-8") as f:
        return json.load(f)

def write_player_data(data: dict):
    player_data = read_player_data()
    player_data["member"].update(data)
    with open(ROOT_DIR / "save_data" / "player_data.json", "w", encoding="UTF-8") as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)

def read_entralink_data(param: str):
    with open(ROOT_DIR / "save_data" / "game_sync.json", encoding="UTF-8") as f:
        return json.load(f).get(param, [])

def write_entralink_data(data: List[dict], data_type: str):
    with open(ROOT_DIR / "save_data" / "game_sync.json", encoding="UTF-8") as f:
        game_sync = json.load(f)

    game_sync[data_type] = data

    with open(ROOT_DIR / "save_data" / "game_sync.json", "w", encoding="UTF-8") as f:
        json.dump(game_sync, f, indent=2, ensure_ascii=False)

with open(ROOT_DIR / "save_data" / "sleeping_pokemon.json", encoding="UTF-8") as f:
    sleeping_pokemon = json.load(f)

player_language = language[read_player_data()["member"]["langcode"]]

chest = ChestManager(ROOT_DIR / "save_data" / "chest_data.json")

crops = CropManager(ROOT_DIR / "save_data" / "crop_data.json")

# --------------------
# Manage Game Sync data
# --------------------

def update_gamesync_status(status: PlayerStatus):
    game_sync_file = ROOT_DIR / "save_data" / "game_sync.json"

    if not game_sync_file.exists():
        raise FileNotFoundError("A sleeping Pokémon must be tucked to bed first.")

    write_player_data({"play_status": status.value})

# --------------------
# Init text lookup dict
# --------------------

def lookup_str(str_type: str, index: int):
    try:
        return raw_text[player_language][str_type][index]
    except KeyError:
        return None

raw_text = {k: {} for k in language.values()}
for folder in (ROOT_DIR / "raw_text").iterdir():
    for file in folder.iterdir():
        with open(ROOT_DIR / "raw_text" / folder.stem / file, "r", encoding="UTF-8") as f:
            strings = f.read().splitlines()

        if file.stem.endswith("_descriptions"):
            raw_text[folder.stem][file.stem] = {}

            for i, val in enumerate(strings):
                string = val.split("\\n")
                res = [None, None, None]
                res[:len(string)] = string

                raw_text[folder.stem][file.stem][i] = res

        else:
            raw_text[folder.stem][file.stem] = {i: val for i, val in enumerate(strings)}