#!/usr/bin/env python3
"""Construit les albums de chantiers a partir de ~/Bureau/photos book entreprise 02/
(un sous-dossier = un projet) : redimensionne, genere les .webp (galerie + mur +
pellicule) et ecrit assets/js/projets.js.

Configuration 2026-09-11 (9 dossiers, cf. demande de l'utilisateur) : les captions
individuelles ne sont PAS renseignees (volume trop important pour une legende par
photo cette fois-ci) - seuls le titre, le resume et la couverture de chaque album
sont soignes. A completer avec Lou si souhaite.

Usage : python3 scripts/build-albums.py
Necessite Pillow (pip3 install --user pillow).
"""
import os, shutil, json
from PIL import Image, ImageOps

SRC = os.path.expanduser("~/Bureau/photos book entreprise 02")
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(PROJ, "assets", "img", "realisations")
JS_OUT = os.path.join(PROJ, "assets", "js", "projets.js")

# (id, dossier source, titre, resume, legende du mur)
ALBUMS = [
    ("longere", "renovation",
     "Restauration complète d'une longère en pierre",
     "D'une ruine à une maison habitable : reprise des maçonneries, charpente neuve, "
     "préau en chêne et aménagements bois.",
     "Une longère en ruine, remise debout"),
    ("maison-courbe", "maison a ossatoire bois",
     "Des maisons neuves en ossature bois",
     "Plusieurs maisons construites en ossature bois, du plancher au bardage, "
     "toiture droite ou courbe.",
     "Des maisons neuves en ossature bois"),
    ("charpente", "charpente",
     "La charpente, du neuf à la reprise",
     "Fermes, pannes, préaux, pergolas et charpentes d'églises : assemblages "
     "taillés à la main, du plan au levage.",
     "La charpente, du neuf à la reprise"),
    ("assemblages", "assemblages",
     "Les assemblages, taillés à la main",
     "Tenons, mortaises, abouts, embrèvements : le geste du trait de charpente, "
     "à l'atelier.",
     "Les assemblages, taillés à la main"),
    ("escaliers", "escaliers",
     "Des escaliers, droits ou courbes",
     "Escaliers sur mesure en bois massif, du plus simple au balancé.",
     "Des escaliers, droits ou courbes"),
    ("couverture", "couverture",
     "La couverture, tuile et zinc",
     "Toitures neuves ou reprises : tuile terre cuite, pavillons et pergolas.",
     "La couverture, tuile et zinc"),
    ("etaiement", "etaiement",
     "Étayer avant de reprendre",
     "Étaiements provisoires en charpente d'église et de bâtiments anciens, "
     "avant travaux de reprise.",
     "Étayer avant de reprendre"),
    ("terrasse", "terrasse",
     "Terrasses et pergolas",
     "Terrasses bois autour de piscines, en Corse et ailleurs, jusqu'à la pergola.",
     "Terrasses et pergolas"),
    ("divers", "Divers",
     "Et tout ce qui se fait à l'établi",
     "Meubles, portes, jouets, une barque... tout ce que le bois permet, à l'atelier.",
     "Et tout ce qui se fait à l'établi"),
]

# fichier choisi comme couverture (index dans la liste triee) pour chaque dossier source
COVERS = {
    "renovation": 21,
    "maison a ossatoire bois": 16,
    "charpente": 18,
    "assemblages": 4,
    "escaliers": 6,
    "couverture": 5,
    "etaiement": 0,
    "terrasse": 4,
    "Divers": 19,
}


def list_photos(folder):
    p = os.path.join(SRC, folder)
    return sorted(f for f in os.listdir(p) if f.lower().endswith((".jpg", ".jpeg", ".png")))


def normalise(im):
    """Egalise exposition/contraste (etirement d'histogramme, 1% ecrete de
    chaque cote) pour attenuer les ecarts entre photos prises a des dates/
    conditions de lumiere differentes."""
    return ImageOps.autocontrast(im, cutoff=1)


def process(src_path, dst_base, edge, q=74):
    im = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    im = normalise(im)
    im.thumbnail((edge, edge), Image.LANCZOS)
    im.save(dst_base + ".jpg", "JPEG", quality=q, optimize=True, progressive=True)
    im.save(dst_base + ".webp", "WEBP", quality=72, method=6)
    # vignette pour la pellicule de la visionneuse
    t = im.copy()
    t.thumbnail((260, 260), Image.LANCZOS)
    t.save(dst_base + "-t.webp", "WEBP", quality=72, method=6)
    return im.size


def main():
    if not os.path.isdir(SRC):
        print(f"Source introuvable : {SRC}")
        return 1

    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(DST)

    out = []
    total = 0
    for pid, folder, titre, resume, wall_cap in ALBUMS:
        files = list_photos(folder)
        if not files:
            print("VIDE :", folder)
            continue
        cover_idx = COVERS.get(folder, 0)
        cover = files[cover_idx]
        ordered = [cover] + [f for f in files if f != cover]

        album_dir = os.path.join(DST, pid)
        os.makedirs(album_dir, exist_ok=True)
        photos = []
        for i, fname in enumerate(ordered):
            edge = 1500 if i == 0 else 1280
            base = os.path.join(album_dir, f"{i:02d}")
            process(os.path.join(SRC, folder, fname), base, edge)
            photos.append({"src": f"assets/img/realisations/{pid}/{i:02d}.jpg", "leg": ""})
            total += 1
        # vignette 760px du mur, a partir de la couverture (00)
        cov_im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, folder, cover))).convert("RGB")
        cov_im = normalise(cov_im)
        cov_im.thumbnail((760, 760), Image.LANCZOS)
        cov_im.save(os.path.join(album_dir, "00-thumb.jpg"), "JPEG", quality=78, optimize=True, progressive=True)
        cov_im.save(os.path.join(album_dir, "00-thumb.webp"), "WEBP", quality=78, method=6)

        out.append({"id": pid, "titre": titre, "resume": resume, "wall": wall_cap, "photos": photos})
        print(f"{pid:16s} {len(photos):3d} photos  (couverture: {cover})")

    # assets/js/projets.js — json.dumps pour un echappement correct (apostrophes
    # francaises, accents) plutot qu'un bricolage repr()/replace() fragile.
    lines = ["/* Genere par scripts/build-albums.py — chantiers de Lou Francois. photos[0] = couverture. */",
             "window.PROJETS = ["]
    for a in out:
        lines.append(" {")
        lines.append(f'  "id": {json.dumps(a["id"], ensure_ascii=False)},')
        lines.append(f'  "titre": {json.dumps(a["titre"], ensure_ascii=False)},')
        lines.append(f'  "resume": {json.dumps(a["resume"], ensure_ascii=False)},')
        lines.append('  "photos": [')
        for p in a["photos"]:
            lines.append("   {")
            lines.append(f'    "src": {json.dumps(p["src"], ensure_ascii=False)},')
            lines.append(f'    "leg": {json.dumps(p["leg"], ensure_ascii=False)}')
            lines.append("   },")
        lines.append("  ]")
        lines.append(" },")
    lines.append("];")
    with open(JS_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nTotal : {total} photos, {len(out)} albums -> {JS_OUT}")
    print("Legendes du mur (a coller dans index.html) :")
    for a in out:
        print(f'  {a["id"]:16s} {a["wall"]!r}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
