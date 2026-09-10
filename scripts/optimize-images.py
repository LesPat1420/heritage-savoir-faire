#!/usr/bin/env python3
"""Point 7 — alleger les images. Part des JPEG deja commits (dossier source disparu).
   - .webp pour les 118 photos d'album (memes dimensions)
   - vignettes 760px (webp + jpg) pour le mur de chantiers
   - cartes / portrait redimensionnes + webp
   - logo / logo-original + webp
Idempotent : on peut relancer sans degrader (les cartes/portrait sont deja
a la taille cible apres le 1er passage, thumbnail ne fait que reduire)."""
import glob, os
from PIL import Image, ImageOps

ROOT = "/home/patrick/Bureau/Sites/Francois/assets/img"
os.chdir(ROOT)

def save_webp(im, path, q=80):
    im.save(path, "WEBP", quality=q, method=6)

def load(path):
    return ImageOps.exif_transpose(Image.open(path))

# 1. webp pour toutes les photos d'album
album = sorted(glob.glob("realisations/*/*.jpg"))
for f in album:
    w = f[:-4] + ".webp"
    save_webp(load(f).convert("RGB"), w, 80)
print(f"albums : {len(album)} webp")

# 2. vignettes du mur (covers NN=00)
for f in sorted(glob.glob("realisations/*/00.jpg")):
    im = load(f).convert("RGB")
    t = im.copy()
    t.thumbnail((760, 760), Image.LANCZOS)
    base = f[:-4] + "-thumb"
    t.save(base + ".jpg", "JPEG", quality=78, optimize=True, progressive=True)
    save_webp(t, base + ".webp", 78)
print("vignettes mur : 11")

# 3. cartes -> 820px de large
for f in sorted(glob.glob("cartes/*.jpg")):
    im = load(f).convert("RGB")
    im.thumbnail((820, 820), Image.LANCZOS)
    im.save(f, "JPEG", quality=80, optimize=True, progressive=True)
    save_webp(im, f[:-4] + ".webp", 82)
print("cartes : 4 (jpg redim + webp)")

# 4. portrait -> 760px de large
im = load("portrait-lou.jpg").convert("RGB")
im.thumbnail((760, 1200), Image.LANCZOS)
im.save("portrait-lou.jpg", "JPEG", quality=82, optimize=True, progressive=True)
save_webp(im, "portrait-lou.webp", 82)
print("portrait :", im.size)

# 5. logo.png (garde l'alpha) -> 512px + webp
im = load("logo.png").convert("RGBA")
im.thumbnail((512, 512), Image.LANCZOS)
im.save("logo.png", "PNG", optimize=True)
im.save("logo.webp", "WEBP", quality=90, method=6)
print("logo.png :", im.size, os.path.getsize("logo.png") // 1024, "KB")

# 6. logo-original.jpg (rond, petit) -> 200px + webp
im = load("logo-original.jpg").convert("RGB")
im.thumbnail((200, 200), Image.LANCZOS)
im.save("logo-original.jpg", "JPEG", quality=84, optimize=True, progressive=True)
save_webp(im, "logo-original.webp", 86)
print("logo-original :", im.size)

# bilan
def mb(p): return sum(os.path.getsize(x) for x in glob.glob(p, recursive=True)) / 1e6
print(f"\nrealisations jpg : {mb('realisations/**/*.jpg'):.1f} MB")
print(f"realisations webp: {mb('realisations/**/*.webp'):.1f} MB")
