#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optimise les photos des chantiers de Lou + genere assets/js/projets.js"""
import os, json, shutil
from PIL import Image, ImageOps

SRC = os.path.expanduser("~/Téléchargements/photos book entreprise 02")
DESK = os.path.expanduser("~/Bureau")
PROJ = os.path.expanduser("~/Bureau/Sites/Francois")
DST = os.path.join(PROJ, "assets/img/realisations")

def S(*p): return os.path.join(SRC, *p)
def D(*p): return os.path.join(DESK, *p)

# ---- Manifeste : id -> (titre, resume, [(chemin_source, legende), ...])  (1re = couverture)
ALBUMS = [
 ("longere", "Restauration complète d'une longère en pierre",
  "D'une ruine à une maison habitable : reprise des murs, charpente neuve, préau, menuiseries et terrasse.",
  [
   (S("Pierrette","final et frontPHOTO-2021.jpg"), "La longère restaurée, l'hiver suivant la fin du chantier"),
   (S("Pierrette","02.jpg"), "Au départ : un pignon effondré et des murs à reprendre"),
   (S("Pierrette","21.jpg"), "Démolition des parties instables, tri des pierres"),
   (S("Pierrette","03.jpg"), "Reprise des maçonneries à la grue"),
   (S("Pierrette","04.jpg"), "Extension en ossature bois greffée sur l'existant"),
   (S("Pierrette","11.jpg"), "Le volume retrouvé, avant charpente définitive"),
   (S("Pierrette","IMG_20210603_171916.jpg"), "Escalier métallique d'accès à l'étage"),
   (S("Pierrette","IMG_20210626_165049.jpg"), "Terrasse bois et garde-corps sur la façade sud"),
   (S("Pierrette","05.jpg"), "Préau en chêne monté sur la façade"),
   (S("Pierrette","06.jpg"), "Le préau vu de dessous, bardage intérieur posé"),
   (S("Pierrette","20210709_162418.jpg"), "Portes en chêne à pentures forgées et niche d'origine"),
   (S("Pierrette","20210709_162425.jpg"), "Encadrements en pierre restitués autour des portes"),
   (S("Pierrette","23.jpg"), "Mur de refend rejointoyé à la chaux"),
   (S("Pierrette","25.jpg"), "Ammonite prise dans une pierre du pays, laissée apparente"),
   (S("Pierrette","IMG_20210626_162814.jpg"), "Platelage de la terrasse en cours de pose"),
  ]),

 ("lavoir", "Lavoir sous charpente chêne, couverture tuile",
  "Charpente traditionnelle taillée à l'atelier puis levée sur les murs anciens du lavoir, et couverture neuve.",
  [
   (S("lavoir du park","05.jpg"), "La charpente levée sur les murs de pierre du lavoir"),
   (S("lavoir du park","01.jpg"), "Tracé et taille de la charpente à l'atelier"),
   (S("lavoir du park","02.jpg"), "Pièces de chêne prêtes à l'assemblage"),
   (S("lavoir du park","04.jpg"), "Montage des fermes sur site"),
   (S("lavoir du park","07.jpg"), "Contrefiches courbes et assemblages apparents"),
   (S("lavoir du park","06.jpg"), "Charpente complète, avant couverture"),
   (S("lavoir du park","09.jpg"), "Écran de sous-toiture et liteaunage"),
   (S("lavoir du park","10.jpg"), "Couverture terminée en tuile de pays"),
  ]),

 ("abri", "Abri de jardin en ossature bois et bardage",
  "Un abri de A à Z : plancher, ossature, charpente, bardage douglas et couverture tuile.",
  [
   (S("abri de jardin Marsannay","IMG_20221012_174907324.jpg"), "L'abri terminé, portes en bois et bardage douglas"),
   (S("abri de jardin Marsannay","IMG_20220826_113041624.jpg"), "Plancher bois sur plots béton"),
   (S("abri de jardin Marsannay","IMG_20220826_120609387.jpg"), "Montage des panneaux d'ossature"),
   (S("abri de jardin Marsannay","IMG_20220826_143051450.jpg"), "Charpente posée sur l'ossature"),
   (S("abri de jardin Marsannay","IMG_20220827_101905524.jpg"), "Volume hors d'eau hors d'air"),
   (S("abri de jardin Marsannay","IMG_20220903_172735751.jpg"), "Couverture tuile et bardage en cours"),
   (S("abri de jardin Marsannay","IMG_20220903_172814767.jpg"), "Bardage à claire-voie posé sur trois faces"),
  ]),

 ("maison-courbe", "Maison contemporaine à toiture courbe",
  "Ossature et charpente bois d'une maison neuve à toit courbe, bardage mélèze, planchers et terrasses.",
  [
   (S("170.jpg"), "La maison livrée, bardage mélèze et toiture zinc courbe"),
   (S("facade cotée entrée.JPG"), "Façade côté entrée en fin de chantier"),
   (S("157.JPG"), "Ossature bois sous pare-pluie"),
   (S("159.JPG"), "Naissance de la toiture courbe"),
   (S("162.jpg"), "Plancher de l'étage"),
   (S("164.jpg"), "Levage des murs préfabriqués"),
   (S("lou perché 2.JPG"), "Lou sur la charpente pendant le montage"),
   (S("etage avec moi.JPG"), "Réglage des arbalétriers courbes à l'étage"),
   (S("169.jpg"), "Pose du bardage mélèze"),
   (S("angle coté feu.JPG"), "Angle de toiture : jonction bardage / zinc"),
   (S("vue du champ.JPG"), "La maison vue depuis le champ"),
   (S("a2.jpg"), "Volume annexe bardé, côté jardin"),
  ]),

 ("halle", "Grande charpente courbe en lamellé-collé",
  "Charpente courbe de grande portée pour un bâtiment agricole, montée à la grue.",
  [
   (S("07.jpg"), "Le bâtiment terminé, longue toiture courbe"),
   (S("03.jpg"), "Levage des arbalétriers courbes"),
   (S("04.jpg"), "Charpente en place sur la structure"),
   (S("05.jpg"), "Façade vitrée sous la charpente"),
   (S("06.jpg"), "Vue d'ensemble en fin de gros œuvre"),
   (S("02.jpg"), "Pièces de lamellé-collé livrées sur site"),
  ]),

 ("assemblages", "Assemblages traditionnels taillés à la main",
  "Le cœur du métier : traits de Jupiter, tenons-mortaises et embrèvements taillés au ciseau et à la scie.",
  [
   (S("Ass 05.jpg"), "Croix de Saint-André taillée dans la masse"),
   (S("ASS 01.jpg"), "Enfourchement en about de pièce"),
   (S("Ass 02.jpg"), "Trait de Jupiter, vue de dessus"),
   (S("Ass 03.jpg"), "Sifflet et clé d'un trait de Jupiter"),
   (S("Ass 04.jpg"), "Assemblage moisé sur poteau"),
   (S("Ass 08.jpg"), "Embrèvement tracé sur pièce ancienne"),
   (S("Ass 12.jpg"), "Trait de Jupiter ouvert avant emboîtage"),
   (S("Ass 13.jpg"), "Croisement à mi-bois de deux entraits"),
   (S("Ass 14.jpg"), "Tenon et clé d'about"),
   (S("Ass 15.jpg"), "Assemblage serré, une fois monté"),
  ]),

 ("bonifacio", "Charpente et terrasse bois face à la mer",
  "Charpente préfabriquée à l'atelier puis levée à la grue, et grande terrasse bois, en Corse.",
  [
   (S("Bonifacio-20150309-02329.jpg"), "Charpente posée, terrasse en construction"),
   (S("DSC00669.JPG"), "La ferme préassemblée, prête au levage"),
   (S("DSC00663.JPG"), "Assemblage de la charpente au sol"),
   (S("DSC00671.JPG"), "Levage à la grue au-dessus du bâti"),
   (S("Bonifacio-20150309-02334.jpg"), "Sous la charpente, terrasse et mur de pierre"),
   (S("Bonifacio-20150319-02363.jpg"), "Toiture zinc terminée, vue du dessus"),
   (S("Bonifacio-20150319-02368.jpg"), "Charpente de l'auvent sur mur maçonné"),
  ]),

 ("comble", "Reprise d'une charpente de comble ancienne",
  "Consolidation et remise en état d'une charpente de comble, pièce par pièce.",
  [
   (S("après 01.jpg"), "Le comble repris, assaini et renforcé"),
   (S("avant 01.jpg"), "État d'origine : bois affaissés et fissures"),
   (S("avant 02.jpg"), "Appuis de charpente à reprendre"),
   (S("première partie.jpg"), "Renforts posés sur la première travée"),
   (S("seconde parie.jpg"), "Seconde travée étayée puis reprise"),
   (S("après 02.jpg"), "Détail d'un about de ferme greffé"),
  ]),

 ("divers", "Menuiserie et ouvrages sur mesure",
  "En dehors de la charpente : tables, portes, escaliers, mobilier et pièces sculptées.",
  [
   (S("IMG_20181024_193611.jpg"), "Grande table en chêne massif, plateau à frises"),
   (S("Divers","IMG_20200429_164751.jpg"), "Table ronde à plateau marqueté en rayons"),
   (S("Divers","IMG_20200429_164834.jpg"), "Table basse à entretoise courbe"),
   (S("Divers","IMG_20200429_164829.jpg"), "Coffre en chêne gravé"),
   (S("Divers","IMG_20200429_164900.jpg"), "Portes de grange cintrées en douglas"),
   (S("Divers","IMG_20200429_164932.jpg"), "Pièce sculptée à la gouge"),
   (S("Divers","IMG_20200429_164938.jpg"), "Arc lamellé-collé cintré à l'atelier"),
   (S("Divers","IMG_20200429_170945.jpg"), "Échiquier marqueté, coffret à tiroir"),
   (S("Divers","IMG_20200429_171007.jpg"), "Hotte de cheminée en chêne"),
   (S("Divers","IMG_20200429_171015.jpg"), "Buffet de cuisine sur mesure"),
   (S("Divers","IMG_20200429_171020.jpg"), "Bibliothèque murale toute hauteur"),
   (S("Divers","IMG_20200429_171038.jpg"), "Escalier extérieur en bois"),
   (S("Resized_Snapchat-1935649492.jpg"), "Lit cabane pour chambre d'enfant"),
  ]),
]

# ---- portrait de Lou (section « Mon histoire », les 3 maquettes)
#      écrit dans assets/img/ (hors DST, non purgé par le rmtree)
SINGLES = {
 "portrait-lou": (D("lou francois.png"), 1200),
}

def opt(src, dst, edge, q=74):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((edge, edge), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
    return os.path.getsize(dst), im.size

if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST)

data = []
total = 0
for aid, titre, resume, photos in ALBUMS:
    entry = {"id": aid, "titre": titre, "resume": resume, "photos": []}
    for i, (src, leg) in enumerate(photos):
        if not os.path.exists(src):
            print("!! manquant:", src); continue
        edge = 1500 if i == 0 else 1280
        rel = f"{aid}/{i:02d}.jpg"
        sz, dim = opt(src, os.path.join(DST, rel), edge)
        total += sz
        entry["photos"].append({"src": f"assets/img/realisations/{rel}", "leg": leg})
    data.append(entry)
    print(f"{aid:14s} {len(entry['photos'])} photos")

for name, (src, edge) in SINGLES.items():
    if not os.path.exists(src):
        print("!! single manquant:", src); continue
    sz, dim = opt(src, os.path.join(PROJ, "assets/img", f"{name}.jpg"), edge, q=82)
    total += sz
    print(f"{name:14s} {dim}")

js = "/* Généré — chantiers de Lou François. photos[0] = couverture. */\n"
js += "window.PROJETS = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
open(os.path.join(PROJ, "assets/js/projets.js"), "w", encoding="utf-8").write(js)

print(f"\nTOTAL {total/1048576:.1f} MB")
