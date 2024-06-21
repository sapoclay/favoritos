import subprocess
import sys

def check_installation(package):
    """Verifica si un paquete está instalado."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    return True

def install_package(package):
    """Instala un paquete utilizando pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    return True

def install_dependencies():
    """Instala todas las dependencias necesarias."""
    dependencies = [
        "validators",
        "Pillow",
        "openpyxl",
        "requests",
        "wget"
        # Agrega aquí todas las dependencias necesarias
    ]

    for dependency in dependencies:
        if not check_installation(dependency):
            print(f"Instalando {dependency}...")
            installed = install_package(dependency)
            if not installed:
                print(f"No se pudo instalar {dependency}.")
                return False

    print("Todas las dependencias están instaladas correctamente.")
    return True

if __name__ == "__main__":
    # Ejecutar la instalación de dependencias
    if not install_dependencies():
        sys.exit(1)  # Salir si la instalación falló
    else:
        # Crear un archivo vacío para marcar que las dependencias están instaladas
        with open("dependencies_installed", "w") as f:
            f.write("Dependencias instaladas correctamente")
        print("Puedes iniciar la aplicación ahora.")
        sys.exit(0)
