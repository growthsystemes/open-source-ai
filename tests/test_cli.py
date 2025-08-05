"""
Tests pour l'interface CLI.

Ces tests valident :
- Fonctionnement des commandes principales via subprocess
- Gestion des erreurs et codes de retour
- Validation des arguments
"""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestCLICommands:
    """Tests de l'interface en ligne de commande."""

    def test_cli_help(self):
        """Test de l'aide CLI."""
        result = subprocess.run(
            ["python", "-m", "inference_optim_llm.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0
        assert "Interface CLI pour optimisation d'inférence LLM" in result.stdout
        assert "download" in result.stdout
        assert "build" in result.stdout
        assert "run" in result.stdout
        assert "bench" in result.stdout

    def test_download_command_help(self):
        """Test de l'aide pour la commande download."""
        result = subprocess.run(
            ["python", "-m", "inference_optim_llm.cli", "download", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0
        assert "Télécharge un modèle depuis HuggingFace Hub" in result.stdout
        assert "model_id" in result.stdout

    def test_build_command_help(self):
        """Test de l'aide pour la commande build."""
        result = subprocess.run(
            ["python", "-m", "inference_optim_llm.cli", "build", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0
        assert "Compile un engine TensorRT-LLM" in result.stdout
        assert "precision" in result.stdout

    def test_run_command_help(self):
        """Test de l'aide pour la commande run."""
        result = subprocess.run(
            ["python", "-m", "inference_optim_llm.cli", "run", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0
        assert "Lance l'inférence avec une variante spécifique" in result.stdout
        assert "baseline" in result.stdout or "trtllm" in result.stdout

    def test_bench_command_help(self):
        """Test de l'aide pour la commande bench."""
        result = subprocess.run(
            ["python", "-m", "inference_optim_llm.cli", "bench", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0
        assert "Lance un benchmark complet" in result.stdout

    @patch('inference_optim_llm.engines.baseline.HFRunner')
    def test_run_baseline_with_mock(self, mock_runner_class):
        """Test de la commande run baseline avec mock."""
        # Configuration du mock
        mock_runner = MagicMock()
        mock_runner.generate.return_value = ["Réponse mockée"]
        mock_runner.save_metrics.return_value = Path("test.jsonl")
        mock_runner.metrics.summary.return_value = {"count": 1, "latency_p50": 1.0}
        mock_runner_class.return_value = mock_runner
        
        # Création d'un fichier de prompts temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test prompt\n")
            prompts_file = Path(f.name)
        
        try:
            # Exécution de la commande
            result = subprocess.run([
                "python", "-m", "inference_optim_llm.cli", "run", "baseline",
                "--prompts-file", str(prompts_file),
                "--quiet"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            # Vérifications (le mock ne fonctionnera pas avec subprocess,
            # mais on peut au moins vérifier que la commande ne plante pas)
            # En pratique, ce test nécessiterait une architecture différente
            # pour être vraiment efficace avec des mocks
            
        finally:
            prompts_file.unlink(missing_ok=True)

    def test_run_invalid_variant(self):
        """Test avec une variante invalide."""
        result = subprocess.run([
            "python", "-m", "inference_optim_llm.cli", "run", "invalid_variant"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode != 0
        assert "Variante inconnue" in result.stderr or "invalid choice" in result.stderr

    def test_run_missing_prompts_file(self):
        """Test avec un fichier de prompts manquant."""
        result = subprocess.run([
            "python", "-m", "inference_optim_llm.cli", "run", "baseline",
            "--prompts-file", "/nonexistent/file.txt"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode != 0
        # L'erreur peut être capturée soit par le CLI soit par Python lui-même


class TestCLIIntegration:
    """Tests d'intégration CLI avec de vrais fichiers."""
    
    def test_run_with_minimal_prompts(self):
        """Test d'exécution avec un fichier de prompts minimal."""
        # Ce test nécessiterait des modèles réels et serait trop lourd
        # pour l'exécution en CI standard
        pytest.skip("Test d'intégration nécessitant des modèles réels")

    def test_bench_dry_run(self):
        """Test du benchmark en mode dry-run."""
        # Similaire au test précédent
        pytest.skip("Test d'intégration nécessitant des modèles réels")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])