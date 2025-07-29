# skyto/interpreter.py

def traduire_linga_vers_python(code_skyto):
    traduction = {
        "monisa": "print",
        "soki": "if",
        "soki_te": "else",
        "pamba_na": "for",
        "kati_na": "in",
        "tala": "def",
        "zongisa": "return",
        "solo": "True",
        "ndambo_te": "False",
        "importa": "import"
    }
    lignes = code_skyto.split("\n")
    code_python = []
    for ligne in lignes:
        for lingala, python in traduction.items():
            ligne = ligne.replace(lingala, python)
        code_python.append(ligne)
    return "\n".join(code_python)


def executer(code_skyto):
    code_python = traduire_linga_vers_python(code_skyto)
    try:
        exec(code_python, globals())
    except Exception as e:
        print(f"Erreur : {e}")
