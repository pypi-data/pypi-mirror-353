"""
Évaluation de modèles pour EasyML
================================

Classes pour évaluer et valider les modèles ML.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import *
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from .config import get_logger

logger = get_logger(__name__)

class ModelEvaluator:
    """Évaluateur de modèles automatique avec métriques avancées."""
    
    def __init__(self, model, task='auto'):
        self.model = model
        self.task = task
        
    def evaluate(self, X_test, y_test, verbose=True):
        """Évalue le modèle sur des données de test avec gestion d'erreurs robuste."""
        try:
            predictions = self.model.predict(X_test)
            
            # Détection automatique du type de tâche
            if self.task == 'classification' or (self.task == 'auto' and len(np.unique(y_test)) <= 20):
                results = self._evaluate_classification(y_test, predictions, X_test)
                task_type = 'classification'
            else:
                results = self._evaluate_regression(y_test, predictions)
                task_type = 'regression'
            
            if verbose:
                self._print_results(results, task_type)
                
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation: {e}")
            raise
    
    def _evaluate_classification(self, y_true, y_pred, X_test=None):
        """Métriques de classification avancées."""
        try:
            results = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision_macro': precision_score(y_true, y_pred, average='macro', zero_division=0),
                'precision_weighted': precision_score(y_true, y_pred, average='weighted', zero_division=0),
                'recall_macro': recall_score(y_true, y_pred, average='macro', zero_division=0),
                'recall_weighted': recall_score(y_true, y_pred, average='weighted', zero_division=0),
                'f1_macro': f1_score(y_true, y_pred, average='macro', zero_division=0),
                'f1_weighted': f1_score(y_true, y_pred, average='weighted', zero_division=0),
                'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
                'classification_report': classification_report(y_true, y_pred, output_dict=True)
            }
            
            # Métriques additionnelles selon le nombre de classes
            n_classes = len(np.unique(y_true))
            
            if n_classes == 2 and hasattr(self.model, 'predict_proba') and X_test is not None:
                try:
                    y_proba = self.model.predict_proba(X_test)[:, 1]
                    results['roc_auc'] = roc_auc_score(y_true, y_proba)
                    results['log_loss'] = log_loss(y_true, y_proba)
                    results['brier_score'] = brier_score_loss(y_true, y_proba)
                except Exception:
                    pass
                    
            elif n_classes > 2 and hasattr(self.model, 'predict_proba') and X_test is not None:
                try:
                    y_proba = self.model.predict_proba(X_test)
                    results['roc_auc_ovr'] = roc_auc_score(y_true, y_proba, multi_class='ovr')
                    results['log_loss'] = log_loss(y_true, y_proba)
                except Exception:
                    pass
            
            # Métriques par classe
            results['balanced_accuracy'] = balanced_accuracy_score(y_true, y_pred)
            results['cohen_kappa'] = cohen_kappa_score(y_true, y_pred)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans l'évaluation de classification: {e}")
            raise
    
    def _evaluate_regression(self, y_true, y_pred):
        """Métriques de régression avancées."""
        try:
            results = {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred),
                'explained_variance': explained_variance_score(y_true, y_pred)
            }
            
            # Métriques additionnelles
            try:
                results['median_ae'] = median_absolute_error(y_true, y_pred)
                results['max_error'] = max_error(y_true, y_pred)
            except ImportError:
                pass
            
            # MAPE (en évitant la division par zéro)
            non_zero_mask = y_true != 0
            if np.any(non_zero_mask):
                results['mape'] = np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100
            else:
                results['mape'] = float('inf')
            
            # Analyse des résidus
            residuals = y_true - y_pred
            results['residuals_mean'] = np.mean(residuals)
            results['residuals_std'] = np.std(residuals)
            results['residuals_skew'] = pd.Series(residuals).skew()
            results['residuals_kurtosis'] = pd.Series(residuals).kurtosis()
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans l'évaluation de régression: {e}")
            raise
    
    def _print_results(self, results, task_type):
        """Affiche les résultats de manière formatée."""
        print("\n" + "="*60)
        print(f"📊 RÉSULTATS D'ÉVALUATION ({task_type.upper()})")
        print("="*60)
        
        if task_type == 'classification':
            print(f"🎯 Accuracy: {results['accuracy']:.4f}")
            print(f"🎯 Precision (weighted): {results['precision_weighted']:.4f}")
            print(f"🎯 Recall (weighted): {results['recall_weighted']:.4f}")
            print(f"🎯 F1-Score (weighted): {results['f1_weighted']:.4f}")
            print(f"⚖️  Balanced Accuracy: {results['balanced_accuracy']:.4f}")
            print(f"🤝 Cohen's Kappa: {results['cohen_kappa']:.4f}")
            
            if 'roc_auc' in results:
                print(f"📈 ROC AUC: {results['roc_auc']:.4f}")
            if 'log_loss' in results:
                print(f"📉 Log Loss: {results['log_loss']:.4f}")
                
        else:  # regression
            print(f"📊 R² Score: {results['r2']:.4f}")
            print(f"📊 RMSE: {results['rmse']:.4f}")
            print(f"📊 MAE: {results['mae']:.4f}")
            print(f"📊 Explained Variance: {results['explained_variance']:.4f}")
            if results['mape'] != float('inf'):
                print(f"📊 MAPE: {results['mape']:.2f}%")
            print(f"📈 Residuals Std: {results['residuals_std']:.4f}")
        
        print("="*60)

class CrossValidator:
    """Validation croisée automatique."""
    
    def __init__(self, cv_folds=5, scoring='auto'):
        self.cv_folds = cv_folds
        self.scoring = scoring
        
    def validate(self, model, X, y):
        """Effectue la validation croisée."""
        if self.scoring == 'auto':
            scoring = 'accuracy' if len(np.unique(y)) <= 10 else 'r2'
        else:
            scoring = self.scoring
            
        scores = cross_val_score(model, X, y, cv=self.cv_folds, scoring=scoring)
        
        return {
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'scores': scores
        }

class MetricsCalculator:
    """Calculateur de métriques avancées."""
    
    @staticmethod
    def classification_report_dict(y_true, y_pred):
        """Rapport de classification en dictionnaire."""
        return classification_report(y_true, y_pred, output_dict=True)
    
    @staticmethod
    def regression_metrics(y_true, y_pred):
        """Métriques complètes de régression."""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        } 