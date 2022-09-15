import re
import csv


base = 'Liste_IL_MAZ.tsv'

identifiants = {}

"""
Ce script a été utilise pour obtenir un fichier CSV contenant les identifiants 
des imprimeurs du CSV de base (avant requête SAPRQL). Il a permis de faire une 
partie des jointures des deux CSV, afin d'ajouter les informations des imprimeurs 
qui avaient un identifiant mais pas de notice d'autorité sur IdRef
"""

with open(base) as tsvfile:
    tsvreader = csv.reader(tsvfile, delimiter="\t")
    next(tsvreader, None)  # cette ligne sert à ne pas lire les headers du fichier
    for row in tsvreader:
        old_id = row[2]
        new_ident = row[2]
        new_ident = re.sub(" ", "", new_ident)
        new_ident = re.sub("^(isni:)", "http://isni.org/isni/", new_ident)
        new_ident = re.sub("^(viaf:)", "http://viaf.org/viaf/", new_ident)
        if old_id:
            identifiants[old_id] = new_ident


if __name__ == "__main__":
    with open('Liste_IL_MAZ2.tsv', 'w+', newline='') as tsvfile2:
        fieldnames = ['ISNI', 'Identifiants']
        tsvwriter = csv.writer(tsvfile2, delimiter="\t")
        tsvwriter.writerow(fieldname for fieldname in fieldnames)
        # tsvwriter.writeheader()
        for key, value in identifiants.items():
            tsvwriter.writerow([key, value])
