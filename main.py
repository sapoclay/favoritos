import subprocess
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, Menu, Toplevel, Label, filedialog
import webbrowser
import json
import os
import validators
from PIL import Image, ImageTk
import openpyxl
import actualizaciones

class URLManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Manager")
        self.categories = []
        self.file_path = "urls.json"
        
        self.load_urls()

        self.add_category_button = tk.Button(root, text="Agregar Categoría", command=self.add_category)
        self.add_category_button.pack(pady=10)

        self.canvas = tk.Canvas(root)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.url_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.url_frame, anchor="n")

        self.url_frame.bind("<Configure>", self.on_frame_configure)

        self.display_urls()

        self.create_menu()

    def load_urls(self):
        self.categories = []
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    content = file.read()
                    if content.strip():
                        loaded_data = json.loads(content)
                        if all(isinstance(item, dict) and 'category' in item and 'urls' in item for item in loaded_data):
                            self.categories = loaded_data
                        else:
                            raise ValueError("Formato incorrecto en el archivo JSON.")
                    else:
                        messagebox.showwarning("Advertencia", "El archivo de URLs está vacío.")
            except (json.JSONDecodeError, ValueError) as e:
                messagebox.showerror("Error", f"Error al cargar URLs: {e}")
        else:
            messagebox.showwarning("Advertencia", "El archivo de URLs no existe. Se creará uno nuevo.")
            self.save_urls()

    def save_urls(self):
        with open(self.file_path, "w") as file:
            json.dump(self.categories, file)

    def add_category(self):
        category = simpledialog.askstring("Agregar Categoría", "Introduce el nombre de la categoría:")
        if category:
            self.categories.append({"category": category, "urls": []})
            self.save_urls()
            self.display_urls()

    def delete_category(self, category):
        self.categories = [cat for cat in self.categories if cat["category"] != category]
        self.save_urls()
        self.display_urls()

    def edit_category(self, old_category):
        new_category = simpledialog.askstring("Editar Categoría", "Edita el nombre de la categoría:", initialvalue=old_category)
        if new_category:
            for cat in self.categories:
                if cat["category"] == old_category:
                    cat["category"] = new_category
            self.save_urls()
            self.display_urls()

    def add_url(self, category):
        url = simpledialog.askstring("Agregar URL", "Introduce la URL:")
        if url:
            if validators.url(url):
                for cat in self.categories:
                    if cat["category"] == category:
                        cat["urls"].append(url)
                self.save_urls()
                self.display_urls()
            else:
                messagebox.showerror("Error", "La URL introducida no es válida.")

    def delete_url(self, category, url):
        for cat in self.categories:
            if cat["category"] == category:
                cat["urls"].remove(url)
        self.save_urls()
        self.display_urls()

    def edit_url(self, category, url):
        new_url = simpledialog.askstring("Editar URL", "Edita la URL:", initialvalue=url)
        if new_url:
            if validators.url(new_url):
                for cat in self.categories:
                    if cat["category"] == category:
                        index = cat["urls"].index(url)
                        cat["urls"][index] = new_url
                self.save_urls()
                self.display_urls()
            else:
                messagebox.showerror("Error", "La URL introducida no es válida.")

    def display_urls(self):
        for widget in self.url_frame.winfo_children():
            widget.destroy()

        for category in self.categories:
            category_frame = tk.Frame(self.url_frame, borderwidth=2, relief="groove")
            category_frame.pack(fill="x", pady=5)

            category_label_frame = tk.Frame(category_frame)
            category_label_frame.pack(side="top", fill="x")

            category_label = tk.Label(category_label_frame, text=category["category"], font=("Helvetica", 14, "bold"), cursor="hand2")
            category_label.pack(side="left", fill="x", expand=True)
            category_label.bind("<Button-1>", lambda e, c=category["category"]: self.edit_category(c))

            delete_category_button = tk.Button(category_label_frame, text="Eliminar Categoría", command=lambda c=category["category"]: self.delete_category(c))
            delete_category_button.pack(side="right")

            add_url_button = tk.Button(category_frame, text="Agregar URL", command=lambda c=category["category"]: self.add_url(c))
            add_url_button.pack(side="top", pady=5)

            for url in category["urls"]:
                frame = tk.Frame(category_frame)
                frame.pack(fill="x", pady=5)

                btn = tk.Button(frame, text=url, command=lambda u=url: self.open_url(u), wraplength=250, justify="left")
                btn.pack(side="left", fill="x", expand=True)

                edit_btn = tk.Button(frame, text="Editar", command=lambda u=url, c=category["category"]: self.edit_url(c, u))
                edit_btn.pack(side="left", padx=5)

                del_btn = tk.Button(frame, text="Eliminar", command=lambda u=url, c=category["category"]: self.delete_url(c, u))
                del_btn.pack(side="right")

        self.url_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.center_buttons()

    def open_url(self, url):
        try:
            webbrowser.open(url, new=1)  # Open in a new browser window
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la URL: {e}")

    def abrir_url_github(self):
        webbrowser.open("https://github.com/sapoclay/favoritos")

    def abrir_ventana_actualizaciones(self):
        actualizaciones.mostrar_ventana_actualizaciones()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.center_buttons()  # Ensure the buttons are centered when the frame is configured

    def center_buttons(self):
        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        for frame in self.url_frame.winfo_children():
            frame.update_idletasks()
            frame_width = frame.winfo_width()
            padx = (canvas_width - frame_width) // 2
            if padx < 0:
                padx = 0
            frame.pack_configure(padx=padx)

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a Excel", command=self.export_to_excel)
        file_menu.add_command(label="Salir", command=self.root.quit)

        preferencias_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Preferencias", menu=preferencias_menu)
        preferencias_menu.add_command(label="Repositorio GitHub", command=self.abrir_url_github)
        preferencias_menu.add_separator()
        preferencias_menu.add_command(label="Buscar Actualizaciones", command=self.abrir_ventana_actualizaciones)

        about_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Acerca de", menu=about_menu)
        about_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        about_window = Toplevel(self.root)
        about_window.title("Acerca de")
        about_window.geometry("300x300")

        label = Label(about_window, text="Gestor de URLs\nVersión 0.5\nDesarrollado por entreunosyceros")
        label.pack(pady=10)

        image_path = "logo.png"
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((150, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = Label(about_window, image=photo)
            img_label.image = photo
            img_label.pack(pady=10)

    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "URLs"

        row = 1
        for category in self.categories:
            sheet[f"A{row}"] = category["category"]
            row += 1
            for url in category["urls"]:
                sheet[f"A{row}"] = url
                row += 1

        try:
            workbook.save(file_path)
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

if __name__ == "__main__":
    if not os.path.exists("dependencies_installed"):
        print("Instalando dependencias...")
        result = subprocess.run([sys.executable, "instalar_dependencias.py"])
        if result.returncode != 0:
            print("Error al instalar dependencias. Saliendo.")
            sys.exit(1)

    root = tk.Tk()
    app = URLManagerApp(root)
    root.geometry("600x600")
    root.resizable(False, False)  # Disable window resizing
    root.mainloop()