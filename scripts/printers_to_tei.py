import csv
import glob
from lxml import etree
import xml.etree.ElementTree as ET
import re

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}


def get_maz_corresp(doc):
    """
    Cette fonction va chercher les @xml:id des mazarinades pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire:
    - en clé (ident) = l'identifiant de l'imprimeur
    - en valeur (corresp) = la valeur du @xml:id des mazarinades qu'il a imprimées
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl//tei:publisher", namespaces=ns)
    att_corresp = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in att_corresp:
            att_corresp[ident] = []
            corresps = doc.xpath("/tei:TEI/@xml:id", namespaces=ns)
            for corresp in corresps:
                corresp = re.sub(" ", "", corresp)
                att_corresp[ident].append(corresp)

    return att_corresp


def get_maz_title(doc):
    """
    Cette fonction va chercher les titres des mazarinades pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire:
    - en clé (ident) = l'identifiant de l'imprimeur
    - en valeur (title) = le texte du titre des mazarinades qu'il a imprimées
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:publisher", namespaces=ns)
    all_titles = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in all_titles:
            all_titles[ident] = []
            titles = doc.xpath("//tei:teiHeader//tei:titleStmt/tei:title[@type='main']/text()", namespaces=ns)
            for title in titles:
                title = re.sub("\n", "", title)
                title = re.sub("\s{2,}", " ", title)
                all_titles[ident].append(title)

    return all_titles


def get_maz_author(doc):
    """ Cette fonction va chercher les auteurs des mazarinades pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire dans un dictionnaire (nested dict):
    - en clé (ident) du premier dictionnaire = l'identifiant de l'imprimeur
    - en valeur = le deuxième dictionnaire
        - en clé du deuxième dictionnaire = variable "author_ids" contenant l'identifiant
        de l'auteur s'il en a un, ou la chaîne de caractères "id" s'il n'y en a pas.
        - en valeur (author_name) du deuxième dictionnaire = le nom complet de l'auteur
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:publisher", namespaces=ns)

    all_authors = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in all_authors:
            all_authors[ident] = {}
            authors = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl//tei:author", namespaces=ns)
            for author in authors:
                if author.xpath("./@ref", namespaces=ns):
                    author_ids = author.xpath("./@ref", namespaces=ns)[0]
                    author_name = author.xpath(".//text()", namespaces=ns)
                    all_authors[ident][author_ids] = author_name
                else:
                    author_name = author.xpath(".//text()", namespaces=ns)
                    all_authors[ident]["id"] = author_name
    return all_authors


def get_maz_pages(doc):
    """
    Cette fonction va chercher le nombre de pages des mazarinades pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire:
    - en clé (ident) = l'identifiant de l'imprimeur
    - en valeur (page) = le nombre de pages des mazarinades qu'il a imprimées
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:publisher", namespaces=ns)

    all_pages = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in all_pages:
            all_pages[ident] = []
            pages = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:extent/tei:measure/@quantity",
                              namespaces=ns)
            for page in pages:
                page = re.sub("\n", "", page)
                page = re.sub("\s{2,}", " ", page)
                all_pages[ident].append(page)

    return all_pages


def get_maz_deco(doc):
    """Cette fonction va chercher le nombre de <figure @type="decoration> (marque d'imprimeur) des mazarinades
    pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire:
    - en clé (ident) = l'identifiant de l'imprimeur
    - en valeur (deco_number) = le nombre (compte) de marques d'imprimeurs trouvées dans les mazarinades qu'il
    a imprimées
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:publisher", namespaces=ns)

    all_deco = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in all_deco:
            all_deco[ident] = []
            decos = doc.xpath("//tei:text//tei:body/tei:p//tei:figure[@type='decoration']", namespaces=ns)

            for deco in decos:
                deco_number = decos.count(deco)
                all_deco[ident].append(deco_number)
                # solution provisoire pour les cas où on a deux marques d'imprimeur
                if all_deco[ident][1:]:
                    all_deco[ident] = [2]

    return all_deco


def get_maz_repo(doc):
    """
    Cette fonction va chercher l'institution de conservation des mazarinades pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire:
    - en clé (ident) = l'identifiant de l'imprimeur
    - en valeur (repo) = le lieu et le nom de l'institution de conservation des mazarinades qu'il a imprimées
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:publisher", namespaces=ns)

    all_repo = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in all_repo:
            all_repo[ident] = []
            repos1 = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:settlement/text()",
                               namespaces=ns)
            repos2 = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:institution/text()",
                               namespaces=ns)
            virgule = [","]
            repos = repos1 + virgule + repos2
            for repo in repos:
                repo = re.sub("\n", "", repo)
                repo = re.sub("\s{2,}", " ", repo)
                all_repo[ident].append(repo)

        return all_repo


def get_maz_idno(doc):
    """
    Cette fonction va chercher les liens vers les numérisations des mazarinades pour chaque imprimeur.
    Elle sert à enrichir les éléments <TEI> du <teiCorpus> des fiches d'imprimeurs.
    Retourne un dictionnaire:
    - en clé (ident) = l'identifiant de l'imprimeur
    - en valeur (idno) = le lien des numérisations des mazarinades qu'il a imprimées
    """

    printers = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:publisher", namespaces=ns)
    all_idno = {}
    for printer in printers:
        ident = printer.get("ref")
        if ident not in all_idno:
            all_idno[ident] = []
            idnos = doc.xpath("//tei:teiHeader//tei:sourceDesc/tei:bibl/tei:ref/@target",
                              namespaces=ns)
            for idno in idnos:
                all_idno[ident].append(idno)

    return all_idno


def to_tei():

    """
    Cette fonction sert à créer automatiquement tout l'encodage des fiches des imprimeurs.
    Elle est construite sur la base d'un élément <teiCorpus>, dont le <teiHeader> contient
    toutes les informations sur l'imprimeur récupérées dans la base imprimeurs (fichier CSV).
    Les élements <TEI> ajoutés à la suite du <teiHeader> contiennent les informations des mazarinades
    imprimées par cet imprimeur, si l'identifiant de l'imprimeur est renseigné dans les mazarinades.
    """

    # on ouvre le fichier CSV de la base imprimeurs
    with open("base_imprimeurs_joined.csv") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",")
        next(csvreader, None)  # cette ligne sert à ne pas lire les headers du fichier
        for row in csvreader:
            # pour chaque ligne (chaque imprimeur) du CSV, on crée les éléments suivants en TEI

            # Élément racine <teiCorpus> : contient les informations sur l'imprimeur
            root = ET.Element('teiCorpus')
            root.set('xmlns', 'http://www.tei-c.org/ns/1.0')

            # <teiHeader> : contient les informations sur l'imprimeur
            teiheader = ET.SubElement(root, 'teiHeader')

            # <fileDesc>
            filedesc = ET.SubElement(teiheader, 'fileDesc')

            # <titleStmt>
            titlestmt = ET.SubElement(filedesc, 'titleStmt')
            title1 = ET.SubElement(titlestmt, 'title')
            title1.set('type', 'standard')
            # récupération de l'isni/viaf sous forme isni:0000, renseigné
            # dans l'@ref du <title>
            isni = row[14]
            if isni:
                title1.set('ref', isni)
            else:
                title1.set('ref', 'isni:0000')

            # récupération du prénom de l'imprimeur, renseigné dans l'élément <forename>
            forename1 = ET.SubElement(title1, 'forename')
            prenom = row[1]
            if prenom:
                forename1.text = prenom

            # récupération du nom de l'imprimeur, renseigné dans l'élément <surname>
            surname1 = ET.SubElement(title1, 'surname')
            nom = row[0]
            if nom:
                surname1.text = nom

            # <editionStmt> : on y indique les informations sur la
            # création des fiches imprimeurs en TEI
            editionstmt = ET.SubElement(filedesc, 'editionStmt')
            edition = ET.SubElement(editionstmt, 'edition')
            respstmt = ET.SubElement(editionstmt, 'respStmt')
            respstmt.set('xml:id', 'ZC')
            respstmt.set('ref', 'orcid:0000-0002-3327-3967')
            name = ET.SubElement(respstmt, 'name')
            name.text = 'Zoé Cappe'
            resp = ET.SubElement(respstmt, 'resp')
            resp.text = 'Créateur de la fiche'

            # <publicationStmt> : on y indique les informations sur le contexte de création
            # desdites fiches, soit le projet Antonomaz
            publicationstmt = ET.SubElement(filedesc, 'publicationStmt')
            publisher = ET.SubElement(publicationstmt, 'publisher')
            publisher.set('ref', 'https://github.com/Antonomaz')
            publisher.set('xml:id', 'Antonomaz')
            publisher.text = 'Antonomaz'
            availability = ET.SubElement(publicationstmt, 'availability')
            availability.set('status', 'restricted')
            availability.set('n', 'cc-by')
            licence = ET.SubElement(availability, 'licence')
            licence.set('target', 'https://creativecommons.org/licenses/by/4.0')

            # <sourceDesc> : contient un <listBibl>, qui lui-même contient un élément
            # <bibl> pour chacun des identifiants de l'imprimeur, renseignés dans
            # des @source
            sourcedesc = ET.SubElement(filedesc, 'sourceDesc')
            listbibl = ET.SubElement(sourcedesc, 'listBibl')
            # récupération des différents identifiants, s'il y en a
            autres_ids = row[15]
            list_ids = list(autres_ids.split(","))
            if list_ids:
                for ident in range(len(list_ids)):
                    identifiant = str(list_ids[ident])
                    if identifiant:
                        bibl = ET.SubElement(listbibl, 'bibl')
                        bibl.set('source', identifiant)
                    else:
                        bibl = ET.SubElement(listbibl, 'bibl')
                        bibl.set('source', 'none')
            idref = row[12]
            if idref:
                bibl = ET.SubElement(listbibl, 'bibl')
                bibl.set('source', idref)

            # <profileDesc> : contient, dans un <particDesc>, puis <listPerson>,
            # puis <person>, les diverses informations sur la vie de l'imprimeur
            profiledesc = ET.SubElement(teiheader, 'profileDesc')
            particdesc = ET.SubElement(profiledesc, 'particDesc')
            listperson = ET.SubElement(particdesc, 'listPerson')
            person = ET.SubElement(listperson, 'person')
            # persName @type="standard" : contient forme normale du nom
            persname1 = ET.SubElement(person, 'persName')
            fullname = row[0] + ', ' + row[1]
            if fullname:
                persname1.set('type', 'standard')
                persname1.text = fullname

            # persName @type="alternative" : s'il y en a, contient les autres
            # formes du nom
            autres_noms = row[2]
            list_noms = list(autres_noms.split("',"))
            if list_noms:
                for nom in range(len(list_noms)):
                    persname2 = ET.SubElement(person, 'persName')
                    persname2.set('type', 'alternative')
                    list_nom = re.sub("^'", "", str(list_noms[nom]))
                    list_nom = re.sub("'$", "", str(list_nom))
                    persname2.text = str(list_nom)

            # récupération du genre de l'imprimeur dans un élément <sex>
            sex = ET.SubElement(person, 'sex')
            gender = row[5]
            sex.text = gender

            # récupération de la date de naissance s'il y en a une dans un élément
            # <birth>. Si la date est connue, elle est renseignée dans un @when avec
            # un @cert qui a pour valeur "high". Si elle est inconnue, le @when a pour
            # valeur par défaut 1600 et le @cert la valeur "low".
            birth = ET.SubElement(person, 'birth')
            birth_date = row[3]
            if birth_date:
                birth.set('when', birth_date)
                birth.set('cert', 'high')
            else:
                birth.set('when', '1600')
                birth.set('cert', 'low')

            # récupération de la date de mort s'il y en a une dans un élément
            # <death>. Si la date est connue, elle est renseignée dans un @when avec
            # un @cert qui a pour valeur "high". Si elle est inconnue, le @when a pour
            # valeur par défaut 1700 et le @cert la valeur "low".
            death = ET.SubElement(person, 'death')
            death_date = row[4]
            if death_date:
                death.set('when', death_date)
                death.set('cert', 'high')
            else:
                death.set('when', '1700')
                death.set('cert', 'low')

            # les fiches ne concernant que des imprimeurs-libraires, l'élément
            # <occupation> prend "Imprimeur-libraire" comme valeur par défaut.
            occupation = ET.SubElement(person, 'occupation')
            occupation.text = "Imprimeur-libraire"

            # les éléments d'adresse (enseigne, rue, ville, indication) sont renseignés dans
            # les éléments <objectName>, <street>, <settlement> et <country> (France par défaut)
            residence = ET.SubElement(person, 'residence')
            enseigne = row[9]
            get_address = row[7] + ' ; ' + row[8]
            rue = row[7]
            indication = row[8]
            city = row[6]

            if enseigne and city and get_address:
                residence.set('cert', 'high')
            elif get_address and city:
                residence.set('cert', 'high')
            else:
                residence.set('cert', 'low')

            address = ET.SubElement(residence, 'address')

            # ajout de l'enseigne s'il y en a une
            objectname = ET.SubElement(address, 'objectName')
            if enseigne:
                objectname.text = enseigne
            # ajout de l'adresse s'il y en a une
            street = ET.SubElement(address, 'street')
            if rue and indication:
                street.text = rue + "  ; " + indication
            elif rue:
                street.text = rue
            elif indication:
                street.text = indication
            # récupération du nom de la ville et son geonames
            settlement = ET.SubElement(address, 'settlement')
            if city:
                settlement.text = city
                cities = {
                    "Anvers": "geonames:2803138",
                    "Bordeaux": "geonames:3031582",
                    "Chalon-sur-Saône": "geonames:3027484",
                    "Dijon": "geonames:3021372",
                    "Lyon": "geonames:2996944",
                    "Marseille": "geonames:2995469",
                    "Orléans": "geonames:2989317",
                    "Paris": "geonames:2988507",
                    "Poitiers": "geonames:2986495",
                    "Pontoise": "geonames:2986140",
                    "Rennes": "geonames:2983990",
                    "Rouen": "geonames:2982652",
                    "Saumur": "geonames:2975758",
                    "Sens": "geonames:2975050",
                    "Toul": "geonames:2972350",
                    "Toulouse": "geonames:2972315",
                    "Tours": "geonames:2972191",
                    "Den Haag": "geonames:2747373"
                }
                for key, value in cities.items():
                    if city == key:
                        settlement.set('ref', value)
            else:
                settlement.set('ref', 'geonames:0000')

            country = ET.SubElement(address, 'country')
            country.text = "France"

            # ajout des éléments biographiques provenant d'Idref
            bio = row[11]

            listevent = ET.SubElement(person, 'listEvent')
            if bio:
                event = ET.SubElement(listevent, 'event')
                label = ET.SubElement(event, 'label')
                label.set('type', 'bio')
                label.set('source', 'IdRef')
                bio = re.sub("^'", "", str(bio))
                bio = re.sub("'$", "", str(bio))
                label.text = str(bio)
            else:
                event = ET.SubElement(listevent, 'event')
                label = ET.SubElement(event, 'label')
                label.set('type', 'bio')

            # ajout des éléments biographiques provenant d'Antonomaz (notes)
            note = row[10]

            if note:
                event = ET.SubElement(listevent, 'event')
                label = ET.SubElement(event, 'label')
                label.set('type', 'bio')
                label.set('source', 'Antonomaz')
                label.text = note

            # <revisionDesc> : permet d'indiquer la date la responsabilité de la création de
            # la fiche et des éventuels changements effectués ensuite
            revisiondesc = ET.SubElement(teiheader, 'revisionDesc')
            listchange = ET.SubElement(revisiondesc, 'listChange')
            change = ET.SubElement(listchange, 'change')
            change.set('when', '2022-07-10')
            change.set('who', '#ZC')
            change.text = "Création de la fiche"

            # TEI : pour chaque imprimeur, on récupère toutes les mazarinades qui contiennent un <publisher> avec son
            # identifiant en parsant les fichiers tei des mazarinades

            files = glob.glob("./Mazarinades/**/*.xml", recursive=True)
            # on limite aux imprimeurs ayant un indentifiant
            if isni:
                for file in files:
                    parser = etree.XMLParser(remove_blank_text=True)
                    doc = etree.parse(file, parser)
                    for key, value in get_maz_corresp(doc).items():
                        # pour chaque imprimeur, si on lui trouve un identifiant identique dans les mazarinades,
                        # on ajoute les mazarinades dans sa fiche au sein d'un élément <TEI>
                        if key == isni:
                            # dans le dictionnaire {Clé(identifiant) : Valeur(xml:id de ses mazarinades)}, on vérifie
                            # que la clé est égale à l'identifiant de l'imprimeur, et on ajoute la valeur du xml:id à
                            # l'attribut @corresp d'un élément TEI par mazarinade. Les valeurs sont récupérées sous
                            # forme de liste.
                            value = re.sub("^[^A-Z]", "", str(value))
                            value = re.sub("'", "", str(value))
                            value = re.sub("[^A-Z]$", ".xml", str(value))
                            tei = ET.SubElement(root, 'TEI')
                            tei.set('corresp', str(value))

                            # <teiHeader> : métadonnées des mazarinades
                            teiheader2 = ET.SubElement(tei, 'teiHeader')
                            filedesc2 = ET.SubElement(teiheader2, 'fileDesc')
                            # <titleStmt>
                            titlestmt2 = ET.SubElement(filedesc2, 'titleStmt')
                            title2 = ET.SubElement(titlestmt2, 'title')
                            # récupération du titre des mazarinades
                            for title_key, title_value in get_maz_title(doc).items():
                                title_value = re.sub("\['", "", str(title_value))
                                title_value = re.sub("'\]", "", str(title_value))
                                title_value = re.sub("\[\"", "", str(title_value))
                                title_value = re.sub("\"\]", "", str(title_value))
                                title2.text = str(title_value)

                            # récupération de l'auteur/des auteurs des mazarinades
                            for authors_dict_key, authors_dict_value in get_maz_author(doc).items():
                                authors_dict = authors_dict_value
                            for author_id, author_name in authors_dict.items():
                                author = ET.SubElement(titlestmt2, 'author')
                                if author_id == "id":
                                    author.set('ref', 'isni:0000')
                                    author.text = ' '.join(author_name)
                                else:
                                    author.set('ref', str(author_id))
                                    author.text = ' '.join(author_name)

                            # <extent> : informations matérielles des mazarinades
                            extent = ET.SubElement(filedesc2, 'extent')
                            # récupération du nombre de pages
                            measure1 = ET.SubElement(extent, 'measure')
                            measure1.set('unit', 'pages')
                            for pages_key, pages_value in get_maz_pages(doc).items():
                                pages_value = re.sub("\['", "", str(pages_value))
                                pages_value = re.sub("'\]", "", str(pages_value))
                                measure1.set('quantity', str(pages_value))

                            # présence ou absence d'une marque d'imprimeur
                            measure2 = ET.SubElement(extent, 'measure')
                            measure2.set('unit', 'decoration')
                            for deco_key, deco_value in get_maz_deco(doc).items():
                                if deco_value:
                                    deco_value = re.sub("\[", "", str(deco_value))
                                    deco_value = re.sub("\]", "", str(deco_value))
                                    measure2.set('quantity', str(deco_value))
                                else:
                                    measure2.set('quantity', '0')

                            # <publicationStmt> : informations sur le contexte de diffusion des
                            # mazarinades dans leur encodage (projet Antonomaz)
                            publicationstmt = ET.SubElement(filedesc2, 'publicationStmt')
                            publisher = ET.SubElement(publicationstmt, 'publisher')
                            publisher.set('ref', 'https://github.com/Antonomaz')
                            publisher.text = 'Antonomaz'
                            availability = ET.SubElement(publicationstmt, 'availability')
                            availability.set('status', 'restricted')
                            availability.set('n', 'cc-by')
                            licence = ET.SubElement(availability, 'licence')
                            licence.set('target', 'https://creativecommons.org/licenses/by/4.0')

                            # <sourceDesc>
                            sourcedesc2 = ET.SubElement(filedesc2, 'sourceDesc')
                            msdesc = ET.SubElement(sourcedesc2, 'msDesc')
                            msidentifier = ET.SubElement(msdesc, 'msIdentifier')

                            # récupération de l'institution de conservation des mazarinades
                            repository = ET.SubElement(msidentifier, 'repository')
                            for repo_key, repo_value in get_maz_repo(doc).items():
                                repo_value = ' '.join(repo_value)
                                repo_value = re.sub(" ,", ",", repo_value)
                                repository.text = repo_value

                            # récupération du lien vers la numérisation des mazarinades
                            idno = ET.SubElement(msidentifier, 'idno')
                            for idno_key, idno_value in get_maz_idno(doc).items():
                                idno_value = re.sub("\['", "", str(idno_value))
                                idno_value = re.sub("'\]", "", str(idno_value))
                                idno.set('source', str(idno_value))

                            physdesc = ET.SubElement(msdesc, 'physDesc')
                            decodesc = ET.SubElement(physdesc, 'decoDesc')
                            deconote = ET.SubElement(decodesc, 'decoNote')
                            text = ET.SubElement(tei, 'text')
                            body = ET.SubElement(text, 'body')
                            div = ET.SubElement(body, 'div')

            # Ajout des @xml:id des imprimeurs, qui correspondent aussi aux noms des fichiers ajoutés
            # ensuite automatiquement
            if fullname:
                fullname2 = row[0] + row[1]
                fullname2 = re.sub(" |\(|\)|'|’|-|,|\.", "", fullname2)
                fullname2 = re.sub("é|è|ë|ê", "e", fullname2)
                fullname2 = re.sub("É||È||Ë||Ê|", "E", fullname2)
                fullname2 = re.sub("ç|Ç", "c", fullname2)
                fullname2 = re.sub("ô|Ô", "o", fullname2)
                xmlids = "IL_" + fullname2
                root.set('xml:id', xmlids)
                # nommage des fichiers
                name_file = 'IL_' + fullname2

            # Écriture des fichiers xml
            tree = ET.ElementTree(root)

            tree.write("imprimeurs_tei/%s.xml" % name_file, xml_declaration=True, encoding="utf-8")


def add_empty_maz():
    """Cette fonction sert à ajouter un élément <TEI> sans information dans les <teiCorpus> des imprimeurs pour lesquels
    on n'a pas de mazarinade"""

    files = glob.glob("imprimeurs_tei/*.xml", recursive=True)
    output = []
    for file in files:
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(file, parser)

        # on crée les éléments à ajouter dans le cas où il n'y a pas d'élément <TEI> dans les fichiers. Tous les
        # attributs et les éléments ont des valeurs neutres quand des valeurs doivent être renseignées.
        tei = etree.Element('TEI', attrib={'corresp': 'none'})
        teiheader = etree.SubElement(tei, 'teiHeader')
        filedesc = etree.SubElement(teiheader, 'fileDesc')
        titleStmt = etree.SubElement(filedesc, 'titleStmt')
        title = etree.SubElement(titleStmt, 'title')
        author = etree.SubElement(titleStmt, 'author', attrib={'ref': 'isni:0000'})
        extent = etree.SubElement(filedesc, 'extent')
        measure = etree.SubElement(extent, 'measure', attrib={'unit': 'pages', 'quantity': '0'})
        publicationstmt = etree.SubElement(filedesc, 'publicationStmt')
        publisher = etree.SubElement(publicationstmt, 'publisher', attrib={'ref': 'https://github.com/Antonomaz',
                                                                           # 'xml:id': 'Antonomaz'
                                                                           })

        publisher.text = 'Antonomaz'
        availability = etree.SubElement(publicationstmt, 'availability', attrib={'status': 'restricted',
                                                                                 'n': 'cc-by'})
        licence = etree.SubElement(availability, 'licence', attrib={
            'target': 'https://creativecommons.org/licenses/by/4.0'})
        sourcedesc = etree.SubElement(filedesc, 'sourceDesc')
        msdesc = etree.SubElement(sourcedesc, 'msDesc')
        msidentifier = etree.SubElement(msdesc, 'msIdentifier')
        repository = etree.SubElement(msidentifier, 'repository')
        repository.text = 'Sans lieu'
        idno = etree.SubElement(msidentifier, 'idno', attrib={'source': 'None'})
        physdesc = etree.SubElement(msdesc, 'physDesc')
        decodesc = etree.SubElement(physdesc, 'decoDesc')
        deconote = etree.SubElement(decodesc, 'decoNote')
        text = etree.SubElement(tei, 'text')
        body = etree.SubElement(text, 'body')
        div = etree.SubElement(body, 'div')

        # on vérifie la présence ou l'absence d'un élément <TEI>. S'il est absent, on ajoute le <TEI> neutre.
        if doc.xpath(".//tei:TEI", namespaces=ns):
            ''
        else:
            teicorpus = doc.xpath("/tei:teiCorpus", namespaces=ns)[0]
            teicorpus.append(tei)
            tei.append(teiheader)
            teiheader.append(filedesc)
            filedesc.append(titleStmt)
            titleStmt.append(title)
            titleStmt.append(author)
            filedesc.append(extent)
            extent.append(measure)
            filedesc.append(publicationstmt)
            publicationstmt.append(publisher)
            publicationstmt.append(availability)
            availability.append(licence)
            filedesc.append(sourcedesc)
            sourcedesc.append(msdesc)
            msdesc.append(msidentifier)
            msidentifier.append(repository)
            msidentifier.append(idno)
            msdesc.append(physdesc)
            physdesc.append(decodesc)
            decodesc.append(deconote)
            tei.append(text)
            text.append(body)
            body.append(div)

            # on écrit dans les fichiers
            with open(file, "w+") as sortie_xml:
                output = etree.tostring(doc, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
                    'utf8')
                sortie_xml.write(str(output))


if __name__ == "__main__":
    # On procède d'abord à l'encodage automatique des fiches d'imprimeurs
    to_tei()
    # Puis on ajoute les <TEI> neutres
    add_empty_maz()

