#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optimise les photos des chantiers de Lou + genere assets/js/projets.js

Source : ~/Bureau/photos book entreprise 02/ — un sous-dossier par projet.
Chaque album ci-dessous : (id, dossier, titre, resume, [(fichier, legende), ...]).
La 1re photo de la liste sert de couverture.

NB : au 2026-09-10 le dossier source n'est plus sur le Bureau. Les images
optimisees sont deja versionnees dans assets/img/realisations/ ; ce script
ne sert qu'a les regenerer si on recupere les photos d'origine. L'ordre des
listes ci-dessous correspond a l'ordre des fichiers NN.jpg deja commites.
"""
import os, json, shutil
from PIL import Image, ImageOps

SRC  = os.path.expanduser("~/Bureau/photos book entreprise 02")
PROJ = os.path.expanduser("~/Bureau/Sites/Francois")
DST  = os.path.join(PROJ, "assets/img/realisations")

ALBUMS = [
 ("longere", "renovation",
  "Restauration complète d'une longère en pierre",
  "D'une ruine à une maison habitable : reprise des maçonneries, charpente neuve, "
  "extension ossature bois, préau en chêne, menuiseries et terrasse.",
  [
   ("PHOTO-2021.jpg",            "La longère restaurée sous la neige, l'hiver suivant la fin du chantier"),
   ("02.jpg",                    "Au départ : un pignon effondré et des murs à reprendre"),
   ("20.jpg",                    "Toiture bâchée pendant la dépose de l'ancienne charpente"),
   ("03.jpg",                    "Reprise des maçonneries à la grue, pierre par pierre"),
   ("04.jpg",                    "Extension en ossature bois greffée sur l'existant"),
   ("05.jpg",                    "Préau en chêne monté contre la façade"),
   ("06.jpg",                    "Le préau vu de l'intérieur, bardage bois posé"),
   ("IMG_20200626_180745.jpg",   "Chantier en cours : murs montés, terrassement autour"),
   ("IMG_20200812_160621.jpg",   "Levage d'un panneau d'ossature pour l'extension"),
   ("23.jpg",                    "Mur gouttereau rejointoyé à la chaux après reprise"),
   ("25.jpg",                    "Ammonite prise dans une pierre du pays, laissée apparente"),
   ("20210709_162418.jpg",       "Porte en chêne à pentures forgées, niche d'origine restituée"),
   ("IMG_20210626_162814.jpg",   "Platelage de la terrasse bois en cours de pose"),
   ("IMG_20210626_165049.jpg",   "Terrasse et garde-corps métal sur la façade sud"),
  ]),

 ("maison-courbe", "maison a ossatoire bois",
  "Maison contemporaine à toiture courbe",
  "Ossature et charpente bois d'une maison neuve à toit cintré : murs préfabriqués, "
  "planchers, charpente courbe, bardage cèdre et couverture zinc.",
  [
   ("angle coté feu.JPG",        "Jonction du bardage cèdre et de la toiture zinc courbe"),
   ("157.JPG",                   "Ossature bois sous pare-pluie, naissance de la toiture cintrée"),
   ("160.JPG",                   "Le galbe de la toiture se dessine sur la façade"),
   ("164.jpg",                   "Levage d'un panneau de bois massif à la grue"),
   ("163.jpg",                   "Murs de refend en panneaux de bois massif à l'étage"),
   ("162.jpg",                   "Pose des panneaux de plancher à l'étage"),
   ("161.jpg",                   "Volume bardé cèdre et pergola, sur soubassement maçonné"),
   ("169.jpg",                   "Pose du bardage cèdre sur la façade échafaudée"),
   ("vue du champ par coté.JPG", "Depuis le pré : lucarne rampante et couverture zinc"),
   ("vue du champ.JPG",          "Volume principal et toiture cintrée, façade arrière"),
  ]),

 ("charpente", "charpente",
  "Charpente bois, du neuf à la restauration",
  "Fermes, préaux, tonnelles et grandes charpentes : taille à l'atelier, assemblages "
  "chevillés, levage à la grue, et reprise de charpentes anciennes.",
  [
   ("HPIM0552.JPG",              "Appentis en bardage cèdre, chevrons de la toiture monopente apparents"),
   ("DSCF1109.JPG",              "Charpente d'une tonnelle à quatre pentes, arbalétriers et empannons assemblés"),
   ("detail arba CF poinçon 1.JPG", "Poinçon décoratif à cul-de-lampe sculpté et aisseliers courbes"),
   ("Bonifacio-20150309-02330.jpg", "Fermes treillis d'un abri, posées sur des murs maçonnés (Corse)"),
   ("DSCF1085.JPG",              "Tonnelle de jardin sur poteaux bois, chevronnage à claire-voie"),
   ("Pergola vue d'en dessous.JPG", "Pergola contemporaine à lames serrées, adossée à une maison"),
   ("IMG-20150625-02733.jpg",    "L'ensemble poinçon-aisseliers levé à la grue"),
   ("IMG_20220818_083212230.jpg", "Ferme cintrée assemblée à blanc sur l'aire de l'atelier"),
   ("IMG_20220819_134846643.jpg", "Ossature de préau en douglas adossée à une grange en pierre"),
   ("IMG_20221026_161339003.jpg", "Charpente neuve reposée sur les murs anciens d'un bâtiment"),
   ("at 02.jpg",                 "Grande charpente de préau ouvert sur poteaux, en douglas"),
   ("b 1.jpg",                   "Le même abri ouvert, vu de la façade arrière"),
   ("m 02.JPG",                  "Levage à la grue d'un pan de toiture cintrée assemblé au sol"),
   ("mo 03.JPG",                 "Levage d'une ferme en arc brisé au-dessus d'une voûte de pierre"),
   ("vue du tout.jpg",           "Charpente de tonnelle terminée sur muret, face au paysage"),
  ]),

 ("lavoir", "lavoir du park",
  "Lavoir sous charpente chêne, couverture tuile",
  "Charpente traditionnelle taillée à l'atelier puis levée sur les murs anciens du "
  "lavoir, contrefiches courbes apparentes et couverture neuve en tuile de pays.",
  [
   ("05.jpg", "La charpente chêne levée sur les murs anciens du lavoir"),
   ("01.jpg", "Fermes taillées et assemblées à blanc à l'atelier"),
   ("02.jpg", "Pièces de chêne calées avant taille des assemblages"),
   ("03.jpg", "Première ferme dressée contre le mur, contrefiches courbes"),
   ("04.jpg", "Réglage d'une ferme sur tréteaux, serre-joints en place"),
   ("07.jpg", "Détail d'un poteau : aisseliers courbes rayonnants"),
   ("06.jpg", "Charpente complète, pannes et chevrons posés"),
   ("08.jpg", "Platelage de rive posé sur la charpente"),
   ("09.jpg", "Écran de sous-toiture et liteaunage sur les longs pans"),
   ("10.jpg", "Couverture terminée en tuile de pays"),
  ]),

 ("assemblages", "assemblages",
  "Assemblages traditionnels taillés à la main",
  "Le cœur du métier : traits de Jupiter, tenons-mortaises, enfourchements et "
  "embrèvements, tracés à l'épure puis taillés au ciseau et à la scie.",
  [
   ("Ass 05.jpg", "Croix de Saint-André taillée dans la masse"),
   ("ASS 01.jpg", "Trait de Jupiter à mi-bois, vue rapprochée"),
   ("Ass 02.jpg", "Enrayure : about mouluré prêt à l'assemblage"),
   ("Ass 03.jpg", "Double trait de Jupiter aligné sur tréteaux"),
   ("Ass 04.jpg", "Assemblage tridimensionnel poteau / entrait / lien"),
   ("Ass 06.jpg", "Épure tracée à la règle sur une pièce ancienne"),
   ("Ass 08.jpg", "Report du trait sur bois de réemploi"),
   ("Ass 12.jpg", "Enfourchement ouvert avant emboîtage"),
   ("Ass 13.jpg", "Croisement à mi-bois de deux pièces"),
   ("Ass 14.jpg", "Tenon et clé d'about, assemblage à sec"),
   ("Ass 15.jpg", "Assemblage serré et chevillé, une fois monté"),
  ]),

 ("escaliers", "escaliers",
  "Escaliers bois, intérieur et extérieur",
  "Escaliers droits, quart et double quart tournant, volées courbes à limon cintré, "
  "et emmarchements extérieurs en bois exotique.",
  [
   ("HPIM2180.JPG",              "Escalier balancé en chêne, vue plongeante"),
   ("HPIM2179.JPG",              "Volée courbe à limon cintré et contremarches"),
   ("HPIM2176.JPG",              "Escalier quart tournant en chêne clair"),
   ("HPIM2177.JPG",              "Escalier suspendu le long du mur, sans contremarche"),
   ("01.jpg",                    "Escalier droit en frêne, rampe à balustres carrés"),
   ("IMG_20190805_112420.jpg",   "Escalier double quartier tournant monté à l'atelier"),
   ("IMG_20210409_182645_02.jpg", "Escalier sous comble, rampe à barreaux"),
   ("IMG00188-20110327-1716.jpg", "Emmarchement extérieur en bois exotique dans un jardin"),
   ("IMG_20200429_171038.jpg",   "Escalier extérieur d'accès, garde-corps à claire-voie"),
   ("HPIM1210.JPG",              "Terrasse à emmarchements successifs autour d'une piscine"),
   ("HPIM1545.JPG",              "Cheminement et marches en bois exotique en pente douce"),
  ]),

 ("couverture", "couverture",
  "Couverture : tuile, zinc et petits ouvrages",
  "Réfection de toitures à deux pans et à croupe en tuile terre cuite, faîtages et "
  "arêtiers scellés, châssis de toit, auvents et petites couvertures bac acier.",
  [
   ("Conca-20120514-00502.jpg",  "Toiture quatre pans refaite en tuile, châssis de toit intégré"),
   ("IMG_20201030_154819.jpg",   "Croupe de toiture en tuile terre cuite neuve"),
   ("IMG_20201102_172311.jpg",   "Réfection de couverture sur charpente conservée"),
   ("IMG_20201102_172340.jpg",   "Toiture à croupe terminée, faîtage et arêtiers scellés"),
   ("IMG-20120427-00400.jpg",    "Auvent de jardin couvert en tuile vernissée"),
   ("349.jpg",                   "Longue toiture rénovée, égouts et rives repris"),
   ("IMG_20221215_155934538.jpg", "Couverture bac acier sur un appentis"),
   ("P1010656.JPG",              "Petite toiture en tuile sur extension maçonnée"),
  ]),

 ("etaiement", "etaiement",
  "Étaiement et reprise de structures",
  "Chevalets, portiques et cintres bois pour soutenir un ouvrage le temps des "
  "travaux : arcs d'église, planchers, pignons et charpentes fragilisées.",
  [
   ("01 (3).JPG",                "Étaiement d'une arche d'église par chevalets bois"),
   ("HPIM1476.JPG",              "Chevalets sous un arc doubleau pendant les travaux"),
   ("c2.JPG",                    "Cintre et étais sous voûte peinte, reprise de charge"),
   ("c3.JPG",                    "Nef étayée pour une intervention en couverture"),
   ("HPIM1870.JPG",              "Contreventement provisoire d'une charpente à l'atelier"),
   ("c1.JPG",                    "Palée d'étaiement sous arc, à l'intérieur de l'édifice"),
   ("IMG-20130727-00424.jpg",    "Portique bois autostable posé sur longrines"),
   ("IMG-20130727-00437.jpg",    "Levage d'un portique d'étaiement préassemblé"),
   ("IMG-20130727-00451.jpg",    "Encadrement de porte étrésillonné dans un mur de pierre"),
   ("IMG_20191129_170406.jpg",   "Béquilles de soutien sous une toiture de hangar"),
   ("IMG_20200623_153634 - Copie.jpg", "Chevalement soutenant un pignon fragilisé"),
  ]),

 ("terrasse", "terrasse",
  "Terrasses bois et pergolas",
  "Terrasses et plages de piscine en bois exotique, formes libres épousées, "
  "garde-corps et pergolas attenantes.",
  [
   ("P7080049.JPG",              "Terrasse bois autour d'une piscine à débordement, face à la mer"),
   ("HPIM0651.JPG",              "Grande terrasse en bois exotique ceinturant la piscine"),
   ("HPIM1943 - Copie.JPG",      "Plage de piscine en lames exotiques, forme libre épousée"),
   ("P7080035.JPG",              "Terrasse et margelles bois entre jardin et bassin"),
   ("P7080037.JPG",              "Cheminement bois sous la pergola, vers la piscine"),
   ("166.jpg",                   "Platelage neuf sur structure, avant huilage"),
   ("167.jpg",                   "Lames posées et garde-corps, terrasse sur pilotis"),
   ("P7200015.JPG",              "Pergola bois et terrasse attenante en cours de finition"),
  ]),

 ("abri", "abri de jardin Marsannay",
  "Abri de jardin en ossature bois",
  "Un abri de A à Z : plancher sur plots, ossature, charpente traditionnelle, "
  "bardage douglas et couverture tuile.",
  [
   ("IMG_20221012_174907324.jpg", "L'abri terminé : bardage douglas et couverture tuile"),
   ("IMG_20220826_113041624.jpg", "Plancher bois sur plots, prêt à recevoir l'ossature"),
   ("IMG_20220826_120609387.jpg", "Montage des panneaux d'ossature sur le plancher"),
   ("IMG_20220826_143051450.jpg", "Charpente traditionnelle posée sur l'ossature"),
   ("IMG_20220827_101905524.jpg", "Volume clos, avant bardage et couverture"),
   ("IMG_20220903_172735751.jpg", "Pose de la couverture tuile et de la sous-face"),
   ("IMG_20220903_172814767.jpg", "Bardage à claire-voie posé sur les faces latérales"),
  ]),

 ("divers", "Divers",
  "Menuiserie et ouvrages sur mesure",
  "En dehors de la charpente : tables, portes, escaliers de meuble, bibliothèques, "
  "mobilier d'enfant et pièces cintrées ou sculptées à l'atelier.",
  [
   ("IMG_20200429_164751.jpg",   "Table ronde à plateau marqueté en rayons"),
   ("IMG_20181024_193620.jpg",   "Grande table de ferme en chêne massif, plateau à frises"),
   ("IMG_20200429_164834.jpg",   "Table basse à double entretoise courbe"),
   ("HPIM2332.JPG",              "Porte d'entrée contemporaine en bois, vitrage vertical"),
   ("IMG-20120402-00289.jpg",    "Portes intérieures et parquet assortis, chêne clair"),
   ("IMG_20200429_164829.jpg",   "Tête de lit d'enfant gravée au pyrograveur"),
   ("IMG_20200429_164900.jpg",   "Portail de grange cintré en douglas"),
   ("IMG_20200429_170945.jpg",   "Hotte de cheminée habillée de chêne mouluré"),
   ("IMG_20200429_171020.jpg",   "Bibliothèque murale toute hauteur sur mesure"),
   ("IMG_20200429_164938.jpg",   "Arc lamellé-collé cintré à l'atelier"),
   ("IMG_20210515_170432.jpg",   "Ensemble mural sculpté dans une pièce à vivre"),
   ("IMG_20200429_171015.jpg",   "Lit cabane en pin pour chambre d'enfant"),
   ("jeux de dame 2.JPG",        "Plateau de dames chinoises tourné et percé"),
  ]),
]


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
missing = 0
for aid, folder, titre, resume, photos in ALBUMS:
    entry = {"id": aid, "titre": titre, "resume": resume, "photos": []}
    for i, (fname, leg) in enumerate(photos):
        src = os.path.join(SRC, folder, fname)
        if not os.path.exists(src):
            print("!! manquant:", src); missing += 1; continue
        edge = 1500 if i == 0 else 1280
        rel = f"{aid}/{len(entry['photos']):02d}.jpg"
        sz, dim = opt(src, os.path.join(DST, rel), edge)
        total += sz
        entry["photos"].append({"src": f"assets/img/realisations/{rel}", "leg": leg})
    data.append(entry)
    print(f"{aid:14s} {len(entry['photos'])} photos")

js = "/* Genere par scripts/build-albums.py — chantiers de Lou Francois. photos[0] = couverture. */\n"
js += "window.PROJETS = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
open(os.path.join(PROJ, "assets/js/projets.js"), "w", encoding="utf-8").write(js)

print(f"\n{missing} manquantes — TOTAL {total/1048576:.1f} MB")
