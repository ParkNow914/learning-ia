"""
Data augmentation para Knowledge Tracing.

Técnicas para aumentar diversidade de dados de treino:
- Window sliding
- Sequence perturbation
- Synthetic student generation
"""

import random
from typing import Dict, List
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataAugmentor:
    """Augmentador de dados para KT."""

    def __init__(self, seed: int = 42):
        """
        Inicializa augmentador.

        Args:
            seed: Seed para reproducibilidade
        """
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def sliding_window(self, sequence: List[Dict], window_size: int = 50, stride: int = 25) -> List[List[Dict]]:
        """
        Cria múltiplas subsequências usando sliding window.

        Args:
            sequence: Sequência original
            window_size: Tamanho da janela
            stride: Passo da janela

        Returns:
            Lista de subsequências
        """
        if len(sequence) < window_size:
            return [sequence]

        subsequences = []
        for i in range(0, len(sequence) - window_size + 1, stride):
            subsequence = sequence[i : i + window_size]
            subsequences.append(subsequence)

        return subsequences

    def perturb_sequence(self, sequence: List[Dict], flip_prob: float = 0.05) -> List[Dict]:
        """
        Perturba sequência com probabilidade de flip em respostas.

        Args:
            sequence: Sequência original
            flip_prob: Probabilidade de flip

        Returns:
            Sequência perturbada
        """
        perturbed = []
        for interaction in sequence:
            interaction_copy = interaction.copy()
            if random.random() < flip_prob:
                interaction_copy["correct"] = 1 - interaction_copy["correct"]
            perturbed.append(interaction_copy)

        return perturbed

    def generate_synthetic_student(
        self,
        item_pool: List[str],
        skill_mapping: Dict[str, List[str]],
        n_interactions: int = 50,
        ability_level: str = "medium",
    ) -> List[Dict]:
        """
        Gera estudante sintético baseado em modelo probabilístico.

        Args:
            item_pool: Pool de itens disponíveis
            skill_mapping: Mapeamento item->skills
            n_interactions: Número de interações
            ability_level: Nível de habilidade ('low', 'medium', 'high')

        Returns:
            Sequência de interações sintéticas
        """
        # Definir parâmetros baseados no nível
        ability_params = {
            "low": {"mean": -0.5, "std": 0.3},
            "medium": {"mean": 0.0, "std": 0.5},
            "high": {"mean": 0.5, "std": 0.3},
        }

        params = ability_params.get(ability_level, ability_params["medium"])
        student_ability = np.random.normal(params["mean"], params["std"])

        sequence = []
        for _ in range(n_interactions):
            item_id = random.choice(item_pool)
            skill_id = skill_mapping.get(item_id, ["unknown"])[0]

            # Simular dificuldade do item
            item_difficulty = np.random.normal(0, 0.5)

            # IRT: P(correct) = 1 / (1 + exp(-(ability - difficulty)))
            prob_correct = 1 / (1 + np.exp(-(student_ability - item_difficulty)))
            correct = 1 if random.random() < prob_correct else 0

            sequence.append(
                {"item_id": item_id, "skill_id": skill_id, "correct": correct, "ability_truth": student_ability}
            )

        return sequence

    def augment_dataset(
        self,
        sequences: List[List[Dict]],
        methods: List[str] = ["sliding_window", "perturb"],
        augmentation_factor: int = 2,
    ) -> List[List[Dict]]:
        """
        Aumenta dataset usando múltiplos métodos.

        Args:
            sequences: Sequências originais
            methods: Métodos a aplicar
            augmentation_factor: Fator de aumento

        Returns:
            Sequências aumentadas
        """
        augmented = list(sequences)  # Manter originais

        for _ in range(augmentation_factor - 1):
            for sequence in sequences:
                for method in methods:
                    if method == "sliding_window" and len(sequence) > 50:
                        windows = self.sliding_window(sequence, window_size=50, stride=30)
                        augmented.extend(windows[:2])  # Limitar para não explodir

                    elif method == "perturb":
                        perturbed = self.perturb_sequence(sequence, flip_prob=0.05)
                        augmented.append(perturbed)

        logger.info(f"Dataset aumentado: {len(sequences)} -> {len(augmented)} sequências")

        return augmented


class FeatureEngineer:
    """Feature engineering para KT."""

    @staticmethod
    def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona features temporais.

        Args:
            df: DataFrame original

        Returns:
            DataFrame com features temporais
        """
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Features por aluno
        df["interaction_number"] = df.groupby("student_id").cumcount() + 1

        # Time since last interaction
        df["time_since_last"] = df.groupby("student_id")["timestamp"].diff().dt.total_seconds()
        df["time_since_last"] = df["time_since_last"].fillna(0)

        # Streak de acertos/erros
        df["correct_streak"] = (
            df.groupby("student_id")["correct"]
            .apply(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumcount() + 1))
            .reset_index(drop=True)
        )

        return df

    @staticmethod
    def add_aggregated_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona features agregadas.

        Args:
            df: DataFrame original

        Returns:
            DataFrame com features agregadas
        """
        df = df.copy()

        # Taxa de acerto por aluno até o momento
        df["student_accuracy_so_far"] = (
            df.groupby("student_id")["correct"].apply(lambda x: x.expanding().mean()).reset_index(drop=True)
        )

        # Taxa de acerto do item (calculada em todo o dataset - cuidado com leakage em produção)
        item_accuracy = df.groupby("item_id")["correct"].mean().to_dict()
        df["item_difficulty"] = df["item_id"].map(item_accuracy)

        # Número de tentativas no item
        df["item_attempts"] = df.groupby(["student_id", "item_id"]).cumcount() + 1

        return df

    @staticmethod
    def create_skill_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features baseadas em habilidades.

        Args:
            df: DataFrame original

        Returns:
            DataFrame com features de habilidades
        """
        df = df.copy()

        # Performance por skill
        df["skill_performance"] = (
            df.groupby(["student_id", "skill_id"])["correct"]
            .apply(lambda x: x.expanding().mean())
            .reset_index(drop=True)
        )

        # Número de skills únicas vistas
        def count_unique_expanding(series):
            """Conta skills únicas acumuladas"""
            unique_counts = []
            seen = set()
            for val in series:
                seen.add(val)
                unique_counts.append(len(seen))
            return pd.Series(unique_counts, index=series.index)

        df["n_skills_seen"] = df.groupby("student_id")["skill_id"].transform(count_unique_expanding)

        return df


def prepare_enhanced_dataset(
    csv_path: str, output_path: str, augment: bool = True, add_features: bool = True
) -> pd.DataFrame:
    """
    Prepara dataset com augmentation e feature engineering.

    Args:
        csv_path: Caminho do CSV original
        output_path: Caminho de saída
        augment: Se True, aplica augmentation
        add_features: Se True, adiciona features

    Returns:
        DataFrame processado
    """
    df = pd.read_csv(csv_path)

    if add_features:
        logger.info("Adicionando features temporais...")
        df = FeatureEngineer.add_temporal_features(df)

        logger.info("Adicionando features agregadas...")
        df = FeatureEngineer.add_aggregated_features(df)

        logger.info("Adicionando features de habilidades...")
        df = FeatureEngineer.create_skill_features(df)

    # Salvar
    df.to_csv(output_path, index=False)
    logger.info(f"Dataset processado salvo em {output_path}")

    return df
