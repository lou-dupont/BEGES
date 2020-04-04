# Consolidation des bilans GES de l'ADEME

Ce code sert à consolider les bilans d'émissions de gaz à effet de serre publiés sur le site de l'ADEME par les enterprises ou organisations françaises. Voir la description ci-dessous pour en savoir plus sur le contexte et le contenu. Les données consolidées sont ensuite rendues disponibles sur le site [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/bilans-demissions-de-ges-publies-sur-le-site-de-lademe-1/).

## Paramétrage du téléversement vers la plateforme

Pour sauvegarder vers [data.gouv.fr](data.gouv.fr), il faut une clef API (qui est secrète). Le mode d'emploi est :
* créer un fichier `params.py` au même niveau que le code `main.py`,
* dans ce fichier, saisir la clef au format `X_API_KEY = "ma_clef_api"`.

## Mode d'emploi manuel

Le traitement est séparé en trois scripts à dérouler dans l'ordre suivant :

1. `download.py` télécharge l'ensemble des pages HTML concernant les bilans GES saisis sur la plateforme,
2. `parse.py` interprête les fichiers HTML pour en extraire les données et les consolider aux formats CSV et Excel,
3. `upload.py` automatise la sauvegarde vers la plateforme de données ouvertes (optionnel, nécessite la clef API).

Les fichiers HTML sont stockés par le premier script et lus par le deuxième script dans un dossier à choisir (par défaut `./html/`). Les fichiers de sorties sont générés dans un dossier à choisir (par défaut `./output/`).

## Mode d'emploi automatisé

Le script `main.py` exécute ces trois étapes dans l'ordre. Pour une exécution toutes les semaines, le samedi à 20h, ajouter la ligne suivante au fichier `/etc/crontab` 
```
0 20 * * 6   root    python3 /srv/BEGES/main.py >/dev/null 2>&1
```

## Description du contexte

Le **Code de l'environnement** dispose ([article L229-25](https://www.legifrance.gouv.fr/affichCodeArticle.do;jsessionid=B27788AA2F0B41AC79977E793273C7FF.tplgfr42s_1?idArticle=LEGIARTI000031694974&cidTexte=LEGITEXT000006074220&dateTexte=20191027)) que certaines organisations doivent établir régulièrement un bilan de leurs émissions de gaz à effet de serre (GES). Les organisations concernées sont :

* les personnes morales de droit privé employant plus de 500 personnes (250 dans les régions et départements d'outre-mer)
* l’État, les régions, les départements, les métropoles, les communautés urbaines, les communautés d'agglomération et les communes ou communautés de communes de plus de 50 000 habitants ainsi que les autres personnes morales de droit public employant plus de 250 personnes.

Ce bilan doit être réalisé tous les 4 ans pour les personnes morales privées et tous les 3 ans pour les personnes morales publiques. Il doit être transmis par voie électronique sur la plateforme [Bilans GES](http://www.bilans-ges.ademe.fr/) de l'[ADEME](https://www.ademe.fr/) et est public.

Les standards internationaux divisent les bilans d'émissions de GES en trois catégories, appelées "*scopes*" :

* le *Scope 1* couvre les émissions directes,
* le *Scope 2* couvre les émissions indirectes associées à l'énergie,
* le *Scope 3* couvre les autres émissions indirectes.

L'obligation de bilan de GES ne couvre que les deux premiers sous-ensembles. La réalisation et la publication d'un inventaire pour le troisième est seulement recommandée.

### Accès à la base officielle

L'article L312-1-1 du Code des Relations entre le Public et l'Administration (CRPA) dispose que les administrations ont l'obligation de publier en ligne "*les données, mises à jour de façon régulière, dont la publication présente un intérêt économique, social, sanitaire ou environnemental*". L'article L300-4 du CRPA ajoute que les données doivent être publiées "*dans un standard ouvert, aisément réutilisable et exploitable par un système de traitement automatisé*".

L'ADEME diffuse sur son site les bilans GES saisis par les organisations via un [moteur de recherche](http://www.bilans-ges.ademe.fr/fr/bilanenligne/bilans/index/siGras/0), mais ne publie pas la base de donnée sous-jacente consolidée de l'ensemble des bilans (pour le moment). Il est donc possible de visualiser chaque bilan un par un, mais pas d'effectuer des traitements automatisés sur ces données. 

### Documentation

La meilleure documentation disponible est celle rédigée et diffusée par l'ADEME, par exemple à partir de la page [Principes des bilans GES](https://www.data.gouv.fr/fr/datasets/base-carbone-complete-de-lademe/) du site officiel. La lecture de cette excellente documentation est indispensable pour bien comprendre le sens des données publiées ci-dessous.

### Description du jeu proposé

Un travail de consolidation artisanale de la base complète est proposé ici. Pour faciliter leur ré-utilisation, les données sont fournies sous deux formats : 
* un fichier **XLSX**, pour une ouverture facile dans Excel, à destination du grand public,
* une archive compressée de cinq fichiers **CSV** (séparateur **virgule**, encodage **UTF-8**), pour un usage automatisé dans un format standard, à destination des informaticien-ne-s.

#### Postes d'émission

Le fichier **scope_items.csv** (ou l'onglet **scope_items** du fichier Excel) décrit les postes d'émission composant chaque *scope*. Il comporte les colonnes suivantes :
* `id` : identifiant numérique du poste,
* `label` : libellé du poste,
* `scope_id` : identifiant du *scope* auquel est rattaché le poste,
* `scope_label`: libellé du *scope*.

#### Bilans réalisés

Le fichier **assessments.csv** (ou l'onglet **assessments** du fichier Excel) décrit les bilans réalisés. Il comporte les colonnes suivantes :
* `id` : identifiant numérique du bilan,
* `organization_name` : nom de l'organisation concernée,
* `organization_description` : description libre de l'organisation,
* `organization_type` : type d'organisation,
* `collectivity_type` : type de collectivité (pour les collectivités territoriales),
* `staff` : effectifs, nombre d'agents ou de salariés de l'organisation,
* `population` : population de la collectivité (pour les collectivités territoriales),
* `consolidation_method` : mode de consolidation du bilan,
* `reporting_year` : année sur laquelle porte le bilan,
* `total_scope_1` : émissions totales (en tonnes équivalent CO2), relatives au *Scope 1* (à l'exclusion du CO2 d'origine biogénique), dont le calcul est obligatoire,
* `total_scope_2` : émissions totales (en tonnes équivalent CO2), relatives au *Scope 2* (à l'exclusion du CO2 d'origine biogénique), dont le calcul est obligatoire,
* `total_scope_3` : émissions totales (en tonnes équivalent CO2), relatives au *Scope 3* (à l'exclusion du CO2 d'origine biogénique), dont le calcul est facultatif,
* `reference_year` : année du bilan de référence,
* `action_plan` : *Oui* ou *Non* selon qu'un plan d'action a été saisi en accompagnement du bilan ou pas,
* `reductions_scope_1_2` : réduction des émissions (en tonnes équivalent CO2) envisagées d'ici le prochain bilan, pour la somme indifférenciée du *Scope 1* et du *Scope 2*,
* `reductions_scope_1` : réduction des émissions (en tonnes équivalent CO2) envisagées d'ici le prochain bilan, pour le *Scope 1*,
* `reductions_scope_2` : réduction des émissions (en tonnes équivalent CO2) envisagées d'ici le prochain bilan, pour le *Scope 2*,
* `reductions_scope_3` : réduction des émissions (en tonnes équivalent CO2) envisagées d'ici le prochain bilan, pour le *Scope 3*,
* `is_draft` : indique si le bilan est encore en "mode brouillon" sur le site de l'ADEME, ou si l'organisation a effectivement cliqué sur "Publier" pour le rendre accessible via le moteur de recherche (seuls ces bilans sont publiés ici, bien que les autres soient accessibles en ligne),
* `source_url` : URL à laquelle est publié le bilan officiel sur le site de l'autorité.

#### Unités légales

Le fichier **legal_units.csv** (ou l'onglet **legal_units** du fichier Excel) décrit les unités légales (les personnes morales ou leurs établissements) concernées par chaque bilan. Chaque bilan peut être lié à zéro (c'est fréquemment le cas pour l'État ou les collectivités territoriales), une ou plusieurs unités légales. Il comporte les colonnes suivantes :
* `assessment_id` : identifiant du bilan par lequel l'unité légale est concernée,
* `legal_unit_id_type` : type d'identifiant pour l'unité légale (*SIREN* pour une organisation ou **SIRET** pour un établissement),
* `legal_unit_id` : valeur de l'identifiant (9 ou 14 chiffres), à recouper avec la [base SIRENE de l'INSEE](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/).

#### Émissions détaillées

Le fichier **emissions.csv** (ou l'onglet **emissions** du fichier Excel) décrit les émissions par poste de chaque bilan. Il comporte les colonnes suivantes : 
* `assessment_id` : identifiant du bilan,
* `type` : type du bilan (*Déclaration* pour le bilan de l'année concernée par la déclaration `reporting_year` et *Référence* pour le bilan de l'année de référence `reference_year`),
* `scope_item_id` : identifiant du poste d'émission,
* `co2` : émissions de dioxyde de carbone, CO2 (en tonnes),
* `ch4` : émissions de méthane, CH4 (en tonnes équivalent CO2),
* `n2o` : émissions de protoxyde d'azote, N2O (en tonnes équivalent CO2),
* `other` : émissions d'autres gaz à effet de serre (en tonnes équivalent CO2),
* `total` : total des émissions de gaz à effet de serre (en tonnes équivalent CO2), qui peut être présent sans que les colonnes précédentes soient remplies (lorsque l'organisation n'a pas détaillé ses émissions par type de gaz),
* `co2_biogenic` : émissions de dioxyde de carbone d'origine biogénique (en tonnes), qui ne sont pas incluses dans le total (voir la page dédiée à la [prise en compte du CO2 d'origine biogénique](http://www.bilans-ges.ademe.fr/documentation/UPLOAD_DOC_FR/index.htm?co2_biogenique.htm) de l'ADEME).

Toutes les quantités sont exprimées en tonnes équivalent CO2. Les conversions sont réalisées grâce aux [PRG à 100 ans](http://www.bilans-ges.ademe.fr/fr/accueil/contenu/index/page/giec/siGras/0).

#### Textes

Le fichier **texts.csv** (ou l'onglet **texts** du fichier Excel) reprend les contenus en texte libre saisis dans chaque bilan. Il comporte les colonnes suivantes :
* `assessment_id` : identifiant du bilan concerné,
* `key` : type de texte (selon les libellés des sections du site officiel),
* `value` : texte libre, qui peut contenir de la mise en forme selon la syntaxe HTML.
