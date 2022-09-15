# Scripts

Contient les scripts qui ont permis d'enrichir la base imprimeurs et de créer les notices en TEI :

- `base_imprimeurs_sparql.py` sert à récupérer les informations des imprimeurs qui ont un identifiant et une notice d'autorité sur IdRef grâce à une requête SPARQL, et à écrire leurs informations dans un fichier TSV (*base_imprimeurs_sparql.tsv*)
- `printers_to_tei.py` sert à créer automatiquement les fiches des imprimeurs en TEI à partir du CSV *base_imprimeurs_joined.csv*, ainsi qu'à ajouter les informations des mazarinades qu'ils ont imprimées dans des éléments <TEI>;
- `recup_ids_liste_IL.py` a servi à récupérer la liste de tous les identifiants des imprimeurs du CSV d'origine (*Liste_IL_MAZ.tsv* dans le dépôt *Temp_Imprimeurs*) afin de faire une des jointures entre la liste d'origine et le TSV de la requête SPARQL.

Scripts réalisés par Zoé Cappe.