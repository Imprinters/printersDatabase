import csv
import re
from SPARQLWrapper import SPARQLWrapper, JSON


# Script qui permet de récupérer les informations des imprimeurs ayant un identifiant (isni ou viaf)
# avec une requête SPARQL sur IdRef


def get_data():
    """ 
    Fonction pour récupérer un identifiant par imprimeur ; 
    Retourne une liste 
    """

    old_base = 'Liste_IL_MAZ.tsv'
    data = []
    # On ouvre une liste vide dans laquelle on place les identifiants, qu'on va récupérer dans l'ancienne liste des
    # imprimeurs
    with open(old_base) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        next(tsvreader, None)  # cette ligne sert à ne pas lire les headers du fichier
        for row in tsvreader:
            ident = row[2]
            # on enlève les espaces vides dans les identifiants et on les complète avec les adresses pour pouvoir les
            # utiliser dans le SPARQL
            ident = re.sub(" ", "", ident)
            ident = re.sub("^(isni:)", "http://isni.org/isni/", ident)
            ident = re.sub("^(viaf:)", "http://viaf.org/viaf/", ident)
            if ident:
                data.append(ident)
        return data


def get_sparql(item):
    """
    Avec cette fonction, pour chacun des identifiants récupérés dans la liste des imprimeurs, on effectue une requête 
    SPARQL sur IdRef pour récupérer les informations qui lui sont liées
    """
    identifier = item

    sparql = SPARQLWrapper("https://data.idref.fr/sparql")
    sparql.setQuery("""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
        PREFIX bio: <http://purl.org/vocab/bio/0.1/>
        PREFIX rdau: <http://rdaregistry.info/Elements/u/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX bnf-onto: <http://data.bnf.fr/ontology/bnf-onto/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?person ?ident ?bnf ?nom ?autreNom ?naissance ?mort ?genre ?infos ?infos2
        WHERE {
            ?person ?num <""" + identifier + """>. 
            ?person a foaf:Person;
            foaf:name ?nom.
            OPTIONAL {?person skos:altLabel ?autreNom}
            OPTIONAL {?person owl:sameAs ?ident}
            OPTIONAL {?person bnf-onto:FRBNF ?bnf}
            OPTIONAL {?person bio:event [a bio:Birth ; bio:date ?naissance]}
            OPTIONAL {?person bio:event [a bio:Death ; bio:date ?mort]} 
            OPTIONAL {?person foaf:gender ?genre}
            OPTIONAL {?person rdau:P60492 ?infos}
            OPTIONAL {?person skos:note ?infos2}
        }
        """)

    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    return results


def get_noms(printer):
    """
    On récupère les différentes formes des noms des imprimeurs qu'on insère 
    dans une liste
    Retourne une liste
    """

    liste_noms = []
    for item in printer["results"]["bindings"]:
        if item not in liste_noms:
            liste_noms.append(item["autreNom"]["value"])

    liste_noms = list(dict.fromkeys(liste_noms))

    return liste_noms


def get_idents(printer):
    """
    On récupère les différents identifiants des imprimeurs qu'on insère 
    dans une liste
    Retourne une liste
    """

    liste_idents = []
    for item in printer["results"]["bindings"]:
        if item not in liste_idents:
            liste_idents.append(item["ident"]["value"])

    liste_idents = list(dict.fromkeys(liste_idents))

    return liste_idents


def get_infos(printer):
    """
    On récupère les différentes informations sur les imprimeurs qu'on insère 
    dans une liste
    Correspond à "infos" dans la requête SPARQL
    Retourne une liste
    """

    liste_infos = []
    for item in printer["results"]["bindings"]:
        if item not in liste_infos:
            liste_infos.append(item["infos"]["value"])

    liste_infos = list(dict.fromkeys(liste_infos))

    return liste_infos


def get_infos2(printer):
    """
    On récupère les différentes informations sur les imprimeurs qu'on insère 
    dans une liste
    Correspond à "infos2" dans la requête SPARQL
    Retourne une liste
    """

    liste_autresinfos = []
    for item in printer["results"]["bindings"]:
        if item["nom"]["value"] == "Cotinet, Arnoul":
            pass
        else:
            liste_autresinfos.append(item["infos2"]["value"])

    liste_autresinfos = list(dict.fromkeys(liste_autresinfos))

    return liste_autresinfos


def get_all():
    """
    Cette fonction écrit les informations des imprimeurs dans un fichier CSV.
    Chaque imprimeur correspond à une ligne du CSV, chaque information (dates, noms...) correspond à 
    une colonne.
    """

    with open('base_imprimeurs_sparql.tsv', 'w+', newline='') as newfile:
        fieldnames = ["Nom", "Lien_IdRef", "Identifiants", "Identifiant_BnF", "Autres_formes_du_Nom", "Naissance",
                      "Mort", "Genre", "Informations", "Autres_Informations"]
        writer = csv.writer(newfile, delimiter='\t')
        writer.writerow(fieldname for fieldname in fieldnames)

        # On récupère les informations des imprimeurs pour ceux qui en ont (les résultats vides, c'est-à-dire 
        # ceux qui n'ont pas de notice sur IdRef, sont ignorés).
        # Pour chacun d'entre eux, on vérifie la présence ou l'absence de l'information.
        # Si l'information est présente, on l'ajoute dans la colonne.
        # Sinon, on insère un None.
        # Les appels de fonctions dans les colonnes permettent d'ajouter les informations qui sont sous forme de
        # listes (autres formes du nom, identifiants, informations)

        for element in liste_result:
            if len(element["results"]["bindings"]) >= 1:
                nom = element["results"]["bindings"][0]["nom"]["value"]
                person = element["results"]["bindings"][0]["person"]["value"]
                imprimeur = element["results"]["bindings"][0]
                if "bnf" in imprimeur:
                    if "autreNom" in imprimeur:
                        if "naissance" in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None, None, None])
                            else:
                                writer.writerow([nom, person, get_idents(element), imprimeur["bnf"]["value"],
                                                get_noms(element), imprimeur["naissance"]["value"],
                                                 None, None, None, None])
                        elif "naissance" not in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"],
                                                             imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], None, None, None])
                            if "mort" not in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"],
                                                             imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None, None, None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None, None, None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None, None, None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"],
                                                             get_noms(element), None, None, None, None, None])

                    elif "autreNom" not in imprimeur:
                        if "naissance" in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"],
                                                             imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None, None, None])
                            else:
                                writer.writerow([nom, person, get_idents(element), imprimeur["bnf"]["value"], None,
                                                imprimeur["naissance"]["value"], None, None, None, None])
                        elif "naissance" not in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             imprimeur["mort"]["value"], None, None, None])
                            elif "mort" not in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             None, None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None, None, None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None, None, None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element),
                                                             imprimeur["bnf"]["value"], None, None,
                                                             None, None, None, None])
                    else:
                        writer.writerow([nom, person, get_idents(element), imprimeur["bnf"]["value"]])

                elif "bnf" not in imprimeur:
                    if "autreNom" in imprimeur:
                        if "naissance" in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None, None, None])
                            else:
                                writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                imprimeur["naissance"]["value"], None, None, None, None])
                        if "naissance" not in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, imprimeur["mort"]["value"],
                                                             imprimeur["genre"]["value"], get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, imprimeur["mort"]["value"],
                                                             imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, imprimeur["mort"]["value"],
                                                             imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None,  get_noms(element),
                                                             None, imprimeur["mort"]["value"], None, None, None])
                            elif "mort" not in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None,
                                                             imprimeur["genre"]["value"], get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None, imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None, imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None, imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None, None, get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None, None, get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, get_noms(element),
                                                             None, None, None, None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None,  get_noms(element),
                                                             None, None, None, None, None])

                    elif "autreNom" not in imprimeur:
                        if "naissance" in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None,
                                                             imprimeur["naissance"]["value"],
                                                             imprimeur["mort"]["value"], None, None, None])
                            else:
                                writer.writerow([nom, person, get_idents(element), None, None,
                                                 imprimeur["naissance"]["value"], None,
                                                 None, None, None])

                        elif "naissance" not in imprimeur:
                            if "mort" in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], imprimeur["genre"]["value"],
                                                             None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], None,
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             imprimeur["mort"]["value"], None, None, None])
                            if "mort" not in imprimeur:
                                if "genre" in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, imprimeur["genre"]["value"],
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, imprimeur["genre"]["value"], None, None])
                                elif "genre" not in imprimeur:
                                    if "infos" in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, None, get_infos(element),
                                                             get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, None, get_infos(element), None])
                                    elif "infos" not in imprimeur:
                                        if "infos2" in imprimeur:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, None,
                                                             None, get_infos2(element)])
                                        else:
                                            writer.writerow([nom, person, get_idents(element), None, None, None,
                                                             None, None, None, None])

                    else:
                        writer.writerow([nom, person, get_idents(element), None, None, None, None, None, None, None])

    return


if __name__ == "__main__":

    liste_id = get_data()

    liste_result = []
    for identifiant in liste_id:
        result = get_sparql(identifiant)
        liste_result.append(result)
    get_all()
