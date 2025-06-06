import sys
import json
import os
from PyQt5 import QtWidgets

adresy = "adresy.json"

class ksiazka_adresowa:
    def __init__(self):
        self.adres = []
        self.wczytanie()

    def wczytanie(self):
        if os.path.exists(adresy):
            with open(adresy, "r", encoding="utf-8") as f:
                self.adres = json.load(f)
        else:
            self.adres = []

    def zapisanie(self):
        with open(adresy, "w", encoding="utf-8") as f:
            json.dump(self.adres, f, ensure_ascii=False, indent=2)

    def dodawanie_adresu(self, address):
        for a in self.adres:
            if a["Imię"].lower() == address["Imię"].lower() and a["Nazwisko"].lower() == address["Nazwisko"].lower():
                return False
        self.adres.append(address)
        self.zapisanie()
        return True

    def usun_adres(self, index):
        if 0 <= index < len(self.adres):
            del self.adres[index]
            self.zapisanie()

    def szukanie(self, key, value):
        return [a for a in self.adres if value.lower() in a.get(key, "").lower()]

    def sortowanie(self, key):
        self.adres.sort(key=lambda x: x.get(key, "").lower())
        self.zapisanie()

    def statystyka_miasta(self):
        statystyka = {}
        for a in self.adres:
            city = a.get("Miasto", "")
            statystyka[city] = statystyka.get(city, 0) + 1
        return statystyka

class ksiazka_adresowaApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ksiazka = ksiazka_adresowa()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Książka adresowa")
        self.resize(800, 500)

        self.inputs = {}
        form_uklad = QtWidgets.QFormLayout()
        for field in ["Imię", "Nazwisko", "Telefon", "Ulica", "Miasto"]:
            self.inputs[field] = QtWidgets.QLineEdit()
            form_uklad.addRow(field + ":", self.inputs[field])

        self.add_btn = QtWidgets.QPushButton("Dodaj")
        self.add_btn.clicked.connect(self.dodawanie_adresu)
        form_uklad.addRow(self.add_btn)

        self.list_widget = QtWidgets.QListWidget()
        self.odswiezanie()

        self.remove_btn = QtWidgets.QPushButton("Usuń zaznaczony")
        self.remove_btn.clicked.connect(self.usuwanie)

        self.szukanie_field = QtWidgets.QComboBox()
        self.szukanie_field.dodajs(["Imię", "Nazwisko", "Telefon", "Ulica", "Miasto"])
        self.szukanie_input = QtWidgets.QLineEdit()
        self.szukanie_btn = QtWidgets.QPushButton("Szukaj")
        self.szukanie_btn.clicked.connect(self.szukanie)
        self.reset_btn = QtWidgets.QPushButton("Resetuj")
        self.reset_btn.clicked.connect(self.odswiezanie)

        szukanie_uklad = QtWidgets.QHBoxLayout()
        szukanie_uklad.addWidget(self.szukanie_field)
        szukanie_uklad.addWidget(self.szukanie_input)
        szukanie_uklad.addWidget(self.szukanie_btn)
        szukanie_uklad.addWidget(self.reset_btn)

        self.sort_name_btn = QtWidgets.QPushButton("Sortuj wg imienia")
        self.sort_name_btn.clicked.connect(lambda: self.sortowanie("Imię"))
        self.sort_surname_btn = QtWidgets.QPushButton("Sortuj wg nazwiska")
        self.sort_surname_btn.clicked.connect(lambda: self.sortowanie("Nazwisko"))

        sort_uklad = QtWidgets.QHBoxLayout()
        sort_uklad.addWidget(self.sort_name_btn)
        sort_uklad.addWidget(self.sort_surname_btn)

        self.statystyka_btn = QtWidgets.QPushButton("Statystyka miast")
        self.statystyka_btn.clicked.connect(self.statystyki)

        main_uklad = QtWidgets.QVBoxLayout()
        main_uklad.addLayout(form_uklad)
        main_uklad.addLayout(szukanie_uklad)
        main_uklad.addWidget(self.list_widget)
        main_uklad.addWidget(self.remove_btn)
        main_uklad.addLayout(sort_uklad)
        main_uklad.addWidget(self.statystyka_btn)
        self.setLayout(main_uklad)

    def dodawanie_adresu(self):
        address = {field: self.inputs[field].text().strip() for field in self.inputs}
        if not address["Imię"] or not address["Nazwisko"]:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Imię i nazwisko są wymagane.")
            return
        if not self.ksiazka.dodawanie_adresu(address):
            QtWidgets.QMessageBox.warning(self, "Błąd", "Adres dla tego użytkownika już istnieje.")
            return
        self.odswiezanie()
        for field in self.inputs:
            self.inputs[field].clear()

    def odswiezanie(self, adres=None):
        if adres is None or not isinstance(adres, list):
            adres = self.ksiazka.adres if isinstance(self.ksiazka.adres, list) else []
        self.list_widget.clear()
        for a in adres:
            self.list_widget.dodaj(f"{a['Imię']} {a['Nazwisko']}, tel: {a['Telefon']}, {a['Ulica']}, {a['Miasto']}")

    def usuwanie(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.ksiazka.usun_adres(row)
            self.odswiezanie()

    def szukanie(self):
        key = self.szukanie_field.currentText()
        value = self.szukanie_input.text().strip()
        if value:
            results = self.ksiazka.szukanie(key, value)
            self.odswiezanie(results)

    def sortowanie(self, key):
        self.ksiazka.sortowanie(key)
        self.odswiezanie()

    def statystyki(self):
        statystyka = self.ksiazka.statystyka_miasta()
        msg = "\n".join([f"{city}: {count}" for city, count in statystyka.items()])
        QtWidgets.QMessageBox.information(self, "Statystyka miast", msg or "Brak danych.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ksiazka_adresowaApp()
    window.show()
    sys.exit(app.exec_())