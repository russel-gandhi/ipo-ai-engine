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
    Outputs historical pattern matching for the requested IPO.
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
    real_peer_count = len(sector_peers[sector_peers['data_source'] == 'real_scraped']) if 'data_source' in sector_peers.columns else 0
    
    # Hardcoded empirical walk-forward accuracy per bucket (from Section 1 evidence)
    wf_accuracy = {
        "loss": 0.60,
        "flat": 0.45,
        "moderate": 0.15,
        "high": 0.25
    }
    
    bucket_acc = wf_accuracy.get(predicted_bucket, 0.48)
    
    # Compute confidence score
    score_val = bucket_acc
    model_agreement = (predicted_bucket == baseline_bucket)
    if not model_agreement:
        score_val -= 0.15
    if real_peer_count < 5:
        score_val -= 0.20
    elif real_peer_count < 10:
        score_val -= 0.10
        
    if score_val >= 0.5:
        confidence_str = "High"
    elif score_val >= 0.3:
        confidence_str = "Moderate"
    else:
        confidence_str = f"Low (Historically poor accuracy for '{predicted_bucket}' estimates)"
        
    if not model_agreement:
        confidence_str += " — Low model agreement, treat with caution"
        
    # Regression
    predicted_gain_pct = float(_regressor.predict(df_features)[0])
    
    # Walk-forward confidence interval using residual std dev
    lower_bound = round(predicted_gain_pct - _residual_std, 1)
    upper_bound = round(predicted_gain_pct + _residual_std, 1)
    
    gain_range_str = f"{lower_bound}% to {upper_bound}%"
    
    return {
        "bucket_estimate": str(predicted_bucket),
        "historical_gain_range": gain_range_str,
        "confidence_score": confidence_str,
        "real_peer_count": real_peer_count,
        "walk_forward_accuracy_for_bucket": bucket_acc,
        "model_agreement": model_agreement,
        "disclaimer": "This output is based on historical pattern matching across similar past IPOs. It is not a prediction, recommendation, or investment advice."
    }

def predict_retroactive(features: dict, cutoff_date: str) -> dict:
    """
    Computes retroactive predictions using only data available prior to cutoff_date.
    """
    from backend.src.model.features import get_feature_pipeline, RelativeIssueSizeTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression
    import numpy as np

    _load_models()
    
    # Filter dataset
    df = _df_historical.copy()
    if 'source_conflict_flag' in df.columns:
        df_real = df[(df['data_source'] == 'real_scraped') & (df['source_conflict_flag'] != True)].copy()
    else:
        df_real = df[df['data_source'] == 'real_scraped'].copy()
        
    df_real['listing_date'] = pd.to_datetime(df_real['listing_date'])
    cutoff_dt = pd.to_datetime(cutoff_date)
    
    train_df = df_real[df_real['listing_date'] < cutoff_dt].copy()
    
    if len(train_df) < 15:
        return {
            "bucket_estimate": "N/A",
            "historical_gain_range": "N/A",
            "confidence_score": "N/A (Insufficient prior data)"
        }
        
    feature_cols = [
        'issue_size', 'sub_retail', 'sub_nii', 'sub_qib', 'sub_overall', 
        'price_band', 'fresh_vs_ofs_ratio', 'sector', 'gmp_trend',
        'anchor_allocation_pct', 'gmp_trajectory', 
        'market_regime_nifty_30d', 'is_sme'
    ]
    
    X_train = train_df[feature_cols]
    y_train_c = train_df['listing_gain_bucket']
    y_train_r = train_df['actual_listing_gain_pct']
    
    clf = Pipeline([
        ('relative_size', RelativeIssueSizeTransformer()),
        ('preprocessor', get_feature_pipeline()),
        ('classifier', GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42))
    ])
    
    reg = Pipeline([
        ('relative_size', RelativeIssueSizeTransformer()),
        ('preprocessor', get_feature_pipeline()),
        ('regressor', GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42))
    ])
    
    baseline = Pipeline([
        ('relative_size', RelativeIssueSizeTransformer()),
        ('preprocessor', get_feature_pipeline()),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    clf.fit(X_train, y_train_c)
    reg.fit(X_train, y_train_r)
    baseline.fit(X_train, y_train_c)
    
    train_preds_r = reg.predict(X_train)
    residual_std = np.std(y_train_r - train_preds_r)
    
    df_f = pd.DataFrame([features])
    
    predicted_bucket = clf.predict(df_f)[0]
    baseline_bucket = baseline.predict(df_f)[0]
    
    wf_accuracy = {"loss": 0.60, "flat": 0.45, "moderate": 0.15, "high": 0.25}
    bucket_acc = wf_accuracy.get(predicted_bucket, 0.48)
    
    score_val = bucket_acc
    model_agreement = (predicted_bucket == baseline_bucket)
    if not model_agreement:
        score_val -= 0.15
        
    if score_val >= 0.5:
        confidence_str = "High"
    elif score_val >= 0.3:
        confidence_str = "Moderate"
    else:
        confidence_str = f"Low (Historically poor accuracy for '{predicted_bucket}')"
        
    if not model_agreement:
        confidence_str += " — Low model agreement"
        
    pred_gain = float(reg.predict(df_f)[0])
    lower_bound = round(pred_gain - residual_std, 1)
    upper_bound = round(pred_gain + residual_std, 1)
    
    return {
        "bucket_estimate": str(predicted_bucket),
        "historical_gain_range": f"{lower_bound}% to {upper_bound}%",
        "confidence_score": confidence_str,
        "predicted_midpoint": pred_gain
    }
