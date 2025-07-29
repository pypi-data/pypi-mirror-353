"""
Visualisation pour EasyML
========================

Fonctions de visualisation automatique pour modèles et données.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc
from .config import get_logger

logger = get_logger(__name__)

def plot_confusion_matrix(y_true, y_pred, labels=None, figsize=(8, 6)):
    """Affiche la matrice de confusion."""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=figsize)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Matrice de Confusion')
    plt.xlabel('Prédictions')
    plt.ylabel('Vérité')
    plt.show()

def plot_roc_curve(y_true, y_score, figsize=(8, 6)):
    """Affiche la courbe ROC."""
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=figsize)
    plt.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('Taux de Faux Positifs')
    plt.ylabel('Taux de Vrais Positifs')
    plt.title('Courbe ROC')
    plt.legend()
    plt.show()

def plot_feature_importance(model, feature_names=None, top_n=15, figsize=(10, 8)):
    """Affiche l'importance des features."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0])
    else:
        logger.warning("Le modèle ne supporte pas l'importance des features")
        return
    
    if feature_names is None:
        feature_names = [f'Feature_{i}' for i in range(len(importances))]
    
    # Tri par importance
    indices = np.argsort(importances)[::-1][:top_n]
    
    plt.figure(figsize=figsize)
    plt.bar(range(len(indices)), importances[indices])
    plt.title('Importance des Features')
    plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=45)
    plt.tight_layout()
    plt.show()

def plot_learning_curve(train_scores, val_scores, figsize=(10, 6)):
    """Affiche les courbes d'apprentissage."""
    plt.figure(figsize=figsize)
    plt.plot(train_scores, label='Score d\'entraînement', marker='o')
    plt.plot(val_scores, label='Score de validation', marker='s')
    plt.title('Courbes d\'Apprentissage')
    plt.xlabel('Époque/Itération')
    plt.ylabel('Score')
    plt.legend()
    plt.show() 