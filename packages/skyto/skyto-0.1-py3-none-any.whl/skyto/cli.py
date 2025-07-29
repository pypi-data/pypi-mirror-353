import sys
from skyto.interpreter import executer

def main():
    if len(sys.argv) != 2:
        print("Utilisation : skyto mon_fichier.lga")
        return
    with open(sys.argv[1], 'r') as fichier:
        code = fichier.read()
        executer(code)
