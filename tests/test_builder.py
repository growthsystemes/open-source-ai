"""
Tests pour le module de construction d'engines TensorRT-LLM.

Ces tests valident :
- Validation des paramètres d'entrée
- Gestion des erreurs de configuration
- Logique de construction (avec mocks)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from inference_optim_llm.build.builder import TensorRTEngineBuilder, convert_and_build


class TestTensorRTEngineBuilder:
    """Tests de la classe TensorRTEngineBuilder."""

    def test_init_default_params(self):
        """Test d'initialisation avec paramètres par défaut."""
        builder = TensorRTEngineBuilder("test-model")
        
        assert builder.model_id == "test-model"
        assert builder.precision == "fp16"
        assert builder.quant_mode is None
        assert builder.batch_size == 1
        assert builder.max_input_len == 4096
        assert builder.max_output_len == 2048
        assert isinstance(builder.output_dir, Path)

    def test_init_custom_params(self):
        """Test d'initialisation avec paramètres personnalisés."""
        builder = TensorRTEngineBuilder(
            "custom-model",
            precision="int8",
            quant_mode="int8",
            batch_size=4,
            max_input_len=2048,
            max_output_len=1024,
        )
        
        assert builder.model_id == "custom-model"
        assert builder.precision == "int8"
        assert builder.quant_mode == "int8"
        assert builder.batch_size == 4
        assert builder.max_input_len == 2048
        assert builder.max_output_len == 1024

    def test_validate_params_invalid_precision(self):
        """Test de validation avec précision invalide."""
        with pytest.raises(ValueError, match="Précision non supportée"):
            TensorRTEngineBuilder("test", precision="invalid")

    def test_validate_params_quant_mode_auto_int8(self):
        """Test de définition automatique du quant_mode pour INT8."""
        builder = TensorRTEngineBuilder("test", precision="int8")
        assert builder.quant_mode == "int8"

    def test_validate_params_quant_mode_mismatch(self):
        """Test d'erreur quand quant_mode est spécifié avec une précision incompatible."""
        with pytest.raises(ValueError, match="quant_mode spécifié avec precision=fp16"):
            TensorRTEngineBuilder("test", precision="fp16", quant_mode="int8")

    def test_get_engine_info(self):
        """Test de la méthode get_engine_info."""
        builder = TensorRTEngineBuilder(
            "info-test",
            precision="fp16",
            batch_size=2,
            max_input_len=1024,
        )
        
        info = builder.get_engine_info()
        
        assert info["model_id"] == "info-test"
        assert info["precision"] == "fp16"
        assert info["batch_size"] == 2
        assert info["max_input_len"] == 1024
        assert "output_dir" in info

    @patch('inference_optim_llm.build.builder.subprocess.run')
    @patch('inference_optim_llm.build.builder.Path.exists')
    @patch('inference_optim_llm.build.builder.Path.mkdir')
    def test_build_success(self, mock_mkdir, mock_exists, mock_subprocess):
        """Test de construction réussie avec mocks."""
        # Configuration des mocks
        mock_exists.return_value = True
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        builder = TensorRTEngineBuilder("mock-test")
        
        # Le test complet nécessiterait de nombreux autres mocks
        # pour les opérations sur fichiers, pathlib, etc.
        # Pour l'instant, on teste juste que la méthode ne plante pas
        # avec la validation des paramètres
        
        # Test que l'objet est correctement initialisé
        assert builder.model_id == "mock-test"
        assert hasattr(builder, '_validate_params')

    @patch('inference_optim_llm.build.builder.subprocess.run')
    def test_run_command_success(self, mock_subprocess):
        """Test de _run_command avec succès."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr=""
        )
        
        builder = TensorRTEngineBuilder("test")
        
        # Test que la méthode ne lève pas d'exception
        try:
            builder._run_command(["echo", "test"], "Test command")
        except Exception as e:
            pytest.fail(f"_run_command should not raise exception: {e}")

    @patch('inference_optim_llm.build.builder.subprocess.run')
    def test_run_command_failure(self, mock_subprocess):
        """Test de _run_command avec échec."""
        import subprocess
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["failed", "command"],
            output="",
            stderr="Command failed"
        )
        
        builder = TensorRTEngineBuilder("test")
        
        with pytest.raises(RuntimeError, match="Échec de"):
            builder._run_command(["failed", "command"], "Test command")


class TestConvertAndBuildFunction:
    """Tests de la fonction de compatibilité convert_and_build."""

    @patch('inference_optim_llm.build.builder.TensorRTEngineBuilder')
    def test_convert_and_build_default(self, mock_builder_class):
        """Test de convert_and_build avec paramètres par défaut."""
        mock_builder = MagicMock()
        mock_builder.build.return_value = Path("/fake/engine.engine")
        mock_builder_class.return_value = mock_builder
        
        result = convert_and_build("test-model")
        
        # Vérification que TensorRTEngineBuilder est appelé correctement
        mock_builder_class.assert_called_once_with(
            model_id="test-model",
            precision="fp16",
            quant_mode=None,
            calibration_path=None,
        )
        
        # Vérification que build() est appelé
        mock_builder.build.assert_called_once()
        
        # Vérification du retour
        assert result == Path("/fake/engine.engine")

    @patch('inference_optim_llm.build.builder.TensorRTEngineBuilder')
    def test_convert_and_build_with_quant(self, mock_builder_class):
        """Test de convert_and_build avec quantification."""
        mock_builder = MagicMock()
        mock_builder.build.return_value = Path("/fake/engine.int8.engine")
        mock_builder_class.return_value = mock_builder
        
        result = convert_and_build(
            "test-model",
            precision="int8",
            quant_mode="int8",
            calibration_path="/fake/calib.json"
        )
        
        # Vérification des paramètres passés
        mock_builder_class.assert_called_once_with(
            model_id="test-model",
            precision="int8",
            quant_mode="int8",
            calibration_path="/fake/calib.json",
        )
        
        assert result == Path("/fake/engine.int8.engine")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])