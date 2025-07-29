"""
Système de cache intelligent pour EasyML
========================================

Cache automatique pour optimiser les performances des opérations répétitives.
"""

import hashlib
import pickle
import json
from pathlib import Path
from typing import Any, Dict, Optional, Callable
import time
import pandas as pd
import numpy as np
from .config import config, get_logger

logger = get_logger(__name__)

class EasyMLCache:
    """Cache intelligent pour les opérations ML."""
    
    def __init__(self, cache_dir=None, max_size_mb=500, ttl_hours=24):
        self.cache_dir = Path(cache_dir or config.get_cache_dir())
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_hours * 3600
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichier de métadonnées
        self.metadata_file = self.cache_dir / 'cache_metadata.json'
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Charge les métadonnées du cache."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_metadata(self):
        """Sauvegarde les métadonnées du cache."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Échec sauvegarde métadonnées cache: {e}")
    
    def _generate_key(self, data: Any, operation: str, **kwargs) -> str:
        """Génère une clé unique pour les données et opération."""
        # Créer un hash des données
        if isinstance(data, pd.DataFrame):
            data_hash = hashlib.md5(
                pd.util.hash_pandas_object(data, index=True).values
            ).hexdigest()
        elif isinstance(data, np.ndarray):
            data_hash = hashlib.md5(data.tobytes()).hexdigest()
        elif isinstance(data, (str, int, float, bool)):
            data_hash = hashlib.md5(str(data).encode()).hexdigest()
        else:
            # Pour d'autres types, utiliser pickle
            try:
                data_hash = hashlib.md5(pickle.dumps(data)).hexdigest()
            except:
                data_hash = hashlib.md5(str(data).encode()).hexdigest()
        
        # Créer un hash des paramètres
        params_str = json.dumps(sorted(kwargs.items()), default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"{operation}_{data_hash}_{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        if key not in self.metadata:
            return None
        
        entry = self.metadata[key]
        
        # Vérifier l'expiration
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            self.delete(key)
            return None
        
        # Charger les données
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    
                # Mettre à jour le dernier accès
                entry['last_access'] = time.time()
                self._save_metadata()
                
                logger.debug(f"🎯 Cache hit: {key}")
                return data
            except Exception as e:
                logger.warning(f"Erreur lecture cache {key}: {e}")
                self.delete(key)
        
        return None
    
    def set(self, key: str, value: Any, operation_info: str = ""):
        """Stocke une valeur dans le cache."""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            
            # Sauvegarder les données
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
            
            # Mettre à jour les métadonnées
            file_size = cache_file.stat().st_size
            self.metadata[key] = {
                'timestamp': time.time(),
                'last_access': time.time(),
                'size_bytes': file_size,
                'operation': operation_info
            }
            
            self._save_metadata()
            self._cleanup_if_needed()
            
            logger.debug(f"💾 Cache set: {key} ({file_size} bytes)")
            
        except Exception as e:
            logger.warning(f"Erreur sauvegarde cache {key}: {e}")
    
    def delete(self, key: str):
        """Supprime une entrée du cache."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()
        
        if key in self.metadata:
            del self.metadata[key]
            self._save_metadata()
    
    def clear(self):
        """Vide complètement le cache."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        
        self.metadata.clear()
        self._save_metadata()
        logger.info("🗑️ Cache vidé complètement")
    
    def _cleanup_if_needed(self):
        """Nettoie le cache si nécessaire."""
        total_size = sum(entry['size_bytes'] for entry in self.metadata.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            logger.info(f"🧹 Nettoyage cache ({total_size / 1024 / 1024:.1f} MB)")
            
            # Trier par dernier accès (LRU)
            sorted_entries = sorted(
                self.metadata.items(),
                key=lambda x: x[1]['last_access']
            )
            
            # Supprimer les plus anciens
            for key, entry in sorted_entries:
                if total_size <= max_size_bytes * 0.8:  # Garder 80% de la taille max
                    break
                
                total_size -= entry['size_bytes']
                self.delete(key)
    
    def stats(self) -> Dict:
        """Retourne les statistiques du cache."""
        total_size = sum(entry['size_bytes'] for entry in self.metadata.values())
        
        return {
            'entries': len(self.metadata),
            'total_size_mb': total_size / 1024 / 1024,
            'max_size_mb': self.max_size_mb,
            'usage_percent': (total_size / (self.max_size_mb * 1024 * 1024)) * 100,
            'cache_dir': str(self.cache_dir)
        }

# Instance globale du cache
_cache = None

def get_cache() -> EasyMLCache:
    """Retourne l'instance globale du cache."""
    global _cache
    if _cache is None:
        _cache = EasyMLCache()
    return _cache

def cached_operation(operation_name: str, ttl_hours: int = 24):
    """Décorateur pour mettre en cache les résultats d'une opération."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Générer la clé de cache
            cache_key = cache._generate_key(
                data=args[0] if args else None,
                operation=f"{func.__name__}_{operation_name}",
                **kwargs
            )
            
            # Essayer de récupérer du cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Calculer le résultat
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Mettre en cache
            operation_info = f"{func.__name__} ({execution_time:.2f}s)"
            cache.set(cache_key, result, operation_info)
            
            return result
        
        return wrapper
    return decorator 