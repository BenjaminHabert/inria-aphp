# inria-aphp

réponse à l'exercice https://github.com/agramfort/inria-aphp-assignment


# Setup

```
git clone https://github.com/BenjaminHabert/inria-aphp.git
cd inria-aphp

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# lint and test
flake8 aphp/
python -m pytest

# running notebooks
export PYTHONPATH=$PYTHONPATH:$(pwd)
jupyter notebook
```

## Organisation des fichiers

- le notebooks [check_raw_patient_data](notebooks/2020-09-13_check_raw_patient_data.ipynb) contient une analyse de qualité des données partients

# Notes

## Qualité des données

Nous indiquons ici les conclusions principales. Ces observations sont prises en compte dans le nettoyage
des données brutes.

### Données patient

20000 lignes

Voir [check_raw_patient_data](notebooks/2020-09-13_check_raw_patient_data.ipynb) pour plus de détails.

- Certains `patient_id` sont dupliqués et ne correspondent pas au même patient. On ne peut donc pas prendre en compte ces
  données: impossible de savoir à quelle personne attribuer l'ID.

- Inversement, un même patient peut être identifié par plusieurs `patient_id`. Il sera nécessaire de conserver l'ensemble
  des IDs d'un patient pour faire une jointure avec d'autres données (tests PCR).

- Dans la date de naissance, seule le mois et le jour de naissance peuvent être exploités (pas l'année). On décide de
  remplacer par une colonne `birthday`.

- L'age semble cohérent mais il est surprenant de ne trouver presque aucun patient de plus de 40 ans.

    ![](images/age_distribution.png)

- On trouve les erreurs habituelles sur le nom et le prénom:
    - inversion des deux colonnes
    - typos

- quelques erreurs de saisie pour `state`. Après correction on constate que les patients viennent de tous les états

    ![](images/state_distribution.png)

- le `postcode` est plutôt bien renseigné. Dans quelques rares cas (14), le code postal est dans la colonne `suburb`
- les `phone_number` sont correctement formatés. Seulement 20% sont des numéros de téléphone mobile.

- **Après nettoyage des valeurs erronnées**, le pourcentage de valeurs manquantes est le suivant:

    ```
    patient_id        0.000000
    given_name        2.189111
    surname           2.138082
    street_number     1.908455
    address_1         3.985304
    suburb            1.035873
    postcode          0.995050
    state            10.644486
    age              19.982650
    phone_number      4.607848
    address_2        60.580701
    birthday         10.965964
    ```


### Tests PCR

- pas de valeurs manquantes. 8800 résultats de test

- on choisit de reformatter la colonne `pcr` en booléen en prenant en compte
  les différents textes (exemple, `'Positive' == 'P' == True`)

- pour 35 `patient_id`: plusieurs résultats de test. On choisit de considérer un ensemble de tests comme positif 
  si au moins l'un de ces tests est positif.

- tous les IDs dans cette table sont présents dans la table des patients. Malheureusement on perd 1.5 % des résultats
  de tests PCR lorsque l'on supprime les patients avec un ID erronné (on ne sait pas à qui attribuer un ID parmis 2
  patients)

- Au final, le nombre de tests positifs est:

    ```
    False    6583
    True     2182
    Name: pcr_positive, dtype: int64
    ```
