import PIL
from PIL import Image
import os
import importlib.resources
import webbrowser
import subprocess
import tempfile
import random
import base64
from io import BytesIO
import ctypes
class utils:
    @staticmethod
    def set_background(file_obj):
        if not file_obj:
            print("ERROR: No file object")
            return "ERROR"

        img_bytes = file_obj.read()
        img = Image.open(BytesIO(img_bytes)).convert("RGBA")


        temp_path = os.path.join(tempfile.gettempdir(), "bacground.png")

        # Save to .ico with varying size (optional, to mimic your original code)
        img.save(temp_path, format="PNG")

            # Set as Windows wallpaper
        ctypes.windll.user32.SystemParametersInfoW(20, 0,temp_path, 0)
        return "SUCCESS"


    def set_cursor(file_obj):
        if not file_obj:
            print("ERROR: No file object")
            return "ERROR"

        try:
            img_bytes = file_obj.read()
            img = Image.open(BytesIO(img_bytes)).convert("RGBA")
            img = img.resize((32, 32))

            temp_path = os.path.join(tempfile.gettempdir(), "cursor.ico")

            # Save to .ico with varying size (optional, to mimic your original code)
            img.save(temp_path, format="ICO", sizes=[(random.randint(20, 32), random.randint(20, 32))])

            # Cursor types to override
            cursor_ids = [
                32512,  # OCR_NORMAL
                32513,  # OCR_IBEAM
                32514,  # OCR_WAIT
                32515,  # OCR_CROSS
                32649,  # OCR_HAND
                32650   # OCR_APPSTARTING
            ]

            for cursor_id in cursor_ids:
                hcursor = ctypes.windll.user32.LoadCursorFromFileW(temp_path)
                if not hcursor:
                    raise ctypes.WinError()
                ctypes.windll.user32.SetSystemCursor(hcursor, cursor_id)

            return "SUCCESS"
        
        except Exception as e:
            print("ERROR:", e)
            return f"ERROR: {str(e)}"
    
    def reset_cursor():
        SPI_SETCURSORS = 0x0057
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, 0)

 