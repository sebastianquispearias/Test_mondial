import os
# import osmnx as ox
# import networkx as nx
# import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# Coordenadas del almacén y de las filiales
# ─────────────────────────────────────────────
almacen = (-22.869234, -43.2802088)  # (lat, lon)
#-22.86923009845225, -43.27791728767326
#-22.795429351447602, -43.1837638753556
branches = [
    {"name": "Supermercados Mundial - Central de Abastecimento (CD)", "lat": -22.86923009845225, "lon": -43.27791728767326,"umbral": 0.3},
    {"name": "Supermercados Mundial Ilha do governador", "lat": -22.795429351447602, "lon": -43.1837638753556,"umbral": 0.2},
    {"name": "Supermercados Mundial Niterói | Jardim Icaraí", "lat": -22.90329731763847, "lon": -43.097307977574474,"umbral": 0.2},
    {"name": "Supermercados Mundial Bairro de Fátima | Riachuelo", "lat": -22.913784590327833, "lon": -43.18711919567261,"umbral": 0.2},
    {"name": "Supermercados Mundial Botafogo", "lat": -22.950919792939537, "lon": -43.18297400667499,"umbral": 0.25},# -22.950919792939537, -43.18297400667499
    {"name": "Supermercados Mundial Copacabana", "lat": -22.968847071451616, "lon": -43.18569489445454,"umbral": 0.25}, # -22.968847071451616, -43.18569489445454
    {"name": "Supermercados Mundial Praça da Bandeira | Matoso", "lat": -22.913507660997, "lon": -43.21345868442778,"umbral": 0.2},
    {"name": "Supermercados Mundial Conde de Bonfim", "lat": -22.92226016543747, "lon": -43.22126815317118,"umbral": 0.2},
    {"name": "Supermercados Mundial Santo Afonso", "lat": -22.923320684429175, "lon": -43.234122459300615,"umbral": 0.2},
    {"name": "Supermercados Mundial Engenho Novo", "lat": -22.899855030010304, "lon": -43.26544016378892,"umbral": 0.2},
    {"name": "Supermercados Mundial Ramos", "lat": -22.855973176741152, "lon": -43.25995496786801,"umbral": 0.2},
    {"name": "Supermercados Mundial Engenho Novo (2)", "lat": -22.900080684412238, "lon": -43.26528885548355,"umbral": 0.2},  
    {"name": "Supermercados Mundial Barrinha", "lat": -23.009991643661735, "lon": -43.29737481730339,"umbral": 0.2},
    {"name": "Supermercados Mundial Jardim Oceânico", "lat": -23.00923876602248, "lon": -43.30488076821857,"umbral": 0.2},
    {"name": "Supermercados Mundial Irajá", "lat": -22.833048563648617, "lon": -43.32723966648674,"umbral": 0.2},
    {"name": "Supermercados Mundial Vaz Lobo", "lat": -22.85494434336315, "lon": -43.32409798182202,"umbral": 0.2},# 
    {"name": "Supermercados Mundial Praça Seca", "lat": -22.8925625769025, "lon": -43.34786118671673,"umbral": 0.2}, # -22.8925625769025, -43.34786118671673
    {"name": "Supermercados Mundial Freguesia", "lat": -22.94388664012063, "lon": -43.34175282812634,"umbral": 0.2},#-22.94388664012063, -43.34175282812634
    {"name": "Supermercados Mundial Curicica", "lat": -22.959994417636395, "lon": -43.39216527050953,"umbral": 0.2}, # -22.959994417636395, -43.39216527050953
    {"name": "Supermercados Mundial Recreio", "lat": -23.00896381288249, "lon": -43.44265287700698,"umbral": 0.2},#-23.00896381288249, -43.44265287700698
    {"name": "Supermercados Mundial Cacuia", "lat": -22.811681637274255, "lon": -43.19022264623345,"umbral": 0.2}, # -22.811681637274255, -43.19022264623345
    {"name": "Supermercados Mundial Abelardo Bueno", "lat": -22.972159599300134, "lon": -43.390580773771156,"umbral": 0.2}, # -22.972159599300134, -43.390580773771156
    {"name": "Recebimento de mercadorias", "lat": -22.835051879437874, "lon": -43.33600956432539,"umbral": 0.2}#-22.835051879437874, -43.33600956432539
]
# ─────────────────────────────────────────────
# Rutas definidas: el nombre de la ruta y sus coordenadas (lon, lat)
# ─────────────────────────────────────────────
# falta rota iraja *----* paz lobo va directo
rutas = {
    "ida almacen a Supermercados Mundial Niterói | Jardim Icaraí": [
        (-43.27713507479095, -22.870095344795047),
        (-43.27524179828137, -22.873192346873537),
        (-43.10381399182438, -22.909812914148624),
        (-43.09754510384212, -22.90331424126231)
    ],
    "vuelta almacen a Supermercados Mundial Niterói | Jardim Icaraí": [
        (-43.09754510384212, -22.90331424126231),
        (-43.10165297859493, -22.908086036413206),
        (-43.27528430659397, -22.87304378360908),
        (-43.27713507479095, -22.870095344795047)
    ],
    "ida almacen a Supermercados Mundial Ilha governador": [
        (-43.27713507479095, -22.870095344795047),
        (-43.274128978867466, -22.87239890540707),
        (-43.26693828123421, -22.87399240617427),
        (-43.23201647434948, -22.85393443700404),
        (-43.18604466824528, -22.79601050189325),
        (-43.18370430510367, -22.79537825495237)
    ],
    "vuelta almacen a Supermercados Mundial Ilha governador": [
        (-43.18370430510367, -22.79537825495237),
        (-43.18613094533853, -22.796059851728735),
        (-43.242101606836684, -22.834384068662526),
        (-43.24517777451732, -22.846971380618733),
        (-43.27551873627754, -22.873204766077993),
        (-43.27713507479095, -22.870095344795047)
    ],
    "ida almacen a Supermercados Mundial Iraja": [
        (-43.27713507479095, -22.870095344795047),
        (-43.278349576595886, -22.873351650012932),
        (-43.28375294068618, -22.870535509536925),
        (-43.29444288762296, -22.865136685408178),
        (-43.328439392021956, -22.831492651264167)
    ],
    "vuelta almacen a Supermercados Mundial Iraja": [
        (-43.32845041741504, -22.831320678307296),
        (-43.28736506800945, -22.867155587104875),
        (-43.28231990394115, -22.872770096789722),
        (-43.278838702341986, -22.873594779113457),
        (-43.27713507479095, -22.870095344795047)
    ]
}
