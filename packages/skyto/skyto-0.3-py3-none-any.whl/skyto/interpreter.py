def traduire_linga_vers_python(code_skyto):
    # Dictionnaire de mots-clés Skyto -> Python
    traduction = {
        "monisa": "print",
        "soki": "if",
        "sk_te": "else",
        "pamba_na": "for",
        "kati_na": "in",
        "tala": "def",
        "zongisa": "return",
        "solo": "True",
        "lokuta": "False",
        "benga": "import"
    }

    lignes = code_skyto.split("\n")
    code_python = []

    for ligne in lignes:
        indentation = len(ligne) - len(ligne.lstrip())
        ligne = ligne.strip()

        # Ignorer lignes vides
        if ligne == "":
            code_python.append("")
            continue

        # Traduire les mots Skyto
        for lingala, python in traduction.items():
            ligne = ligne.replace(lingala, python)

        # Ajouter ":" à la fin des instructions de contrôle
        # if ligne.startswith(("if ", "else", "for ", "def ")) and not ligne.endswith(":"):
        #     ligne += ":"

        # Restaurer indentation
        code_python.append(" " * indentation + ligne)

    return "\n".join(code_python)


def executer(code_skyto):
    code_python = traduire_linga_vers_python(code_skyto)
    try:
        exec(code_python, globals())
    except Exception as e:
        print(f"Erreur pendant l'exécution du code Skyto :\n{e}")