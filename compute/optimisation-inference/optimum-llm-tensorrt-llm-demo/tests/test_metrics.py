"""
Tests pour le module inference_optim_llm.core.metrics.

Ces tests valident :
- Calcul des quantiles sur séries vides et séries à 1 élément
- Export/import JSONL et cohérence des données
- Fonctionnement du pattern singleton
- Calculs de percentiles (numpy vs pure Python)
"""

import json
import math
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from inference_optim_llm.core.metrics import MetricsCollector, _percentile


class TestPercentileFunction:
    """Tests de la fonction _percentile avec edge cases."""

    def test_empty_list(self):
        """Test avec liste vide."""
        result = _percentile([], 50)
        assert math.isnan(result)

    def test_single_value(self):
        """Test avec un seul élément."""
        result = _percentile([42.0], 50)
        assert result == 42.0
        
        # Test avec différents percentiles
        assert _percentile([42.0], 0) == 42.0
        assert _percentile([42.0], 100) == 42.0

    def test_simple_values(self):
        """Test avec des valeurs simples."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        # Tests de percentiles standards
        assert _percentile(values, 0) == 1.0
        assert _percentile(values, 50) == 3.0
        assert _percentile(values, 100) == 5.0

    def test_numpy_vs_pure_python(self):
        """Test de cohérence entre numpy et pure Python."""
        values = [1.5, 2.3, 3.7, 4.1, 5.9, 6.2, 7.8, 8.4, 9.1, 10.6]
        
        # Force l'utilisation de pure Python
        with patch('inference_optim_llm.core.metrics.HAS_NUMPY', False):
            pure_python_result = _percentile(values, 75)
        
        # Utilise numpy si disponible (sinon même résultat)
        numpy_result = _percentile(values, 75)
        
        # Les résultats doivent être très proches (tolérance pour différences d'implémentation)
        assert abs(pure_python_result - numpy_result) < 0.01

    def test_percentile_edge_cases(self):
        """Test des cas limites des percentiles."""
        values = [10.0, 20.0, 30.0]
        
        # 0% = min, 100% = max
        assert _percentile(values, 0) == 10.0
        assert _percentile(values, 100) == 30.0
        
        # 50% sur nombre impair d'éléments
        assert _percentile(values, 50) == 20.0


class TestMetricsCollector:
    """Tests du collecteur de métriques."""

    def setup_method(self):
        """Reset des singletons avant chaque test."""
        MetricsCollector.reset_all()

    def test_singleton_behavior(self):
        """Test du pattern singleton par nom."""
        mc1 = MetricsCollector("test")
        mc2 = MetricsCollector("test")
        mc3 = MetricsCollector("other")
        
        assert mc1 is mc2  # Même nom = même instance
        assert mc1 is not mc3  # Nom différent = instance différente
        assert mc1.name == "test"
        assert mc3.name == "other"

    def test_empty_collector(self):
        """Test d'un collecteur vide."""
        mc = MetricsCollector("empty")
        summary = mc.summary()
        
        assert summary["name"] == "empty"
        assert summary["count"] == 0
        assert len(summary) == 2  # Seulement name et count

    def test_add_single_sample(self):
        """Test d'ajout d'un échantillon simple."""
        mc = MetricsCollector("single")
        mc.add(
            prompt="Bonjour",
            latency=1.5,
            tokens=10,
            memory_mb=512.0,
            power_w=150.0
        )
        
        summary = mc.summary()
        assert summary["name"] == "single"
        assert summary["count"] == 1
        assert summary["latency_p50"] == 1.5
        assert summary["latency_mean"] == 1.5
        assert summary["tps_p50"] == 10 / 1.5  # tokens per second
        assert summary["memory_max"] == 512.0
        assert summary["power_mean"] == 150.0

    def test_multiple_samples_statistics(self):
        """Test avec plusieurs échantillons et calculs statistiques."""
        mc = MetricsCollector("multiple")
        
        # Ajouter des échantillons avec des valeurs connues
        samples = [
            (1.0, 10),  # latency, tokens
            (2.0, 20),
            (3.0, 30),
            (4.0, 40),
            (5.0, 50),
        ]
        
        for latency, tokens in samples:
            mc.add(
                prompt=f"Prompt {latency}",
                latency=latency,
                tokens=tokens,
                memory_mb=100.0 + latency * 10,  # Mémoire croissante
                power_w=200.0,  # Puissance constante
            )
        
        summary = mc.summary()
        
        # Vérifications basiques
        assert summary["count"] == 5
        assert summary["latency_p50"] == 3.0  # Médiane de [1,2,3,4,5]
        assert summary["latency_mean"] == 3.0  # Moyenne de [1,2,3,4,5]
        assert summary["latency_max"] == 5.0
        
        # Débit (tokens/seconde)
        expected_tps = [10/1, 20/2, 30/3, 40/4, 50/5]  # [10, 10, 10, 10, 10]
        assert summary["tps_p50"] == 10.0
        assert summary["tps_mean"] == 10.0
        
        # Mémoire max (doit être la plus élevée)
        assert summary["memory_max"] == 150.0  # 100 + 5*10
        
        # Puissance moyenne
        assert summary["power_mean"] == 200.0

    def test_nan_handling(self):
        """Test de la gestion des valeurs NaN."""
        mc = MetricsCollector("nan_test")
        
        # Ajouter des échantillons avec des NaN
        mc.add("prompt1", 1.0, 10, memory_mb=math.nan, power_w=150.0)
        mc.add("prompt2", 2.0, 20, memory_mb=512.0, power_w=math.nan)
        mc.add("prompt3", 3.0, 30)  # memory_mb et power_w par défaut = NaN
        
        summary = mc.summary()
        
        # Les calculs doivent ignorer les NaN
        assert summary["count"] == 3
        assert summary["latency_mean"] == 2.0  # (1+2+3)/3
        assert summary["memory_max"] == 512.0  # Seule valeur non-NaN
        assert summary["power_mean"] == 150.0  # Seule valeur non-NaN

    def test_jsonl_export_import(self):
        """Test d'export/import JSONL et cohérence des données."""
        mc = MetricsCollector("jsonl_test")
        
        # Données de test
        test_data = [
            ("Bonjour", 1.2, 15, 256.0, 120.0),
            ("Comment ça va ?", 2.1, 25, 384.0, 135.0),
            ("Au revoir", 0.8, 8, math.nan, math.nan),
        ]
        
        for prompt, latency, tokens, memory, power in test_data:
            mc.add(prompt, latency, tokens, memory, power)
        
        # Export vers fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            result_path = mc.to_json(tmp_path)
            assert result_path == tmp_path.resolve()
            assert tmp_path.exists()
            
            # Lecture et vérification du contenu
            lines = tmp_path.read_text(encoding='utf-8').strip().split('\n')
            assert len(lines) == 3
            
            # Vérification de chaque ligne
            for i, line in enumerate(lines):
                data = json.loads(line)
                original = test_data[i]
                
                assert data["prompt"] == original[0]
                assert abs(data["latency"] - original[1]) < 1e-6
                assert data["tokens"] == original[2]
                assert data["tps"] == original[2] / original[1]  # Calcul automatique
                
                # Gestion des NaN
                if math.isnan(original[3]):
                    assert math.isnan(data["memory_mb"])
                else:
                    assert abs(data["memory_mb"] - original[3]) < 1e-6
                    
                if math.isnan(original[4]):
                    assert math.isnan(data["power_w"])
                else:
                    assert abs(data["power_w"] - original[4]) < 1e-6
                    
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_dump_all_functionality(self):
        """Test de la fonction dump_all avec plusieurs collecteurs."""
        # Créer plusieurs collecteurs
        mc1 = MetricsCollector("variant1")
        mc1.add("test1", 1.0, 10)
        
        mc2 = MetricsCollector("variant2")
        mc2.add("test2", 2.0, 20)
        mc2.add("test3", 3.0, 30)
        
        # Test dump_all
        all_data = MetricsCollector.dump_all()
        
        assert len(all_data) == 2
        assert "variant1" in all_data
        assert "variant2" in all_data
        
        assert all_data["variant1"]["count"] == 1
        assert all_data["variant2"]["count"] == 2
        assert all_data["variant1"]["latency_mean"] == 1.0
        assert all_data["variant2"]["latency_mean"] == 2.5  # (2+3)/2

    def test_collector_reinitialization(self):
        """Test qu'un collecteur existant n'est pas réinitialisé."""
        mc1 = MetricsCollector("persistent")
        mc1.add("first", 1.0, 10)
        
        # Récupération du même collecteur (ne doit pas effacer les données)
        mc2 = MetricsCollector("persistent")
        assert mc1 is mc2
        assert mc2.summary()["count"] == 1
        
        # Ajout de nouvelles données
        mc2.add("second", 2.0, 20)
        assert mc1.summary()["count"] == 2  # mc1 et mc2 sont la même instance


if __name__ == "__main__":
    # Exécution simple des tests pour développement
    pytest.main([__file__, "-v"])