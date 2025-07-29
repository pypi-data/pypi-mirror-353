
from PIL import Image
import os
import importlib.resources
import webbrowser
import subprocess
import random
class furry:
    def randomimage(nsfw=False):
        path = "safe" if not nsfw else "sus"
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        files = [f for f in os.listdir(path=path) if os.path.isfile(f) and f.lower().endswith(image_extensions)]

        if not files:
            raise FileNotFoundError("No image files found in the current directory.")
        
        random.shuffle(files)
        chosen_file = random.choice(files)
        

        img = Image.open(chosen_file)
        return img


