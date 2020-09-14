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

