# ============================================================
# HISTORIA MEDIEVAL (antigua + medieval mezcladas)
# ============================================================
MEDIEVAL_FACIL = [
    ("¿Quién construyó las pirámides de Giza?", "los egipcios"),
    ("¿Cuál era la capital del Imperio Romano?", "roma"),
    ("¿Quién fue el primer emperador romano?", "augusto"),
    ("¿En qué año cayó el Imperio Romano de Occidente?", "476"),
    ("¿Cómo se llamaba el líder de los hunos que invadió Europa?", "atila"),
    ("¿Qué emperador bizantino construyó Santa Sofía?", "justiniano"),
    ("¿Qué ciudad fue el centro del Imperio Bizantino?", "constantinopla"),
    ("¿Quién fue el primer rey de los francos?", "clodoveo"),
    ("¿Qué emperador fue coronado por el Papa en el año 800?", "carlomagno"),
    ("¿Cuál era el idioma del Imperio Romano de Oriente?", "griego"),
]

MEDIEVAL_NORMAL = [
    ("¿En qué año Colón llegó a América?", "1492"),
    ("¿Quién fue el líder de la Primera Cruzada?", "godofredo de bouillon"),
    ("¿Qué rey inglés firmó la Carta Magna?", "juan sin tierra"),
    ("¿Qué dinastía gobernó China durante la Ruta de la Seda?", "han"),
    ("¿Cómo se llamaba el sistema social de la Edad Media?", "feudalismo"),
    ("¿Qué vikingo llegó a América antes que Colón?", "leif erikson"),
    ("¿Quién fue el fundador del Islam?", "mahoma"),
    ("¿Qué batalla marcó el fin de la invasión musulmana en Europa?", "poitiers"),
    ("¿Qué emperador romano dividió el imperio en dos?", "diocleciano"),
    ("¿Qué civilización construyó Machu Picchu?", "inca"),
]

MEDIEVAL_DIFICIL = [
    ("¿En qué año se firmó el Tratado de Verdún?", "843"),
    ("¿Quién fue el último emperador del Imperio Romano de Occidente?", "romulo augustulo"),
    ("¿Qué emperador bizantino reconquistó parte del Imperio Romano?", "justiniano"),
    ("¿En qué año comenzó la Guerra de los Cien Años?", "1337"),
    ("¿Quién fue el primer califa del Islam?", "abubéker"),
    ("¿Qué papa convocó la Primera Cruzada?", "urbano ii"),
    ("¿En qué año cayó Constantinopla?", "1453"),
    ("¿Qué rey francés fue canonizado como San Luis?", "luis ix"),
    ("¿Qué tratado dividió el mundo entre España y Portugal?", "tordesillas"),
    ("¿Quién fue el último emperador azteca?", "cuauhtemoc"),
]


# ============================================================
# HISTORIA MODERNA Y CONTEMPORÁNEA (mezcladas)
# ============================================================
MODERNO_FACIL = [
    ("¿En qué año estalló la Revolución Francesa?", "1789"),
    ("¿Quién fue el primer presidente de Estados Unidos?", "george washington"),
    ("¿En qué año se independizó Estados Unidos?", "1776"),
    ("¿Quién fue el líder de la Revolución Rusa de 1917?", "lenin"),
    ("¿En qué año terminó la Segunda Guerra Mundial?", "1945"),
    ("¿Quién fue el canciller alemán durante la Segunda Guerra Mundial?", "hitler"),
    ("¿En qué año llegó el hombre a la Luna?", "1969"),
    ("¿Quién fue el primer presidente negro de Estados Unidos?", "barack obama"),
    ("¿En qué año cayó el Muro de Berlín?", "1989"),
    ("¿Quién fue el líder de la Revolución Cubana?", "fidel castro"),
]

MODERNO_NORMAL = [
    ("¿Quién fue el emperador francés derrotado en Waterloo?", "napoleon"),
    ("¿En qué año comenzó la Primera Guerra Mundial?", "1914"),
    ("¿Qué país lanzó la primera bomba atómica?", "estados unidos"),
    ("¿Quién fue el líder de la independencia de la India?", "mahatma gandhi"),
    ("¿En qué año se fundó la ONU?", "1945"),
    ("¿Quién fue el primer hombre en el espacio?", "yuri gagarin"),
    ("¿Qué muro dividió Berlín durante la Guerra Fría?", "muro de berlin"),
    ("¿Quién fue el presidente de EE.UU. durante la crisis de los misiles?", "kennedy"),
    ("¿En qué año se disolvió la Unión Soviética?", "1991"),
    ("¿Quién fue el líder del apartheid en Sudáfrica?", "nelson mandela"),
]

MODERNO_DIFICIL = [
    ("¿En qué año se firmó el Tratado de Versalles?", "1919"),
    ("¿Quién fue el primer secretario general de la ONU?", "trygve lie"),
    ("¿En qué año se produjo la Revolución Industrial?", "1760"),
    ("¿Qué país fue el primero en reconocer la independencia de EE.UU.?", "francia"),
    ("¿Quién fue el arquitecto de la unificación alemana?", "otto von bismarck"),
    ("¿En qué año se hundió el Titanic?", "1912"),
    ("¿Quién fue el primer ministro británico durante la Segunda Guerra Mundial?", "churchill"),
    ("¿En qué año se produjo la Revolución China?", "1949"),
    ("¿Qué presidente ordenó el lanzamiento de las bombas atómicas?", "truman"),
    ("¿En qué año se firmó el Tratado de Maastricht?", "1992"),
]


# ============================================================
# DICCIONARIO
# ============================================================
MUNDO = {
    "medieval": {
        "facil": MEDIEVAL_FACIL,
        "normal": MEDIEVAL_NORMAL,
        "dificil": MEDIEVAL_DIFICIL,
    },
    "moderno": {
        "facil": MODERNO_FACIL,
        "normal": MODERNO_NORMAL,
        "dificil": MODERNO_DIFICIL,
    },
} 
