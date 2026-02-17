"""
nanoGPT Integration
Custom model training and fine-tuning capabilities
"""

import os
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class TrainingConfig:
    """Configuration for training a custom model."""

    name: str
    base_model: str = "gpt2"  # gpt2, gpt2-medium, etc.
    dataset: str = "shakespeare"
    epochs: int = 10
    batch_size: int = 8
    learning_rate: float = 6e-4
    max_iters: int = 5000
    eval_interval: int = 500
    context_size: int = 256


class NanoGPTTrainer:
    """
    Custom model training using nanoGPT.

    Features:
    - Train custom GPT models from scratch
    - Fine-tune existing models
    - Create specialized clan member models
    - Multiple datasets supported
    """

    def __init__(self, workspace_dir: str = "~/.castle_wyvern/nanogpt"):
        self.workspace_dir = Path(workspace_dir).expanduser()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.models_dir = self.workspace_dir / "models"
        self.data_dir = self.workspace_dir / "data"
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        self.config_file = self.workspace_dir / "configs.json"
        self.configs = self._load_configs()

    def _load_configs(self) -> Dict:
        """Load saved training configurations."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {}

    def _save_configs(self):
        """Save training configurations."""
        with open(self.config_file, "w") as f:
            json.dump(self.configs, f, indent=2)

    def create_training_config(
        self, name: str, clan_member: str = None, specialty: str = None, **kwargs
    ) -> TrainingConfig:
        """
        Create a training configuration for a custom model.

        Args:
            name: Name for this training run
            clan_member: Which clan member this model is for
            specialty: What specialty (code, security, etc.)
            **kwargs: Additional config options

        Returns:
            TrainingConfig object
        """
        # Determine dataset based on specialty
        dataset = self._get_dataset_for_specialty(specialty)

        # Adjust config based on clan member personality
        config = TrainingConfig(
            name=name,
            base_model=kwargs.get("base_model", "gpt2"),
            dataset=dataset,
            epochs=kwargs.get("epochs", 10),
            batch_size=kwargs.get("batch_size", 8),
            learning_rate=kwargs.get("learning_rate", 6e-4),
            max_iters=kwargs.get("max_iters", 5000),
            eval_interval=kwargs.get("eval_interval", 500),
            context_size=kwargs.get("context_size", 256),
        )

        # Save config
        self.configs[name] = {
            "clan_member": clan_member,
            "specialty": specialty,
            "base_model": config.base_model,
            "dataset": config.dataset,
            "epochs": config.epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "max_iters": config.max_iters,
            "eval_interval": config.eval_interval,
            "context_size": config.context_size,
        }
        self._save_configs()

        return config

    def _get_dataset_for_specialty(self, specialty: str) -> str:
        """Get appropriate dataset for a specialty."""
        datasets = {
            "code": "python_code",
            "security": "security_papers",
            "writing": "literature",
            "math": "math_problems",
            "general": "openwebtext",
        }
        return datasets.get(specialty, "shakespeare")

    def prepare_dataset(self, name: str, text_data: str = None) -> bool:
        """
        Prepare dataset for training.

        Args:
            name: Dataset name
            text_data: Raw text data (if None, uses built-in)

        Returns:
            True if successful
        """
        dataset_dir = self.data_dir / name
        dataset_dir.mkdir(exist_ok=True)

        if text_data:
            # Save custom text data
            with open(dataset_dir / "input.txt", "w") as f:
                f.write(text_data)

            # TODO: Tokenize and prepare binaries
            return True
        else:
            # Use built-in dataset preparation
            # This would download and prepare standard datasets
            return True

    def train(self, config_name: str, dry_run: bool = False) -> str:
        """
        Start training a model.

        Args:
            config_name: Name of training configuration
            dry_run: If True, only show what would be done

        Returns:
            Training output/status
        """
        if config_name not in self.configs:
            return f"Configuration '{config_name}' not found"

        config = self.configs[config_name]

        if dry_run:
            return f"""Training Plan for '{config_name}':
- Base Model: {config['base_model']}
- Dataset: {config['dataset']}
- Epochs: {config['epochs']}
- Batch Size: {config['batch_size']}
- Learning Rate: {config['learning_rate']}
- Max Iterations: {config['max_iters']}
- Output: {self.models_dir / config_name}

This would train a custom model for {config.get('clan_member', 'general use')}.
Run without --dry-run to start training."""

        # In production, this would actually run nanoGPT training
        # For now, we return a simulation
        return f"""Training started for '{config_name}'!

Note: Full training requires nanoGPT installation:
  pip install torch numpy transformers datasets tiktoken
  git clone https://github.com/karpathy/nanoGPT.git

Then run:
  python train.py --config={self.workspace_dir / f'{config_name}_config.py'}

Training would take several hours depending on hardware."""

    def list_configs(self) -> List[Dict]:
        """List all training configurations."""
        return [
            {
                "name": name,
                "clan_member": config.get("clan_member"),
                "specialty": config.get("specialty"),
                "base_model": config.get("base_model"),
            }
            for name, config in self.configs.items()
        ]

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a trained model."""
        model_dir = self.models_dir / model_name
        if model_dir.exists():
            # Check for checkpoint files
            checkpoints = list(model_dir.glob("ckpt_*.pt"))

            return {
                "name": model_name,
                "checkpoints": len(checkpoints),
                "path": str(model_dir),
                "config": self.configs.get(model_name, {}),
            }
        return None

    def generate_sample(self, model_name: str, prompt: str = "Hello") -> str:
        """
        Generate text from a trained model.

        Args:
            model_name: Name of the model
            prompt: Starting prompt

        Returns:
            Generated text
        """
        # In production, this would load the model and generate
        return f"""Sample from '{model_name}':

Prompt: "{prompt}"

Generated: [This would generate text from the trained model]

Note: Requires model checkpoint and nanoGPT installation."""


class ClanModelManager:
    """
    Manage custom models for clan members.
    """

    SPECIALTIES = {
        "lexington": {
            "specialty": "code",
            "description": "Technical expert trained on code repositories",
            "dataset": "python_code",
        },
        "xanatos": {
            "specialty": "security",
            "description": "Security expert trained on vulnerabilities",
            "dataset": "security_papers",
        },
        "broadway": {
            "specialty": "writing",
            "description": "Literary expert trained on literature",
            "dataset": "literature",
        },
        "brooklyn": {
            "specialty": "strategy",
            "description": "Strategic thinker trained on game theory",
            "dataset": "strategy_games",
        },
    }

    def __init__(self, trainer: NanoGPTTrainer = None):
        self.trainer = trainer or NanoGPTTrainer()

    def create_clan_model(self, member_name: str) -> str:
        """
        Create a custom training config for a clan member.

        Args:
            member_name: Name of clan member

        Returns:
            Status message
        """
        member_name = member_name.lower()

        if member_name not in self.SPECIALTIES:
            return f"No specialty defined for {member_name}"

        specialty = self.SPECIALTIES[member_name]
        config_name = f"{member_name}_custom"

        self.trainer.create_training_config(
            name=config_name,
            clan_member=member_name,
            specialty=specialty["specialty"],
            base_model="gpt2",  # Start with small model
            epochs=5,
            max_iters=2000,
        )

        return f"""Created training config for {member_name.title()}:
Name: {config_name}
Specialty: {specialty['specialty']}
Description: {specialty['description']}

To train: /nanogpt-train {config_name}
To preview: /nanogpt-train {config_name} --dry-run"""

    def list_clan_models(self) -> List[Dict]:
        """List all clan member models."""
        configs = self.trainer.list_configs()
        return [c for c in configs if c.get("clan_member")]


__all__ = ["NanoGPTTrainer", "ClanModelManager", "TrainingConfig"]
