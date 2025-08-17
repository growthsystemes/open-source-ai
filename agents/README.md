---
# You can also start simply with 'default'
theme: default
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: black
# some information about your slides (markdown enabled)
title: Context Engineering pour les Agents IA
info: |
  ## Slidev Starter Template
  Presentation slides for developers.
# apply unocss classes to the current slide
class: text-center

drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
# open graph
seoMeta:
  # By default, Slidev will use ./og-image.png if it exists,
  # or generate one from the first slide if not found.
  ogImage: auto
  # ogImage: https://cover.sli.dev
---

# Context Engineering pour tes Agents IA

Les stratégies à adopter pour construire des Agents IA robustes

<div @click="$slidev.nav.next" class="mt-12 py-1" hover:bg="white op-10">
  Appuyer sur espace pour la prochaine page<carbon:arrow-right />
</div>

<div class="abs-br m-6 text-xl">
  <a href="https://github.com/slidevjs/slidev" target="_blank" class="slidev-icon-btn">
    <carbon:logo-github />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---

<div class="flex justify-center">

# [Communauté n°1 sur les Agents IA](https://www.skool.com/ai-builder-2894/about)

</div>

<div class="flex justify-center">

<img src="./assets/skool.png"
     alt="f"
     class="rounded-xl shadow-lg border border-gray-600 w-145 hover:scale-110 transition-transform duration-300" />

</div>

---

# Context Engineering?

Les Agents IA pour interagir avec leurs environnement ont besoin de contextes sur celui-ci pour performer la tache donnée.

## **Cest quoi ?**

> ### **Context Engineering** : L'art de remplir la fenêtre de contexte d'un LLM avec juste les bonnes informations pour la prochaine étape/tâche.

<!--
You can have `style` tag in markdown to override the style for the current page.
Learn more: https://sli.dev/features/slide-scope-style
-->

<style>
h1 {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

<!--
Here is another comment.
-->

---

## Les différentes **sources de contexte** (Types)

<div grid="~ rows-2 gap-12 items-center" class="flex justify-center">

<div>

- [ ] **Instructions**
- [ ] **Connaissance externe (RAG,Base de données,...)**
- [ ] **Outil à disposition**
- [ ] **Feedback d'outils**

</div>

<div>
<img src="./assets/analogie_start.png"
     alt="analogie-start"
     class="rounded-xl shadow-lg border border-gray-600 w-96 hover:scale-130 transition-transform duration-300" />
</div>

</div>

---

# Pourquoi sur les Agents IA c'est très complexe?

<div grid="~ rows-2" class="flex justify-center">

1. Les **Agents IA** bouclent pour performer **des tâches plus complexes**
2. Les **Agents IA** utilisent souvent énormement de tokens

<div grid="~ ">

<img src="./assets/boucle_hard_agents.png"
     alt="t"
     class="rounded-xl shadow-lg border border-gray-600 w-96 hover:scale-130 transition-transform duration-300" />

<img src="./assets/harder_agents.png"
     alt="bonjour"
     class="rounded-xl shadow-lg border border-gray-600 w-96 hover:scale-130 transition-transform duration-300" />

</div>

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

<div grid="~ cols-2 gap-2">

<div>
<Tweet id="1937033436746903741" scale="0.70"/>
</div>

<div grid="~ rows-2 gap-0.5 items-start">

- #### **Context Poisoning** : Quand une hallucination rentre dans le contexte
- #### **Context Distraction** : Quand le contexte dépasse l'entrainement
- #### **Context Confusion** : Quand du contexte superflue influence la réponse
- #### **Context Clash** : Quand des parties du contexte sont en désaccord

> ### Context Engineering devient **critique** quand on **construit** des agents

</div>

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# Les stratégies de contrôle du contexte

<div grid="~ rows-4 items-start" class="justify-center h-full">

### 1. **Ecriture du contexte** : _**Sauvegarder** du contexte en dehors de **la fenetre** du LLM pour aider l'agent à faire la tâche._

### 2. **Selectionne le contexte** : _**Envoyer** dans la fenêtre de contexte du LLM_

### 3. **Compresser le contexte** : _Retenir uniquement les **tokens/informations** requises pour la tâche_

### 4. **Isoler le contexte** : _**Séparer** pour aider l'agent sur la tâche_

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# Ecriture de contexte

> **Sauvegarder** du contexte en dehors de **la fenetre** du LLM pour aider l'agent à faire la tâche.

Les humains résouent des tâches, en prenant des notes et en se rappelant de choses pour le futur liés à la tâche.

1. **Notes** ---> Bloc-notes (ScratchPad)
2. **Se Rappeler** ---> Mémoire

---

<div grid="~ cols-2 items-start" class="justify-center h-full">

<div>

## Bloc-notes (ScratchPad)

> Concept de de **persister** l'information pendant qu'un agent réalise une tâche

Exemples [Anthropic multi-agent researcher](youtube.com) :

> _L'agent LeadResearcher commence par penser à l'approche and **sauvegarde** le plan dans sa **Mémoire** pour persister le context, si la **fenêtre de contexte** dépasse 200k tokens il sera tronqué et il est important de retenir le plan._

Pour palier à ce problème on peut mettre un **objet d'état** (runtime) ou un fichier

</div>

<div>

## Mémoire

1. **Generative Agents** synthétisent la mémoire des collections des feedback des anciens agents
2. **ChaGPT**, **Cursor**, **Windsurf** générent automatiquement leurs mémoires.

![](./assets/writing-context.png)

</div>

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# Selection de contexte

> #### _**Envoyer** dans la fenêtre de contexte du LLM du contexte qui **aide l'agent à réaliser la tâche**_

<div grid="~ gap-8">

<div>

### [Scratchpads]()

- [ ] Appel d'outils
- [ ] L'état de conversations

</div>

<div>

### [Mémoires]()

- [ ] Few-shots examples ---> **(mémoire épisodique)**
- [ ] Instructions ---> **(mémoire procédural)**
- [ ] Faits ---> **(mémoire sémantique)**

</div>

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# Tableau des différents type de mémoires

- Instructions ---> **Rules files / CLAUDE.md (PRD)**
- Faits ---> **Collections**

<div>

| Type de mémoire | Ce qui sauvegarde | Exemple Humain                 | Exemple d'agent              |
| --------------- | ----------------- | ------------------------------ | ---------------------------- |
| **Semantique**  | Faits             | Choses qu'on apprend à l'école | Des faits sur l'utilisateur  |
| **Episodique**  | Experiences       | Choses que tu as faits         | Actions passèes de l'agent   |
| **Procédurale** | Instructions      | Instint ou la motricité        | Le Système prompt de l'agent |

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}

table {
  table-layout: fixed; /* ou fixed si tu veux des colonnes de largeur fixe */
  width: 100; /* rétrécit le tableau au contenu */
}

table th, table td {
  padding: 20px 25px; /* réduit l’espace intérieur */
}
</style>

---

# Exemples de cas concrets

## Outils

- RAG sur la description des outils : [Une recherche récente]() montre que ca améliore la qualité de la selection de l'outils 3x

## Connaissances

<div grid="~ cols-3">

- RAG
- **Code Agent** : Les plus grosses RAG apps (large-scale)

<Tweet id="1899630200780153274" scale="0.7"/>

<Tweet id="1899630246862966837" scale="0.7"/>

</div>

---

# Synthese/Compression du contexte

> **Retenir** uniquement les **tokens/informations** requises pour la tâche

## **Synthétiser**

<div grid="~ cols-2 gaps-5">

<div grid="~ rows-2">

- **Claude Code** auto compact : [Anthropic gèrer le coûts efficacements](https://docs.anthropic.com/en/docs/claude-code/costs)

- Sections de travails complète : [**Anthropic** et leurs multi-agents de recherches](https://www.anthropic.com/engineering/multi-agent-research-system)
- Passer le contexte aux sub-agents (linéaire) : [**Cognition**](https://cognition.ai/blog/dont-build-multi-agents)

<div>

## **Trimming**

- _Méthode heuristisque_ : Récuperer les derniers messages
- _Méthode Apprises_ : [**Provence** : Context pruning for
  retrieval-augmented generation](https://arxiv.org/pdf/2501.16214)

</div>
</div>

<img src="./assets/context_compression.png"
     alt="test"
     class="rounded-xl shadow-lg border border-gray-600 w-96" />

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# **Isolation** du contexte

> **Séparer** pour aider l'agent sur la tâche

[Models - Pydantic](https://docs.pydantic.dev/latest/concepts/models/)

<div class="flex justify-center">

[Multi-Agent de Recherche **d'Anthtopic**]()

</div>

<div class="flex justify-center">

<img src="./assets/isolation-context-multi-agents.png"
     alt="isolationcontexte"
     class="rounded-xl shadow-lg border border-gray-600 w-125 over:scale-110 transition-transform duration-300" />

</div>

---

# **Environnements**

- [**Hugging Open-Source DeepReasearch** - "Freeing" our search agents](https://huggingface.co/blog/open-deep-research)

<div class="justify-center flex">

<img src="./assets/isolation-context-code.png"
     alt="context code"
     class="rounded-xl shadow-lg border border-gray-600 w-full over:scale-110 transition-transform duration-300" />

</div>

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# **Contexte Engineering** et **Langgraph**

## Tracing + Evaluation

- [Get started with LangSmith](https://docs.smith.langchain.com/)

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# **Ecriture** dans Langgraph

## Scratchpad

- **Checkpointing** pour persister les états d'agents entre plusieurs sessions

## Mémoire

- **Long-term memory** pour persister le contexte entre plusieurs sessions

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# **Selection** dans Langgraph

### Outil

- [**Langgraph Big Tool**](https://github.com/langchain-ai/langgraph-bigtool)

### Connaissances

- [**Agentic RAG**](https://blog.langchain.com/agentic-rag-with-langgraph/)

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# **Compression** dans Langgraph

### Synthétisation + Trimming

- Synthése, trimming de l'historique de messages : [**Add memory**](https://docs.langchain.com/langgraph-platform/langgraph-basics/3-add-memory)
- La framework permet de gérer facilement et définir la logique dans chacun des noeuds (Low-Level)
  Post-procession tool execution : [**langchain-ai/open-deep-research**](https://github.com/langchain-ai/open_deep_research)
  [**utils.py**](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/utils.py)

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# **Isolation** dans Langgraph

## Multi-Agent

- [https://github.com/langchain-ai/**langgraph-supervisor-py**](https://github.com/langchain-ai/langgraph-supervisor-py)
- [https://github.com/langchain-ai/**langgraph-swarm-py**](https://github.com/langchain-ai/langgraph-swarm-py)
- [Langchain Conceptual Guide : **Multi Agent Architectures**](https://www.youtube.com/watch?v=4nZl32FwU-o&ab_channel=LangChain)
- [**Mutli-agent swarms** with Langgraph](https://www.youtube.com/watch?v=JeyDrn1dSUQ&pp=ygUbbXVsdGkgYWdlbnQgc3dhcm0gbGFuZ2dyYXBo0gcJCa0JAYcqIYzv)

## Environement

- [**E2B + Langgraph** : Github : https://github.com/e2b-dev](https://github.com/e2b-dev)
- [Pyodide : Langchain Sandbox : **Run Untrusted Python Safely for AI Agents**](https://www.youtube.com/watch?v=FBnER2sxt0w&t=10s&pp=ygUVcnUgbiB1bnRydXN0ZWQgcHl0aG9u)

## **State** (Etat)

- [**State object** : Overview Define graph schema](https://blog.langchain.com/langgraph/)

<style>
strong {
  background-color: #2B90B6;
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---
