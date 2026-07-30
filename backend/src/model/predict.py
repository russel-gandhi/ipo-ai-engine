import joblib
import pandas as pd
import os
import warnings

# Suppress sklearn warnings about feature names
warnings.filterwarnings("ignore", category=UserWarning)

# Global variables to cache models in memory
_classifier = None
_regressor = None
_baseline = None
_residual_std = None
_df_historical = None

def _load_models():
    global _classifier, _regressor, _baseline, _residual_std, _df_historical
    if _classifier is None or _regressor is None:
        base_dir = os.path.dirname(__file__)
        models_dir = os.path.join(base_dir, '..', '..', 'models')
        data_path = os.path.join(base_dir, '..', 'data', 'historical_ipos.csv')
        
        clf_path = os.path.join(models_dir, 'ipo_xgb_classifier_v1.pkl')
        reg_path = os.path.join(models_dir, 'ipo_xgb_regressor_v1.pkl')
        base_path = os.path.join(models_dir, 'ipo_baseline_classifier_v1.pkl')
        std_path = os.path.join(models_dir, 'regressor_residual_std.pkl')
        
        if not os.path.exists(clf_path):
            raise FileNotFoundError("Model files not found. Please run train.py first.")
            
        _classifier = joblib.load(clf_path)
        _regressor = joblib.load(reg_path)
        _baseline = joblib.load(base_path)
        _residual_std = joblib.load(std_path)
        _df_historical = pd.read_csv(data_path)

def predict_listing_gain(features: dict) -> dict:
    """
    Predicts the listing gain bucket and exact percentage.
    `features` should match the VerdictRequest schema keys.
    """
    _load_models()
    
    # Convert features dict to a pandas DataFrame
    df_features = pd.DataFrame([features])
    
    sector = features.get('sector', '')
    
    # Classification
    predicted_bucket = _classifier.predict(df_features)[0]
    baseline_bucket = _baseline.predict(df_features)[0]
    
    # Peer extraction
    sector_peers = _df_historical[_df_historical['sector'].str.lower() == sector.lower()]
    total_peer_count = len(sector_peers)
    real_peer_count = len(sector_peers[sector_peers['data_source'] == 'real_scraped']) if 'data_source' in sector_peers.columns else 0
    
    # Base confidence score (probability of the predicted class)
    probabilities = _classifier.predict_proba(df_features)[0]
    classes = _classifier.classes_
    class_index = list(classes).index(predicted_bucket)
    base_confidence = float(probabilities[class_index])
    
    # Adjust confidence based on agreement with baseline
    if predicted_bucket != baseline_bucket:
        base_confidence *= 0.7 # Penalty for disagreement
        
    # Adjust confidence based on real peer availability
    if real_peer_count < 5:
        base_confidence *= 0.5
    elif real_peer_count < 10:
        base_confidence *= 0.8
        
    # Regression
    predicted_gain_pct = float(_regressor.predict(df_features)[0])
    
    # Walk-forward confidence interval using residual std dev
    lower_bound = predicted_gain_pct - _residual_std
    upper_bound = predicted_gain_pct + _residual_std
    
    return {
        "bucket_estimate": str(predicted_bucket),
        "historical_gain_range": (round(lower_bound, 2), round(upper_bound, 2)),
        "confidence_score": round(base_confidence, 2),
        "real_peer_count": real_peer_count,
        "total_peer_count": total_peer_count,
        "disclaimer": "This prediction incorporates a walk-forward confidence interval. The model's baseline LOOCV accuracy was 0.88, but true out-of-sample performance in volatile markets may be lower."
    }
