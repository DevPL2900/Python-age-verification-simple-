import tkinter as tk
from tkinter import messagebox
import random
import datetime

# Farb-Konfiguration für Rezeptarten
REZEPT_FARBEN = {
    "Rosa":  {"bg": "#FFB6C1", "beschreibung": "Kassenrezept",     "gueltig": "28 Tage"},
    "Blau":  {"bg": "#ADD8E6", "beschreibung": "Privatrezept",     "gueltig": "3 Monate"},
    "Grün":  {"bg": "#90EE90", "beschreibung": "Empfehlung",       "gueltig": "unbegrenzt"},
    "Gelb":  {"bg": "#FFFF99", "beschreibung": "Betäubungsmittel", "gueltig": "7 Tage"},
}

class RezeptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arzt-Rezept System")
        self.root.geometry("620x700")
        self.root.configure(bg="#f0f4f8")
        self.root.resizable(False, False)

        self.versicherung_var    = tk.StringVar(value="")
        self.verschreibung_var   = tk.BooleanVar()
        self.betaeubung_var      = tk.BooleanVar()
        self.gewaehlte_farbe     = tk.StringVar(value="Rosa")

        self._build_ui()

    def _build_ui(self):
        # ── Titel ──────────────────────────────────────────────────────────────
        titel = tk.Label(
            self.root, text="🏥  Rezept ausstellen",
            font=("Georgia", 20, "bold"),
            bg="#f0f4f8", fg="#1a3c5e"
        )
        titel.pack(pady=(18, 4))

        tk.Label(
            self.root, text="Arzt-Praxis-Software  •  Rezeptverwaltung",
            font=("Georgia", 10, "italic"), bg="#f0f4f8", fg="#6b8cae"
        ).pack(pady=(0, 14))

        # ── Versicherungsart ──────────────────────────────────────────────────
        self._section("1.  Versicherungsart")
        vbox = tk.Frame(self.root, bg="#f0f4f8")
        vbox.pack(pady=4)
        for text, wert in [("Gesetzlich versichert (GKV)", "gesetzlich"),
                            ("Privat versichert (PKV)",     "privat")]:
            tk.Radiobutton(
                vbox, text=text, variable=self.versicherung_var, value=wert,
                font=("Helvetica", 11), bg="#f0f4f8", fg="#1a3c5e",
                activebackground="#f0f4f8", selectcolor="#1a3c5e"
            ).pack(anchor="w", padx=30)

        # ── Rezeptart ─────────────────────────────────────────────────────────
        self._section("2.  Rezeptart")
        cbox = tk.Frame(self.root, bg="#f0f4f8")
        cbox.pack(pady=4)
        tk.Checkbutton(
            cbox, text="Verschreibungspflichtig  (Rx)",
            variable=self.verschreibung_var,
            font=("Helvetica", 11), bg="#f0f4f8", fg="#1a3c5e",
            activebackground="#f0f4f8", selectcolor="#1a3c5e"
        ).pack(anchor="w", padx=30)
        tk.Checkbutton(
            cbox, text="Betäubungsmittel  (BtM-Rezept)",
            variable=self.betaeubung_var,
            font=("Helvetica", 11), bg="#f0f4f8", fg="#8b0000",
            activebackground="#f0f4f8", selectcolor="#8b0000",
            command=self._btm_gewaehlt
        ).pack(anchor="w", padx=30)

        # ── Farbe wählen ──────────────────────────────────────────────────────
        self._section("3.  Rezeptfarbe wählen")
        info_text = (
            "Rosa = Kassenrezept (28 Tage)  •  Blau = Privatrezept (3 Monate)\n"
            "Grün = Empfehlung (unbegrenzt)  •  Gelb = Betäubungsmittel (7 Tage)"
        )
        tk.Label(
            self.root, text=info_text,
            font=("Helvetica", 8), bg="#f0f4f8", fg="#555"
        ).pack()

        farb_frame = tk.Frame(self.root, bg="#f0f4f8")
        farb_frame.pack(pady=6)
        self.farb_buttons = {}
        for farbe, info in REZEPT_FARBEN.items():
            btn = tk.Button(
                farb_frame, text=f"  {farbe}  ",
                bg=info["bg"], fg="#1a3c5e",
                font=("Helvetica", 11, "bold"),
                relief="raised", bd=2,
                width=8,
                command=lambda f=farbe: self._farbe_setzen(f)
            )
            btn.pack(side="left", padx=6)
            self.farb_buttons[farbe] = btn
        self._farbe_setzen("Rosa")           # Standard

        # ── Freitext ──────────────────────────────────────────────────────────
        self._section("4.  Ärztliche Notizen / Diagnose")
        self.notiz_text = tk.Text(
            self.root, height=5, width=62,
            font=("Helvetica", 11),
            bg="white", fg="#222",
            relief="solid", bd=1,
            wrap="word"
        )
        self.notiz_text.pack(padx=20, pady=4)
        self.notiz_text.insert("1.0", "Hier Diagnose, Medikament und Dosierung eingeben …")
        self.notiz_text.bind("<FocusIn>",  self._notiz_focus_in)
        self.notiz_text.bind("<FocusOut>", self._notiz_focus_out)

        # ── Button ────────────────────────────────────────────────────────────
        tk.Button(
            self.root,
            text="📋   Krankenschein ausstellen",
            font=("Helvetica", 13, "bold"),
            bg="#1a3c5e", fg="white",
            activebackground="#0d2540",
            relief="flat", cursor="hand2",
            padx=20, pady=10,
            command=self._ausstellen
        ).pack(pady=18)

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────

    def _section(self, titel):
        tk.Label(
            self.root, text=titel,
            font=("Helvetica", 12, "bold"),
            bg="#f0f4f8", fg="#1a3c5e"
        ).pack(anchor="w", padx=20, pady=(10, 2))

    def _farbe_setzen(self, farbe):
        self.gewaehlte_farbe.set(farbe)
        for f, btn in self.farb_buttons.items():
            btn.config(relief="raised", bd=2)
        self.farb_buttons[farbe].config(relief="sunken", bd=4)

    def _btm_gewaehlt(self):
        if self.betaeubung_var.get():
            self._farbe_setzen("Gelb")
            self.verschreibung_var.set(True)

    def _notiz_focus_in(self, _event):
        if self.notiz_text.get("1.0", "end-1c") == "Hier Diagnose, Medikament und Dosierung eingeben …":
            self.notiz_text.delete("1.0", "end")
            self.notiz_text.config(fg="#222")

    def _notiz_focus_out(self, _event):
        if not self.notiz_text.get("1.0", "end-1c").strip():
            self.notiz_text.insert("1.0", "Hier Diagnose, Medikament und Dosierung eingeben …")
            self.notiz_text.config(fg="#aaa")

    def _ausstellen(self):
        # ── Validierung ──
        if not self.versicherung_var.get():
            messagebox.showwarning("Fehlende Angabe", "Bitte Versicherungsart auswählen.")
            return

        farbe      = self.gewaehlte_farbe.get()
        info       = REZEPT_FARBEN[farbe]
        notiz      = self.notiz_text.get("1.0", "end-1c").strip()
        platzhalter = "Hier Diagnose, Medikament und Dosierung eingeben …"
        if notiz == platzhalter:
            notiz = "—"

        versicherung   = "Gesetzlich (GKV)" if self.versicherung_var.get() == "gesetzlich" else "Privat (PKV)"
        verschreibung  = "✔ Ja" if self.verschreibung_var.get() else "✘ Nein"
        betaeubung     = "✔ Ja" if self.betaeubung_var.get()    else "✘ Nein"
        rezept_nr      = random.randint(100000, 999999)
        datum          = datetime.date.today().strftime("%d.%m.%Y")

        # ── Zusammenfassungs-Fenster ──
        fenster = tk.Toplevel(self.root)
        fenster.title("Rezept ausgestellt")
        fenster.geometry("480x460")
        fenster.configure(bg=info["bg"])
        fenster.resizable(False, False)

        tk.Label(
            fenster,
            text=f"🩺  {info['beschreibung'].upper()}",
            font=("Georgia", 17, "bold"),
            bg=info["bg"], fg="#1a3c5e"
        ).pack(pady=(20, 4))

        tk.Label(
            fenster,
            text=f"Rezept-Nr.: {rezept_nr}   •   Datum: {datum}",
            font=("Helvetica", 9), bg=info["bg"], fg="#444"
        ).pack(pady=(0, 12))

        # Tabelle der Details
        details = [
            ("Versicherung",         versicherung),
            ("Rezeptfarbe",          f"{farbe}  –  {info['beschreibung']}"),
            ("Gültigkeit",           info["gueltig"]),
            ("Verschreibungspfl.",   verschreibung),
            ("Betäubungsmittel",     betaeubung),
            ("Notizen / Diagnose",   notiz),
        ]
        tbl = tk.Frame(fenster, bg=info["bg"])
        tbl.pack(padx=30, fill="x")
        for label, wert in details:
            row = tk.Frame(tbl, bg=info["bg"])
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text=f"{label}:", width=22, anchor="w",
                font=("Helvetica", 10, "bold"), bg=info["bg"], fg="#1a3c5e"
            ).pack(side="left")
            tk.Label(
                row, text=wert, anchor="w", wraplength=230,
                font=("Helvetica", 10), bg=info["bg"], fg="#222"
            ).pack(side="left")

        # Trennlinie
        tk.Frame(fenster, height=1, bg="#999").pack(fill="x", padx=30, pady=14)

        def neues_rezept():
            fenster.destroy()
            self._formular_zuruecksetzen()

        tk.Button(
            fenster,
            text="✚  Neues Rezept ausstellen",
            font=("Helvetica", 11, "bold"),
            bg="#1a3c5e", fg="white",
            activebackground="#0d2540",
            relief="flat", cursor="hand2",
            padx=16, pady=8,
            command=neues_rezept
        ).pack(pady=4)

        tk.Button(
            fenster,
            text="Schließen",
            font=("Helvetica", 10),
            bg="#888", fg="white",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=fenster.destroy
        ).pack(pady=(4, 16))

    def _formular_zuruecksetzen(self):
        self.versicherung_var.set("")
        self.verschreibung_var.set(False)
        self.betaeubung_var.set(False)
        self._farbe_setzen("Rosa")
        self.notiz_text.delete("1.0", "end")
        self.notiz_text.insert("1.0", "Hier Diagnose, Medikament und Dosierung eingeben …")
        self.notiz_text.config(fg="#aaa")


if __name__ == "__main__":
    root = tk.Tk()
    app = RezeptApp(root)
    root.mainloop()
