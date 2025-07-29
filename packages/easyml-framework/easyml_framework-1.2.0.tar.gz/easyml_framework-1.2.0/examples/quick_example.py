#!/usr/bin/env python3
"""
Exemple rapide d'utilisation d'EasyML
=====================================

Ce script montre comment utiliser EasyML en quelques lignes.
"""

import sys
sys.path.insert(0, '..')

import easyml as ez

def main():
    print("🚀 Exemple EasyML - Classification Automatique")
    print("=" * 50)
    
    # 1. Création de données d'exemple
    print("📝 Création de données d'exemple...")
    data = ez.create_sample_data('classification', n_samples=1000, n_features=10)
    print(f"✅ Données créées: {data.shape}")
    
    # 2. Exploration rapide
    print("\n🔍 Exploration des données...")
    ez.explore_data(data, show_plots=False)
    
    # 3. Classification automatique
    print("\n🤖 Classification automatique...")
    model = ez.AutoClassifier()
    model.fit(data, target='target')
    
    # 4. Prédictions sur de nouvelles données
    print("\n🎯 Test de prédiction...")
    new_data = ez.create_sample_data('classification', n_samples=100, n_features=10)
    new_data = new_data.drop(columns=['target'])  # Supprimer la cible
    
    predictions = model.predict(new_data)
    print(f"✅ Prédictions effectuées: {len(predictions)} échantillons")
    print(f"📊 Classes prédites: {set(predictions)}")
    
    # 5. Évaluation
    print("\n📈 Évaluation du modèle...")
    print(f"Score d'entraînement: {model.training_score:.3f}")
    print(f"Score de validation: {model.validation_score:.3f}")
    print(f"Meilleur modèle: {model.best_model_name}")
    
    print("\n🎉 Exemple terminé avec succès!")

if __name__ == '__main__':
    main() 