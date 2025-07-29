# skyto/cli.py

import sys
from skyto import interpreter

def main():
    if len(sys.argv) < 2:
        print("Usage: skyto <fichier.sto>")
        return

    fichier_path = sys.argv[1]

    try:
        with open(fichier_path, 'r') as fichier:
            code = fichier.read()
            interpreter.executer(code)
    except FileNotFoundError:
        print(f"Fichier introuvable : {fichier_path}")
