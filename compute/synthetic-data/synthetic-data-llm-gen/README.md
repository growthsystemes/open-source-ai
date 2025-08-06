# Synthetic Data LLM Generation Demo

Ce dépôt illustre comment **générer automatiquement des jeux de données tabulaires réalistes** à l’aide de Large Language Models (LLM) et de la librairie **LangChain**.
Trois cas d’usage sont fournis :

| Domaine                  | Fichier modèle                    | Exemple de sortie                       |
| ------------------------ | --------------------------------- | --------------------------------------- |
| Transactions financières | `FinancialTransaction` (pydantic) | `financial_records.csv` _(généré)_      |
| Ressources humaines (RH) | `EmployeeHR` (pydantic)           | `hr_records_example.csv` _(pré-généré)_ |
| Dossiers médicaux        | `MedicalRecord` (pydantic)        | `medical_records.csv` _(généré)_        |

> Le notebook **`synthetic_data_gen.ipynb`** montre pas-à-pas comment définir un schéma `pydantic`, construire un prompt few-shot, puis appeler `create_openai_data_generator` pour produire un fichier CSV en masse.

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Pré-requis](#pré-requis)
3. [Installation rapide](#installation-rapide)
4. [Premiers pas](#premiers-pas)
5. [Structure du projet](#structure-du-projet)
6. [Personnaliser vos jeux de données](#personnaliser-vos-jeux-de-données)
7. [Limitations et bonnes pratiques](#limitations-et-bonnes-pratiques)
8. [Contribuer](#contribuer)
9. [Licence](#licence)

---

## Fonctionnalités

- **Schéma déclaratif** : définissez simplement votre modèle de données avec `pydantic`.
- **Prompt Few-Shot** automatique : le générateur compose un prompt d’exemples pour guider l’LLM.
- **Paramétrage fin** : température, nombre d’itérations, taille de lot, etc.
- **Export CSV prêt à l’emploi** : idéal pour tests, démos, prototypage ou complétion de datasets réels.
- **100 % Python** : pas de dépendances systèmes lourdes.

---

## Pré-requis

| Logiciel                | Version conseillée |
| ----------------------- | ------------------ |
| Python                  | ≥ 3.10             |
| pip / venv ou conda     | Dernière version   |
| Compte OpenAI + clé API | Obligatoire        |

Créez un fichier `.env` ou exportez la variable :

```bash
export OPENAI_API_KEY="votre_clé_secrète"
```
