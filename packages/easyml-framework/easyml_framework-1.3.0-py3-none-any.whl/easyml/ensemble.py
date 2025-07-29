"""
Ensemble Learning intelligent pour EasyML
=========================================

Classes pour combiner automatiquement plusieurs modèles et améliorer les performances.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from sklearn.ensemble import VotingClassifier, VotingRegressor
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.base import clone
import warnings
warnings.filterwarnings('ignore')

from .config import get_logger
from .models import AutoClassifier, AutoRegressor
from .evaluation import ModelEvaluator
from .cache import cached_operation

logger = get_logger(__name__)

class SmartEnsemble:
    """Ensemble intelligent qui sélectionne et combine automatiquement les meilleurs modèles."""
    
    def __init__(self, task='auto', ensemble_method='voting', 
                 diversity_threshold=0.1, performance_threshold=0.8,
                 max_models=5, random_state=None):
        self.task = task
        self.ensemble_method = ensemble_method  # 'voting', 'stacking', 'blending'
        self.diversity_threshold = diversity_threshold
        self.performance_threshold = performance_threshold
        self.max_models = max_models
        self.random_state = random_state
        
        self.base_models = []
        self.ensemble_model = None
        self.model_performances = {}
        self.model_diversity = {}
        self.is_fitted = False
        
    def fit(self, X, y, test_size=0.2):
        """Entraîne l'ensemble en sélectionnant les meilleurs modèles."""
        logger.info("🎭 Démarrage de l'ensemble learning intelligent...")
        
        # Détection automatique de la tâche
        if self.task == 'auto':
            unique_values = len(np.unique(y))
            self.task = 'classification' if unique_values <= 20 else 'regression'
        
        logger.info(f"📊 Tâche détectée: {self.task}")
        
        # Génération des modèles candidats
        candidate_models = self._generate_candidate_models()
        
        # Évaluation des modèles
        model_scores = self._evaluate_models(candidate_models, X, y)
        
        # Sélection des modèles par performance
        top_models = self._select_by_performance(model_scores)
        
        # Sélection finale par diversité
        final_models = self._select_by_diversity(top_models, X, y)
        
        # Création de l'ensemble
        self.ensemble_model = self._create_ensemble(final_models)
        
        # Entraînement final
        self.ensemble_model.fit(X, y)
        self.is_fitted = True
        
        logger.info(f"✅ Ensemble créé avec {len(final_models)} modèles")
        return self
    
    def _generate_candidate_models(self) -> Dict[str, Any]:
        """Génère une liste de modèles candidats diversifiés."""
        models = {}
        
        if self.task == 'classification':
            from sklearn.ensemble import (
                RandomForestClassifier, GradientBoostingClassifier,
                ExtraTreesClassifier, AdaBoostClassifier
            )
            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.naive_bayes import GaussianNB
            
            models.update({
                'rf': RandomForestClassifier(n_estimators=100, random_state=self.random_state),
                'gb': GradientBoostingClassifier(n_estimators=100, random_state=self.random_state),
                'et': ExtraTreesClassifier(n_estimators=100, random_state=self.random_state),
                'ada': AdaBoostClassifier(n_estimators=100, random_state=self.random_state),
                'lr': LogisticRegression(random_state=self.random_state, max_iter=1000),
                'svm': SVC(probability=True, random_state=self.random_state),
                'knn': KNeighborsClassifier(),
                'nb': GaussianNB(),
            })
            
        else:  # regression
            from sklearn.ensemble import (
                RandomForestRegressor, GradientBoostingRegressor,
                ExtraTreesRegressor, AdaBoostRegressor
            )
            from sklearn.linear_model import LinearRegression, Ridge, Lasso
            from sklearn.svm import SVR
            from sklearn.neighbors import KNeighborsRegressor
            
            models.update({
                'rf': RandomForestRegressor(n_estimators=100, random_state=self.random_state),
                'gb': GradientBoostingRegressor(n_estimators=100, random_state=self.random_state),
                'et': ExtraTreesRegressor(n_estimators=100, random_state=self.random_state),
                'ada': AdaBoostRegressor(n_estimators=100, random_state=self.random_state),
                'lr': LinearRegression(),
                'ridge': Ridge(random_state=self.random_state),
                'lasso': Lasso(random_state=self.random_state),
                'svr': SVR(),
                'knn': KNeighborsRegressor(),
            })
        
        # Ajouter XGBoost et LightGBM si disponibles
        try:
            import xgboost as xgb
            if self.task == 'classification':
                models['xgb'] = xgb.XGBClassifier(random_state=self.random_state, eval_metric='logloss')
            else:
                models['xgb'] = xgb.XGBRegressor(random_state=self.random_state)
        except ImportError:
            pass
        
        try:
            import lightgbm as lgb
            if self.task == 'classification':
                models['lgb'] = lgb.LGBMClassifier(random_state=self.random_state, verbosity=-1)
            else:
                models['lgb'] = lgb.LGBMRegressor(random_state=self.random_state, verbosity=-1)
        except ImportError:
            pass
        
        logger.info(f"🔧 {len(models)} modèles candidats générés")
        return models
    
    @cached_operation("model_evaluation")
    def _evaluate_models(self, models: Dict, X, y) -> Dict[str, float]:
        """Évalue les performances de tous les modèles candidats."""
        scores = {}
        scoring = 'accuracy' if self.task == 'classification' else 'r2'
        
        for name, model in models.items():
            try:
                cv_scores = cross_val_score(
                    model, X, y, cv=5, scoring=scoring, n_jobs=-1
                )
                scores[name] = cv_scores.mean()
                logger.info(f"📊 {name}: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
                
            except Exception as e:
                logger.warning(f"Erreur avec {name}: {e}")
                scores[name] = 0.0
        
        return scores
    
    def _select_by_performance(self, scores: Dict[str, float]) -> List[str]:
        """Sélectionne les modèles par performance."""
        # Filtrer les modèles au-dessus du seuil
        good_models = [
            name for name, score in scores.items() 
            if score >= self.performance_threshold * max(scores.values())
        ]
        
        # Prendre les N meilleurs si pas assez
        if len(good_models) < 2:
            good_models = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:self.max_models]
        
        logger.info(f"🎯 {len(good_models)} modèles sélectionnés par performance")
        return good_models
    
    def _select_by_diversity(self, model_names: List[str], X, y) -> List[str]:
        """Sélectionne les modèles les plus diversifiés."""
        if len(model_names) <= 2:
            return model_names
        
        # Calculer les prédictions de chaque modèle
        predictions = {}
        models = self._generate_candidate_models()
        
        for name in model_names:
            try:
                model = clone(models[name])
                model.fit(X, y)
                if self.task == 'classification':
                    pred = model.predict_proba(X)
                else:
                    pred = model.predict(X)
                predictions[name] = pred
            except Exception as e:
                logger.warning(f"Erreur diversité {name}: {e}")
                continue
        
        # Calculer la diversité (corrélation inverse)
        diversity_matrix = self._calculate_diversity(predictions)
        
        # Sélection gloutonne des modèles les plus diversifiés
        selected = [model_names[0]]  # Commencer par le meilleur
        
        for _ in range(min(self.max_models - 1, len(model_names) - 1)):
            best_candidate = None
            best_diversity = -1
            
            for candidate in model_names:
                if candidate in selected:
                    continue
                
                # Calculer la diversité moyenne avec les modèles sélectionnés
                avg_diversity = np.mean([
                    diversity_matrix.get((candidate, selected_model), 0)
                    for selected_model in selected
                ])
                
                if avg_diversity > best_diversity:
                    best_diversity = avg_diversity
                    best_candidate = candidate
            
            if best_candidate and best_diversity > self.diversity_threshold:
                selected.append(best_candidate)
            else:
                break
        
        logger.info(f"🎭 {len(selected)} modèles sélectionnés par diversité")
        return selected
    
    def _calculate_diversity(self, predictions: Dict) -> Dict:
        """Calcule la matrice de diversité entre les modèles."""
        diversity = {}
        model_names = list(predictions.keys())
        
        for i, model1 in enumerate(model_names):
            for j, model2 in enumerate(model_names[i+1:], i+1):
                pred1 = predictions[model1]
                pred2 = predictions[model2]
                
                if self.task == 'classification':
                    # Pour la classification, utiliser la divergence Jensen-Shannon
                    if pred1.shape == pred2.shape:
                        # Moyenne des distributions
                        m = 0.5 * (pred1 + pred2)
                        # Divergence KL
                        kl1 = np.sum(pred1 * np.log(pred1 / m + 1e-10), axis=1)
                        kl2 = np.sum(pred2 * np.log(pred2 / m + 1e-10), axis=1)
                        # Divergence JS
                        js_div = 0.5 * (kl1 + kl2).mean()
                        diversity[(model1, model2)] = js_div
                        diversity[(model2, model1)] = js_div
                else:
                    # Pour la régression, utiliser 1 - corrélation
                    corr = np.corrcoef(pred1, pred2)[0, 1]
                    div = 1 - abs(corr) if not np.isnan(corr) else 0
                    diversity[(model1, model2)] = div
                    diversity[(model2, model1)] = div
        
        return diversity
    
    def _create_ensemble(self, selected_models: List[str]):
        """Crée l'ensemble final avec les modèles sélectionnés."""
        models = self._generate_candidate_models()
        estimators = [(name, models[name]) for name in selected_models]
        
        if self.ensemble_method == 'voting':
            if self.task == 'classification':
                ensemble = VotingClassifier(
                    estimators=estimators,
                    voting='soft'  # Utilise les probabilités
                )
            else:
                ensemble = VotingRegressor(estimators=estimators)
                
        elif self.ensemble_method == 'stacking':
            from sklearn.ensemble import StackingClassifier, StackingRegressor
            from sklearn.linear_model import LogisticRegression, LinearRegression
            
            if self.task == 'classification':
                meta_learner = LogisticRegression(random_state=self.random_state)
                ensemble = StackingClassifier(
                    estimators=estimators,
                    final_estimator=meta_learner,
                    cv=5
                )
            else:
                meta_learner = LinearRegression()
                ensemble = StackingRegressor(
                    estimators=estimators,
                    final_estimator=meta_learner,
                    cv=5
                )
        
        return ensemble
    
    def predict(self, X):
        """Prédit avec l'ensemble."""
        if not self.is_fitted:
            raise RuntimeError("L'ensemble doit être entraîné avant de prédire")
        
        return self.ensemble_model.predict(X)
    
    def predict_proba(self, X):
        """Prédit les probabilités (classification uniquement)."""
        if not self.is_fitted:
            raise RuntimeError("L'ensemble doit être entraîné avant de prédire")
        
        if self.task != 'classification':
            raise ValueError("predict_proba n'est disponible que pour la classification")
        
        return self.ensemble_model.predict_proba(X)
    
    def get_model_weights(self) -> Dict[str, float]:
        """Retourne les poids des modèles dans l'ensemble."""
        if hasattr(self.ensemble_model, 'estimators_'):
            weights = {}
            for name, _ in self.ensemble_model.estimators:
                weights[name] = 1.0 / len(self.ensemble_model.estimators)
            return weights
        return {}

class AutoEnsemble:
    """Ensemble automatique qui optimise tout automatiquement."""
    
    def __init__(self, random_state=None):
        self.random_state = random_state
        self.ensemble = None
        self.is_fitted = False
    
    def fit(self, data, target=None, test_size=0.2):
        """Entraîne automatiquement le meilleur ensemble."""
        logger.info("🤖 Démarrage de l'ensemble automatique...")
        
        # Préparation des données comme dans AutoClassifier
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        if isinstance(data, pd.DataFrame):
            if target:
                if target in data.columns:
                    X = data.drop(columns=[target])
                    y = data[target]
                else:
                    raise ValueError(f"Colonne cible '{target}' non trouvée")
            else:
                raise ValueError("Spécifiez la colonne target")
        else:
            X, y = data, target
        
        # Preprocessing automatique
        from .preprocessing import DataCleaner
        from sklearn.preprocessing import StandardScaler
        
        cleaner = DataCleaner()
        X_clean = cleaner.fit_transform(X)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)
        
        # Créer et entraîner l'ensemble
        self.ensemble = SmartEnsemble(random_state=self.random_state)
        self.ensemble.fit(X_scaled, y, test_size=test_size)
        
        # Stocker les preprocessors
        self.cleaner = cleaner
        self.scaler = scaler
        self.is_fitted = True
        
        logger.info("✅ Ensemble automatique entraîné avec succès")
        return self
    
    def predict(self, data):
        """Prédit avec l'ensemble automatique."""
        if not self.is_fitted:
            raise RuntimeError("L'ensemble doit être entraîné avant de prédire")
        
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        # Preprocessing
        data_clean = self.cleaner.transform(data)
        data_scaled = self.scaler.transform(data_clean)
        
        return self.ensemble.predict(data_scaled)
    
    def predict_proba(self, data):
        """Prédit les probabilités avec l'ensemble automatique."""
        if not self.is_fitted:
            raise RuntimeError("L'ensemble doit être entraîné avant de prédire")
        
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        # Preprocessing
        data_clean = self.cleaner.transform(data)
        data_scaled = self.scaler.transform(data_clean)
        
        return self.ensemble.predict_proba(data_scaled) 