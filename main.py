import tkinter as tk
from tkinter import simpledialog, messagebox, Menu, Toplevel, Label, filedialog
import webbrowser
import json
import os
import validators
from PIL import Image, ImageTk  # Necesitarás instalar Pillow (pip install pillow)
import openpyxl  # Para generar el archivo Excel

class URLManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Manager")
        self.urls = []
        self.file_path = "urls.json"
        
        self.load_urls()

        self.add_url_button = tk.Button(root, text="Agregar URL", command=self.add_url)
        self.add_url_button.pack(pady=10)

        self.canvas = tk.Canvas(root)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.url_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.url_frame, anchor="n")

        self.url_frame.bind("<Configure>", self.on_frame_configure)

        self.display_urls()

    def load_urls(self):
        self.urls = []
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    content = file.read()
                    if content.strip():  # Verificar si el contenido no está vacío
                        self.urls = json.loads(content)
                    else:
                        messagebox.showwarning("Advertencia", "El archivo de URLs está vacío.")
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Error al cargar URLs: {e}")
        else:
            messagebox.showwarning("Advertencia", "El archivo de URLs no existe. Se creará uno nuevo.")
            self.save_urls()  # Guarda una lista vacía inicial en un nuevo archivo

    def save_urls(self):
        with open(self.file_path, "w") as file:
            json.dump(self.urls, file)

    def add_url(self):
        url = simpledialog.askstring("Agregar URL", "Introduce la URL:")
        if url:
            if validators.url(url):
                self.urls.append(url)
                self.save_urls()
                self.display_urls()
            else:
                messagebox.showerror("Error", "La URL introducida no es válida.")

    def delete_url(self, url):
        self.urls.remove(url)
        self.save_urls()
        self.display_urls()

    def display_urls(self):
        for widget in self.url_frame.winfo_children():
            widget.destroy()

        for url in self.urls:
            frame = tk.Frame(self.url_frame)
            frame.pack(fill="x", pady=5)
            btn = tk.Button(frame, text=url, command=lambda u=url: self.open_url(u), wraplength=250, justify="left")
            btn.pack(side="left", fill="x", expand=True)
            del_btn = tk.Button(frame, text="Eliminar", command=lambda u=url: self.delete_url(u))
            del_btn.pack(side="right")

        self.url_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.center_buttons()

    def open_url(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la URL: {e}")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
    def abrir_url_github(self):
        webbrowser.open("https://github.com/sapoclay/favoritos")
        
            # Función para abrir la ventana de actualizaciones
    def abrir_ventana_actualizaciones(self):
        # Importar el módulo actualizaciones.py
        import actualizaciones
        # Llamar a la función para mostrar la ventana de actualizaciones
        actualizaciones.mostrar_ventana_actualizaciones()

    def center_buttons(self):
        for frame in self.url_frame.winfo_children():
            frame.update_idletasks()  # Actualizar el frame para obtener dimensiones correctas
            # Calcular el padding necesario para centrar el frame en el canvas
            padx = (self.canvas.winfo_width() - frame.winfo_width()) // 2
            frame.pack_configure(padx=(padx, 0))  # Añadir padding al frame para centrarlo

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a Excel", command=self.export_to_excel)
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Crear el menú Preferencias
        preferencias_menu = Menu(self.root, tearoff=0)
        menubar.add_cascade(label="Preferencias", menu=preferencias_menu)
        preferencias_menu.add_command(label="Repositorio GitHub", command=self.abrir_url_github)
        preferencias_menu.add_separator()
        preferencias_menu.add_command(
            label="Buscar Actualizaciones", command=self.abrir_ventana_actualizaciones
        )


        about_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Acerca de", menu=about_menu)
        about_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        about_window = Toplevel(self.root)
        about_window.title("Acerca de")
        about_window.geometry("300x300")

        label = Label(about_window, text="Gestor de URLs\nVersión 0.5\nDesarrollado por entreunosyceros")
        label.pack(pady=10)

        # Cargar imagen (asegúrate de tener una imagen en el mismo directorio que este script)
        image_path = "logo.png"  # Reemplaza con tu imagen
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((150, 150), Image.LANCZOS)  # Cambiar ANTIALIAS por LANCZOS
            photo = ImageTk.PhotoImage(img)
            img_label = Label(about_window, image=photo)
            img_label.image = photo  # Guardar referencia de la imagen para que no se recoja por el garbage collector
            img_label.pack(pady=10)

    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return  # El usuario canceló la operación

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "URLs"

        sheet["A1"] = "URL"

        for idx, url in enumerate(self.urls, start=2):
            sheet[f"A{idx}"] = url

        try:
            workbook.save(file_path)
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = URLManagerApp(root)
    root.geometry("400x400")
    root.mainloop()
