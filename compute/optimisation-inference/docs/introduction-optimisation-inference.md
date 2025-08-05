# Introduction à l'optimisation de l'Inférence

L’inférence représente aujourd’hui près de **90 % de la facture GPU** d’un service IA : par exemple, un cluster de 8 H100 loué à l’heure dans le cloud peut dépasser **276 k $ par an**, soit plus du double d’un déploiement on-prem équivalent.:contentReference[oaicite:3]{index=3} Réduire ce poste n’est plus une option, c’est un impératif économique pour toute offre fondée sur les grands modèles de langage.

**Inference-Optim-LLM** répond à cet enjeu en fournissant un banc d’essai reproductible qui compare, à matériel constant, une implémentation **PyTorch baseline** à son équivalent **TensorRT-LLM** optimisé. Le dépôt met à disposition :

- **Images Docker verrouillées** pour garantir la reproductibilité ;
- **Scripts de conversion et de benchmark** (`build/`, `cli.py`) couvrant quantization FP8/INT8, batching dynamique, paged-attention et speculative decoding ;
- **Collecte temps réel des métriques** (latence, TPS, VRAM, puissance) via NVML ;
- **Post-processing automatique** générant des rapports `.jsonl` et `.md`.

Selon l’étude de référence, la combinaison de ces techniques **divise par trois le coût d’inférence** sur Llama-2 70B et libère jusqu’à **48 k € de marge annuelle** pour un budget GPU de 10 k €/mois.:contentReference[oaicite:4]{index=4} Ce dépôt traduit ces gains théoriques en **résultats mesurables**, prêts à être reproduits sur tout GPU moderne (RTX 4070, A100, H100).

Développé par **Quentin Gavila** et l’équipe **Growthsystemes**, Inference-Optim-LLM constitue la base opérationnelle idéale pour évaluer, optimiser et industrialiser vos workloads LLM.

