"""Géolocalisation des sables : table de centroïdes pays / territoires / sous-régions FR.

Aucune dépendance réseau. Utilisé par le script de build et par l'upload.
"""
import re
import unicodedata


def fold(s):
    """Normalise une chaîne : sans accents, sans parenthèses, MAJUSCULES."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("?", " ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" .,-")
    return s.upper()


# Centroïdes (lat, lon) — clés = pays/territoire "foldé"
CENTROIDS = {
    "FRANCE BRETAGNE": (48.2, -3.0),
    "FRANCE CORSE": (42.15, 9.1),
    "FRANCE SUD": (43.4, 6.2),
    "FRANCE SUD-OUEST": (44.0, -1.1),
    "FRANCE OUEST": (46.5, -1.6),
    "FRANCE NORD": (50.7, 1.7),
    "FRANCE": (46.6, 2.4),
    "USA": (39.5, -98.35),
    "CANARIES": (28.3, -16.5),
    "EGYPTE": (26.8, 30.8),
    "TURQUIE": (39.0, 35.2),
    "GUADELOUPE": (16.25, -61.55),
    "BRESIL": (-12.0, -45.0),
    "INDONESIE": (-2.5, 118.0),
    "ITALIE": (42.5, 12.5),
    "REPUBLIQUE DOMINICAINE": (18.7, -70.2),
    "POLYNESIE FRANCAISE": (-17.6, -149.6),
    "MAROC": (31.8, -7.1),
    "INDE": (21.0, 78.0),
    "ESPAGNE": (40.0, -3.7),
    "GRECE": (39.0, 22.0),
    "CAP VERT": (16.0, -24.0),
    "MEXIQUE": (23.6, -102.5),
    "CANADA": (56.0, -96.0),
    "TUNISIE": (34.0, 9.5),
    "PEROU": (-9.2, -75.0),
    "MAURITANIE": (20.3, -10.0),
    "JORDANIE": (31.0, 36.5),
    "THAILANDE": (15.0, 101.0),
    "VIETNAM": (16.0, 108.0),
    "NOUVELLE ZELANDE": (-41.0, 173.0),
    "ILE MAURICE": (-20.3, 57.55),
    "MALI": (17.6, -4.0),
    "ARGENTINE": (-38.0, -63.6),
    "OMAN": (21.0, 57.0),
    "KENYA": (-0.5, 37.9),
    "SENEGAL": (14.5, -14.5),
    "PORTO RICO": (18.2, -66.5),
    "GUYANE FRANCAISE": (4.0, -53.0),
    "SRI LANKA": (7.9, 80.7),
    "ISLANDE": (64.9, -19.0),
    "AFRIQUE DU SUD": (-30.6, 22.9),
    "TANZANIE": (-6.4, 34.9),
    "MARTINIQUE": (14.64, -61.02),
    "MONTSERRAT": (16.74, -62.19),
    "COSTA RICA": (9.7, -83.8),
    "CHILI": (-35.7, -71.5),
    "ISRAEL": (31.4, 35.0),
    "MALAISIE": (4.2, 108.0),
    "MYANMAR": (21.9, 95.9),
    "MALDIVES": (3.2, 73.2),
    "PORTUGAL": (39.4, -8.2),
    "ROYAUME UNI": (54.0, -2.5),
    "SEYCHELLES": (-4.6, 55.5),
    "NOUVELLE CALEDONIE": (-21.3, 165.5),
    "ALGERIE": (28.0, 2.6),
    "DJIBOUTI": (11.8, 42.6),
    "ILE DE LA REUNION": (-21.1, 55.5),
    "BARBUDA": (17.63, -61.77),
    "CUBA": (21.5, -79.5),
    "PANAMA": (8.5, -80.1),
    "ARGENTINE/CHILI": (-40.0, -71.5),
    "BOLIVIE": (-20.2, -67.5),
    "COLOMBIE": (4.6, -74.3),
    "ARABIE SAOUDITE": (23.9, 45.1),
    "DUBAI": (25.2, 55.3),
    "EMIRATS ARABES UNIS": (24.0, 54.0),
    "ISRAEL, JORDANIEPALESTINE": (31.5, 35.5),
    "PAKISTAN": (30.4, 69.3),
    "CHINE": (35.9, 104.2),
    "ALLEMAGNE": (51.2, 10.4),
    "BELGIQUE": (51.1, 3.0),
    "DANNEMARK": (56.0, 10.0),
    "IRLANDE": (53.4, -8.0),
    "JERSEY": (49.21, -2.13),
    "LETTONIE": (56.9, 24.6),
    "MALTE": (35.9, 14.4),
    "POLOGNE": (52.0, 19.1),
    "AUSTRALIE": (-25.3, 133.8),
}


def locate(country):
    """Renvoie (lat, lon) pour un pays/territoire, ou None si inconnu."""
    return CENTROIDS.get(fold(country))
