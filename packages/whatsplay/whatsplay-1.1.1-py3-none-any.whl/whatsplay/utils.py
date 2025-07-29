import cv2
import numpy as np
import platform
import subprocess
def show_qr_window(qr_image_bytes):
    """
    Shows a QR code window with proper sizing and settings.
    Now works with Playwright's screenshot bytes format.
    """
    # Convert Playwright's screenshot bytes to OpenCV image
    nparr = np.frombuffer(qr_image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    window_name = "Scan WhatsApp QR Code"
    # Create window with proper settings
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, image)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    
    # Resize window for better visibility
    if image is not None:
        height, width = image.shape[:2]
        target_size = 500
        aspect_ratio = width / height
        new_width = int(target_size * aspect_ratio)
        cv2.resizeWindow(window_name, new_width, target_size)
    
    # Display window until key press or timeout
    cv2.waitKey(1)  # This will show the window and return immediately

def close_all_windows():
    """
    Ensures all OpenCV windows are closed
    """
    cv2.destroyAllWindows()
    # Sometimes windows don't close properly on Windows, so we need to call waitKey
    cv2.waitKey(1)


def copy_file_to_clipboard(filepath):
    system = platform.system()
    
    if system == "Windows":
        # En Windows usamos PowerShell Set-Clipboard -LiteralPath
        command = ['powershell', 'Set-Clipboard', '-LiteralPath', filepath]
        try:
            subprocess.run(command, check=True)
            print("Archivo copiado al portapapeles en Windows.")
        except subprocess.CalledProcessError:
            print("Error copiando archivo al portapapeles en Windows.")
    
    elif system == "Linux":
        # En Linux no hay un portapapeles nativo para archivos como en Windows,
        # pero podemos copiar la ruta como texto al portapapeles (ejemplo con xclip)
        try:
            # Asegúrate de tener xclip instalado: sudo apt install xclip
            subprocess.run(['xclip', '-selection', 'clipboard'], input=filepath.encode(), check=True)
            print("Ruta del archivo copiada al portapapeles en Linux (como texto).")
        except FileNotFoundError:
            print("xclip no está instalado. Instálalo para copiar al portapapeles.")
        except subprocess.CalledProcessError:
            print("Error copiando ruta al portapapeles en Linux.")
    
    else:
        print(f"Sistema operativo '{system}' no soportado para copiar archivos al portapapeles.")