"""
Monitoring léger pour EasyML
============================

Surveillance automatique des performances des modèles.
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from collections import deque
import json
from datetime import datetime
import threading

from .config import get_logger, config

logger = get_logger(__name__)

class ModelMonitor:
    """Surveillant de modèle ML léger et efficace."""
    
    def __init__(self, model_name: str, window_size: int = 1000):
        self.model_name = model_name
        self.window_size = window_size
        
        # Historiques avec limite de mémoire
        self.predictions_times = deque(maxlen=window_size)
        self.error_count = 0
        self.total_predictions = 0
        self.baseline_time = None
        
        # Thread-safety
        self.lock = threading.Lock()
        
        logger.info(f"🔍 Monitor activé pour {model_name}")
    
    def log_prediction(self, input_data: Any, prediction: Any, execution_time: float):
        """Enregistre une prédiction et son temps d'exécution."""
        with self.lock:
            self.predictions_times.append(execution_time)
            self.total_predictions += 1
            
            # Établir baseline après 50 prédictions
            if self.baseline_time is None and len(self.predictions_times) >= 50:
                self.baseline_time = np.mean(list(self.predictions_times)[-50:])
                logger.info(f"📈 Baseline établi: {self.baseline_time:.3f}s")
            
            # Alerte si performance dégradée
            if (self.baseline_time and 
                len(self.predictions_times) >= 10 and
                execution_time > self.baseline_time * 3):
                
                recent_avg = np.mean(list(self.predictions_times)[-10:])
                if recent_avg > self.baseline_time * 2:
                    logger.warning(f"🚨 Performance dégradée pour {self.model_name}: "
                                 f"{recent_avg:.3f}s vs {self.baseline_time:.3f}s baseline")
    
    def log_error(self, error: Exception):
        """Enregistre une erreur."""
        with self.lock:
            self.error_count += 1
            error_rate = self.error_count / max(1, self.total_predictions)
            
            if error_rate > 0.01:  # Plus de 1% d'erreurs
                logger.warning(f"🚨 Taux d'erreur élevé pour {self.model_name}: {error_rate:.2%}")
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques actuelles."""
        with self.lock:
            if not self.predictions_times:
                return {'status': 'no_data'}
            
            times = list(self.predictions_times)
            return {
                'total_predictions': self.total_predictions,
                'error_count': self.error_count,
                'error_rate': self.error_count / max(1, self.total_predictions),
                'avg_time': np.mean(times),
                'p95_time': np.percentile(times, 95),
                'baseline_time': self.baseline_time,
                'status': 'healthy' if self.error_count / max(1, self.total_predictions) < 0.01 else 'degraded'
            }

# Décorateur pour surveiller automatiquement
def monitored(model_name: str):
    """Décorateur pour surveillance automatique des prédictions."""
    monitor = ModelMonitor(model_name)
    
    def decorator(predict_func):
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            
            try:
                result = predict_func(self, *args, **kwargs)
                execution_time = time.time() - start_time
                
                monitor.log_prediction(
                    input_data=args[0] if args else None,
                    prediction=result,
                    execution_time=execution_time
                )
                
                return result
                
            except Exception as e:
                monitor.log_error(e)
                raise
                
        wrapper._monitor = monitor
        return wrapper
    return decorator

class PerformanceProfiler:
    """Profileur simple pour les opérations ML."""
    
    def __init__(self):
        self.profiles = {}
    
    def profile(self, operation_name: str):
        """Décorateur de profiling."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    if operation_name not in self.profiles:
                        self.profiles[operation_name] = []
                    
                    self.profiles[operation_name].append(duration)
                    
                    # Garder seulement les 100 dernières mesures
                    if len(self.profiles[operation_name]) > 100:
                        self.profiles[operation_name] = self.profiles[operation_name][-100:]
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Erreur dans {operation_name}: {e}")
                    raise
                    
            return wrapper
        return decorator
    
    def get_stats(self, operation_name: str = None) -> Dict:
        """Stats du profiling."""
        if operation_name:
            times = self.profiles.get(operation_name, [])
            if not times:
                return {}
            
            return {
                'operation': operation_name,
                'count': len(times),
                'avg_time': np.mean(times),
                'min_time': np.min(times),
                'max_time': np.max(times),
                'p95_time': np.percentile(times, 95)
            }
        else:
            return {name: self.get_stats(name) for name in self.profiles.keys()}

# Instance globale
_profiler = PerformanceProfiler()

def profile(operation_name: str):
    """Décorateur global de profiling."""
    return _profiler.profile(operation_name)

def get_profile_stats(operation_name: str = None):
    """Stats du profileur global."""
    return _profiler.get_stats(operation_name) 