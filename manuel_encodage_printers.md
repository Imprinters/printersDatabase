# Manuel d'encodage des imprimeurs

Les fiches des imprimeurs sont construites au sein d'un élément englobant <teiCorpus>, dans lequel on insère à la fois les informations sur les imprimeurs et les mazarinades qu'ils ont imprimées (s'il y en a dans le corpus).

## Ajout d'informations sur les imprimeurs

Les informations sur les imprimeurs sont renseignées dans le <teiHeader> du <teiCorpus>.

Selon les sources d'où proviennent les informations (IdRef, Antonomaz ou Moreau), celles-ci peuvent être plus ou moins fournies. Certains imprimeurs n'ont ainsi aucune information de renseignée, et leur fiche "vide" se présente alors sous cette forme :

```XML
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0" xml:id="IL_BenarLouis">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title type="standard" ref="isni:0000">
          <forename>Louis</forename>
          <surname>Benar</surname>
        </title>
      </titleStmt>
      <editionStmt>
        <edition/>
        <respStmt xml:id="ZC" ref="orcid:0000-0002-3327-3967">
          <name>Zoé Cappe</name>
          <resp>Créateur de la fiche</resp>
        </respStmt>
      </editionStmt>
      <publicationStmt>
        <publisher ref="https://github.com/Antonomaz" xml:id="Antonomaz">Antonomaz</publisher>
        <availability status="restricted" n="cc-by">
          <licence target="https://creativecommons.org/licenses/by/4.0"/>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <listBibl>
          <bibl source="none"/>
        </listBibl>
      </sourceDesc>
    </fileDesc>
    <profileDesc>
      <particDesc>
        <listPerson>
          <person>
            <persName type="standard">Benar, Louis</persName>
            <persName type="alternative"/>
            <sex>M</sex>
            <birth when="1600" cert="low"/>
            <death when="1700" cert="low"/>
            <occupation>Imprimeur-libraire</occupation>
            <residence cert="low">
              <address>
                <objectName/>
                <street> ; </street>
                <settlement ref="geonames:0000"/>
                <country>France</country>
              </address>
            </residence>
            <listEvent>
              <event>
                <label type="bio" source="IdRef"/>
              </event>
            </listEvent>
          </person>
        </listPerson>
      </particDesc>
    </profileDesc>
    <revisionDesc>
      <listChange>
        <change when="2022-07-10" who="#ZC">Création de la fiche</change>
      </listChange>
    </revisionDesc>
  </teiHeader>
  <!-- pour les mazarinades, voir la partie suivante -->
</teiCorpus>
```

Si l'on souhaite enrichir une fiche imprimeur, en premier lieu, il est préférable de vérifier que l'attribut `@xml:id` de l'élément `<teiCorpus>` contient bien en valeur "IL_" suivi du "Nom" et "Prénom" de l'imprimeur, donc sous cette forme "IL_NomPrenom" (par exemple : *IL_AlliotGervais*"

Puis :

### fileDesc et titleStmt

Au sein de l'élément `<titleStmt>`, l'élément `<title>` a pour attribut `@ref`. Si l'imprimeur n'a pas d'identifiant de type ISNI ou VIAF, il prend par défaut la valeur *"isni:0000"*. Si l'identifiant de l'imprimeur peut être ajouté, il sera à indiqué sous la forme *"isni:numéro"*, *"viaf:numéro"* ou "bnf:numéro". Dans le cas où l'imprimeur a plusieurs identifiants, on préfèrera indiquer l'ISNI, sinon le viaf, ou la BnF.

Dans l'élément `<title>`, si ces informations ne s'y trouvent pas, on indique le prénom de l'imprimeur dans un élément `<forename>` et son nom de famille dans un élément `<surname>`.

*Exemple :*
```XML
<titleStmt>
    <title type="standard" ref="isni:0000000121202363">
        <forename>Gervais</forename>
        <surname>Alliot</surname>
    </title>
</titleStmt>
```

### fileDesc et sourceDesc

Dans le `<sourceDesc>` et son sous-élément `<listBibl>`, on indique dans un ou des éléments `<bibl>` le ou les identifiants de l'imprimeur, s'il en a. Chaque `<bibl>` correspond à un identifiant, et celui-ci est à renseigner en valeur de son attribut `@source` sous forme de lien.

*Exemple :*
```XML
<sourceDesc>
    <listBibl>
        <bibl source="http://data.bnf.fr/ark:/12148/cb12229635p#foaf:Person"/>
        <bibl source="http://viaf.org/viaf/224751101"/>
        <bibl source="http://isni.org/isni/0000000362335140"/>
    </listBibl>
</sourceDesc>
```


### profileDesc, particDesc, listPerson

Dans ces trois éléments on trouve l'élément `<person>`, dans lequel peuvent être renseignées toutes les informations complémentaires de l'imprimeur.

- le `<persName @type="standard">` doit contenir la forme normalisée du nom (Nom, Prénom)
- le `<persName @type="alternative">` peut contenir les autres formes du nom de l'imprimeur si elles existent. Il peut être répété autant de fois qu'il y a de formes du nom (on crée ainsi un nouveau `<persName>` de ce type pour chacune des formes du nom)

*Exemple :*
```XML
 <persName type="standard">Belley, Jacques</persName>
 <persName type="alternative">'Bellay, Jacques</persName>
 <persName type="alternative">'Barlay, Jacques</persName>
 <persName type="alternative">'Beley, Jacques</persName>
 <persName type="alternative">'Bellé, Jacques</persName>
 <persName type="alternative">'Berlay, Jacques'</persName>
```

- L'élément `<sex>` doit contenir le genre de l'imprimeur, qui doit être renseigné sous la forme *M* ou *F*.
- Les dates de naissance et de mort sont à indiquer respectivment dans des éléments `<birth>` et `<death>`, en tant que valeur de l'attribut `@when` et non en texte de l'élément (la balise doit rester auto-fermante). Si la ou les dates sont connues et indiquées en valeur de cet attribut, on changera alors aussi la valeur de l'attribut `@cert` en *high*. Si la ou les dates sont inconnues, on conservera la forme par défaut.

*Exemple :*
```XML
 <sex>M</sex>
 <birth when="1624" cert="high"/>
 <death when="1655" cert="high"/>
```

- L'élément `<occupation>` contient par défaut la valeur *Imprimeur-libraire" et n'est pas à modifier.
- L'élément `<residence>` contient les éléments d'adresse de l'imprimeur. Si un élément d'adresse est connu, on change sa valeur en *high*.
	Dans le `<address>` du `<residence>`, on indique l'adresse principale de l'imprimeur.
	L'enseigne, si elle est connue, est à indiquer dans `<objectName>`.
	La rue et les indications d'emplacement, s'il y en a, sont à indiquer dans `<street>`.
	La ville, si elle est connue, est à indiquer dans `<settlement>`. Cet élément doit aussi prendre pour attribut `@ref` le geonames de la ville, sous la forme `geonames:numéro`.
	Le pays, par défaut la France, est à indiquer dans l'élément `<country>`.

*Exemple :*
```XML
<residence cert="high">
    <address>
        <objectName>Au pied de biche</objectName>
        <street>rue Saint-Jacques ; proche des Jacobins</street>
        <settlement ref="geonames:2988507">Paris</settlement>
        <country>France</country>
    </address>
</residence>
```

- Les informations sur la vie de l'imprimeur sont à renseigner dans l'élément `<listEvent>`. Les informations sont divisées selon leur source, par exemple *IdRef* ou *Antonomaz*. Pour chaque type d'informations, on crée un élement `<event>`. Dans celui-ci, on crée un élément `<label>` qui contiendra les informations. Celui-ci prend pour attributs `@type` avec pour valeur *bio* (pour indiquer qu'il s'agit d'élement biographiques), et `@source` qui prend pour valeur la source des informations.

*Exemple :*
```XML
<listEvent>
    <event>
        <label type="bio" source="IdRef">'Imprimeur du roi à Toul (Meurthe-et-Moselle).
             Activité attestée en 1647. Associé avec Jean Laurent.'</label>
    </event>
    <event>
        <label type="bio" source="Antonomaz">imprimeur du roi à Toul.</label>
    </event>
</listEvent>
```

### Modifications

Les modifications effectuées sur la fiche sont à indiquer à deux endroits :
	1. dans le `<fileDesc>`, dans son sous-élément `<respStmt>`. Les initiales de la personnes sont à indiquer en valeur de son attribut `@xml:id`, et son numéro ORCID, s'il existe, en valeur de l'attribut `@ref`. Son nom complet doit être indiqué dans le sous-élément `<name>` et son rôle dans le deuxième sous-élément `<resp>`.
	2.  dans les éléments `<revisionDesc>` et `<listChange>`, avec un sous-élément `<change>` pour chaque modification. Cet élément prend en attribut `@when` la date de modification (sous la forme AAAA-MM-JJ) et avec l'attribut `@who` qui prend en valeur un "#" devant les initiales de la personne.

*Exemple:*
```XML
<!-- ... -->
<editionStmt>
    <edition/>
    <respStmt xml:id="ZC" ref="orcid:0000-0002-3327-3967">
        <name>Zoé Cappe</name>
        <resp>Créateur de la fiche</resp>
    </respStmt>
</editionStmt>
<!-- ... -->
<revisionDesc>
    <listChange>
        <change when="2022-07-10" who="#ZC">Création de la fiche</change>
    </listChange>
</revisionDesc>
```

## Ajout de mazarinades dans les fiches imprimeurs

Les mazarinades sont à ajouter des des éléments `<TEI>`, sous le `<teiHeader>` contenant les informations sur l'imprimeur, à l'intérieur du `<teiCorpus>`.

Tous les imprimeurs ont au moins un élément `<TEI>` existant, soit parce que des mazarinades leur sont déjà associées, soit parce qu'il n'y en a pas. Dans le second cas, le `<TEI>` est alors vide, et se présente sous la forme suivante :

```XML
<teiCorpus>  
  <!-- ... -->
  <TEI corresp="none">
    <teiHeader>
      <fileDesc>
        <titleStmt>
          <title/>
          <author ref="isni:0000"/>
        </titleStmt>
        <extent>
          <measure unit="pages" quantity="0"/>
        </extent>
        <publicationStmt>
          <publisher ref="https://github.com/Antonomaz">Antonomaz</publisher>
          <availability status="restricted" n="cc-by">
            <licence target="https://creativecommons.org/licenses/by/4.0"/>
          </availability>
        </publicationStmt>
        <sourceDesc>
          <msDesc>
            <msIdentifier>
              <repository>Sans lieu</repository>
              <idno source="None"/>
            </msIdentifier>
            <physDesc>
              <decoDesc>
                <decoNote/>
              </decoDesc>
            </physDesc>
          </msDesc>
        </sourceDesc>
      </fileDesc>
    </teiHeader>
    <text>
      <body>
        <div/>
      </body>
    </text>
  </TEI>
</teiCorpus>
```

Pour ajouter une nouvelle mazarinade à la fiche d'un imprimeur, on commence par indiquer le nom du fichier de la mazarinade dans l'attribut `@corresp` de l'élément `<TEI>`, au lieu du *none* qui est renseigné par défaut. (*par exemple : <TEI corresp="Moreau1975_GBOOKS.xml">*)

Ensuite, seuls les éléments du `<fileDesc>` sont à compléter.

### Le titleStmt

Dans le `<titleStmt>`, on indique à la fois le titre de la mazarinade et son ou ses auteurs.

Le titre est dans un élément `<title>`, et chaque auteur est à indiquer dans un élément `<author>` distinct, avec en attribut `@ref` son identifiant (ISNI ou VIAF), sous la même forme que pour les imprimeurs dans leur `<title>`. Si l'auteur n'a pas d'identifiant, on l'indique sous la forme `@ref="isni:0000"`. Si l'auteur est inconnu, la balise `<author>` sera alors auto-fermante avec un `@ref="0000"`.

*Exemples :*
```XML
<titleStmt>
     <title>Consultation et ordonnance des médecins de l’État pour la purgation de la
            France malade, par le sieur Du Teil.</title>
    <author ref="isni:0000000054900937">Jean Du Teil</author>
</titleStmt>
```

```XML
<titleStmt>
    <title>Prediction où se voit comme le roy Charles II. Roy de la Grand' Bretagne
        doit estre remis aux royaumes d'Angleterre, Escosse &amp; Irlande apres la
        mort de son pere. Avec la conference du feu Roy &amp; le docteur Henderson
        Escossois touchant le gouvernement de l'Eglise anglicane. Ensemble diverses
        pieces de quoy le contenu est en la page suivante. Le tout en suitte du
        portrait royal.</title>
    <author ref="isni:0000000118675506">Charles II</author>
    <author ref="isni:0000000123209622">Charles I</author>
    <author ref="isni:0000">Alexander Henderson</author>
    <author ref="isni:0000000081702805">John Suckling</author>
    <author ref="isni:0000000062998962">Paul Grebner</author>
</titleStmt>
```


```XML
<titleStmt>
    <title>Justes (les) complaintes des bourgeois de Paris, adressées à messieurs du
        Parlement.</title>
    <author ref="isni:0000"/>
</titleStmt>
```

### L'extent

L'élément `<extent>` sert à donner des informations sur les particularités physiques des documents. Les informations qui nous intéressent ici sont le nombre de pages et la présence ou l'absence d'une marque d'imprimeur.

En sous-élement de `<extent>`, il faut donc deux éléments `<measure>` :

- le premier prend pour premier attribut `@unit="pages"`, et pour second attribut `@quantity`, avec comme valeur le nombre de pages de la mazarinade ;
- le deuxième prend pour premier attribut `@unit="decoration"`, et pour second attribut `@quantity`, avec pour valeur le nombre de marques d'imprimeurs dans la mazarinade (donc *0* s'il n'y en a pas).

*Exemples :*

```XML
<extent>
    <measure unit="pages" quantity="8"/>
    <measure unit="decoration" quantity="1"/>
</extent>
```

```XML
<extent>
    <measure unit="pages" quantity="4"/>
    <measure unit="decoration" quantity="0"/>
</extent>
``` 

### sourceDesc, msDesc et msIdentifier

Dans le `<msIdentifier`, deux éléments nous intéressent : le `<repository>` et le `<idno>`.

- `<repository>` doit contenir le lieu (la ville) et le nom de l'institution de conservation de la mazarinade dont on a la numérisation (*par exemple : Paris, Bibliothèque nationale de France*)
- `<idno>` est une balise auto-fermante, il contient dans son attribut `@source` le lien vers la numérisation de ladite mazarinade (*par exemple : source="https://books.google.fr/books?id=uktKAAAAcAAJ"*).
