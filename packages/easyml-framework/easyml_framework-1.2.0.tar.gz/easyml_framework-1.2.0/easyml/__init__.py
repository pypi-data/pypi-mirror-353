"""
EasyML Framework - Un framework ML simplifié et complet pour Python
==================================================================

EasyML rend le Machine Learning accessible à tous avec une API simple 
et des fonctionnalités automatisées.

Exemple d'utilisation:
    >>> import easyml as ez
    >>> model = ez.AutoClassifier()
    >>> model.fit('data.csv', target='label')
    >>> predictions = model.predict('new_data.csv')
"""

__version__ = "1.2.0"
__author__ = "EasyML Team"
__email__ = "contact@easyml.dev"

# Import des classes principales
from .models import (
    AutoClassifier,
    AutoRegressor,
    TextClassifier,
    TimeSeriesPredictor,
    ClusterAnalyzer,
)

from .preprocessing import (
    DataCleaner,
    FeatureEngine,
    TextProcessor,
)

from .utils import (
    load_data,
    explore_data,
    compare_models,
    deploy_model,
    create_sample_data,
)

from .cache import (
    get_cache,
    cached_operation,
)

from .ensemble import (
    SmartEnsemble,
    AutoEnsemble,
)

from .visualization import (
    plot_confusion_matrix,
    plot_roc_curve,
    plot_feature_importance,
    plot_learning_curve,
)

from .evaluation import (
    ModelEvaluator,
    CrossValidator,
    MetricsCalculator,
)

# Configuration par défaut
from .config import setup_logging, set_random_seed

# Import optionnels pour compatibilité
try:
    from .deep_learning import DeepClassifier, DeepRegressor
    __has_deep_learning__ = True
except ImportError:
    __has_deep_learning__ = False

try:
    from .nlp_advanced import AdvancedNLP, LanguageModel
    __has_advanced_nlp__ = True
except ImportError:
    __has_advanced_nlp__ = False

# Configuration automatique
setup_logging()
set_random_seed(42)

# Classes et fonctions exposées publiquement
__all__ = [
    # Modèles principaux
    'AutoClassifier',
    'AutoRegressor', 
    'TextClassifier',
    'TimeSeriesPredictor',
    'ClusterAnalyzer',
    'SmartEnsemble',
    'AutoEnsemble',
    
    # Preprocessing
    'DataCleaner',
    'FeatureEngine', 
    'TextProcessor',
    
    # Utilitaires
    'load_data',
    'explore_data',
    'compare_models',
    'deploy_model',
    'create_sample_data',
    'get_cache',
    'cached_operation',
    
    # Visualisation
    'plot_confusion_matrix',
    'plot_roc_curve', 
    'plot_feature_importance',
    'plot_learning_curve',
    
    # Évaluation
    'ModelEvaluator',
    'CrossValidator',
    'MetricsCalculator',
]

# Ajout conditionnel des modules optionnels
if __has_deep_learning__:
    __all__.extend(['DeepClassifier', 'DeepRegressor'])

if __has_advanced_nlp__:
    __all__.extend(['AdvancedNLP', 'LanguageModel'])

def get_version():
    """Retourne la version d'EasyML."""
    return __version__

def list_models():
    """Liste tous les modèles disponibles."""
    models = [
        'AutoClassifier - Classification automatique',
        'AutoRegressor - Régression automatique', 
        'TextClassifier - Classification de texte',
        'TimeSeriesPredictor - Prédiction temporelle',
        'ClusterAnalyzer - Analyse de clustering',
    ]
    
    if __has_deep_learning__:
        models.extend([
            'DeepClassifier - Classification avec réseaux de neurones',
            'DeepRegressor - Régression avec réseaux de neurones'
        ])
    
    return models

def quick_start():
    """Guide de démarrage rapide."""
    print("""
    🚀 EasyML - Démarrage Rapide
    ============================
    
    1. Classification automatique:
       >>> model = ez.AutoClassifier()
       >>> model.fit('data.csv', target='label')
       
    2. Régression automatique:
       >>> model = ez.AutoRegressor()
       >>> model.fit('data.csv', target='price')
       
    3. Nettoyage de données:
       >>> cleaner = ez.DataCleaner()
       >>> clean_data = cleaner.transform('data.csv')
       
    4. Exploration de données:
       >>> ez.explore_data('data.csv')
       
    Voir la documentation complète: help(easyml)
    """)

# Message de bienvenue (optionnel, peut être désactivé)
import os
if os.getenv('EASYML_WELCOME', '1') == '1':
    print(f"🚀 EasyML {__version__} chargé avec succès!")
    if not __has_deep_learning__:
        print("💡 Tip: pip install easyml-framework[deep] pour le deep learning")
    if not __has_advanced_nlp__:
        print("💡 Tip: pip install easyml-framework[nlp] pour NLP avancé") 