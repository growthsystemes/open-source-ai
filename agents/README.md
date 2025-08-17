# **Context Engineering pour tes Agents IA**



## **Context Engineering ?**

Les Agents IA pour interagir avec leurs environnement ont besoin de contextes sur celui-ci pour performer la tache donnée.

## **Cest quoi ?**


::: dark
### **Context Engineering** : L'art de remplir la fenêtre de contexte d'un LLM avec juste les bonnes informations pour la prochaine étape/tâche.

::: success

## Source de contexte possibles : 
[ ] Instructions
[ ] Connaissance externe (RAG,Base de données,...)
[ ] Outil à disposition
[ ] Feedback d'outils

:::

# Les stratégies pour contrôler son contexte


::: dark

#### 1. Ecriture du contexte
**Sauvegarder** du contexte en dehors de** la fenetre** du LLM pour aider l'agent à faire la tâche.
#### 2. Selectionne le contexte
**Envoyer** dans la fenêtre de contexte du  LLM
#### 3. Compresser le contexte
Retenir uniquement les **tokens/informations** requises pour la tâche
#### 4. Isoler le contexte
**Séparer**pour aider l'agent sur la tâche

:::


::: warning
### **Langgraph** est concu et **construit** pour supporter ces différentes stratégies
:::

::: light
### 1. Ecriture du contexte
::: success
F
:::

::: light
### 2. Sélectionner le contexte
::: success
FAURE
:::

::: light
### 3. Compresser le contexte
::: success
FAURE
:::

::: light
### 4. Isoler le contexte
::: success
FAURE
:::
