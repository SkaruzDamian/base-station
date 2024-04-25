import os
import tkinter as tk
from tkinter import ttk
import random
import math
import time

class SymulacjaKolejki(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stacja bazowa")
        self.geometry("1200x1200")
        self.entry_widgets = []
        self.kanaly = []

        self.tworz_widgety()

    def tworz_widgety(self):
        self.ramka_parametrow = tk.LabelFrame(self, text="Parametry")
        self.ramka_parametrow.pack(pady=10, padx=10)

        self.dodaj_pole_parametru("Liczba kanałów", 10)
        self.dodaj_pole_parametru("Długość kolejki", 10)
        self.dodaj_pole_parametru("Natężenie ruchu [lambda]", 1.0)
        self.dodaj_pole_parametru("Średni czas rozmowy", 20.0)
        self.dodaj_pole_parametru("Odchylenie standardowe", 5.0)
        self.dodaj_pole_parametru("Minimalny czas rozmowy", 10.0)
        self.dodaj_pole_parametru("Maksymalny czas rozmowy", 30.0)
        self.dodaj_pole_parametru("Czas symulacji", 30.0)

        self.ramka_kanalow = tk.LabelFrame(self, text="Kanały")
        self.ramka_kanalow.pack(pady=10, padx=10)

        self.ramka_wynikow = tk.LabelFrame(self, text="Wyniki")
        self.ramka_wynikow.pack(pady=10, padx=10)

        self.tekst_wynikow = tk.Text(self.ramka_wynikow, height=8, width=50)
        self.tekst_wynikow.pack()

        self.przycisk_start = tk.Button(self, text="Start", command=self.uruchom_symulacje)
        self.przycisk_start.pack(pady=5)

        self.przycisk_pauzy = tk.Button(self, text="Pauza", command=self.pauzuj_symulacje, state=tk.DISABLED)
        self.przycisk_pauzy.pack(pady=5)

        self.ramka_grafow = tk.LabelFrame(self, text="Grafy")
        self.ramka_grafow.pack(side=tk.RIGHT, pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.graf_w = tk.Canvas(self.ramka_grafow, width=400, height=400, bg="white")
        self.graf_w.pack(side=tk.LEFT, padx=5)
        self.graf_q = tk.Canvas(self.ramka_grafow, width=400, height=400, bg="white")
        self.graf_q.pack(side=tk.LEFT, padx=5)
        self.graf_ro = tk.Canvas(self.ramka_grafow, width=400, height=400, bg="white")
        self.graf_ro.pack(side=tk.LEFT, padx=5)

        self.aktualizuj_grafy_z_osiami()

    def aktualizuj_wyswietl_kanaly(self, num_channels):
        for kanal in self.kanaly:
            kanal.pack_forget()
        self.kanaly = [tk.Canvas(self.ramka_kanalow, width=20, height=20, bg="green") for _ in range(num_channels)]
        for kanal in self.kanaly:
            kanal.pack(side=tk.LEFT, padx=5)

    def dodaj_pole_parametru(self, label_text, default_value):
        frame = tk.Frame(self.ramka_parametrow)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        label = tk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)

        pole = tk.Entry(frame)
        pole.insert(0, str(default_value))
        pole.pack(side=tk.LEFT)
        self.entry_widgets.append(pole)

    def wyodrebnij_wartosci_pola(self, container):
        params = []
        for child in container.winfo_children():
            if isinstance(child, tk.Entry):
                params.append(float(child.get()))
            elif hasattr(child, 'winfo_children'):
                params.extend(self.wyodrebnij_wartosci_pola(child))
        return params

    def uruchom_symulacje(self):
        
        params = self.wyodrebnij_wartosci_pola(self.ramka_parametrow)

        self.symulacja = Symulacja(*params)
        self.running = True
        self.przycisk_start.config(state=tk.DISABLED)
        self.przycisk_pauzy.config(state=tk.NORMAL)
        self.symuluj()

    def pauzuj_symulacje(self):
        self.running = False
        self.przycisk_start.config(state=tk.NORMAL)
        self.przycisk_pauzy.config(state=tk.DISABLED)

    def symuluj(self):
        if self.running:
            liczba_kanalow = int(self.entry_widgets[0].get())
            self.aktualizuj_wyswietl_kanaly(liczba_kanalow)

            dlugosc_kolejki = int(self.entry_widgets[1].get())
            lambda_wartosc = float(self.entry_widgets[2].get())
            srednia = float(self.entry_widgets[3].get())
            odchylenie_std = float(self.entry_widgets[4].get())
            min_czas = float(self.entry_widgets[5].get())
            max_czas = float(self.entry_widgets[6].get())
            czas_symulacji = float(self.entry_widgets[7].get())

            wynik = self.symulacja.krok_symulacji(liczba_kanalow, dlugosc_kolejki, lambda_wartosc, srednia, odchylenie_std, min_czas, max_czas, czas_symulacji)

            dodatkowe_info = (
                f"Liczba Poissona: {wynik['poisson_number']}\n"
                f"Liczba Gaussa: {wynik['gaussian_number']}\n"
                f"Liczba Klientów: {wynik['num_customers']}\n"
                f"Czas Przybycia: {wynik['arrival_time']}\n"
                f"Czas Obsługi: {wynik['service_time']}\n"
                f"Lambda i: {wynik['lambda_i']}\n"
                f"Mi i: {wynik['mi_i']}\n"
                f"Ro i: {wynik['ro_i']}\n"
            )

            wyniki_str = f"Czas: {wynik['current_time']}, W kolejce: {wynik['queued']}, Obsłużeni: {wynik['served']}, Odrzuceni: {wynik['rejected']}\n{dodatkowe_info}\n"
            self.tekst_wynikow.insert(tk.END, wyniki_str)

            for i, kanal in enumerate(self.kanaly):
                if i < liczba_kanalow:
                    kanal.config(bg="green" if wynik['status_kanalow'][i] else "red")

                else:
                    kanal.config(bg="gray")

            self.aktualizuj_graf_w(wynik['w_values'])
            self.aktualizuj_graf_q(wynik['q_values'])
            self.aktualizuj_graf_ro(wynik['ro_values'])

            if self.symulacja.aktualny_czas == 1:
                self.zapisz_poczatkowe_parametry_symulacji_do_pliku(liczba_kanalow, dlugosc_kolejki, lambda_wartosc, srednia, odchylenie_std, min_czas, max_czas, czas_symulacji)

            if self.running and self.symulacja.aktualny_czas < self.symulacja.czas_symulacji:
                self.dodaj_wyniki_symulacji_do_pliku(wynik['q_values'], wynik['w_values'], wynik['ro_values'])
                time.sleep(1)
                self.after(100, self.symuluj)

    def zapisz_poczatkowe_parametry_symulacji_do_pliku(self, liczba_kanalow, dlugosc_kolejki, lambda_wartosc, srednia, odchylenie_std, min_czas, max_czas, czas_symulacji):
        filename = "wyniki_symulacji.txt"
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "w", encoding="utf-8") as plik:
            plik.write(f"Liczba kanałów: {liczba_kanalow}, Długość kolejki: {dlugosc_kolejki}, Lambda: {lambda_wartosc}, Średnia: {srednia}, Odchylenie std: {odchylenie_std}, Min czas: {min_czas}, Max czas: {max_czas}, Czas symulacji: {czas_symulacji}\n")

    def dodaj_wyniki_symulacji_do_pliku(self, q_values, w_values, ro_values):
        filename = "wyniki_symulacji.txt"
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "a") as plik:
            aktualny_czas = self.symulacja.aktualny_czas
            ostatnia_wartosc_q = q_values[-1] if q_values else "N/A"
            ostatnia_wartosc_w = w_values[-1] if w_values else "N/A"
            ostatnia_wartosc_ro = ro_values[-1] if ro_values else "N/A"
            plik.write(f"Czas: {aktualny_czas}, Q: {ostatnia_wartosc_q}, W: {ostatnia_wartosc_w}, Ro: {ostatnia_wartosc_ro}\n")

    def aktualizuj_grafy_z_osiami(self):
        self.aktualizuj_graf_z_osiami(self.graf_w, 30, 10)
        self.aktualizuj_graf_z_osiami(self.graf_q, 30, 10)
        self.aktualizuj_graf_z_osiami(self.graf_ro, 30, 1)

    def aktualizuj_graf_z_osiami(self, graf, max_x_value, max_y_value):
        graf.delete("all")

        left_margin, right_margin = 50, 350
        top_margin, bottom_margin = 50, 350

        graf.create_line(left_margin, bottom_margin, right_margin, bottom_margin, width=2)
        graf.create_line(left_margin, bottom_margin, left_margin, top_margin, width=2)

        x_ticks = 10
        for i in range(x_ticks + 1):
            x = left_margin + i * ((right_margin - left_margin) / x_ticks)
            graf.create_line(x, bottom_margin, x, bottom_margin - 5, width=2)
            etykieta = i * (max_x_value / x_ticks)
            graf.create_text(x, bottom_margin + 10, text=f"{int(etykieta)}", anchor=tk.N)

        y_ticks = 10
        for i in range(y_ticks + 1):
            y = bottom_margin - i * ((bottom_margin - top_margin) / y_ticks)
            graf.create_line(left_margin, y, left_margin + 5, y, width=2)
            etykieta = i * (max_y_value / y_ticks)
            graf.create_text(left_margin - 10, y, text=f"{etykieta:.1f}", anchor=tk.E)

    def aktualizuj_graf_z_danymi(self, graf, wartosci, kolor="blue", max_x_value=None, max_y_value=None):
        if not wartosci:
            return

        max_x_value = max_x_value if max_x_value is not None else len(wartosci)
        max_y_value = max_y_value if max_y_value is not None else max(wartosci + [1])

        self.aktualizuj_graf_z_osiami(graf, max_x_value, max_y_value)

        for i in range(1, len(wartosci)):
            x1 = 50 + (i - 1) * (300 / max_x_value)
            y1 = 350 - ((wartosci[i - 1] / max_y_value) * 300)
            x2 = 50 + i * (300 / max_x_value)
            y2 = 350 - ((wartosci[i] / max_y_value) * 300)
            graf.create_line(x1, y1, x2, y2, fill=kolor, width=2)

    def aktualizuj_graf_w(self, w_values):
        max_y_value = max(w_values + [10])
        self.aktualizuj_graf_z_danymi(self.graf_w, w_values, kolor="blue", max_x_value=self.symulacja.czas_symulacji, max_y_value=max_y_value)

    def aktualizuj_graf_q(self, q_values):
        max_y_value = max(q_values + [10])
        self.aktualizuj_graf_z_danymi(self.graf_q, q_values, kolor="green", max_x_value=self.symulacja.czas_symulacji, max_y_value=max_y_value)

    def aktualizuj_graf_ro(self, ro_values):
        self.aktualizuj_graf_z_danymi(self.graf_ro, ro_values, kolor="red", max_x_value=self.symulacja.czas_symulacji, max_y_value=1)

class Symulacja:
    def __init__(self, liczba_kanalow, dlugosc_kolejki, lambda_wartosc, srednia, odchylenie_std, min_czas, max_czas, czas_symulacji):
        self.liczba_kanalow = int(liczba_kanalow)
        self.dlugosc_kolejki = dlugosc_kolejki
        self.lambda_wartosc = lambda_wartosc
        self.srednia = srednia
        self.odchylenie_std = odchylenie_std
        self.min_czas = min_czas
        self.max_czas = max_czas
        self.czas_symulacji = czas_symulacji

        self.status_kanalow = [False] * self.liczba_kanalow
        self.timery_kanalow = [0] * self.liczba_kanalow
        self.czas_do_nastepnego_polaczenia = 0
        self.aktualny_czas = 0
        self.dlugosc_kolejki = 0
        self.obsuzeni_klienci = 0
        self.odrzucone_polaczenia = 0
        self.laczna_liczba_klientow = 0
        self.laczny_czas_w_kolejce = 0
        self.wartosci_w = []
        self.wartosci_q = []
        self.wartosci_ro = []

    def generator_poissona(self, lambda_wartosc):
        num2 = -1
        num3 = 1.0
        num4 = math.exp(-lambda_wartosc)
        while num3 > num4:
            num5 = random.random()
            num3 *= num5
            num2 += 1
        return num2

    def generator_gaussa(self, srednia, odchylenie_std, min_czas, max_czas):
        num5 = 1.0 / (odchylenie_std * math.sqrt(2.0 * math.pi)) * random.random()
        a1 = srednia + math.sqrt(abs(math.log(1.0 / (num5 * odchylenie_std * math.sqrt(2.0 * math.pi)))) * 2.0 * odchylenie_std * odchylenie_std)
        a2 = srednia - math.sqrt(abs(math.log(1.0 / (num5 * odchylenie_std * math.sqrt(2.0 * math.pi)))) * 2.0 * odchylenie_std * odchylenie_std)
        num6 = a2 if a2 >= 0.0 else a1
        if num6 < min_czas:
            num6 = min_czas
        elif num6 > max_czas:
            num6 = max_czas
        return num6

    def krok_symulacji(self, liczba_kanalow, dlugosc_kolejki, lambda_wartosc, srednia, odchylenie_std, min_czas, max_czas, czas_symulacji):
        for i in range(liczba_kanalow):
            if self.status_kanalow[i]:
                self.timery_kanalow[i] -= 1
                if self.timery_kanalow[i] == 0:
                    self.status_kanalow[i] = False
                    self.obsuzeni_klienci += 1
                    if self.dlugosc_kolejki > 0:
                        czas_obslugi = self.generator_gaussa(srednia, odchylenie_std, min_czas, max_czas)
                        self.timery_kanalow[i] = czas_obslugi
                        self.status_kanalow[i] = True
                        self.dlugosc_kolejki -= 1

        if self.czas_do_nastepnego_polaczenia == 0:
            while self.czas_do_nastepnego_polaczenia == 0:
                czas_obslugi = self.generator_gaussa(srednia, odchylenie_std, min_czas, max_czas)
                for i in range(liczba_kanalow):
                    if not self.status_kanalow[i]:
                        self.status_kanalow[i] = True
                        self.timery_kanalow[i] = czas_obslugi
                        break
                else:
                    if self.dlugosc_kolejki < dlugosc_kolejki:
                        self.dlugosc_kolejki += 1
                        self.laczny_czas_w_kolejce += czas_obslugi
                    else:
                        self.odrzucone_polaczenia += 1
                self.laczna_liczba_klientow += 1
                self.czas_do_nastepnego_polaczenia = self.generator_poissona(lambda_wartosc)

        self.aktualny_czas += 1
        self.czas_do_nastepnego_polaczenia -= 1
        self.wartosci_w.append(self.laczny_czas_w_kolejce / self.laczna_liczba_klientow if self.laczna_liczba_klientow > 0 else 0)
        self.wartosci_q.append(self.dlugosc_kolejki)
        self.wartosci_ro.append(lambda_wartosc / ((self.obsuzeni_klienci / self.aktualny_czas * liczba_kanalow) if self.aktualny_czas > 0 and self.obsuzeni_klienci > 0 else 1) if self.aktualny_czas > 0 else 0)

        dostepne_kanaly = liczba_kanalow - sum(self.status_kanalow)
        wynik = {
            "status_kanalow": self.status_kanalow,
            "poisson_number": self.czas_do_nastepnego_polaczenia,
            "gaussian_number": self.generator_gaussa(srednia, odchylenie_std, min_czas, max_czas),
            "num_customers": self.laczna_liczba_klientow,
            "arrival_time": self.czas_do_nastepnego_polaczenia,
            "service_time": self.aktualny_czas,
            "lambda_i": lambda_wartosc,
            "mi_i": 1 / srednia,
            "ro_i": self.wartosci_ro[-1],
            "queued": self.dlugosc_kolejki,
            "available": dostepne_kanaly,
            "served": self.obsuzeni_klienci,
            "next_call_time": self.czas_do_nastepnego_polaczenia,
            "rejected": self.odrzucone_polaczenia,
            "current_time": self.aktualny_czas,
            "w_values": self.wartosci_w,
            "q_values": self.wartosci_q,
            "ro_values": self.wartosci_ro,
        }

        return wynik


app = SymulacjaKolejki()
app.mainloop()
