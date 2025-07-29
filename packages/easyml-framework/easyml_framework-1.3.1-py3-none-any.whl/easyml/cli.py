"""
Interface en ligne de commande pour EasyML
==========================================
"""

import argparse
import sys
from pathlib import Path
from . import __version__, quick_start, list_models
from .utils import explore_data, create_sample_data
from .models import AutoClassifier, AutoRegressor
from .config import get_logger

logger = get_logger(__name__)

def main():
    """Point d'entrée principal du CLI."""
    parser = argparse.ArgumentParser(
        description='EasyML - Framework ML simplifié',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemples:
  easyml --version                    # Afficher la version
  easyml --quick-start               # Guide de démarrage
  easyml --explore data.csv          # Explorer des données
  easyml --sample classification     # Créer des données d'exemple
  easyml --auto-classify data.csv target  # Classification automatique
        '''
    )
    
    parser.add_argument('--version', action='version', version=f'EasyML {__version__}')
    parser.add_argument('--quick-start', action='store_true', help='Afficher le guide de démarrage')
    parser.add_argument('--list-models', action='store_true', help='Lister les modèles disponibles')
    parser.add_argument('--explore', type=str, help='Explorer un fichier de données')
    parser.add_argument('--sample', choices=['classification', 'regression', 'text'], 
                       help='Créer des données d\'exemple')
    parser.add_argument('--auto-classify', nargs=2, metavar=('DATA', 'TARGET'),
                       help='Classification automatique')
    parser.add_argument('--auto-regress', nargs=2, metavar=('DATA', 'TARGET'),
                       help='Régression automatique')
    
    args = parser.parse_args()
    
    if args.quick_start:
        quick_start()
    
    elif args.list_models:
        models = list_models()
        print("🤖 Modèles disponibles:")
        for model in models:
            print(f"  • {model}")
    
    elif args.explore:
        try:
            explore_data(args.explore)
        except Exception as e:
            logger.error(f"Erreur lors de l'exploration: {e}")
            sys.exit(1)
    
    elif args.sample:
        try:
            data = create_sample_data(args.sample)
            filename = f"sample_{args.sample}.csv"
            data.to_csv(filename, index=False)
            print(f"📝 Données d'exemple créées: {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de la création d'échantillon: {e}")
            sys.exit(1)
    
    elif args.auto_classify:
        try:
            data_file, target = args.auto_classify
            model = AutoClassifier()
            model.fit(data_file, target=target)
            model_file = f"auto_classifier_{target}.pkl"
            model.save(model_file)
            print(f"🏆 Modèle de classification sauvegardé: {model_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la classification: {e}")
            sys.exit(1)
    
    elif args.auto_regress:
        try:
            data_file, target = args.auto_regress
            model = AutoRegressor()
            model.fit(data_file, target=target)
            model_file = f"auto_regressor_{target}.pkl"
            model.save(model_file)
            print(f"🏆 Modèle de régression sauvegardé: {model_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la régression: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 