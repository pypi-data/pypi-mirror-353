"""
Utilitaires pour EasyML
======================

Fonctions helper pour chargement, sauvegarde, exploration de données, etc.
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

from .config import config, get_logger

logger = get_logger(__name__)

def load_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Charge des données depuis différents formats de fichiers.
    
    Args:
        filepath: Chemin vers le fichier de données
        
    Returns:
        DataFrame pandas avec les données chargées
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {filepath}")
    
    # Détection automatique du format
    extension = filepath.suffix.lower()
    
    try:
        if extension == '.csv':
            # Tentative avec différents séparateurs
            try:
                data = pd.read_csv(filepath)
            except:
                try:
                    data = pd.read_csv(filepath, sep=';')
                except:
                    data = pd.read_csv(filepath, sep='\t')
        
        elif extension in ['.xlsx', '.xls']:
            data = pd.read_excel(filepath)
        
        elif extension == '.json':
            data = pd.read_json(filepath)
        
        elif extension == '.parquet':
            data = pd.read_parquet(filepath)
        
        elif extension == '.feather':
            data = pd.read_feather(filepath)
        
        elif extension == '.pkl':
            data = pd.read_pickle(filepath)
        
        else:
            # Tentative avec CSV par défaut
            data = pd.read_csv(filepath)
        
        logger.info(f"📁 Données chargées: {data.shape} depuis {filepath}")
        return data
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {filepath}: {e}")
        raise

def save_data(data: pd.DataFrame, filepath: Union[str, Path], format='auto'):
    """
    Sauvegarde des données dans différents formats.
    
    Args:
        data: DataFrame à sauvegarder
        filepath: Chemin de destination
        format: Format de sauvegarde ('auto', 'csv', 'excel', 'parquet', etc.)
    """
    filepath = Path(filepath)
    
    if format == 'auto':
        extension = filepath.suffix.lower()
    else:
        extension = f'.{format}'
        filepath = filepath.with_suffix(extension)
    
    # Créer le répertoire si nécessaire
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if extension == '.csv':
            data.to_csv(filepath, index=False)
        elif extension in ['.xlsx', '.xls']:
            data.to_excel(filepath, index=False)
        elif extension == '.json':
            data.to_json(filepath, orient='records', indent=2)
        elif extension == '.parquet':
            data.to_parquet(filepath, index=False)
        elif extension == '.feather':
            data.to_feather(filepath)
        elif extension == '.pkl':
            data.to_pickle(filepath)
        else:
            data.to_csv(filepath, index=False)
        
        logger.info(f"💾 Données sauvegardées: {filepath}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde: {e}")
        raise

def explore_data(data: Union[str, Path, pd.DataFrame], show_plots=True):
    """
    Analyse exploratoire automatique des données.
    
    Args:
        data: Données à explorer (fichier ou DataFrame)
        show_plots: Afficher les graphiques
        
    Returns:
        Dictionnaire avec les statistiques d'exploration
    """
    if isinstance(data, (str, Path)):
        data = load_data(data)
    
    logger.info("🔍 Démarrage de l'exploration des données...")
    
    exploration = {}
    
    # Informations de base
    exploration['shape'] = data.shape
    exploration['memory_usage'] = data.memory_usage(deep=True).sum() / 1024**2  # MB
    exploration['dtypes'] = data.dtypes.value_counts().to_dict()
    
    # Valeurs manquantes
    missing_info = data.isnull().sum()
    missing_pct = (missing_info / len(data) * 100).round(2)
    exploration['missing_values'] = {
        'total': missing_info.sum(),
        'by_column': missing_info[missing_info > 0].to_dict(),
        'percentages': missing_pct[missing_pct > 0].to_dict()
    }
    
    # Doublons
    exploration['duplicates'] = data.duplicated().sum()
    
    # Colonnes numériques
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        exploration['numeric_stats'] = data[numeric_cols].describe().to_dict()
        
        # Détection d'outliers (méthode IQR)
        outliers = {}
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            outlier_count = ((data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))).sum()
            if outlier_count > 0:
                outliers[col] = outlier_count
        exploration['outliers'] = outliers
    
    # Colonnes catégorielles
    categorical_cols = data.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        cat_info = {}
        for col in categorical_cols:
            unique_count = data[col].nunique()
            cat_info[col] = {
                'unique_values': unique_count,
                'most_frequent': data[col].mode().iloc[0] if len(data[col].mode()) > 0 else None,
                'frequency': data[col].value_counts().iloc[0] if len(data[col]) > 0 else 0
            }
        exploration['categorical_info'] = cat_info
    
    # Corrélations (pour colonnes numériques)
    if len(numeric_cols) > 1:
        corr_matrix = data[numeric_cols].corr()
        # Paires avec corrélation élevée
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.8:
                    high_corr.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        exploration['high_correlations'] = high_corr
    
    # Affichage des résultats
    print("📊 EXPLORATION DES DONNÉES")
    print("=" * 50)
    print(f"📏 Dimensions: {exploration['shape'][0]} lignes × {exploration['shape'][1]} colonnes")
    print(f"💾 Mémoire utilisée: {exploration['memory_usage']:.2f} MB")
    print(f"🔄 Doublons: {exploration['duplicates']}")
    
    if exploration['missing_values']['total'] > 0:
        print(f"\n❌ Valeurs manquantes: {exploration['missing_values']['total']} total")
        for col, count in exploration['missing_values']['by_column'].items():
            pct = exploration['missing_values']['percentages'][col]
            print(f"   • {col}: {count} ({pct}%)")
    
    if 'outliers' in exploration and exploration['outliers']:
        print(f"\n🎯 Outliers détectés:")
        for col, count in exploration['outliers'].items():
            print(f"   • {col}: {count} outliers")
    
    if 'high_correlations' in exploration and exploration['high_correlations']:
        print(f"\n🔗 Corrélations élevées:")
        for corr in exploration['high_correlations']:
            print(f"   • {corr['feature1']} ↔ {corr['feature2']}: {corr['correlation']:.3f}")
    
    # Graphiques
    if show_plots and len(data) > 0:
        _create_exploration_plots(data, numeric_cols, categorical_cols)
    
    return exploration

def _create_exploration_plots(data, numeric_cols, categorical_cols):
    """Crée les graphiques d'exploration."""
    plt.style.use('default')
    
    # Graphique 1: Distribution des variables numériques
    if len(numeric_cols) > 0:
        n_cols = min(4, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        if len(numeric_cols) <= 4:
            fig, axes = plt.subplots(1, len(numeric_cols), figsize=(4*len(numeric_cols), 4))
            if len(numeric_cols) == 1:
                axes = [axes]
        else:
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows))
            axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols):
            if i < len(axes):
                axes[i].hist(data[col].dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                axes[i].set_title(f'Distribution: {col}')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Fréquence')
        
        # Masquer les axes non utilisés
        for i in range(len(numeric_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    # Graphique 2: Matrice de corrélation
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        corr_matrix = data[numeric_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f')
        plt.title('Matrice de Corrélation')
        plt.tight_layout()
        plt.show()
    
    # Graphique 3: Top variables catégorielles
    if len(categorical_cols) > 0:
        # Prendre les 4 premières variables catégorielles
        top_cats = categorical_cols[:4]
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()
        
        for i, col in enumerate(top_cats):
            if i < 4:
                value_counts = data[col].value_counts().head(10)
                axes[i].bar(range(len(value_counts)), value_counts.values, color='lightcoral')
                axes[i].set_title(f'Top 10: {col}')
                axes[i].set_xticks(range(len(value_counts)))
                axes[i].set_xticklabels(value_counts.index, rotation=45, ha='right')
                axes[i].set_ylabel('Count')
        
        # Masquer les axes non utilisés
        for i in range(len(top_cats), 4):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()

def compare_models(models_dict: Dict[str, Any], data, target, cv_folds=5):
    """
    Compare plusieurs modèles sur les mêmes données.
    
    Args:
        models_dict: Dictionnaire {nom: modèle}
        data: Données d'entrée
        target: Variable cible
        cv_folds: Nombre de folds pour la validation croisée
        
    Returns:
        DataFrame avec les résultats de comparaison
    """
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import accuracy_score, mean_squared_error
    
    if isinstance(data, (str, Path)):
        data = load_data(data)
    
    # Préparation des données
    if isinstance(target, str):
        X = data.drop(columns=[target])
        y = data[target]
    else:
        X = data
        y = target
    
    # Preprocessing basique
    from .preprocessing import DataCleaner
    cleaner = DataCleaner()
    X_clean = cleaner.fit_transform(X)
    
    results = []
    
    logger.info("🏁 Comparaison des modèles...")
    
    for name, model in models_dict.items():
        try:
            # Déterminer le type de scoring
            if hasattr(y, 'nunique') and y.nunique() <= 10:
                scoring = 'accuracy'
            else:
                scoring = 'neg_mean_squared_error'
            
            # Validation croisée
            scores = cross_val_score(model, X_clean, y, cv=cv_folds, scoring=scoring)
            
            results.append({
                'Model': name,
                'Mean_Score': scores.mean(),
                'Std_Score': scores.std(),
                'Min_Score': scores.min(),
                'Max_Score': scores.max()
            })
            
            logger.info(f"✓ {name}: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
            
        except Exception as e:
            logger.warning(f"❌ Erreur avec {name}: {e}")
            continue
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Mean_Score', ascending=False)
    
    # Graphique de comparaison
    if len(results_df) > 0:
        plt.figure(figsize=(10, 6))
        plt.bar(results_df['Model'], results_df['Mean_Score'], 
                yerr=results_df['Std_Score'], capsize=5, alpha=0.7)
        plt.title('Comparaison des Modèles')
        plt.ylabel('Score de Validation Croisée')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    return results_df

def save_model(model, filepath: Union[str, Path]):
    """
    Sauvegarde un modèle.
    
    Args:
        model: Modèle à sauvegarder
        filepath: Chemin de destination
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if not filepath.suffix:
        filepath = filepath.with_suffix('.pkl')
    
    joblib.dump(model, filepath)
    logger.info(f"💾 Modèle sauvegardé: {filepath}")

def load_model(filepath: Union[str, Path]):
    """
    Charge un modèle sauvegardé.
    
    Args:
        filepath: Chemin vers le modèle
        
    Returns:
        Modèle chargé
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Modèle non trouvé: {filepath}")
    
    model = joblib.load(filepath)
    logger.info(f"📁 Modèle chargé: {filepath}")
    return model

def deploy_model(model, model_name: str, create_api=True):
    """
    Déploie un modèle (version simple).
    
    Args:
        model: Modèle à déployer
        model_name: Nom du modèle
        create_api: Créer une API simple
    """
    from datetime import datetime
    
    # Sauvegarde avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = config.get_models_dir() / f"{model_name}_{timestamp}.pkl"
    
    save_model(model, model_path)
    
    if create_api:
        # Création d'un script API simple
        api_code = f'''
"""
API simple pour le modèle {model_name}
Généré automatiquement par EasyML
"""

import joblib
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)
model = joblib.load('{model_path}')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        df = pd.DataFrame(data)
        predictions = model.predict(df)
        return jsonify({{'predictions': predictions.tolist()}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({{'status': 'healthy', 'model': '{model_name}'}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        api_path = config.get_models_dir() / f"{model_name}_api.py"
        with open(api_path, 'w') as f:
            f.write(api_code)
        
        logger.info(f"🚀 API créée: {api_path}")
        logger.info("💡 Pour lancer l'API: python " + str(api_path))
    
    return model_path

def create_sample_data(dataset_type='classification', n_samples=1000, n_features=10):
    """
    Crée des données d'exemple pour tester EasyML.
    
    Args:
        dataset_type: Type de dataset ('classification', 'regression', 'text')
        n_samples: Nombre d'échantillons
        n_features: Nombre de features
        
    Returns:
        DataFrame avec les données d'exemple
    """
    from sklearn.datasets import make_classification, make_regression
    
    if dataset_type == 'classification':
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_features//2,
            n_redundant=n_features//4,
            n_classes=3,
            random_state=42
        )
        
        # Conversion en DataFrame
        df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        df['target'] = y
        
        # Ajout de quelques valeurs manquantes
        df.loc[df.sample(n=n_samples//20).index, 'feature_0'] = np.nan
        
    elif dataset_type == 'regression':
        X, y = make_regression(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_features//2,
            noise=0.1,
            random_state=42
        )
        
        df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        df['target'] = y
        
    elif dataset_type == 'text':
        # Dataset de sentiment simple
        texts = [
            "This product is amazing!", "I love it so much",
            "Great quality and fast delivery", "Highly recommended",
            "This is terrible", "Worst purchase ever",
            "Complete waste of money", "Very disappointed",
            "It's okay, nothing special", "Average product"
        ] * (n_samples // 10)
        
        sentiments = ['positive'] * (n_samples // 3) + \
                    ['negative'] * (n_samples // 3) + \
                    ['neutral'] * (n_samples - 2 * (n_samples // 3))
        
        df = pd.DataFrame({
            'text': texts[:n_samples],
            'sentiment': sentiments
        })
    
    logger.info(f"📝 Données d'exemple créées: {df.shape} ({dataset_type})")
    return df 