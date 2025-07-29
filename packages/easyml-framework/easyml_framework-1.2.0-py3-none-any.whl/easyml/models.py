"""
Modèles ML automatisés pour EasyML
==================================

Classes principales pour classification, régression, NLP, etc.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Imports scikit-learn
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    ExtraTreesClassifier, ExtraTreesRegressor,
    AdaBoostClassifier, AdaBoostRegressor
)
from sklearn.linear_model import (
    LogisticRegression, LinearRegression, Ridge, Lasso,
    ElasticNet, SGDClassifier, SGDRegressor
)
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV,
    RandomizedSearchCV, StratifiedKFold, KFold
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

# Imports locaux
from .config import config, get_logger
from .preprocessing import DataCleaner, FeatureEngine, TextProcessor
from .utils import load_data, save_model, load_model
from .visualization import plot_confusion_matrix, plot_feature_importance
from .evaluation import ModelEvaluator

logger = get_logger(__name__)

class BaseModel:
    """Classe de base pour tous les modèles EasyML."""
    
    def __init__(self, random_state=None, n_jobs=None):
        self.random_state = random_state or config.get('random_seed')
        self.n_jobs = n_jobs or config.get('parallel_jobs')
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.target_name = None
        self.is_fitted = False
        self.training_score = None
        self.validation_score = None
        
    def _prepare_data(self, data, target=None):
        """Prépare les données pour l'entraînement."""
        if isinstance(data, str):
            data = load_data(data)
        
        if isinstance(data, pd.DataFrame):
            if target:
                if target in data.columns:
                    X = data.drop(columns=[target])
                    y = data[target]
                    self.target_name = target
                else:
                    raise ValueError(f"Colonne cible '{target}' non trouvée")
            else:
                X = data
                y = None
        else:
            X = data
            y = target
            
        if X is not None:
            self.feature_names = list(X.columns) if hasattr(X, 'columns') else None
            
        return X, y
    
    def save(self, filepath):
        """Sauvegarde le modèle."""
        filepath = Path(filepath)
        if not filepath.suffix:
            filepath = filepath.with_suffix('.pkl')
        
        save_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'is_fitted': self.is_fitted,
            'training_score': self.training_score,
            'validation_score': self.validation_score,
            'model_type': self.__class__.__name__
        }
        
        joblib.dump(save_data, filepath)
        logger.info(f"Modèle sauvegardé: {filepath}")
        
    def load(self, filepath):
        """Charge un modèle sauvegardé."""
        filepath = Path(filepath)
        save_data = joblib.load(filepath)
        
        self.model = save_data['model']
        self.scaler = save_data.get('scaler')
        self.label_encoder = save_data.get('label_encoder')
        self.feature_names = save_data.get('feature_names')
        self.target_name = save_data.get('target_name')
        self.is_fitted = save_data.get('is_fitted', False)
        self.training_score = save_data.get('training_score')
        self.validation_score = save_data.get('validation_score')
        
        logger.info(f"Modèle chargé: {filepath}")

class AutoClassifier(BaseModel):
    """Classification automatique avec sélection de modèle optimale."""
    
    def __init__(self, optimization='auto', cv_folds=None, random_state=None, n_jobs=None, 
                 tune_hyperparams=True, scoring='accuracy'):
        super().__init__(random_state, n_jobs)
        self.optimization = optimization
        self.cv_folds = cv_folds or config.get('default_cv_folds')
        self.tune_hyperparams = tune_hyperparams
        self.scoring = scoring
        self.best_model_name = None
        self.model_scores = {}
        self.best_params = {}
        
    def fit(self, data, target=None, test_size=None):
        """Entraîne automatiquement le meilleur modèle de classification."""
        logger.info("🚀 Démarrage de la classification automatique...")
        
        X, y = self._prepare_data(data, target)
        test_size = test_size or config.get('default_test_size')
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state,
            stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Preprocessing automatique
        self.cleaner = DataCleaner()
        X_train_clean = self.cleaner.fit_transform(X_train)
        X_test_clean = self.cleaner.transform(X_test)
        
        # Standardisation
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train_clean)
        X_test_scaled = self.scaler.transform(X_test_clean)
        
        # Encodage des labels
        self.label_encoder = LabelEncoder()
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Modèles à tester
        models = self._get_models()
        
        # Filtrer les modèles disponibles
        available_models = {name: model for name, model in models.items() if model is not None}
        logger.info(f"📊 Évaluation de {len(available_models)} modèles disponibles...")
        
        if not available_models:
            raise RuntimeError("Aucun modèle disponible pour l'entraînement")
        
        best_score = 0
        best_model = None
        
        for name, model in available_models.items():
            try:
                # Optimisation des hyperparamètres si activée
                if self.tune_hyperparams:
                    optimized_model, best_params = self._optimize_hyperparams(
                        model, name, X_train_scaled, y_train_encoded
                    )
                    self.best_params[name] = best_params
                else:
                    optimized_model = model
                    self.best_params[name] = {}
                
                # Cross-validation avec le modèle optimisé
                cv_scores = cross_val_score(
                    optimized_model, X_train_scaled, y_train_encoded,
                    cv=self.cv_folds, scoring=self.scoring, n_jobs=self.n_jobs
                )
                mean_score = cv_scores.mean()
                self.model_scores[name] = mean_score
                
                param_info = f" (params: {self.best_params[name]})" if self.best_params[name] else ""
                logger.info(f"{name}: {mean_score:.4f} (+/- {cv_scores.std() * 2:.4f}){param_info}")
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_model = optimized_model
                    self.best_model_name = name
                    
            except Exception as e:
                logger.warning(f"Erreur avec {name}: {e}")
                continue
        
        # Entraînement du meilleur modèle
        if best_model is not None:
            logger.info(f"🏆 Meilleur modèle: {self.best_model_name}")
            best_model.fit(X_train_scaled, y_train_encoded)
            self.model = best_model
            
            # Scores finaux
            self.training_score = best_model.score(X_train_scaled, y_train_encoded)
            self.validation_score = best_model.score(X_test_scaled, y_test_encoded)
            
            logger.info(f"📈 Score d'entraînement: {self.training_score:.4f}")
            logger.info(f"📈 Score de validation: {self.validation_score:.4f}")
            
            self.is_fitted = True
            
            # Sauvegarde automatique
            if config.get('auto_save_models'):
                self.save(config.get_models_dir() / f'auto_classifier_{self.best_model_name.lower()}.pkl')
        else:
            raise RuntimeError("Aucun modèle n'a pu être entraîné")
        
        return self
    
    def _get_models(self):
        """Retourne les modèles à tester."""
        models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=100, random_state=self.random_state, n_jobs=self.n_jobs
            ),
            'GradientBoosting': GradientBoostingClassifier(
                n_estimators=100, random_state=self.random_state
            ),
            'XGBoost': self._get_xgboost_classifier(),
            'LightGBM': self._get_lightgbm_classifier(),
            'LogisticRegression': LogisticRegression(
                random_state=self.random_state, max_iter=1000, n_jobs=self.n_jobs
            ),
            'SVM': SVC(random_state=self.random_state, probability=True),
            'KNeighbors': KNeighborsClassifier(n_jobs=self.n_jobs),
            'ExtraTrees': ExtraTreesClassifier(
                n_estimators=100, random_state=self.random_state, n_jobs=self.n_jobs
            ),
            'AdaBoost': AdaBoostClassifier(
                n_estimators=100, random_state=self.random_state
            ),
            'NaiveBayes': GaussianNB(),
        }
        
        return models
    
    def _get_xgboost_classifier(self):
        """Retourne un classificateur XGBoost avec gestion d'erreur."""
        try:
            import xgboost as xgb
            return xgb.XGBClassifier(
                n_estimators=100,
                random_state=self.random_state,
                n_jobs=self.n_jobs,
                eval_metric='logloss'
            )
        except ImportError:
            logger.warning("XGBoost non disponible, installation avec: pip install xgboost")
            return None
    
    def _get_lightgbm_classifier(self):
        """Retourne un classificateur LightGBM avec gestion d'erreur."""
        try:
            import lightgbm as lgb
            return lgb.LGBMClassifier(
                n_estimators=100,
                random_state=self.random_state,
                n_jobs=self.n_jobs,
                verbosity=-1
            )
        except ImportError:
            logger.warning("LightGBM non disponible, installation avec: pip install lightgbm")
            return None
    
    def _optimize_hyperparams(self, model, model_name, X, y):
        """Optimise les hyperparamètres d'un modèle."""
        from sklearn.model_selection import RandomizedSearchCV
        from scipy.stats import randint, uniform
        
        # Définir les espaces de recherche pour chaque modèle
        param_grids = {
            'RandomForest': {
                'n_estimators': randint(50, 200),
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': randint(2, 20),
                'min_samples_leaf': randint(1, 10)
            },
            'GradientBoosting': {
                'n_estimators': randint(50, 200),
                'learning_rate': uniform(0.01, 0.3),
                'max_depth': randint(3, 10)
            },
            'LogisticRegression': {
                'C': uniform(0.01, 100),
                'solver': ['liblinear', 'lbfgs']
            },
            'SVM': {
                'C': uniform(0.1, 100),
                'gamma': ['scale', 'auto'] + list(uniform(0.001, 1).rvs(5))
            },
            'KNeighbors': {
                'n_neighbors': randint(3, 15),
                'weights': ['uniform', 'distance']
            }
        }
        
        if model_name not in param_grids:
            return model, {}
        
        try:
            # Recherche randomisée plus rapide que GridSearch
            search = RandomizedSearchCV(
                model, param_grids[model_name],
                n_iter=20,  # Limité pour la vitesse
                cv=min(3, self.cv_folds),  # CV réduite pour l'optimisation
                scoring=self.scoring,
                n_jobs=self.n_jobs,
                random_state=self.random_state
            )
            
            search.fit(X, y)
            logger.info(f"🔧 {model_name} optimisé: {search.best_params_}")
            
            return search.best_estimator_, search.best_params_
            
        except Exception as e:
            logger.warning(f"Échec de l'optimisation pour {model_name}: {e}")
            return model, {}
    
    def predict(self, data):
        """Prédit les classes pour de nouvelles données."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")
        
        try:
            if isinstance(data, str):
                data = load_data(data)
            
            # Validation des données
            if data is None or data.empty:
                raise ValueError("Données vides ou None fournies")
            
            # Preprocessing avec le DataCleaner utilisé pendant l'entraînement
            if not hasattr(self, 'cleaner'):
                logger.warning("DataCleaner non trouvé, utilisation d'un nouveau")
                cleaner = DataCleaner()
                data_clean = cleaner.fit_transform(data)
            else:
                data_clean = self.cleaner.transform(data)
            
            # Vérification de compatibilité des features
            if data_clean.shape[1] != self.scaler.n_features_in_:
                raise ValueError(
                    f"Nombre de features incompatible: {data_clean.shape[1]} "
                    f"vs {self.scaler.n_features_in_} attendues"
                )
            
            data_scaled = self.scaler.transform(data_clean)
            
            # Prédictions
            predictions_encoded = self.model.predict(data_scaled)
            predictions = self.label_encoder.inverse_transform(predictions_encoded)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            raise
    
    def predict_proba(self, data):
        """Prédit les probabilités des classes."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")
        
        if isinstance(data, str):
            data = load_data(data)
            
        # Preprocessing
        cleaner = DataCleaner()
        data_clean = cleaner.transform(data)
        data_scaled = self.scaler.transform(data_clean)
        
        # Probabilités
        if hasattr(self.model, 'predict_proba'):
            probas = self.model.predict_proba(data_scaled)
            return probas
        else:
            raise AttributeError("Ce modèle ne supporte pas predict_proba")
    
    def evaluate(self, data=None, target=None):
        """Évalue le modèle sur des données de test."""
        evaluator = ModelEvaluator(self.model, task='classification')
        return evaluator.evaluate(data, target)
    
    def plot_results(self):
        """Affiche les résultats visuels."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné")
        
        # Graphique des scores des modèles
        import matplotlib.pyplot as plt
        
        models = list(self.model_scores.keys())
        scores = list(self.model_scores.values())
        
        plt.figure(figsize=(10, 6))
        plt.bar(models, scores)
        plt.title('Comparaison des Modèles de Classification')
        plt.ylabel('Score de Validation Croisée')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

class AutoRegressor(BaseModel):
    """Régression automatique avec sélection de modèle optimale."""
    
    def __init__(self, optimization='auto', cv_folds=None, random_state=None, n_jobs=None):
        super().__init__(random_state, n_jobs)
        self.optimization = optimization
        self.cv_folds = cv_folds or config.get('default_cv_folds')
        self.best_model_name = None
        self.model_scores = {}
        
    def fit(self, data, target=None, test_size=None):
        """Entraîne automatiquement le meilleur modèle de régression."""
        logger.info("🚀 Démarrage de la régression automatique...")
        
        X, y = self._prepare_data(data, target)
        test_size = test_size or config.get('default_test_size')
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        
        # Preprocessing automatique
        cleaner = DataCleaner()
        X_train_clean = cleaner.fit_transform(X_train)
        X_test_clean = cleaner.transform(X_test)
        
        # Standardisation
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train_clean)
        X_test_scaled = self.scaler.transform(X_test_clean)
        
        # Modèles à tester
        models = self._get_models()
        
        # Évaluation des modèles
        logger.info("📊 Évaluation des modèles...")
        best_score = float('-inf')
        best_model = None
        
        for name, model in models.items():
            try:
                # Cross-validation avec R²
                cv_scores = cross_val_score(
                    model, X_train_scaled, y_train,
                    cv=self.cv_folds, scoring='r2', n_jobs=self.n_jobs
                )
                mean_score = cv_scores.mean()
                self.model_scores[name] = mean_score
                
                logger.info(f"{name}: {mean_score:.4f} (+/- {cv_scores.std() * 2:.4f})")
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    self.best_model_name = name
                    
            except Exception as e:
                logger.warning(f"Erreur avec {name}: {e}")
                continue
        
        # Entraînement du meilleur modèle
        if best_model is not None:
            logger.info(f"🏆 Meilleur modèle: {self.best_model_name}")
            best_model.fit(X_train_scaled, y_train)
            self.model = best_model
            
            # Scores finaux
            self.training_score = best_model.score(X_train_scaled, y_train)
            self.validation_score = best_model.score(X_test_scaled, y_test)
            
            logger.info(f"📈 Score d'entraînement (R²): {self.training_score:.4f}")
            logger.info(f"📈 Score de validation (R²): {self.validation_score:.4f}")
            
            self.is_fitted = True
            
            # Sauvegarde automatique
            if config.get('auto_save_models'):
                self.save(config.get_models_dir() / f'auto_regressor_{self.best_model_name.lower()}.pkl')
        else:
            raise RuntimeError("Aucun modèle n'a pu être entraîné")
        
        return self
    
    def _get_models(self):
        """Retourne les modèles à tester."""
        models = {
            'RandomForest': RandomForestRegressor(
                n_estimators=100, random_state=self.random_state, n_jobs=self.n_jobs
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=100, random_state=self.random_state
            ),
            'LinearRegression': LinearRegression(n_jobs=self.n_jobs),
            'Ridge': Ridge(random_state=self.random_state),
            'Lasso': Lasso(random_state=self.random_state, max_iter=2000),
            'ElasticNet': ElasticNet(random_state=self.random_state, max_iter=2000),
            'SVR': SVR(),
            'KNeighbors': KNeighborsRegressor(n_jobs=self.n_jobs),
            'ExtraTrees': ExtraTreesRegressor(
                n_estimators=100, random_state=self.random_state, n_jobs=self.n_jobs
            ),
        }
        
        return models
    
    def predict(self, data):
        """Prédit les valeurs pour de nouvelles données."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")
        
        if isinstance(data, str):
            data = load_data(data)
            
        # Preprocessing
        cleaner = DataCleaner()
        data_clean = cleaner.transform(data)
        data_scaled = self.scaler.transform(data_clean)
        
        # Prédictions
        predictions = self.model.predict(data_scaled)
        
        return predictions
    
    def evaluate(self, data=None, target=None):
        """Évalue le modèle sur des données de test."""
        evaluator = ModelEvaluator(self.model, task='regression')
        return evaluator.evaluate(data, target)

class TextClassifier(BaseModel):
    """Classification de texte automatique."""
    
    def __init__(self, vectorizer='tfidf', max_features=None, random_state=None, n_jobs=None):
        super().__init__(random_state, n_jobs)
        self.vectorizer_type = vectorizer
        self.max_features = max_features or config.get('max_features_auto')
        self.vectorizer = None
        self.text_processor = TextProcessor()
        
    def fit(self, data, text_column, target, test_size=None):
        """Entraîne un classifieur de texte."""
        logger.info("🚀 Démarrage de la classification de texte...")
        
        if isinstance(data, str):
            data = load_data(data)
        
        X_text = data[text_column]
        y = data[target]
        
        # Preprocessing du texte
        X_processed = self.text_processor.fit_transform(X_text)
        
        # Vectorisation
        if self.vectorizer_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=(1, 2)
            )
        else:
            self.vectorizer = CountVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=(1, 2)
            )
        
        X_vectorized = self.vectorizer.fit_transform(X_processed)
        
        # Division train/test
        test_size = test_size or config.get('default_test_size')
        X_train, X_test, y_train, y_test = train_test_split(
            X_vectorized, y, test_size=test_size, random_state=self.random_state
        )
        
        # Encodage des labels
        self.label_encoder = LabelEncoder()
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        
        # Entraînement avec Naive Bayes (optimal pour le texte)
        from sklearn.naive_bayes import MultinomialNB
        self.model = MultinomialNB()
        self.model.fit(X_train, y_train_encoded)
        
        # Scores
        self.training_score = self.model.score(X_train, y_train_encoded)
        y_test_encoded = self.label_encoder.transform(y_test)
        self.validation_score = self.model.score(X_test, y_test_encoded)
        
        logger.info(f"📈 Score d'entraînement: {self.training_score:.4f}")
        logger.info(f"📈 Score de validation: {self.validation_score:.4f}")
        
        self.is_fitted = True
        return self
    
    def predict(self, texts):
        """Prédit la classe pour des textes."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")
        
        if isinstance(texts, str):
            texts = [texts]
        
        # Preprocessing et vectorisation
        texts_processed = self.text_processor.transform(texts)
        texts_vectorized = self.vectorizer.transform(texts_processed)
        
        # Prédiction
        predictions_encoded = self.model.predict(texts_vectorized)
        predictions = self.label_encoder.inverse_transform(predictions_encoded)
        
        if len(predictions) == 1:
            return predictions[0]
        return predictions

class TimeSeriesPredictor(BaseModel):
    """Prédiction de séries temporelles."""
    
    def __init__(self, window_size=30, random_state=None):
        super().__init__(random_state)
        self.window_size = window_size
        
    def fit(self, data, target_column, date_column=None):
        """Entraîne un modèle de prédiction temporelle."""
        logger.info("🚀 Démarrage de la prédiction temporelle...")
        
        if isinstance(data, str):
            data = load_data(data)
        
        # Tri par date si spécifiée
        if date_column:
            data = data.sort_values(date_column)
        
        # Création des features temporelles
        X, y = self._create_sequences(data[target_column].values)
        
        # Division temporelle (pas aléatoire pour les séries temporelles)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Modèle simple (peut être amélioré avec LSTM)
        from sklearn.ensemble import RandomForestRegressor
        self.model = RandomForestRegressor(
            n_estimators=100, random_state=self.random_state, n_jobs=self.n_jobs
        )
        
        self.model.fit(X_train, y_train)
        
        # Scores
        self.training_score = self.model.score(X_train, y_train)
        self.validation_score = self.model.score(X_test, y_test)
        
        logger.info(f"📈 Score d'entraînement: {self.training_score:.4f}")
        logger.info(f"📈 Score de validation: {self.validation_score:.4f}")
        
        self.is_fitted = True
        return self
    
    def _create_sequences(self, data):
        """Crée les séquences pour l'apprentissage."""
        X, y = [], []
        for i in range(self.window_size, len(data)):
            X.append(data[i-self.window_size:i])
            y.append(data[i])
        return np.array(X), np.array(y)
    
    def predict(self, data, steps=1):
        """Prédit les prochaines valeurs."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")
        
        if isinstance(data, str):
            data = load_data(data)
        
        # Utilise les dernières valeurs pour prédire
        last_sequence = data[-self.window_size:].values.reshape(1, -1)
        predictions = []
        
        for _ in range(steps):
            pred = self.model.predict(last_sequence)[0]
            predictions.append(pred)
            
            # Met à jour la séquence
            last_sequence = np.roll(last_sequence, -1)
            last_sequence[0, -1] = pred
        
        return np.array(predictions)

class ClusterAnalyzer(BaseModel):
    """Analyse de clustering automatique."""
    
    def __init__(self, n_clusters='auto', algorithm='kmeans', random_state=None):
        super().__init__(random_state)
        self.n_clusters = n_clusters
        self.algorithm = algorithm
        
    def fit(self, data):
        """Effectue le clustering des données."""
        logger.info("🚀 Démarrage de l'analyse de clustering...")
        
        if isinstance(data, str):
            data = load_data(data)
        
        # Preprocessing
        cleaner = DataCleaner()
        data_clean = cleaner.fit_transform(data)
        
        # Standardisation
        self.scaler = StandardScaler()
        data_scaled = self.scaler.fit_transform(data_clean)
        
        # Sélection automatique du nombre de clusters
        if self.n_clusters == 'auto':
            self.n_clusters = self._find_optimal_clusters(data_scaled)
        
        # Choix de l'algorithme
        if self.algorithm == 'kmeans':
            self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        elif self.algorithm == 'dbscan':
            self.model = DBSCAN()
        else:
            self.model = AgglomerativeClustering(n_clusters=self.n_clusters)
        
        # Clustering
        self.labels = self.model.fit_predict(data_scaled)
        
        logger.info(f"📊 {len(np.unique(self.labels))} clusters identifiés")
        
        self.is_fitted = True
        return self
    
    def _find_optimal_clusters(self, data, max_k=10):
        """Trouve le nombre optimal de clusters avec la méthode du coude."""
        inertias = []
        K_range = range(2, min(max_k + 1, len(data) // 2))
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state)
            kmeans.fit(data)
            inertias.append(kmeans.inertia_)
        
        # Méthode du coude simplifiée
        diffs = np.diff(inertias)
        optimal_k = K_range[np.argmax(diffs)] if len(diffs) > 0 else 3
        
        logger.info(f"🎯 Nombre optimal de clusters détecté: {optimal_k}")
        return optimal_k
    
    def predict(self, data):
        """Prédit les clusters pour de nouvelles données."""
        if not self.is_fitted:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")
        
        if isinstance(data, str):
            data = load_data(data)
        
        # Preprocessing
        cleaner = DataCleaner()
        data_clean = cleaner.transform(data)
        data_scaled = self.scaler.transform(data_clean)
        
        # Prédiction
        if hasattr(self.model, 'predict'):
            return self.model.predict(data_scaled)
        else:
            # Pour DBSCAN qui n'a pas de predict
            return self.model.fit_predict(data_scaled)