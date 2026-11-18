import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DB_NAME = "bmi_history.db"


def classify_bmi(bmi, age):
    # Adult BMI cut-offs should not be applied to people under 20.
    if age < 20:
        return "Adult categories not applicable"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Healthy weight"
    if bmi < 30:
        return "Overweight"
    return "Obesity"


class BMIDatabase:
    def __init__(self, db_name=DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                height_cm REAL NOT NULL,
                weight_kg REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def add_record(self, name, age, height, weight, bmi, category):
        self.connection.execute(
            """INSERT INTO bmi_records
               (name, age, height_cm, weight_kg, bmi, category, recorded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, age, height, weight, bmi, category,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.connection.commit()

    def get_records(self):
        return self.connection.execute(
            """SELECT id, name, age, height_cm, weight_kg, bmi, category, recorded_at
               FROM bmi_records ORDER BY id DESC"""
        ).fetchall()

    def delete_record(self, record_id):
        self.connection.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()


class BMICalculatorApp:
    BG = "#101522"
    PANEL = "#192438"
    TEXT = "#edf3ff"
    MUTED = "#9baac1"
    ACCENT = "#55c7e8"
    GREEN = "#62d6a5"

    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator | Health Tracker")
        self.root.geometry("1080x760")
        self.root.minsize(900, 650)
        self.root.configure(bg=self.BG)
        self.db = BMIDatabase()
        self.current_bmi = None
        self.current_category = None

        self._style()
        self._build_ui()
        self.refresh_history()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=self.PANEL,
                        foreground=self.TEXT,
                        fieldbackground=self.PANEL,
                        rowheight=28,
                        borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                        background="#263650",
                        foreground=self.TEXT,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", "#24566d")])
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=9)
        style.configure("TCombobox", padding=6)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=24, pady=(18, 12))
        tk.Label(header, text="BMI CALCULATOR",
                 font=("Segoe UI", 25, "bold"), fg=self.ACCENT,
                 bg=self.BG).pack(anchor="w")
        tk.Label(header, text="PERSONAL HEALTH TRACKER  •  PYTHON + SQLITE",
                 font=("Segoe UI", 9, "bold"), fg=self.MUTED,
                 bg=self.BG).pack(anchor="w", pady=(2, 0))

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=24, pady=8)

        left = tk.Frame(body, bg=self.PANEL, padx=20, pady=18)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.configure(width=330)
        left.pack_propagate(False)

        tk.Label(left, text="Your details", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 16))

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()

        self._field(left, "Full name", self.name_var, "e.g. Alex")
        self._field(left, "Age (years)", self.age_var, "e.g. 22")
        self._field(left, "Height (cm)", self.height_var, "e.g. 170")
        self._field(left, "Weight (kg)", self.weight_var, "e.g. 65")

        ttk.Button(left, text="Calculate BMI", command=self.calculate).pack(fill="x", pady=(15, 7))
        ttk.Button(left, text="Save record", command=self.save_record).pack(fill="x", pady=5)
        ttk.Button(left, text="Reset fields", command=self.reset_fields).pack(fill="x", pady=5)

        tk.Label(left, text="BMI = weight (kg) / height (m)²",
                 bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9),
                 wraplength=280).pack(anchor="w", pady=(18, 4))

        right = tk.Frame(body, bg=self.BG)
        right.pack(side="left", fill="both", expand=True)

        result = tk.Frame(right, bg=self.PANEL, padx=20, pady=17)
        result.pack(fill="x")
        tk.Label(result, text="YOUR RESULT", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.bmi_label = tk.Label(result, text="--.-", bg=self.PANEL,
                                  fg=self.ACCENT, font=("Segoe UI", 36, "bold"))
        self.bmi_label.pack(anchor="w", pady=(2, 0))
        self.category_label = tk.Label(result, text="Enter your details to calculate",
                                       bg=self.PANEL, fg=self.TEXT,
                                       font=("Segoe UI", 12, "bold"))
        self.category_label.pack(anchor="w")
        self.advice_label = tk.Label(result, text="BMI is a screening measure, not a diagnosis.",
                                     bg=self.PANEL, fg=self.MUTED,
                                     font=("Segoe UI", 9), wraplength=620,
                                     justify="left")
        self.advice_label.pack(anchor="w", pady=(8, 0))

        history_header = tk.Frame(right, bg=self.BG)
        history_header.pack(fill="x", pady=(17, 7))
        tk.Label(history_header, text="BMI HISTORY", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(history_header, text="Refresh", command=self.refresh_history).pack(side="right")
        ttk.Button(history_header, text="Delete selected", command=self.delete_selected).pack(side="right", padx=7)

        table_frame = tk.Frame(right, bg=self.PANEL)
        table_frame.pack(fill="both", expand=True)
        columns = ("id", "date", "name", "bmi", "category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        headings = {"id": "ID", "date": "Date", "name": "Name",
                    "bmi": "BMI", "category": "Category"}
        widths = {"id": 42, "date": 145, "name": 125, "bmi": 65, "category": 155}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 6))

        chart_frame = tk.Frame(right, bg=self.PANEL, padx=10, pady=8)
        chart_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.figure = Figure(figsize=(6.2, 2.25), dpi=100, facecolor=self.PANEL)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_chart([])

        footer = tk.Label(self.root,
            text="For adults 20+: standard adult BMI categories shown. For ages under 20, use a clinician's age- and sex-specific assessment.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8))
        footer.pack(fill="x", padx=24, pady=(7, 12))

    def _field(self, parent, label, variable, placeholder):
        tk.Label(parent, text=label, bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 4))
        entry = ttk.Entry(parent, textvariable=variable, font=("Segoe UI", 10))
        entry.pack(fill="x", ipady=5, pady=(0, 7))
        entry.insert(0, "")
        entry.configure()
        entry.bind("<Return>", lambda event: self.calculate())

    def _validate(self):
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("Please enter your name.")
        try:
            age = int(self.age_var.get())
            height = float(self.height_var.get())
            weight = float(self.weight_var.get())
        except ValueError:
            raise ValueError("Age must be a whole number. Height and weight must be numbers.")
        if not 1 <= age <= 120:
            raise ValueError("Please enter an age between 1 and 120.")
        if not 50 <= height <= 250:
            raise ValueError("Please enter a height between 50 and 250 cm.")
        if not 2 <= weight <= 500:
            raise ValueError("Please enter a weight between 2 and 500 kg.")
        return name, age, height, weight

    def calculate(self):
        try:
            name, age, height, weight = self._validate()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return False

        height_m = height / 100
        self.current_bmi = weight / (height_m ** 2)
        self.current_category = classify_bmi(self.current_bmi, age)

        self.bmi_label.config(text=f"{self.current_bmi:.1f}")
        self.category_label.config(text=self.current_category)
        if age < 20:
            note = ("BMI calculated, but adult cut-offs are not appropriate under age 20. "
                    "A pediatric BMI percentile assessment uses age and sex.")
        else:
            note = ("This is a screening result. It does not account for muscle mass, "
                    "pregnancy, or individual health factors.")
        self.advice_label.config(text=f"{name}, your BMI is {self.current_bmi:.1f}. {note}")
        return True

    def save_record(self):
        if self.current_bmi is None:
            if not self.calculate():
                return
        try:
            name, age, height, weight = self._validate()
            self.db.add_record(name, age, height, weight,
                               round(self.current_bmi, 2), self.current_category)
            self.refresh_history()
            messagebox.showinfo("Saved", "Your BMI record has been saved.")
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))

    def refresh_history(self):
        records = self.db.get_records()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in records:
            record_id, name, age, height, weight, bmi, category, recorded_at = row
            self.tree.insert("", "end", values=(
                record_id, recorded_at, name, f"{bmi:.1f}", category
            ))
        self._draw_chart(records)

    def _draw_chart(self, records):
        self.ax.clear()
        self.ax.set_facecolor(self.PANEL)
        self.figure.patch.set_facecolor(self.PANEL)
        # Plot in chronological order, showing the most recent 20 entries.
        ordered = list(reversed(records[:20]))
        if ordered:
            labels = [r[7][5:16] for r in ordered]
            values = [r[5] for r in ordered]
            self.ax.plot(labels, values, marker="o", linewidth=2, color="#55c7e8")
            self.ax.set_title("BMI over time", color=self.TEXT, fontsize=10)
            self.ax.set_ylabel("BMI", color=self.MUTED)
            self.ax.tick_params(axis="x", colors=self.MUTED, labelrotation=25, labelsize=7)
            self.ax.tick_params(axis="y", colors=self.MUTED, labelsize=8)
            self.ax.grid(True, alpha=0.18)
            for spine in self.ax.spines.values():
                spine.set_color("#3a4a63")
        else:
            self.ax.text(0.5, 0.5, "Save a BMI record to see your trend",
                         ha="center", va="center", color=self.MUTED,
                         transform=self.ax.transAxes)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a record", "Choose a history row first.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete the selected BMI record?"):
            return
        for item in selected:
            record_id = self.tree.item(item, "values")[0]
            self.db.delete_record(int(record_id))
        self.refresh_history()

    def reset_fields(self):
        for variable in (self.name_var, self.age_var, self.height_var, self.weight_var):
            variable.set("")
        self.current_bmi = None
        self.current_category = None
        self.bmi_label.config(text="--.-")
        self.category_label.config(text="Enter your details to calculate")
        self.advice_label.config(text="BMI is a screening measure, not a diagnosis.")

    def close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
