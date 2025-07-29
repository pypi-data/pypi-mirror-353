"""
Configuration globale pour EasyML
=================================

Gère les paramètres par défaut, le logging et les seeds.
"""

import logging
import random
import numpy as np
import os
from pathlib import Path

# Configuration par défaut
DEFAULT_CONFIG = {
    'random_seed': 42,
    'logging_level': 'INFO',
    'auto_save_models': True,
    'default_cv_folds': 5,
    'default_test_size': 0.2,
    'max_features_auto': 10000,
    'parallel_jobs': -1,
    'cache_dir': '.easyml_cache',
    'models_dir': 'easyml_models',
    'plots_dir': 'easyml_plots',
}

class EasyMLConfig:
    """Configuration globale d'EasyML."""
    
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """Charge la configuration depuis les variables d'environnement."""
        env_mapping = {
            'EASYML_RANDOM_SEED': ('random_seed', int),
            'EASYML_LOGGING_LEVEL': ('logging_level', str),
            'EASYML_AUTO_SAVE': ('auto_save_models', lambda x: x.lower() == 'true'),
            'EASYML_CV_FOLDS': ('default_cv_folds', int),
            'EASYML_TEST_SIZE': ('default_test_size', float),
            'EASYML_MAX_FEATURES': ('max_features_auto', int),
            'EASYML_JOBS': ('parallel_jobs', int),
            'EASYML_CACHE_DIR': ('cache_dir', str),
            'EASYML_MODELS_DIR': ('models_dir', str),
            'EASYML_PLOTS_DIR': ('plots_dir', str),
        }
        
        for env_var, (config_key, converter) in env_mapping.items():
            if env_var in os.environ:
                try:
                    self._config[config_key] = converter(os.environ[env_var])
                except (ValueError, TypeError):
                    pass  # Ignore invalid values
    
    def get(self, key, default=None):
        """Récupère une valeur de configuration."""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """Définit une valeur de configuration."""
        self._config[key] = value
    
    def update(self, **kwargs):
        """Met à jour plusieurs valeurs de configuration."""
        self._config.update(kwargs)
    
    def reset(self):
        """Remet la configuration par défaut."""
        self._config = DEFAULT_CONFIG.copy()
        self._load_from_env()
    
    def get_cache_dir(self):
        """Retourne le répertoire de cache."""
        cache_dir = Path(self.get('cache_dir'))
        cache_dir.mkdir(exist_ok=True)
        return cache_dir
    
    def get_models_dir(self):
        """Retourne le répertoire des modèles."""
        models_dir = Path(self.get('models_dir'))
        models_dir.mkdir(exist_ok=True)
        return models_dir
    
    def get_plots_dir(self):
        """Retourne le répertoire des graphiques."""
        plots_dir = Path(self.get('plots_dir'))
        plots_dir.mkdir(exist_ok=True)
        return plots_dir

# Instance globale de configuration
config = EasyMLConfig()

def setup_logging(level=None):
    """Configure le système de logging d'EasyML."""
    if level is None:
        level = config.get('logging_level', 'INFO')
    
    # Configuration du logger principal
    logger = logging.getLogger('easyml')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Éviter les doublons de handlers
    if not logger.handlers:
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Format des messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    # Réduire la verbosité des autres bibliothèques
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('sklearn').setLevel(logging.WARNING)
    
    return logger

def set_random_seed(seed=None):
    """Définit le seed aléatoire pour la reproductibilité."""
    if seed is None:
        seed = config.get('random_seed', 42)
    
    # Python random
    random.seed(seed)
    
    # NumPy
    np.random.seed(seed)
    
    # Scikit-learn utilise NumPy, donc déjà configuré
    
    # TensorFlow (si disponible)
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except ImportError:
        pass
    
    # PyTorch (si disponible)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
    
    config.set('random_seed', seed)

def get_logger(name='easyml'):
    """Récupère un logger configuré."""
    return logging.getLogger(name)

def set_config(**kwargs):
    """Interface pratique pour modifier la configuration."""
    config.update(**kwargs)

def get_config(key=None):
    """Interface pratique pour lire la configuration."""
    if key is None:
        return config._config.copy()
    return config.get(key)

def reset_config():
    """Remet la configuration par défaut."""
    config.reset()

# Configuration automatique au chargement
logger = setup_logging()

def print_config():
    """Affiche la configuration actuelle."""
    print("🔧 Configuration EasyML:")
    print("=" * 25)
    for key, value in config._config.items():
        print(f"{key}: {value}")
    print()

# Contexte manager pour configuration temporaire
class temporary_config:
    """Context manager pour modifier temporairement la configuration."""
    
    def __init__(self, **kwargs):
        self.temp_config = kwargs
        self.original_config = {}
    
    def __enter__(self):
        # Sauvegarder la configuration actuelle
        for key in self.temp_config:
            self.original_config[key] = config.get(key)
        
        # Appliquer la configuration temporaire
        config.update(**self.temp_config)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restaurer la configuration originale
        config.update(**self.original_config) 