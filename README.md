# GrowthSystemes – Open Source AI Toolkit

Bienvenue sur le dépôt **open‑source** de l’organisation **GrowthSystemes**.  
Notre objectif est de :

1. Mutualiser progressivement toutes les briques techniques internes (agents IA, scripts d’infrastructure, générateurs de données, workflows d’automatisation, etc.).  
2. Les rendre accessibles à la communauté sous licence open‑source lorsqu’elles n’exposent pas d’éléments propriétaires ou sensibles.  

Ce dépôt sert donc de point d’entrée unique : clonage, expérimentation, contributions et suivi de la feuille de route.

---

## Structure du dépôt

| Dossier / Fichier | Rôle |
| ----------------- | ---- |
| **`agents/`**     | Agents IA basés sur LangGraph / LangChain (analyse concurrentielle, extraction d’insights, etc.). Chaque sous‑dossier contient un agent autonome + instructions d’install. |
| **`compute/`**    | Modules de calcul lourd : génération de données synthétiques pour LLM, pipelines de fine‑tuning, notebooks d’expérimentation. |
| **`infra/`**      | Infrastructure‑as‑Code (Docker, Terraform, scripts d’approvisionnement cloud) et modèles de déploiement pour reproduire nos environnements. |
| **`workflows/`**  | Chaînes d’automatisation (Make, n8n, Airflow) prêtes à l’emploi : scraping, enriched‑lead pipelines, intégrations CRM, etc. |
| **`.gitmodules`** | Déclaration de sous‑modules Git pour réutiliser des librairies ou projets tiers sans dupliquer le code. |
| **`LICENSE`**     | Licence open‑source applicable (voir section Licence). |

Cette arborescence évoluera : des dossiers additionnels pourront apparaître (par exemple `docs/`, `examples/`, `datasets/`).

---

## Prérequis

| Besoin | Version minimale recommandée |
| ------ | --------------------------- |
| **Git** | 2.40 |
| **Python** | 3.10 |
| **Docker** | 24.x |
| **Poetry** (ou pip + virtualenv) | 1.6 |

---

## Installation rapide

```bash
# 1. Cloner le dépôt principal + sous‑modules
git clone --recursive https://github.com/growthsystemes/open-source-ai.git
cd open-source-ai

# 2. Créer l’environnement Python
python -m venv .venv
source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt         # ou `poetry install`

# 3. Lancer les tests unitaires (optionnel)
pytest -q
