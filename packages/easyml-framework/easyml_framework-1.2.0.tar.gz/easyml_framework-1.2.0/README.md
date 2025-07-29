# 🚀 EasyML Framework

Un framework Machine Learning simplifié et complet pour Python qui rend l'IA accessible à tous.

## ✨ Fonctionnalités

- **🔧 AutoML** - Machine Learning automatisé en quelques lignes
- **📊 Preprocessing** - Nettoyage et préparation de données intelligent
- **🤖 Modèles** - Classification, régression, clustering, NLP
- **📈 Visualisation** - Graphiques et métriques automatiques
- **🚀 Déploiement** - Export de modèles prêts pour la production
- **⚡ Performance** - Optimisations automatiques et parallélisation

## 🛠️ Installation

```bash
# Installation de base
pip install easyml-framework

# Installation complète avec toutes les dépendances
pip install easyml-framework[deep,nlp,viz]

# Installation en mode développement
pip install easyml-framework[dev]
```

## 🚀 Démarrage Rapide

### Classification Automatique

```python
import easyml as ez

# Charger vos données
model = ez.AutoClassifier()
model.fit('data.csv', target='label')

# Prédictions automatiques
predictions = model.predict('new_data.csv')

# Évaluation complète
model.evaluate()
```

### Preprocessing Intelligent

```python
# Nettoyage automatique
cleaner = ez.DataCleaner()
clean_data = cleaner.transform('messy_data.csv')

# Feature engineering
features = ez.FeatureEngine()
enhanced_data = features.generate_features(clean_data)
```

### Visualisation Automatique

```python
# Analyse exploratoire automatique
ez.explore_data('data.csv')

# Visualisation de modèle
model.plot_results()
model.plot_feature_importance()
```

## 📚 Exemples Complets

### Prédiction de Prix Immobilier

```python
import easyml as ez

# 1. Chargement et exploration
data = ez.load_data('houses.csv')
ez.explore_data(data)

# 2. Preprocessing automatique
cleaner = ez.DataCleaner(auto_encode=True, handle_missing='smart')
data_clean = cleaner.fit_transform(data)

# 3. Modèle de régression
model = ez.AutoRegressor(optimization='auto', cv_folds=5)
model.fit(data_clean, target='price')

# 4. Évaluation et export
results = model.evaluate()
model.save('house_price_model.pkl')
```

### Classification de Sentiment

```python
import easyml as ez

# NLP automatique
nlp_model = ez.TextClassifier()
nlp_model.fit('reviews.csv', text_column='comment', target='sentiment')

# Prédiction sur nouveau texte
sentiment = nlp_model.predict("Ce produit est fantastique!")
print(f"Sentiment: {sentiment}")  # Positif
```

## 🔧 API Complète

### Classes Principales

- **`ez.AutoClassifier()`** - Classification automatique
- **`ez.AutoRegressor()`** - Régression automatique
- **`ez.TextClassifier()`** - Classification de texte
- **`ez.TimeSeriesPredictor()`** - Prédiction temporelle
- **`ez.ClusterAnalyzer()`** - Analyse de clustering
- **`ez.DataCleaner()`** - Nettoyage de données
- **`ez.FeatureEngine()`** - Feature engineering

### Utilitaires

- **`ez.load_data()`** - Chargement intelligent de données
- **`ez.explore_data()`** - Analyse exploratoire automatique
- **`ez.compare_models()`** - Comparaison de modèles
- **`ez.deploy_model()`** - Déploiement en API

## 📊 Métriques et Visualisations

EasyML génère automatiquement :

- Matrices de confusion
- Courbes ROC et AUC
- Feature importance
- Courbes d'apprentissage
- Analyse de résidus
- Métriques de performance complètes

## 🚀 Installation et Tests

```bash
# Cloner le repository
git clone https://github.com/easyml/easyml-framework.git
cd easyml-framework

# Installation en mode développement
pip install -e .[dev]

# Lancer les tests
pytest tests/

# Lancer les exemples
python examples/classification_example.py
```

## 📖 Documentation

- [Guide Utilisateur Complet](docs/user_guide.md)
- [Référence API](docs/api_reference.md)
- [Exemples Avancés](examples/)
- [Tutoriels Vidéo](docs/tutorials.md)

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

## 🆘 Support

- 📧 Email: support@easyml.dev
- 💬 Discord: [EasyML Community](https://discord.gg/easyml)
- 🐛 Issues: [GitHub Issues](https://github.com/easyml/easyml-framework/issues) 