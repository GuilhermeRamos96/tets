anestesicos = {
    "Benzocaína": {
        "tipo": "Éster",
        "pKa": 3.5,
        "base_percent": 100,
        "inicio_acao": "-"
    },
    "Procaína": {
        "tipo": "Éster",
        "pKa": 9.1,
        "base_percent": 2,
        "inicio_acao": "14-18"
    },
    "Mepivacaína": {
        "tipo": "Amida",
        "pKa": 7.7,
        "base_percent": 33,
        "inicio_acao": "2-4"
    },
    "Lidocaína": {
        "tipo": "Amida",
        "pKa": 7.7,
        "base_percent": 29,
        "inicio_acao": "2-4"
    },
    "Prilocaína": {
        "tipo": "Amida",
        "pKa": 7.7,
        "base_percent": 25,
        "inicio_acao": "2-4"
    },
    "Articaína": {
        "tipo": "Amida",
        "pKa": 7.8,
        "base_percent": 29,
        "inicio_acao": "2-4"
    },
    "Bupivacaína": {
        "tipo": "Amida",
        "pKa": 8.1,
        "base_percent": 17,
        "inicio_acao": "5-8"
    }
}

esquema_distribuicao = {
    "extracelular": {
        "pH": 7.4,
        "RNH_percent": 75,
        "RN_percent": 25,
        "RNH_quantidade": 750,
        "RN_quantidade": 250
    },
    "intracelular": {
        "pH": 7.4,
        "RNH_percent": 75,
        "RN_percent": 25,
        "RNH_quantidade": 180,
        "RN_quantidade": 70
    }
}

def calcular_base_livre(pKa, pH):
    return 100 / (1 + 10**(pKa - pH))
