
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import time
import threading

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ==================================================
# KONFIGURASI
# ==================================================

BG = "#F5F6FA"
WHITE = "#FFFFFF"
PRIMARY = "#635BDB"
PRIMARY_DARK = "#4F46B8"
TEXT = "#25263A"
MUTED = "#88899B"
BORDER = "#E9EAF1"
GREEN = "#239B77"
ORANGE = "#E69B42"
RED = "#DB626C"

DATA_FILE = "data_nilai_mahasiswa_10000.csv"


# ==================================================
# ALGORITMA SORTING
# ==================================================

def bubble_sort(data):
    arr = data.copy()
    n = len(arr)

    for i in range(n):
        swapped = False

        for j in range(n - i - 1):
            if arr[j]["Nilai"] > arr[j + 1]["Nilai"]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        if not swapped:
            break

    return arr


def selection_sort(data):
    arr = data.copy()

    for i in range(len(arr)):
        minimum = i

        for j in range(i + 1, len(arr)):
            if arr[j]["Nilai"] < arr[minimum]["Nilai"]:
                minimum = j

        arr[i], arr[minimum] = arr[minimum], arr[i]

    return arr


def insertion_sort(data):
    arr = data.copy()

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j]["Nilai"] > key["Nilai"]:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return arr


def merge_sort(data):
    if len(data) <= 1:
        return data.copy()

    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])

    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i]["Nilai"] <= right[j]["Nilai"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result


def quick_sort(data):
    arr = data.copy()

    if len(arr) <= 1:
        return arr

    stack = [(0, len(arr) - 1)]

    while stack:
        low, high = stack.pop()

        if low >= high:
            continue

        pivot = arr[(low + high) // 2]["Nilai"]
        i, j = low, high

        while i <= j:
            while arr[i]["Nilai"] < pivot:
                i += 1

            while arr[j]["Nilai"] > pivot:
                j -= 1

            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1

        if low < j:
            stack.append((low, j))

        if i < high:
            stack.append((i, high))

    return arr


ALGORITHMS = {
    "Bubble Sort": bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort
}


COMPLEXITIES = [
    ("Bubble Sort", "O(n)", "O(n²)", "O(n²)", "O(1)"),
    ("Selection Sort", "O(n²)", "O(n²)", "O(n²)", "O(1)"),
    ("Insertion Sort", "O(n)", "O(n²)", "O(n²)", "O(1)"),
    ("Merge Sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)"),
    ("Quick Sort", "O(n log n)", "O(n log n)", "O(n²)", "O(log n) rata-rata")
]


# ==================================================
# MEMBACA DATA CSV
# ==================================================

def load_data():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        DATA_FILE
    )

    if not os.path.exists(path):
        messagebox.showerror(
            "File Tidak Ditemukan",
            f"File {DATA_FILE} tidak ditemukan.\n\n"
            "Letakkan file CSV dalam folder yang sama dengan main.py."
        )
        return []

    data = []

    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            required = {"NIM", "Nama", "Prodi", "Nilai"}

            if not required.issubset(set(reader.fieldnames or [])):
                messagebox.showerror(
                    "Format CSV Salah",
                    "Kolom CSV harus berisi: NIM, Nama, Prodi, Nilai"
                )
                return []

            for row in reader:
                try:
                    data.append({
                        "NIM": row["NIM"],
                        "Nama": row["Nama"],
                        "Prodi": row["Prodi"],
                        "Nilai": float(row["Nilai"])
                    })
                except (ValueError, TypeError):
                    continue

    except Exception as error:
        messagebox.showerror("Kesalahan", str(error))

    return data


# ==================================================
# APLIKASI UTAMA
# ==================================================

class SortingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sortify - Student Analytics")
        self.root.geometry("1250x780")
        self.root.minsize(1050, 650)
        self.root.configure(bg=BG)

        self.data = load_data()
        self.results = {}
        self.sorting_busy = False
        self.current_canvas = None

        self.setup_style()
        self.create_layout()
        self.show_page("Dashboard")

    # ==================================================
    # STYLE
    # ==================================================

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            fieldbackground=WHITE,
            rowheight=38,
            font=("Segoe UI", 9),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#EFEEFF",
            foreground=TEXT,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=10
        )

        style.map(
            "Treeview",
            background=[("selected", "#E8E6FF")],
            foreground=[("selected", TEXT)]
        )

        style.configure("TCombobox", padding=8, font=("Segoe UI", 9))
        style.configure("TEntry", padding=8, font=("Segoe UI", 9))

    # ==================================================
    # LAYOUT DAN SCROLL
    # ==================================================

    def create_layout(self):
        self.sidebar = tk.Frame(self.root, bg=WHITE, width=235)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=WHITE)
        logo.pack(fill="x", padx=22, pady=(30, 35))

        tk.Label(
            logo, text="S", font=("Segoe UI", 20, "bold"),
            fg=WHITE, bg=PRIMARY, width=2
        ).pack(side="left", padx=(0, 10))

        logo_text = tk.Frame(logo, bg=WHITE)
        logo_text.pack(side="left")

        tk.Label(
            logo_text, text="SORTIFY",
            font=("Segoe UI", 15, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w")

        tk.Label(
            logo_text, text="STUDENT ANALYTICS",
            font=("Segoe UI", 7, "bold"),
            fg=MUTED, bg=WHITE
        ).pack(anchor="w")

        tk.Label(
            self.sidebar, text="MENU UTAMA",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED, bg=WHITE
        ).pack(anchor="w", padx=25, pady=(0, 12))

        menus = [
            ("▦", "Dashboard"),
            ("▤", "Data Mahasiswa"),
            ("◈", "Analisis Kompleksitas")
        ]

        self.menu_buttons = {}

        for symbol, name in menus:
            btn = tk.Button(
                self.sidebar,
                text=f"  {symbol}     {name}",
                font=("Segoe UI", 10, "bold"),
                bg=WHITE,
                fg=MUTED,
                activebackground="#EFEEFF",
                activeforeground=PRIMARY,
                relief="flat",
                anchor="w",
                padx=15,
                pady=14,
                cursor="hand2",
                command=lambda n=name: self.show_page(n)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.menu_buttons[name] = btn

        tk.Frame(
            self.sidebar, bg=BORDER, height=1
        ).pack(side="bottom", fill="x", padx=20, pady=15)

        tk.Label(
            self.sidebar,
            text="PROJECT STRUKTUR DATA\nSorting Algorithm",
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=WHITE,
            justify="left"
        ).pack(side="bottom", anchor="w", padx=22, pady=(0, 18))

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="right", fill="both", expand=True)

        self.topbar = tk.Frame(self.main, bg=WHITE, height=65)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.top_title = tk.Label(
            self.topbar,
            text="Dashboard",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT,
            bg=WHITE
        )
        self.top_title.pack(side="left", padx=30)

        tk.Label(
            self.topbar,
            text="STUDENT SORTING SYSTEM",
            font=("Segoe UI", 8, "bold"),
            fg=PRIMARY,
            bg=WHITE
        ).pack(side="right", padx=30)

        self.scrollbar = ttk.Scrollbar(self.main, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.content_canvas = tk.Canvas(
            self.main,
            bg=BG,
            highlightthickness=0,
            borderwidth=0,
            yscrollcommand=self.scrollbar.set
        )
        self.content_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.content_canvas.yview)

        self.container = tk.Frame(self.content_canvas, bg=BG)

        self.container_window = self.content_canvas.create_window(
            (0, 0),
            window=self.container,
            anchor="nw"
        )

        self.container.bind("<Configure>", self.update_scroll_region)
        self.content_canvas.bind("<Configure>", self.resize_content)

        self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind_all("<Button-4>", self.on_mousewheel_linux)
        self.root.bind_all("<Button-5>", self.on_mousewheel_linux)

    def update_scroll_region(self, event=None):
        self.content_canvas.configure(
            scrollregion=self.content_canvas.bbox("all")
        )

    def resize_content(self, event):
        self.content_canvas.itemconfigure(
            self.container_window,
            width=event.width
        )

    def on_mousewheel(self, event):
        x, y = self.root.winfo_pointerxy()
        left = self.content_canvas.winfo_rootx()
        top = self.content_canvas.winfo_rooty()
        right = left + self.content_canvas.winfo_width()
        bottom = top + self.content_canvas.winfo_height()

        if left <= x <= right and top <= y <= bottom:
            self.content_canvas.yview_scroll(
                int(-event.delta / 120), "units"
            )

    def on_mousewheel_linux(self, event):
        x, y = self.root.winfo_pointerxy()
        left = self.content_canvas.winfo_rootx()
        top = self.content_canvas.winfo_rooty()
        right = left + self.content_canvas.winfo_width()
        bottom = top + self.content_canvas.winfo_height()

        if left <= x <= right and top <= y <= bottom:
            if event.num == 4:
                self.content_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.content_canvas.yview_scroll(1, "units")

    # ==================================================
    # KOMPONEN DESAIN
    # ==================================================

    def clear_page(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_canvas = None
        self.content_canvas.yview_moveto(0)

    def heading(self, title, subtitle):
        tk.Label(
            self.container,
            text=title,
            font=("Segoe UI", 23, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w", padx=30, pady=(25, 4))

        tk.Label(
            self.container,
            text=subtitle,
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", padx=30, pady=(0, 20))

    def card(self, parent, title, value, color=PRIMARY, detail=""):
        frame = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Frame(frame, bg=color, height=4).pack(fill="x")

        tk.Label(
            frame, text=title.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=MUTED, bg=WHITE
        ).pack(anchor="w", padx=17, pady=(16, 7))

        tk.Label(
            frame, text=value,
            font=("Segoe UI", 20, "bold"),
            fg=color, bg=WHITE,
            wraplength=200
        ).pack(anchor="w", padx=17)

        tk.Label(
            frame, text=detail,
            font=("Segoe UI", 8),
            fg=MUTED, bg=WHITE
        ).pack(anchor="w", padx=17, pady=(7, 16))

        return frame

    def make_button(self, parent, text, command, color=PRIMARY):
        return tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg=WHITE,
            activebackground=PRIMARY_DARK,
            activeforeground=WHITE,
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            command=command
        )

    # ==================================================
    # NAVIGASI
    # ==================================================

    def show_page(self, name):
        self.clear_page()
        self.top_title.config(text=name)

        for menu, btn in self.menu_buttons.items():
            if menu == name:
                btn.config(bg="#EFEEFF", fg=PRIMARY)
            else:
                btn.config(bg=WHITE, fg=MUTED)

        pages = {
            "Dashboard": self.dashboard_page,
            "Data Mahasiswa": self.data_page,
            "Analisis Kompleksitas": self.analysis_page,
            "Grafik": self.graph_page,
            "Infografis": self.infographic_page
        }

        if name in pages:
            pages[name]()

        self.root.after_idle(self.update_scroll_region)

    # ==================================================
    # DASHBOARD
    # ==================================================

    def dashboard_page(self):
        self.heading(
            "Dashboard",
            "Selamat datang di Student Sorting Analytics"
        )

        total = len(self.data)

        if total:
            values = [x["Nilai"] for x in self.data]
            average = sum(values) / total
            highest = max(values)
            lowest = min(values)
        else:
            average = highest = lowest = 0

        cards = tk.Frame(self.container, bg=BG)
        cards.pack(fill="x", padx=22)

        items = [
            ("Total Mahasiswa", f"{total:,}", PRIMARY, "Jumlah data mahasiswa"),
            ("Rata-rata Nilai", f"{average:.2f}", GREEN, "Nilai rata-rata"),
            ("Nilai Tertinggi", f"{highest:.2f}", ORANGE, "Skor maksimum"),
            ("Nilai Terendah", f"{lowest:.2f}", RED, "Skor minimum")
        ]

        for title, value, color, detail in items:
            c = self.card(cards, title, value, color, detail)
            c.pack(side="left", fill="both", expand=True, padx=7)

        panel = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        panel.pack(fill="x", padx=30, pady=25)

        tk.Label(
            panel,
            text="STUDENT SORTING ANALYTICS",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w", padx=25, pady=(25, 8))

        tk.Label(
            panel,
            text=(
                "Aplikasi pengolahan dan analisis nilai mahasiswa "
                "menggunakan lima algoritma sorting.\n\n"
                "Aplikasi ini dirancang untuk membandingkan kecepatan "
                "pengurutan data serta mempelajari kompleksitas waktu "
                "dan ruang setiap algoritma."
            ),
            font=("Segoe UI", 10),
            fg=MUTED, bg=WHITE,
            justify="left", wraplength=850
        ).pack(anchor="w", padx=25, pady=(0, 20))

        self.make_button(
            panel,
            "LIHAT DATA MAHASISWA",
            lambda: self.show_page("Data Mahasiswa")
        ).pack(anchor="w", padx=25, pady=(0, 25))

        info = tk.Frame(self.container, bg=BG)
        info.pack(fill="x", padx=30, pady=10)

        tk.Label(
            info,
            text="ALGORITMA YANG DIGUNAKAN",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT, bg=BG
        ).pack(anchor="w", pady=(5, 12))

        for name in ALGORITHMS:
            tk.Label(
                info,
                text=f"●   {name}",
                font=("Segoe UI", 10),
                fg=MUTED, bg=BG
            ).pack(anchor="w", pady=5)

        extra = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        extra.pack(fill="x", padx=30, pady=25)

        tk.Label(
            extra,
            text="TUJUAN APLIKASI",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w", padx=20, pady=(20, 10))

        tk.Label(
            extra,
            text=(
                "1. Mengurutkan nilai mahasiswa secara ascending dan descending.\n\n"
                "2. Mempelajari lima algoritma sorting.\n\n"
                "3. Mengukur waktu eksekusi setiap algoritma.\n\n"
                "4. Membandingkan kompleksitas algoritma.\n\n"
                "5. Menampilkan hasil pengujian dalam bentuk grafik dan infografis."
            ),
            font=("Segoe UI", 10),
            fg=MUTED, bg=WHITE,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 25))

    # ==================================================
    # DATA MAHASISWA
    # ==================================================

    def data_page(self):
        self.heading(
            "Data Mahasiswa",
            "Kelola, cari, dan urutkan data nilai mahasiswa"
        )

        control = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        control.pack(fill="x", padx=30, pady=5)

        top = tk.Frame(control, bg=WHITE)
        top.pack(fill="x", padx=15, pady=15)

        search_var = tk.StringVar()
        algorithm_var = tk.StringVar(value="Bubble Sort")
        order_var = tk.StringVar(value="Ascending")

        search_entry = ttk.Entry(
            top, textvariable=search_var, width=23
        )
        search_entry.pack(side="left", padx=5)

        ttk.Combobox(
            top,
            textvariable=algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=17
        ).pack(side="left", padx=5)

        ttk.Combobox(
            top,
            textvariable=order_var,
            values=["Ascending", "Descending"],
            state="readonly",
            width=14
        ).pack(side="left", padx=5)

        status = tk.Label(
            control,
            text="Menampilkan data mahasiswa",
            font=("Segoe UI", 8),
            fg=MUTED, bg=WHITE
        )
        status.pack(anchor="w", padx=20, pady=(0, 10))

        table_frame = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        table_frame.pack(
            fill="both", expand=True, padx=30, pady=15
        )

        columns = ("NIM", "Nama", "Prodi", "Nilai")

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        widths = [140, 240, 180, 100]

        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        current_data = self.data.copy()

        def display(rows):
            tree.delete(*tree.get_children())

            for item in rows[:1000]:
                tree.insert(
                    "",
                    "end",
                    values=(
                        item["NIM"],
                        item["Nama"],
                        item["Prodi"],
                        f'{item["Nilai"]:.2f}'
                    )
                )

            status.config(
                text=f"Menampilkan {min(len(rows), 1000):,} dari {len(rows):,} data"
            )

        def search(*args):
            keyword = search_var.get().lower()

            filtered = [
                item for item in self.data
                if keyword in item["NIM"].lower()
                or keyword in item["Nama"].lower()
                or keyword in item["Prodi"].lower()
            ]

            display(filtered)

        def sort_data():
            if self.sorting_busy:
                return

            self.sorting_busy = True
            status.config(text="Sedang mengurutkan data...")

            name = algorithm_var.get()
            function = ALGORITHMS[name]
            source = current_data.copy()
            descending = order_var.get() == "Descending"

            def worker():
                try:
                    start = time.perf_counter()
                    result = function(source)
                    elapsed = time.perf_counter() - start

                    if descending:
                        result.reverse()

                    def finish():
                        nonlocal current_data
                        current_data = result
                        display(result)
                        status.config(
                            text=f"{name} selesai dalam {elapsed:.6f} detik"
                        )
                        self.sorting_busy = False

                    self.root.after(0, finish)

                except Exception as error:
                    def show_error():
                        self.sorting_busy = False
                        messagebox.showerror("Kesalahan Sorting", str(error))

                    self.root.after(0, show_error)

            threading.Thread(target=worker, daemon=True).start()

        search_var.trace_add("write", search)

        self.make_button(
            top, "URUTKAN", sort_data
        ).pack(side="left", padx=8)

        display(self.data)

    # ==================================================
    # ANALISIS KOMPLEKSITAS
    # ==================================================

    def analysis_page(self):
        self.heading(
            "Analisis Kompleksitas",
            "Perbandingan efisiensi waktu dan penggunaan memori algoritma"
        )

        table_frame = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        table_frame.pack(fill="x", padx=30, pady=5)

        columns = (
            "Algoritma", "Best Case", "Average Case",
            "Worst Case", "Space Complexity"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=7
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=145, anchor="center")

        for row in COMPLEXITIES:
            tree.insert("", "end", values=row)

        tree.pack(fill="x", padx=10, pady=12)

        explanation = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        explanation.pack(fill="x", padx=30, pady=18)

        tk.Label(
            explanation,
            text="PENJELASAN ALGORITMA",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w", padx=20, pady=(20, 12))

        descriptions = [
            ("Bubble Sort", "Membandingkan elemen yang berdekatan."),
            ("Selection Sort", "Memilih elemen terkecil pada setiap iterasi."),
            ("Insertion Sort", "Menyisipkan elemen ke posisi yang tepat."),
            ("Merge Sort", "Membagi data menjadi bagian kecil lalu menggabungkannya."),
            ("Quick Sort", "Membagi data berdasarkan elemen pivot.")
        ]

        for name, desc in descriptions:
            row = tk.Frame(explanation, bg=WHITE)
            row.pack(fill="x", padx=20, pady=7)

            tk.Label(
                row, text=name,
                font=("Segoe UI", 9, "bold"),
                fg=PRIMARY, bg=WHITE,
                width=18, anchor="w"
            ).pack(side="left")

            tk.Label(
                row, text=desc,
                font=("Segoe UI", 9),
                fg=MUTED, bg=WHITE
            ).pack(side="left")

        tk.Label(
            explanation,
            text=(
                "Keterangan: n merupakan jumlah data mahasiswa. "
                "Kompleksitas menggambarkan pertumbuhan kebutuhan waktu "
                "atau ruang ketika jumlah data bertambah."
            ),
            font=("Segoe UI", 9),
            fg=MUTED, bg=WHITE,
            wraplength=850, justify="left"
        ).pack(anchor="w", padx=20, pady=20)

        extra = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        extra.pack(fill="x", padx=30, pady=10)

        tk.Label(
            extra,
            text="KESIMPULAN TEORI",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w", padx=20, pady=(20, 10))

        tk.Label(
            extra,
            text=(
                "• Bubble Sort mudah dipahami, tetapi kurang efisien untuk data besar.\n\n"
                "• Selection Sort memiliki jumlah pertukaran yang relatif sedikit.\n\n"
                "• Insertion Sort efektif untuk data kecil atau hampir terurut.\n\n"
                "• Merge Sort memiliki waktu yang konsisten, tetapi memerlukan ruang tambahan.\n\n"
                "• Quick Sort umumnya cepat pada kasus rata-rata, tetapi memiliki kasus terburuk O(n²)."
            ),
            font=("Segoe UI", 10),
            fg=MUTED, bg=WHITE,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.make_button(
            self.container,
            "LIHAT GRAFIK PERBANDINGAN  →",
            self.open_graph
        ).pack(anchor="e", padx=35, pady=20)

    # ==================================================
    # PENGUJIAN ALGORITMA
    # ==================================================

    def open_graph(self):
        if self.sorting_busy:
            return

        if not self.data:
            messagebox.showwarning(
                "Data Kosong",
                "Tidak ada data mahasiswa untuk diuji."
            )
            return

        if self.results:
            self.show_page("Grafik")
            return

        self.clear_page()
        self.sorting_busy = True

        self.heading(
            "Pengujian Algoritma",
            "Sedang melakukan perbandingan waktu eksekusi"
        )

        loading = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        loading.pack(fill="x", padx=30, pady=30)

        tk.Label(
            loading,
            text="PENGUJIAN SEDANG BERLANGSUNG",
            font=("Segoe UI", 15, "bold"),
            fg=PRIMARY, bg=WHITE
        ).pack(pady=(30, 10))

        tk.Label(
            loading,
            text=(
                "Aplikasi sedang menguji lima algoritma sorting.\n"
                "Proses dapat membutuhkan waktu, terutama untuk "
                "algoritma O(n²) pada 10.000 data."
            ),
            font=("Segoe UI", 10),
            fg=MUTED, bg=WHITE,
            justify="center"
        ).pack(pady=(0, 30))

        def worker():
            results = {}

            try:
                for name, function in ALGORITHMS.items():
                    start = time.perf_counter()
                    function(self.data)
                    elapsed = time.perf_counter() - start
                    results[name] = elapsed

                def finish():
                    self.results = results
                    self.sorting_busy = False
                    self.show_page("Grafik")

                self.root.after(0, finish)

            except Exception as error:
                def show_error():
                    self.sorting_busy = False
                    messagebox.showerror("Kesalahan Pengujian", str(error))
                    self.show_page("Analisis Kompleksitas")

                self.root.after(0, show_error)

        threading.Thread(target=worker, daemon=True).start()

    # ==================================================
    # HALAMAN GRAFIK
    # ==================================================

    def graph_page(self):
        self.heading(
            "Grafik Perbandingan",
            "Visualisasi waktu eksekusi lima algoritma sorting"
        )

        if not self.results:
            tk.Label(
                self.container,
                text="Belum ada hasil pengujian.",
                bg=BG, fg=MUTED
            ).pack(pady=50)
            return

        panel = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        panel.pack(fill="both", expand=True, padx=30, pady=10)

        names = list(self.results.keys())
        values = list(self.results.values())

        fig = Figure(figsize=(9, 4.7), dpi=100)
        ax = fig.add_subplot(111)

        bars = ax.barh(
            names,
            values,
            color="#7770E8",
            height=0.55
        )

        ax.set_title(
            "Execution Time Comparison",
            fontsize=13,
            fontweight="bold",
            pad=15
        )
        ax.set_xlabel("Waktu Eksekusi (detik)")
        ax.set_ylabel("Algoritma")
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)

        for bar, value in zip(bars, values):
            ax.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                f" {value:.6f} s",
                va="center",
                fontsize=9
            )

        fig.tight_layout()

        self.current_canvas = FigureCanvasTkAgg(fig, master=panel)
        self.current_canvas.draw()

        self.current_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        fastest = min(self.results, key=self.results.get)

        summary = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        summary.pack(fill="x", padx=30, pady=10)

        tk.Label(
            summary,
            text="HASIL PENGUJIAN",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tk.Label(
            summary,
            text=(
                f"Algoritma tercepat: {fastest}\n"
                f"Waktu eksekusi: {self.results[fastest]:.6f} detik"
            ),
            font=("Segoe UI", 10),
            fg=GREEN, bg=WHITE,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        buttons = tk.Frame(self.container, bg=BG)
        buttons.pack(pady=20)

        self.make_button(
            buttons,
            "← ANALISIS",
            lambda: self.show_page("Analisis Kompleksitas"),
            "#85859A"
        ).pack(side="left", padx=8)

        self.make_button(
            buttons,
            "BUKA INFOGRAFIS →",
            lambda: self.show_page("Infografis")
        ).pack(side="left", padx=8)

    # ==================================================
    # INFOGRAFIS VISUAL
    # ==================================================

    def infographic_page(self):
        self.heading(
            "Infografis Hasil Analisis",
            "Visualisasi ringkas hasil eksperimen algoritma sorting"
        )

        if not self.results:
            tk.Label(
                self.container,
                text="Lakukan pengujian algoritma terlebih dahulu.",
                bg=BG,
                fg=MUTED
            ).pack(pady=50)
            return

        total = len(self.data)
        fastest = min(self.results, key=self.results.get)
        fastest_time = self.results[fastest]
        slowest = max(self.results, key=self.results.get)
        slowest_time = self.results[slowest]

        # POSTER INFOGRAFIS

        poster = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        poster.pack(fill="x", padx=30, pady=10)

        # HEADER INFOGRAFIS

        header = tk.Frame(poster, bg="#29245E")
        header.pack(fill="x")

        tk.Label(
            header,
            text="SORTIFY",
            font=("Segoe UI", 11, "bold"),
            fg="#BDB8FF",
            bg="#29245E"
        ).pack(anchor="w", padx=28, pady=(22, 5))

        tk.Label(
            header,
            text="MENGENAL EFISIENSI\nALGORITMA SORTING",
            font=("Segoe UI", 25, "bold"),
            fg=WHITE,
            bg="#29245E",
            justify="left"
        ).pack(anchor="w", padx=28)

        tk.Label(
            header,
            text=(
                "Analisis perbandingan lima algoritma pengurutan "
                "berdasarkan waktu eksekusi dan kompleksitas."
            ),
            font=("Segoe UI", 10),
            fg="#D8D5FF",
            bg="#29245E",
            wraplength=750,
            justify="left"
        ).pack(anchor="w", padx=28, pady=(10, 24))

        # BAGIAN 1: ANGKA UTAMA

        section1 = tk.Frame(poster, bg=WHITE)
        section1.pack(fill="x", padx=22, pady=(22, 8))

        tk.Label(
            section1,
            text="01  RINGKASAN PENGUJIAN",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 12))

        stat_row = tk.Frame(section1, bg=WHITE)
        stat_row.pack(fill="x")

        stats = [
            ("JUMLAH DATA", f"{total:,}", PRIMARY),
            ("JUMLAH ALGORITMA", "5", GREEN),
            ("ALGORITMA TERCEPAT", fastest, ORANGE)
        ]

        for title, value, color in stats:
            box = tk.Frame(
                stat_row,
                bg="#F7F7FC",
                highlightbackground=BORDER,
                highlightthickness=1
            )
            box.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            tk.Label(
                box,
                text=title,
                font=("Segoe UI", 8, "bold"),
                fg=MUTED,
                bg="#F7F7FC"
            ).pack(anchor="w", padx=12, pady=(13, 5))

            tk.Label(
                box,
                text=value,
                font=("Segoe UI", 16, "bold"),
                fg=color,
                bg="#F7F7FC",
                wraplength=190
            ).pack(anchor="w", padx=12, pady=(0, 13))

        # BAGIAN 2: GRAFIK WAKTU EKSEKUSI

        chart_section = tk.Frame(poster, bg=WHITE)
        chart_section.pack(fill="x", padx=22, pady=(22, 8))

        tk.Label(
            chart_section,
            text="02  PERBANDINGAN WAKTU EKSEKUSI",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            chart_section,
            text="Semakin pendek batang, semakin cepat waktu eksekusinya.",
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 12))

        chart_box = tk.Frame(chart_section, bg="#F7F7FC")
        chart_box.pack(fill="x")

        chart_canvas = tk.Canvas(
            chart_box,
            height=260,
            bg="#F7F7FC",
            highlightthickness=0
        )
        chart_canvas.pack(fill="x", padx=10, pady=12)

        colors = {
            "Bubble Sort": "#8B83E8",
            "Selection Sort": "#E6A14A",
            "Insertion Sort": "#48A88B",
            "Merge Sort": "#4F91D9",
            "Quick Sort": "#D9788A"
        }

        def draw_bars(event=None):
            chart_canvas.delete("all")

            width = max(chart_canvas.winfo_width(), 500)
            label_width = 135
            value_width = 100
            bar_start = label_width
            bar_end = width - value_width
            max_bar_width = max(bar_end - bar_start, 100)

            maximum = max(self.results.values()) or 1
            row_height = 48

            for index, (name, value) in enumerate(self.results.items()):
                y = 24 + index * row_height
                bar_width = max((value / maximum) * max_bar_width, 4)
                color = colors.get(name, PRIMARY)

                chart_canvas.create_text(
                    8, y + 10,
                    text=name,
                    anchor="w",
                    fill=TEXT,
                    font=("Segoe UI", 9, "bold")
                )

                chart_canvas.create_rectangle(
                    bar_start,
                    y,
                    bar_end,
                    y + 20,
                    fill="#E9EAF1",
                    outline=""
                )

                chart_canvas.create_rectangle(
                    bar_start,
                    y,
                    bar_start + bar_width,
                    y + 20,
                    fill=color,
                    outline=""
                )

                chart_canvas.create_text(
                    width - 8,
                    y + 10,
                    text=f"{value:.5f} s",
                    anchor="e",
                    fill=TEXT,
                    font=("Segoe UI", 8, "bold")
                )

        chart_canvas.bind("<Configure>", draw_bars)
        self.root.after(100, draw_bars)

        # BAGIAN 3: KOMPLEKSITAS

        complexity_section = tk.Frame(poster, bg=WHITE)
        complexity_section.pack(fill="x", padx=22, pady=(22, 8))

        tk.Label(
            complexity_section,
            text="03  PETA KOMPLEKSITAS ALGORITMA",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 12))

        complexity_table = tk.Frame(
            complexity_section,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        complexity_table.pack(fill="x")

        headers = [
            "ALGORITMA",
            "BEST",
            "AVERAGE",
            "WORST"
        ]

        header_row = tk.Frame(complexity_table, bg="#29245E")
        header_row.pack(fill="x")

        for index, title in enumerate(headers):
            tk.Label(
                header_row,
                text=title,
                font=("Segoe UI", 8, "bold"),
                fg=WHITE,
                bg="#29245E",
                anchor="w" if index == 0 else "center",
                width=19 if index == 0 else 13,
                padx=8,
                pady=11
            ).pack(side="left", fill="x", expand=True)

        for index, row in enumerate(COMPLEXITIES):
            bg_color = "#F7F7FC" if index % 2 == 0 else WHITE
            row_frame = tk.Frame(complexity_table, bg=bg_color)
            row_frame.pack(fill="x")

            values = [row[0], row[1], row[2], row[3]]

            for col_index, value in enumerate(values):
                tk.Label(
                    row_frame,
                    text=value,
                    font=(
                        "Segoe UI",
                        8,
                        "bold" if col_index == 0 else "normal"
                    ),
                    fg=PRIMARY if col_index == 0 else TEXT,
                    bg=bg_color,
                    anchor="w" if col_index == 0 else "center",
                    width=19 if col_index == 0 else 13,
                    padx=8,
                    pady=11
                ).pack(side="left", fill="x", expand=True)

        # BAGIAN 4: TEMUAN PENTING

        insight = tk.Frame(poster, bg=WHITE)
        insight.pack(fill="x", padx=22, pady=(22, 8))

        tk.Label(
            insight,
            text="04  TEMUAN PENTING",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 12))

        findings = [
            (
                "TERCEPAT",
                fastest,
                f"{fastest_time:.6f} detik",
                GREEN
            ),
            (
                "TERLAMBAT",
                slowest,
                f"{slowest_time:.6f} detik",
                RED
            )
        ]

        for label, name, value, color in findings:
            item = tk.Frame(
                insight,
                bg="#F7F7FC",
                highlightbackground=BORDER,
                highlightthickness=1
            )
            item.pack(fill="x", pady=4)

            tk.Frame(
                item,
                bg=color,
                width=5
            ).pack(side="left", fill="y")

            content = tk.Frame(item, bg="#F7F7FC")
            content.pack(side="left", fill="x", expand=True, padx=13, pady=10)

            tk.Label(
                content,
                text=label,
                font=("Segoe UI", 8, "bold"),
                fg=color,
                bg="#F7F7FC"
            ).pack(anchor="w")

            tk.Label(
                content,
                text=f"{name} — {value}",
                font=("Segoe UI", 10, "bold"),
                fg=TEXT,
                bg="#F7F7FC"
            ).pack(anchor="w", pady=(3, 0))

        # BAGIAN 5: KESIMPULAN

        conclusion_box = tk.Frame(
            poster,
            bg="#EFEEFF"
        )
        conclusion_box.pack(fill="x", padx=22, pady=(22, 18))

        tk.Label(
            conclusion_box,
            text="05  KESIMPULAN",
            font=("Segoe UI", 11, "bold"),
            fg=PRIMARY_DARK,
            bg="#EFEEFF"
        ).pack(anchor="w", padx=17, pady=(16, 8))

        conclusion_text = (
            f"Pengujian terhadap {total:,} data mahasiswa menunjukkan "
            f"bahwa {fastest} memperoleh waktu eksekusi tercepat, yaitu "
            f"{fastest_time:.6f} detik. Namun, hasil pengujian dapat "
            "dipengaruhi oleh perangkat, kondisi data, dan implementasi "
            "algoritma. Secara teori, Merge Sort memiliki kompleksitas "
            "O(n log n) pada seluruh kasus, sedangkan algoritma sederhana "
            "seperti Bubble Sort, Selection Sort, dan Insertion Sort "
            "umumnya memiliki kompleksitas rata-rata O(n²)."
        )

        tk.Label(
            conclusion_box,
            text=conclusion_text,
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#EFEEFF",
            justify="left",
            wraplength=850
        ).pack(anchor="w", padx=17, pady=(0, 17))

        # FOOTER INFOGRAFIS

        footer = tk.Frame(poster, bg="#29245E")
        footer.pack(fill="x")

        tk.Label(
            footer,
            text="SORTIFY  |  STUDENT SORTING ANALYTICS",
            font=("Segoe UI", 9, "bold"),
            fg=WHITE,
            bg="#29245E"
        ).pack(pady=(15, 4))

        tk.Label(
            footer,
            text="PROJECT STRUKTUR DATA",
            font=("Segoe UI", 8),
            fg="#D8D5FF",
            bg="#29245E"
        ).pack(pady=(0, 15))

        self.make_button(
            self.container,
            "← KEMBALI KE GRAFIK",
            lambda: self.show_page("Grafik"),
            "#85859A"
        ).pack(anchor="e", padx=35, pady=20)


# ==================================================
# MENJALANKAN PROGRAM
# ==================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SortingApp(root)
    root.mainloop()
