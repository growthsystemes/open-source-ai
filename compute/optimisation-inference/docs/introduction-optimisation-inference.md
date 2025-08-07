# Introduction à l'optimisation de l'Inférence (TensorRT-LLM)

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-GPU%20Optimized-green?logo=nvidia)](https://nvidia.com)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python)](https://python.org)

<img width="1536" height="1024" alt="image (8)" src="https://github.com/user-attachments/assets/0946ed65-1e46-457f-9321-c89887d3bec4" />

## Table des matières complète  
### (Étude « Optimisation de l’Inférence » + Projet *Inference‑Optim‑LLM*)

### **Partie 1 – Étude “Optimisation de l’Inférence LLM”** : 
1.  [Résumé exécutif](#1-résumé-exécutif)    
2.  [Fondamentaux de l’inférence](#3-fondamentaux-de-linférence)  
    3.1 [Comprendre l’inférence](#31-comprendre-linférence)  
    3.2 [Tokenisation & représentations](#32-tokenisation--représentations)  
    3.3 [Attention head & calcul matriciel](#33-attention-head--calcul-matriciel)  
    3.4 [Rôle du KV‑cache](#34-rôle-du-kv-cache)  
    3.5 [Impact des prompts sur la mémoire](#35-impact-des-prompts-sur-la-mémoire)  
3.  [Leviers d’optimisation](#4-leviers-doptimisation)  
    4.1 [Quantization FP8 / INT8](#41-quantization-fp8--int8)  
    4.2 [In‑flight batching](#42-in‑flight-batching)  
    4.3 [Paged KV‑cache](#43-paged-kv-cache)  
    4.4 [Speculative decoding](#44-speculative-decoding)  
4.  [Architecture de référence](#5-architecture-de-référence)  
5.  [Benchmark & résultats](#6-benchmark--résultats)  
6.  [Analyse économique](#7-analyse-économique)  
7.  [Feuille de route d’industrialisation](#8-feuille-de-route-dindustrialisation)  
8.  [Conclusion](#9-conclusion)  
9. [Références](#10-références) 


## 1. Résumé exécutif<a id="1-résumé-exécutif"></a>

### Pourquoi l’optimisation d’inférence est devenue critique  

**Contexte :**
- **Poids économique** : jusqu’à **90 % de la facture IA** provient de l’inférence. Dans l’étude interne, un cluster de **8 × H100** coûte **276 k $ / an** en *on‑demand* AWS, soit **+128 %** vs un achat on‑prem équivalent.:contentReference[oaicite:7]{index=7}  
- **Tension sur la mémoire** : la mémoire représente près de **40 % du coût matériel** d’un serveur IA ; elle devient le principal poste de dépense quand la taille des modèles augmente.:contentReference[oaicite:1]{index=1}  
- **Pression sur les prix GPU** : pour rester compétitif face aux futurs GB200 NVL72, le tarif horaire d’un H100 devrait tomber à ~**0,98 $/h** selon SemiAnalysis.:contentReference[oaicite:2]{index=2}  

### Levier : l’optimisation logicielle  

Paradigme émergent : Software-Defined AI Infrastructure
Face à la commoditisation progressive du matériel, la différenciation se déplace vers la couche logicielle. Les entreprises qui maîtrisent l'optimisation d'inférence bénéficient d'un effet de levier multiplicateur :

- Réduction directe des coûts : -30 à -70% sur la facture cloud
- Amélioration des SLA : latence réduite de 40%+
- Scalabilité : +50% de workloads sur la même infrastructure
  

> Les leviers logiciels (quantization FP8/INT8, *in‑flight batching*, *paged KV cache*, *speculative decoding*) font baisser la facture cloud de **30 → 70 %** ou augmentent de **50 %** la charge utile sur la même machine.:contentReference[oaicite:8]{index=8}  

NVIDIA formalise ces techniques dans TensorRT‑LLM. La dernière version double le throughput et réduit la latence de plus de 40 % grâce à ses kernels dédiés et son batching dynamique.

<img width="1770" height="980" alt="leviers-optimisation-inference" src="https://github.com/user-attachments/assets/8c2e25ef-043e-4c72-8bbe-aa17b7539f91" />


### Preuve par la pratique : **tensor-rt-llm** 

Le dépôt [https://github.com/growthsystemes/open-source-ai](https://github.com/growthsystemes/open-source-ai/tree/main/compute/optimisation-inference/tensor-rt-llm) fournit un banc d’essai Dockerisé qui compare, à matériel constant, une implémentation PyTorch baseline à son équivalent TensorRT‑LLM optimisé.

### benchmarks : TinyLlama‑1.1B Chat
Pour évaluer l’impact de TensorRT‑LLM sur un modèle compact, nous avons exécuté la même méthodologie sur TinyLlama‑1.1B Chat. Les tests ont été automatisés via un pipeline Docker sans compilation locale.

| Métrique (RTX 4070) | PyTorch | TensorRT-LLM | Gain |
|---------------------|---------|--------------|------|
| Latence moyenne | 627,9 ms | 260,3 ms | 2,41× plus rapide |
| Débit moyen | 864,4 tok/s | 2 723,2 tok/s | 3,15× plus rapide |
| Mémoire GPU | 2,60 GB | 2,61 GB | ≈ identique |

Ces mesures, obtenues sur des prompts d’environ 100 tokens et une génération de 200 tokens, démontrent que TensorRT‑LLM reste pertinent même sur des modèles sub‑2B paramètres. Les gains croissent avec la longueur des séquences et la taille du modèle.


### Impact business  

- **Économie directe** : sur un budget GPU de **10 k €/mois**, un gain moyen de **40 %** libère **≈ 48 k € de marge annuelle**.:contentReference[oaicite:9]{index=9}  
- **Décision stratégique** : lorsque les coûts d’hébergement convergent, la **différenciation se joue sur l’efficacité logicielle** et non plus sur l’accès au matériel.  

### Feuille de route recommandée  

1. **Auditer les workloads** : profiler prompts, batch, latence cible.  
2. **Prototyper avec *Inference‑Optim‑LLM*** : valider les gains FP8, batching, paged‑attention sur un GPU local.  
3. **Industrialiser TensorRT‑LLM** : intégrer la compilation, le *serving* et la télémétrie dans CI/CD.  
4. **Optimisation continue** : introduire le *speculative decoding* et ajuster dynamiquement le batch en fonction du trafic.  

> **En résumé**, l’optimisation d’inférence est le levier n° 1 pour abaisser le *Total Cost of Ownership* des LLM ; le duo *Étude + Projet de démo* fournit à la fois le **cadre analytique** et le **kit opérationnel** pour passer de la théorie aux économies mesurables.


L’inférence représente aujourd’hui près de **90 % de la facture GPU** d’un service IA : par exemple, un cluster de 8 H100 loué à l’heure dans le cloud peut dépasser **276 k $ par an**, soit plus du double d’un déploiement on-prem équivalent.:contentReference[oaicite:3]{index=3} Réduire ce poste n’est plus une option, c’est un impératif économique pour toute offre fondée sur les grands modèles de langage.

**Inference-Optim-LLM** répond à cet enjeu en fournissant un banc d’essai reproductible qui compare, à matériel constant, une implémentation **PyTorch baseline** à son équivalent **TensorRT-LLM** optimisé. Le dépôt met à disposition :

- **Images Docker verrouillées** pour garantir la reproductibilité ;
- **Scripts de conversion et de benchmark** (`build/`, `cli.py`) couvrant quantization FP8/INT8, batching dynamique, paged-attention et speculative decoding ;
- **Collecte temps réel des métriques** (latence, TPS, VRAM, puissance) via NVML ;
- **Post-processing automatique** générant des rapports `.jsonl` et `.md`.

Selon l’étude de référence, la combinaison de ces techniques **divise par trois le coût d’inférence** sur Llama-2 70B et libère jusqu’à **48 k € de marge annuelle** pour un budget GPU de 10 k €/mois.:contentReference[oaicite:4]{index=4} Ce dépôt traduit ces gains théoriques en **résultats mesurables**, prêts à être reproduits sur tout GPU moderne (RTX 4070, A100, H100).

Développé par **Quentin Gavila** et l’équipe **Growthsystemes**, Inference-Optim-LLM constitue la base opérationnelle idéale pour évaluer, optimiser et industrialiser vos workloads LLM.

## Comment les LLM utilise l'attention_head pour processer les tokens 
![Graphiques-Inferences---Frame-5](https://github.com/user-attachments/assets/5def98ca-90d5-4fcf-b437-dd28e504182c)

### Comment intervient le KV-cache
![Graphiques-Inferences---Frame-7](https://github.com/user-attachments/assets/190474cf-d9c8-44f0-b807-120b520772a1)

