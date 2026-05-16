#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from urllib.parse import quote, unquote, parse_qs, urlencode

from server import run

import game_data

ROOT_DIR = Path(__file__).resolve().parent

def inject_htm_playerdata() -> None:
    """Inject player_data.json into Dream_Park.htm so it displays the correct information on the UI."""
    
    with open(ROOT_DIR / "save_data" / "player_data.json") as f:
        player_data = json.load(f)

    htm_file = ROOT_DIR / "DreamWorld_data" / "Dream_Park.htm"

    htm_data = bs(htm_file.read_text(), "html.parser")
    
    # entire player_data package
    flashvars_param = htm_data.find_all("param", attrs={"name": "flashvars"})[1]
    
    flashvars = unquote(flashvars_param.get("value"))
    flashvars = parse_qs(flashvars)
    flashvars["json"] = [json.dumps(player_data)]
    flashvars = urlencode(flashvars, doseq=True)

    flashvars_param["value"] = quote(flashvars)

    username_tag = htm_data.find("span", attrs={"id": "header-pglname"}).find_next("span")
    rom_name_tag = htm_data.find("span", attrs={"id": "header-romname"}).find_next("span")

    # username
    username_tag.string = player_data["member"]["pgl_name"]

    # rom name
    rom_name_tag.string = player_data["member"]["rom_name"]

    # profile picture
    pfp_tag = htm_data.find("div", attrs={"class": "logged-in"}).find_next("img")
    pfp_tag.attrs["src"] = f"Dream_Park_files/{player_data['member']['avator_id']}.png"

    htm_file.write_text(str(htm_data))

def write_entralinked_data(entralink_dir):
    version_language = {
        "WHITE_JAPANESE": (20, 1, "ポケットモンスター ホワイト"),
        "WHITE_ENGLISH":  (20, 2, "Pokémon White Version"),
        "WHITE_FRENCH":   (20, 3, "Pokémon Version Blanche"),
        "WHITE_ITALIAN":  (20, 4, "Pokémon Versione Bianca"),
        "WHITE_GERMAN":   (20, 5, "Pokémon Weiße Edition"),
        "WHITE_SPANISH":  (20, 7, "Pokémon Edición Blanca"),
        "WHITE_KOREAN":   (20, 8, "포켓몬스터 화이트"),

        "BLACK_JAPANESE": (21, 1, "ポケットモンスター ブラック"),
        "BLACK_ENGLISH":  (21, 2, "Pokémon Black Version"),
        "BLACK_FRENCH":   (21, 3, "Pokémon Version Noire"),
        "BLACK_ITALIAN":  (21, 4, "Pokémon Versione Nera"),
        "BLACK_GERMAN":   (21, 5, "Pokémon Schwarze Edition"),
        "BLACK_SPANISH":  (21, 7, "Pokémon Edición Negra"),
        "BLACK_KOREAN":   (21, 8, "포켓몬스터 블랙"),

        "WHITE_2_JAPANESE": (22, 1, "ポケットモンスター ホワイト２"),
        "WHITE_2_ENGLISH":  (22, 2, "Pokémon White Version 2"),
        "WHITE_2_FRENCH":   (22, 3, "Pokémon Version Blanche 2"),
        "WHITE_2_ITALIAN":  (22, 4, "Pokémon Versione Bianca 2"),
        "WHITE_2_GERMAN":   (22, 5, "Pokémon Weiße Edition 2"),
        "WHITE_2_SPANISH":  (22, 7, "Pokémon Edición Blanca 2"),
        "WHITE_2_KOREAN":   (22, 8, "포켓몬스터 화이트2"),

        "BLACK_2_JAPANESE": (23, 1, "ポケットモンスター ブラック２"),
        "BLACK_2_ENGLISH":  (23, 2, "Pokémon Black Version 2"),
        "BLACK_2_FRENCH":   (23, 3, "Pokémon Version Noire 2"),
        "BLACK_2_ITALIAN":  (23, 4, "Pokémon Versione Nera 2"),
        "BLACK_2_GERMAN":   (23, 5, "Pokémon Schwarze Edition 2"),
        "BLACK_2_SPANISH":  (23, 7, "Pokémon Edición Negra 2"),
        "BLACK_2_KOREAN":   (23, 8, "포켓몬스터 블랙2")
    }

    with open(Path(entralink_dir) / "data.json", "r") as f:
        data = json.load(f)

    with open(ROOT_DIR / "save_data" / "player_data.json") as f:
        player_data = json.load(f)

    with open(ROOT_DIR / "save_data" / "sleeping_pokemon.json") as f:
        sleeper_data = json.load(f)

    rom_id, langcode, rom_name = version_language[data["gameVersion"]]

    form_str = ""
    if data["dreamerInfo"]["form"]:
        form_str = f"-{data['dreamerInfo']['form']}"
    
    pkmn_info = game_data.pokemon_info[f"{data['dreamerInfo']['species']}{form_str}"]

    player_data["member"].update({ 
        "send_pokemon_count": player_data["member"]["send_pokemon_count"] + 1,
        "rom_id":             rom_id,
        "rom_name":           rom_name,
        #"player_badge_num":   "8",          #not currently tracked by Entralinked
        #"alter_rom_name":     "PlayerName", #not currently tracked by Entralinked
        "langcode":           langcode,
        "pokemon_no":         str(data["dreamerInfo"]["species"]),
        "pokemon_name":       pkmn_info["pokemon_name"],
        "form_no":            str(data["dreamerInfo"]["form"]),
        "type1":              pkmn_info["type1"],
        "type2":              pkmn_info["type2"],
        "gscd":               data["gameSyncId"]
    })

    pkmn_gender = (0 if data["dreamerInfo"]["gender"] == "MALE" else
                   1 if data["dreamerInfo"]["gender"] == "FEMALE" else 2)

    sleeper_data.update({
        "pokemon_no":        data["dreamerInfo"]["species"],
        "pokemon_name":      pkmn_info["pokemon_name"],
        "form_no":           str(data["dreamerInfo"]["form"]),
        "type1":             pkmn_info["type1"],
        "type2":             pkmn_info["type2"],
        "pokemon_nickname":  data["dreamerInfo"]["nickname"] if data["dreamerInfo"]["nickname"] != pkmn_info["pokemon_name"] else None,
        "oyaname":           data["dreamerInfo"]["trainerName"],
        "level":             data["dreamerInfo"]["level"],
        "sex":               pkmn_gender,
        "personality":       data["dreamerInfo"]["nature"].title(),
        #"ball_name":        "Cherish Ball" #not currently tracked by Entralinked
    })

    with open(ROOT_DIR / "save_data" / "player_data.json", "w") as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)

    with open(ROOT_DIR / "save_data" / "sleeping_pokemon.json", "w") as f:
        json.dump(sleeper_data, f, indent=2, ensure_ascii=False)

    game_data.player_data = player_data
    game_data.sleeping_pokemon = sleeper_data

def init_entralinked():
    entralinked_config = ROOT_DIR / "json_data" / "entralinked.json"

    if entralinked_config.exists():
        with open(entralinked_config, "r") as f:
            config = json.load(f)
            entralink_dir = config["entralink_dir"]
            print("ENTRALINKED: Loaded Entralinked path")

        return entralink_dir

    else:
        import tkinter as tk
        from tkinter.filedialog import askdirectory

        root = tk.Tk()
        root.withdraw()

        print("ENTRALINKED: Select the folder that contains entralinked.jar")
        entralink_root_dir = askdirectory(title="Select the folder that contains entralinked.jar")
        
        print("ENTRALINKED: Select the folder that corresponds to the Game Sync code")
        entralink_dir = askdirectory(title="Select the folder that corresponds to the Game Sync code", initialdir=Path(entralink_root_dir) / "players")

        if Path(entralink_dir).parts[-2] != "players":
            print("ENTRALINKED: Error selecting Entralinked data folder. Starting server normally.")
            return
        
        with open(entralinked_config, "w+") as f:
            json.dump({"entralink_dir":entralink_dir}, f, indent=2)
            print("ENTRALINKED: Saved Entralinked path")

        return entralink_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dream Park HTTP server")
    parser.add_argument("port", nargs="?", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--random", action="store_true", default=False)
    parser.add_argument("--run-webpage", action='store_true', default=False)
    parser.add_argument("--entralinked", action="store_true", help="Enable Entralinked support")
    args = parser.parse_args()

    if args.run_webpage:
        from bs4 import BeautifulSoup as bs
        inject_htm_playerdata()

    if args.entralinked:
        entralink_dir = init_entralinked()
        write_entralinked_data(entralink_dir)

    game_data.crops.process_berry_growth()
    
    run(port=args.port, debug=args.debug, is_random=args.random)