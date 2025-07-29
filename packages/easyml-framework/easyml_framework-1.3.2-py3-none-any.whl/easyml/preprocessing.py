"""
Preprocessing et Feature Engineering pour EasyML
===============================================

Classes pour nettoyer, transformer et enrichir les données.
"""

import numpy as np
import pandas as pd
import re
from typing import Union, List, Dict, Any, Optional
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    LabelEncoder, OneHotEncoder, OrdinalEncoder
)
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
import warnings
warnings.filterwarnings('ignore')

from .config import config, get_logger

logger = get_logger(__name__)

class DataCleaner:
    """Nettoyage automatique des données."""
    
    def __init__(self, 
                 handle_missing='auto',
                 remove_duplicates=True,
                 auto_encode=True,
                 remove_outliers=False,
                 outlier_method='iqr'):
        self.handle_missing = handle_missing
        self.remove_duplicates = remove_duplicates
        self.auto_encode = auto_encode
        self.remove_outliers = remove_outliers
        self.outlier_method = outlier_method
        
        # Stockage des transformations
        self.imputers = {}
        self.encoders = {}
        self.feature_types = {}
        self.outlier_bounds = {}
        self.columns_to_drop = []
        self.is_fitted = False
        
    def fit(self, data):
        """Ajuste le nettoyeur sur les données d'entraînement."""
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        self.original_columns = list(data.columns)
        self._analyze_features(data)
        self._prepare_imputers(data)
        self._prepare_encoders(data)
        
        if self.remove_outliers:
            self._detect_outliers(data)
        
        self.is_fitted = True
        logger.info("🧹 DataCleaner ajusté avec succès")
        return self
    
    def transform(self, data):
        """Transforme les données selon les règles apprises."""
        if not self.is_fitted:
            raise RuntimeError("DataCleaner doit être ajusté avant la transformation")
        
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        data_clean = data.copy()
        
        # Suppression des doublons
        if self.remove_duplicates:
            initial_rows = len(data_clean)
            data_clean = data_clean.drop_duplicates()
            removed_rows = initial_rows - len(data_clean)
            if removed_rows > 0:
                logger.info(f"🗑️ {removed_rows} doublons supprimés")
        
        # Gestion des valeurs manquantes
        data_clean = self._handle_missing_values(data_clean)
        
        # Suppression des outliers
        if self.remove_outliers:
            data_clean = self._remove_outliers(data_clean)
        
        # Encodage automatique
        if self.auto_encode:
            data_clean = self._encode_features(data_clean)
        
        # Suppression des colonnes inutiles
        data_clean = data_clean.drop(columns=self.columns_to_drop, errors='ignore')
        
        logger.info(f"✅ Données nettoyées: {data_clean.shape}")
        return data_clean
    
    def fit_transform(self, data):
        """Ajuste et transforme les données en une seule étape."""
        return self.fit(data).transform(data)
    
    def _analyze_features(self, data):
        """Analyse les types de features."""
        self.feature_types = {}
        
        for col in data.columns:
            if data[col].dtype in ['int64', 'float64']:
                # Numérique - vérifier si c'est catégoriel
                unique_vals = data[col].nunique()
                if unique_vals <= 10 and unique_vals < len(data) * 0.05:
                    self.feature_types[col] = 'categorical_numeric'
                else:
                    self.feature_types[col] = 'numeric'
            elif data[col].dtype == 'object':
                # Texte - vérifier si c'est catégoriel ou texte libre
                unique_vals = data[col].nunique()
                if unique_vals <= 50 and unique_vals < len(data) * 0.5:
                    self.feature_types[col] = 'categorical_text'
                else:
                    self.feature_types[col] = 'text'
            elif data[col].dtype == 'datetime64[ns]':
                self.feature_types[col] = 'datetime'
            else:
                self.feature_types[col] = 'other'
        
        logger.info(f"📊 Types de features détectés: {len(self.feature_types)} colonnes")
    
    def _prepare_imputers(self, data):
        """Prépare les imputeurs pour les valeurs manquantes."""
        self.imputers = {}
        
        for col in data.columns:
            if data[col].isnull().sum() > 0:
                feature_type = self.feature_types[col]
                
                if feature_type in ['numeric']:
                    if self.handle_missing == 'auto':
                        # KNN pour les features numériques avec peu de missing
                        if data[col].isnull().sum() / len(data) < 0.2:
                            self.imputers[col] = KNNImputer(n_neighbors=5)
                        else:
                            self.imputers[col] = SimpleImputer(strategy='median')
                    else:
                        self.imputers[col] = SimpleImputer(strategy=self.handle_missing)
                
                elif feature_type in ['categorical_text', 'categorical_numeric']:
                    self.imputers[col] = SimpleImputer(strategy='most_frequent')
                
                else:
                    self.imputers[col] = SimpleImputer(strategy='constant', fill_value='unknown')
                
                # Ajuster l'imputeur
                if feature_type == 'numeric':
                    self.imputers[col].fit(data[col].values.reshape(-1, 1))
                else:
                    self.imputers[col].fit(data[[col]])
    
    def _handle_missing_values(self, data):
        """Gère les valeurs manquantes."""
        data_clean = data.copy()
        
        for col, imputer in self.imputers.items():
            if col in data_clean.columns:
                feature_type = self.feature_types[col]
                
                if feature_type == 'numeric':
                    data_clean[col] = imputer.transform(data_clean[col].values.reshape(-1, 1)).flatten()
                else:
                    data_clean[col] = imputer.transform(data_clean[[col]])[:, 0]
        
        return data_clean
    
    def _prepare_encoders(self, data):
        """Prépare les encodeurs pour les variables catégorielles."""
        self.encoders = {}
        
        for col in data.columns:
            feature_type = self.feature_types[col]
            
            if feature_type in ['categorical_text']:
                unique_vals = data[col].nunique()
                
                if unique_vals <= 10:
                    # One-hot encoding pour peu de catégories
                    self.encoders[col] = OneHotEncoder(sparse=False, handle_unknown='ignore')
                    self.encoders[col].fit(data[[col]])
                else:
                    # Label encoding pour beaucoup de catégories
                    self.encoders[col] = LabelEncoder()
                    self.encoders[col].fit(data[col].dropna())
            
            elif feature_type == 'datetime':
                # Les dates seront décomposées en features
                pass
    
    def _encode_features(self, data):
        """Encode les variables catégorielles."""
        data_clean = data.copy()
        
        for col, encoder in self.encoders.items():
            if col in data_clean.columns:
                if isinstance(encoder, OneHotEncoder):
                    # One-hot encoding
                    encoded = encoder.transform(data_clean[[col]])
                    feature_names = [f"{col}_{cat}" for cat in encoder.categories_[0]]
                    
                    # Remplacer la colonne originale
                    data_clean = data_clean.drop(columns=[col])
                    encoded_df = pd.DataFrame(encoded, columns=feature_names, index=data_clean.index)
                    data_clean = pd.concat([data_clean, encoded_df], axis=1)
                
                elif isinstance(encoder, LabelEncoder):
                    # Label encoding
                    data_clean[col] = encoder.transform(data_clean[col])
        
        # Traitement des dates
        for col in data_clean.columns:
            if self.feature_types.get(col) == 'datetime':
                if data_clean[col].dtype == 'datetime64[ns]':
                    # Extraction de features temporelles
                    data_clean[f"{col}_year"] = data_clean[col].dt.year
                    data_clean[f"{col}_month"] = data_clean[col].dt.month
                    data_clean[f"{col}_day"] = data_clean[col].dt.day
                    data_clean[f"{col}_dayofweek"] = data_clean[col].dt.dayofweek
                    
                    # Supprimer la colonne date originale
                    data_clean = data_clean.drop(columns=[col])
        
        return data_clean
    
    def _detect_outliers(self, data):
        """Détecte les outliers dans les données numériques."""
        self.outlier_bounds = {}
        
        for col in data.columns:
            if self.feature_types.get(col) == 'numeric':
                if self.outlier_method == 'iqr':
                    Q1 = data[col].quantile(0.25)
                    Q3 = data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                elif self.outlier_method == 'zscore':
                    mean = data[col].mean()
                    std = data[col].std()
                    
                    lower_bound = mean - 3 * std
                    upper_bound = mean + 3 * std
                
                self.outlier_bounds[col] = (lower_bound, upper_bound)
    
    def _remove_outliers(self, data):
        """Supprime les outliers."""
        data_clean = data.copy()
        initial_rows = len(data_clean)
        
        for col, (lower, upper) in self.outlier_bounds.items():
            if col in data_clean.columns:
                data_clean = data_clean[
                    (data_clean[col] >= lower) & (data_clean[col] <= upper)
                ]
        
        removed_rows = initial_rows - len(data_clean)
        if removed_rows > 0:
            logger.info(f"🎯 {removed_rows} outliers supprimés")
        
        return data_clean

class FeatureEngine:
    """Génération automatique de features."""
    
    def __init__(self, 
                 create_polynomials=True,
                 create_interactions=True,
                 create_aggregations=True,
                 max_features=None):
        self.create_polynomials = create_polynomials
        self.create_interactions = create_interactions
        self.create_aggregations = create_aggregations
        self.max_features = max_features or config.get('max_features_auto')
        
        self.feature_selector = None
        self.numeric_columns = []
        self.is_fitted = False
    
    def fit(self, data, target=None):
        """Ajuste le générateur de features."""
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        self.numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Si une cible est fournie, préparer le sélecteur de features
        if target is not None:
            if isinstance(target, str) and target in data.columns:
                y = data[target]
                X = data.drop(columns=[target])
            else:
                y = target
                X = data
            
            # Déterminer le type de tâche
            if y.dtype in ['int64', 'float64'] and y.nunique() > 10:
                score_func = f_regression
            else:
                score_func = f_classif
            
            self.feature_selector = SelectKBest(
                score_func=score_func, 
                k=min(self.max_features, len(X.columns))
            )
        
        self.is_fitted = True
        logger.info("🔧 FeatureEngine ajusté avec succès")
        return self
    
    def transform(self, data):
        """Génère de nouvelles features."""
        if not self.is_fitted:
            raise RuntimeError("FeatureEngine doit être ajusté avant la transformation")
        
        if isinstance(data, str):
            from .utils import load_data
            data = load_data(data)
        
        data_enhanced = data.copy()
        initial_features = len(data_enhanced.columns)
        
        # Features polynomiales
        if self.create_polynomials:
            data_enhanced = self._create_polynomial_features(data_enhanced)
        
        # Features d'interaction
        if self.create_interactions:
            data_enhanced = self._create_interaction_features(data_enhanced)
        
        # Features d'agrégation
        if self.create_aggregations:
            data_enhanced = self._create_aggregation_features(data_enhanced)
        
        # Sélection des meilleures features
        if self.feature_selector is not None:
            data_enhanced = self._select_best_features(data_enhanced)
        
        final_features = len(data_enhanced.columns)
        logger.info(f"✨ Features générées: {initial_features} → {final_features}")
        
        return data_enhanced
    
    def fit_transform(self, data, target=None):
        """Ajuste et transforme en une seule étape."""
        return self.fit(data, target).transform(data)
    
    def _create_polynomial_features(self, data):
        """Crée des features polynomiales."""
        for col in self.numeric_columns:
            if col in data.columns:
                # Carré
                data[f"{col}_squared"] = data[col] ** 2
                
                # Racine carrée (pour valeurs positives)
                if (data[col] >= 0).all():
                    data[f"{col}_sqrt"] = np.sqrt(data[col])
                
                # Log (pour valeurs positives)
                if (data[col] > 0).all():
                    data[f"{col}_log"] = np.log(data[col])
        
        return data
    
    def _create_interaction_features(self, data):
        """Crée des features d'interaction."""
        numeric_cols = [col for col in self.numeric_columns if col in data.columns]
        
        # Limiter le nombre d'interactions pour éviter l'explosion
        max_interactions = min(10, len(numeric_cols) * (len(numeric_cols) - 1) // 2)
        interactions_created = 0
        
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                if interactions_created >= max_interactions:
                    break
                
                # Produit
                data[f"{col1}_x_{col2}"] = data[col1] * data[col2]
                
                # Ratio (éviter division par zéro)
                if (data[col2] != 0).all():
                    data[f"{col1}_div_{col2}"] = data[col1] / data[col2]
                
                interactions_created += 1
        
        return data
    
    def _create_aggregation_features(self, data):
        """Crée des features d'agrégation."""
        numeric_cols = [col for col in self.numeric_columns if col in data.columns]
        
        if len(numeric_cols) > 1:
            # Statistiques globales
            data['total_sum'] = data[numeric_cols].sum(axis=1)
            data['total_mean'] = data[numeric_cols].mean(axis=1)
            data['total_std'] = data[numeric_cols].std(axis=1)
            data['total_max'] = data[numeric_cols].max(axis=1)
            data['total_min'] = data[numeric_cols].min(axis=1)
        
        return data
    
    def _select_best_features(self, data):
        """Sélectionne les meilleures features."""
        # Cette méthode nécessiterait la cible pour la sélection
        # Pour l'instant, on garde toutes les features
        return data

class TextProcessor:
    """Preprocessing de texte."""
    
    def __init__(self, 
                 lowercase=True,
                 remove_punctuation=True,
                 remove_numbers=False,
                 remove_stopwords=True,
                 stemming=False):
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_stopwords = remove_stopwords
        self.stemming = stemming
        
        self.is_fitted = False
        
        # Stopwords de base (anglais)
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 
            'that', 'the', 'to', 'was', 'will', 'with', 'the', 'this'
        }
    
    def fit(self, texts):
        """Ajuste le processeur de texte."""
        self.is_fitted = True
        logger.info("📝 TextProcessor ajusté avec succès")
        return self
    
    def transform(self, texts):
        """Transforme les textes."""
        if not self.is_fitted:
            raise RuntimeError("TextProcessor doit être ajusté avant la transformation")
        
        if isinstance(texts, str):
            texts = [texts]
        
        processed_texts = []
        
        for text in texts:
            if pd.isna(text):
                processed_texts.append("")
                continue
            
            processed = str(text)
            
            # Minuscules
            if self.lowercase:
                processed = processed.lower()
            
            # Suppression de la ponctuation
            if self.remove_punctuation:
                processed = re.sub(r'[^\w\s]', '', processed)
            
            # Suppression des nombres
            if self.remove_numbers:
                processed = re.sub(r'\d+', '', processed)
            
            # Suppression des stopwords
            if self.remove_stopwords:
                words = processed.split()
                words = [word for word in words if word not in self.stopwords]
                processed = ' '.join(words)
            
            # Nettoyage des espaces
            processed = ' '.join(processed.split())
            
            processed_texts.append(processed)
        
        return processed_texts
    
    def fit_transform(self, texts):
        """Ajuste et transforme en une seule étape."""
        return self.fit(texts).transform(texts) 