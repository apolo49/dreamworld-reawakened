import sys
import json
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore, uic

import extra_data
import load_save_gen5

ROOT_DIR = Path(__file__).resolve().parent

type_colors = {
    None:       "lightgray",
	"Normal":   "#ada594",
	"Fighting": "#a55239",
	"Flying":   "#9cadf7",
	"Poison":   "#b55aa5",
	"Ground":   "#d6b55a",
	"Rock":     "#bda55a",
	"Bug":      "#adbd21",
	"Ghost":    "#6363b5",
	"Steel":    "#adadc6",
	"Fire":     "#f75231",
	"Water":    "#399cff",
	"Grass":    "#7bce52",
	"Electric": "#ffc631",
	"Psychic":  "#ff73a5",
	"Ice":      "#5acee7",
	"Dragon":   "#7b63e7",
	"Dark":     "#735a4a"
}

class PkmnSpriteEntry(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, image_path, width, height, name):
        super().__init__()
        self.name = name
        
        original_pixmap = QtGui.QPixmap(image_path)
        
        scaled_pixmap = original_pixmap.scaled(
            width, height, 
            QtCore.Qt.KeepAspectRatio, 
            QtCore.Qt.FastTransformation
        )

        self.is_selected = False
        
        self.setPixmap(scaled_pixmap)
        self.setAlignment(QtCore.Qt.AlignCenter)

        self.default_style = "border: 3px solid #444; border-radius: 10px; background: white;"
        self.hover_style = "border: 3px solid #777; border-radius: 10px; background: #f0f0f0;"
        self.highlight_style = "border: 3px solid #4A90E2; border-radius: 10px; background: #dcecff;"

        self.setStyleSheet(self.default_style)

    def setSelected(self, is_selected):
        self.is_selected = is_selected

        if is_selected:
            self.setStyleSheet(self.highlight_style)
        else:
            self.setStyleSheet(self.default_style)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.name)

    def enterEvent(self, event):
        if not self.is_selected:
            self.setStyleSheet(self.hover_style)

    def leaveEvent(self, event):
        if not self.is_selected:
            self.setStyleSheet(self.default_style)

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(ROOT_DIR / "pkmn_manager.ui", self) 
        
        self.selected_sprite = None

        self.party_sprites = {}
        self.storage_sprites = {}
        
        self.partyGrid.setSpacing(1)
        self.storageGrid.setSpacing(1)

        self.selected_box = 1
        self.box_data.currentIndexChanged.connect(self.changeBox)

        self.ball_image = QtWidgets.QLabel()
        self.ball_image.setFixedWidth(24)
        self.species_info.insertWidget(2, self.ball_image)

        self.load_save.clicked.connect(self.select_save_file)

        self.send_DW.setEnabled(False)
        self.send_DW.clicked.connect(self.send_to_DW)

        self.setFixedSize(self.size())

        self.setStyleSheet("""
        QGroupBox {
            border: 1px solid #888;
            border-radius: 8px;
            margin-top: 10px;
            font-weight: bold;
            font-family: "Roboto";
            font-size: 18px;    
            background: #f5f5f5;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }
                           
        QLineEdit {
            font-family: "Monospace";
            font-size: 16px;
        }
                           
        QComboBox {
            font-family: "Monospace";
            font-size: 18px;
        }
        """)

    def select_save_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Save File",
            "",
            "Save Files (*.sav);;All Files (*)"
        )

        if file_path:
            self.save_path.setText(file_path)
            self.sf = load_save_gen5.SaveFile(file_path)
            self.tr_data = self.sf.trainer()

            self.box_data.clear()
            for i in range(self.sf.box_layout().num_boxes):
                name = self.sf.box_layout().get_box_name(i)
                self.box_data.addItem(f"#{i+1} — {name}")

            self.load_save.setEnabled(False)

            self.clear_layout(self.partyGrid)
            self.clear_layout(self.storageGrid)

            self.populate_party(self.partyGrid, 3, 2)
            self.populate_storage(self.storageGrid, 5, 6)

            self.init_trainer_data(self.tr_data)

    def init_trainer_data(self, trainer):
        self.save_trainer_name.setText(trainer.name)
        self.country.setText(trainer.country)
        self.region.setText(trainer.region if trainer.region else None)

        if trainer.country:
            self.country.setText(trainer.country)
            self.country.setStyleSheet("background: white;")
        else:
            self.country.setText(None)
            self.country.setStyleSheet("background: lightgray;")

        if trainer.region:
            self.region.setText(trainer.region)
            self.region.setStyleSheet("background: white;")
        else:
            self.region.setText(None)
            self.region.setStyleSheet("background: lightgray;")

        self.language.setText(extra_data.language[trainer.language])
        self.version.setText(extra_data.version[trainer.game])

        if trainer.gender == "Male":
            self.save_trainer_gender.setText("♂")
            self.save_trainer_gender.setStyleSheet("color: #3355FF;")
        elif trainer.gender == "Female":
            self.save_trainer_gender.setText("♀")
            self.save_trainer_gender.setStyleSheet("color: #FF77DD;")

        self.num_badges.setText(str(trainer.num_badges))

    def send_to_DW(self):
        grid_type, index = self.selected_sprite.name.split("_")
        index = int(index)
        
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)

        if grid_type == "party":
            pkmn = self.sf.get_party_pokemon(slot=index)

        elif grid_type == "storage":
            pkmn = self.sf.get_box_pokemon(box=self.selected_box, slot=index)

        SAVE_DATA_DIR = ROOT_DIR.parent / "save_data"

        with open(SAVE_DATA_DIR / "player_data.json", "r", encoding="UTF-8") as f:
            player_data = json.load(f)

        player_data["member"].update({
            "country_id": "220", #str(extra_data.country.index(self.tr_data.country)),
            "send_pokemon_count": player_data["member"]["send_pokemon_count"] + 1,
            "rom_id": self.tr_data.game,
            "rom_name": extra_data.version[self.tr_data.game],
            "player_badge_num": str(self.tr_data.num_badges),
            "alter_rom_name": self.tr_data.name,
            "langcode": self.tr_data.language,
            
            "pokemon_no": str(pkmn.natdex),
            "pokemon_name": pkmn.species,
            "form_no": str(pkmn.form),
            "type1": pkmn.type1,
            "type2": pkmn.type2,
        })

        pokemon_data = {
            "pokemon_no":        pkmn.natdex,
            "pokemon_name":      pkmn.species,
            "form_no":           str(pkmn.form),
            "type1":             pkmn.type1,
            "type2":             pkmn.type2,
            "pokemon_nickname":  pkmn.nickname,
            "oyaname":           pkmn.trainer_name,
            "level":             pkmn.level,
            "sex":               pkmn.gender,
            "personality":       pkmn.nature,
            "ball_name":         pkmn.ball
        }

        with open(SAVE_DATA_DIR / "player_data.json", "w+", encoding="UTF-8") as f:
            f.write(json.dumps(player_data, indent=2, ensure_ascii=False))

        with open(SAVE_DATA_DIR / "sleeping_pokemon.json", "w+", encoding="UTF-8") as f:
            f.write(json.dumps(pokemon_data, indent=2, ensure_ascii=False))

        self.send_DW.setEnabled(False)
        self.done.setText("Done!")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def changeBox(self):
        self.selected_box = self.box_data.currentIndex() + 1

        self.clear_layout(self.storageGrid)

        self.storage_sprites = {}
        self.selected_sprite = None

        self.populate_storage(self.storageGrid, 5, 6)

    def populate_party(self, layout, rows, cols):
        self.party_sprites = {}
        index = 0
        for r in range(rows):
            for c in range(cols):
                pkmn_data = self.sf.get_party_pokemon(slot=index)

                if pkmn_data.natdex == 0:
                    index += 1
                    continue

                form_str = ""
                if pkmn_data.form:
                    form_str = f"-{pkmn_data.form}"
                if (pkmn_data.natdex in (521, 592, 593) and pkmn_data.gender == 1):
                    form_str = "-1"
                
                sprite = PkmnSpriteEntry(str(ROOT_DIR / "sprites" / "pokemon" / f"{pkmn_data.natdex}{form_str}.png"), 64, 64, f"party_{index}")
                sprite.clicked.connect(self.on_sprite_clicked)
                layout.addWidget(sprite, r, c)

                self.party_sprites[index] = sprite
                index += 1
                

    def populate_storage(self, layout, rows, cols):
        self.storage_sprites = {}
        index = 0
        for r in range(rows):
            for c in range(cols):
                pkmn_data = self.sf.get_box_pokemon(box=self.selected_box, slot=index)

                if pkmn_data.natdex == 0:
                    index += 1
                    continue

                form_str = ""
                if pkmn_data.form:
                    form_str = f"-{pkmn_data.form}"
                if (pkmn_data.natdex in (521, 592, 593) and pkmn_data.gender == 1):
                    form_str = "-1"
                
                sprite = PkmnSpriteEntry(str(ROOT_DIR / "sprites" / "pokemon" / f"{pkmn_data.natdex}{form_str}.png"), 64, 64, f"storage_{index}")
                sprite.clicked.connect(self.on_sprite_clicked)
                layout.addWidget(sprite, r, c)

                self.storage_sprites[index] = sprite
                index += 1

    def on_sprite_clicked(self, name):
        grid_type, index = name.split("_")
        index = int(index)

        self.send_DW.setEnabled(True)
        
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)

        if grid_type == "party":
            self.selected_sprite = self.party_sprites.get(index)
            if self.selected_sprite:
                self.selected_sprite.setSelected(True)
                pkmn = self.sf.get_party_pokemon(slot=index)

        elif grid_type == "storage":
            self.selected_sprite = self.storage_sprites.get(index)
            if self.selected_sprite:
                self.selected_sprite.setSelected(True)
                pkmn = self.sf.get_box_pokemon(box=self.selected_box, slot=index)

        if self.selected_sprite:
            self.natdex.setText(f"{str(pkmn.natdex).zfill(3)}")
            self.species.setText(pkmn.species)

            self.ball_image.setPixmap(QtGui.QPixmap(str(ROOT_DIR / "sprites" / "balls" / f"{pkmn.ball}.png")))
            
            if pkmn.gender == 0:
                self.pkmn_gender.setText("♂")
                self.pkmn_gender.setStyleSheet("color: #3355FF;")
            elif pkmn.gender == 1:
                self.pkmn_gender.setText("♀")
                self.pkmn_gender.setStyleSheet("color: #FF77DD;")
            else:
                self.pkmn_gender.setText(None)
                self.pkmn_gender.setStyleSheet("color: black;")
            
            form_str = f"{pkmn.natdex}-{pkmn.form}"
            if form_str in extra_data.form_names:
                self.form.setText(extra_data.form_names[form_str])
                self.form.setStyleSheet("background: white;")
            else:
                self.form.setText(None)
                self.form.setStyleSheet("background: lightgray;")
            
            nickname = pkmn.nickname if pkmn.nickname != pkmn.species else None
            if nickname:
                self.nickname.setText(nickname)
                self.nickname.setStyleSheet("background: white;")
            else:
                self.nickname.setText(None)
                self.nickname.setStyleSheet("background: lightgray;")

            self.level.setText(str(pkmn.level))

            self.type1.setText(pkmn.type1)
            self.type1.setStyleSheet(f"background: {type_colors[pkmn.type1]};")

            self.type2.setText(pkmn.type2)
            self.type2.setStyleSheet(f"background: {type_colors[pkmn.type2]};")
            
            self.trainer_name.setText(pkmn.trainer_name)

            if pkmn.trainer_gender == "Male":
                self.trainer_gender.setText("♂")
                self.trainer_gender.setStyleSheet("color: #3355FF;")
            elif pkmn.trainer_gender == "Female":
                self.trainer_gender.setText("♀")
                self.trainer_gender.setStyleSheet("color: #FF77DD;")

            self.nature.setText(pkmn.nature)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())