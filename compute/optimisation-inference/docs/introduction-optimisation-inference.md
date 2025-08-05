# Introduction à l'optimisation de l'Inférence

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-GPU%20Optimized-green?logo=nvidia)](https://nvidia.com)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python)](https://python.org)

<img width="1536" height="1024" alt="image (8)" src="https://github.com/user-attachments/assets/0946ed65-1e46-457f-9321-c89887d3bec4" />

## Table des matières complète  
### (Étude « Optimisation de l’Inférence » + Projet *Inference‑Optim‑LLM*)

### **Partie 1 – Étude “Optimisation de l’Inférence LLM”** :contentReference[oaicite:2]{index=2}
1.  [Résumé exécutif](#1-résumé-exécutif)  
2.  [Contexte & enjeux](#2-contexte--enjeux)  
3.  [Fondamentaux de l’inférence](#3-fondamentaux-de-linférence)  
    3.1 [Comprendre l’inférence](#31-comprendre-linférence)  
    3.2 [Tokenisation & représentations](#32-tokenisation--représentations)  
    3.3 [Attention head & calcul matriciel](#33-attention-head--calcul-matriciel)  
    3.4 [Rôle du KV‑cache](#34-rôle-du-kv-cache)  
    3.5 [Impact des prompts sur la mémoire](#35-impact-des-prompts-sur-la-mémoire)  
4.  [Leviers d’optimisation](#4-leviers-doptimisation)  
    4.1 [Quantization FP8 / INT8](#41-quantization-fp8--int8)  
    4.2 [In‑flight batching](#42-in‑flight-batching)  
    4.3 [Paged KV‑cache](#43-paged-kv-cache)  
    4.4 [Speculative decoding](#44-speculative-decoding)  
5.  [Architecture de référence](#5-architecture-de-référence)  
6.  [Benchmark & résultats](#6-benchmark--résultats)  
7.  [Analyse économique](#7-analyse-économique)  
8.  [Feuille de route d’industrialisation](#8-feuille-de-route-dindustrialisation)  
9.  [Conclusion](#9-conclusion)  
10. [Références](#10-références) 


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

