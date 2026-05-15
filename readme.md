# Pokemon Dream World - Reawakened

# Standalone startup
- Run `python3 main.py` in the terminal
    - Load http://127.0.0.1:8080/DreamWorld_data/src/swf/theme/assets/common/main.swf with the standalone Adobe Flash Player (download: [Windows](https://archive.org/download/standaloneflashplayers/fp/fp_32/32.0.0.465/flashplayer32_0r0_465_win_sa.exe), [Mac](https://archive.org/download/standaloneflashplayers/fp/fp_32/32.0.0.465/flashplayer32_0r0_465_mac_sa.dmg), [Linux](https://archive.org/download/standaloneflashplayers/fp/fp_32/32.0.0.465/flashplayer32_0r0_465_linux_sa.x86_64.tar.gz)); or
 
# Flash browser startup

**Ruffle will not work!!!**

- Run `main.py --run-webpage` if you want to run the game in browser
    - This requires you to run `pip install bs4` first
    - Access http://127.0.0.1:8080/ in a browser that supports Flash

# Save data manager
This requires the installation of PyQt5 with `pip install PyQt5`

If you open the terminal inside `save_data_manager` and run `python3 save_manager.py`, through a UI you can load a Gen5 save file (.sav only) and "send" a Pokémon to the Dream World. This will modify both `save_data/player_data.json` and `save_data/sleeping_pokemon.json`.

# Other Info

Save data will be pulled from the three files in `save_data`, and these can be edited as desired.

Save data that is currently managed by the server:
- Functionality related to Berries. Planting, watering, and harvesting work as expected. Berries will grow over time and their water level will deplete. When harvesting Berries, they will be placed in the player's Treasure Chest, which will be updated on disk as well.

