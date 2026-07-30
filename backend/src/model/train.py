import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score, mean_squared_error
import os
import sys

from backend.src.model.features import get_feature_pipeline

def train_models():
    print("Loading historical IPO data...")
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical_ipos.csv')
    df = pd.read_csv(csv_path)
    
    # Sort by listing_date for walk-forward validation
    df['listing_date'] = pd.to_datetime(df['listing_date'])
    df = df.sort_values(by='listing_date').reset_index(drop=True)
    
    # Clean NaNs in critical columns
    critical_cols = [
        'issue_size', 'sub_retail', 'sub_nii', 'sub_qib', 'sub_overall', 
        'price_band', 'fresh_vs_ofs_ratio', 'sector', 'gmp_trend', 
        'listing_gain_bucket', 'actual_listing_gain_pct', 'anchor_allocation_pct',
        'relative_issue_size', 'gmp_trajectory', 'market_regime_nifty_30d', 'is_sme'
    ]
    df = df.dropna(subset=critical_cols)
    
    # Strictly isolate real_scraped data for the honest baseline per user request
    df_real = df[df['data_source'] == 'real_scraped'].copy()
    
    print(f"Data shape (All real scraped rows): {df_real.shape}")
    
    feature_cols = [
        'issue_size', 'sub_retail', 'sub_nii', 'sub_qib', 'sub_overall', 
        'price_band', 'fresh_vs_ofs_ratio', 'sector', 'gmp_trend',
        'anchor_allocation_pct', 'relative_issue_size', 'gmp_trajectory', 
        'market_regime_nifty_30d', 'is_sme'
    ]
    
    X = df_real[feature_cols]
    y_class = df_real['listing_gain_bucket']
    y_reg = df_real['actual_listing_gain_pct']
    
    # Models
    clf = Pipeline([
        ('preprocessor', get_feature_pipeline()),
        ('classifier', GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42))
    ])
    
    reg = Pipeline([
        ('preprocessor', get_feature_pipeline()),
        ('regressor', GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42))
    ])
    
    # Ensemble Baseline
    baseline = Pipeline([
        ('preprocessor', get_feature_pipeline()),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    # --- Walk-Forward Validation ---
    print("\n--- Running Walk-Forward (Time-Based) Validation ---")
    
    # Define rolling windows manually (e.g. up to 2021, up to 2023, up to present)
    windows = [
        (pd.to_datetime('2021-01-01'), pd.to_datetime('2022-12-31')),
        (pd.to_datetime('2023-01-01'), pd.to_datetime('2024-12-31')),
        (pd.to_datetime('2025-01-01'), pd.to_datetime('2026-12-31'))
    ]
    
    results_report = ["# ML Pipeline V2 Validation Report\n"]
    
    overall_y_true_c = []
    overall_y_pred_c = []
    overall_y_true_r = []
    overall_y_pred_r = []
    
    for start, end in windows:
        train_mask = df_real['listing_date'] < start
        test_mask = (df_real['listing_date'] >= start) & (df_real['listing_date'] <= end)
        
        X_train, y_train_c, y_train_r = X[train_mask], y_class[train_mask], y_reg[train_mask]
        X_test, y_test_c, y_test_r = X[test_mask], y_class[test_mask], y_reg[test_mask]
        
        if len(X_train) == 0 or len(X_test) == 0:
            continue
            
        clf.fit(X_train, y_train_c)
        reg.fit(X_train, y_train_r)
        
        preds_c = clf.predict(X_test)
        preds_r = reg.predict(X_test)
        
        acc = accuracy_score(y_test_c, preds_c)
        rmse = np.sqrt(mean_squared_error(y_test_r, preds_r))
        mae = mean_absolute_error(y_test_r, preds_r)
        
        overall_y_true_c.extend(y_test_c)
        overall_y_pred_c.extend(preds_c)
        overall_y_true_r.extend(y_test_r)
        overall_y_pred_r.extend(preds_r)
        
        msg = f"## Window: {start.year} to {end.year}\n"
        msg += f"- Train Size: {len(X_train)}, Test Size: {len(X_test)}\n"
        msg += f"- Classifier Accuracy: {acc:.2f}\n"
        msg += f"- Regressor RMSE: {rmse:.2f}%, MAE: {mae:.2f}%\n"
        results_report.append(msg)
        print(msg)
        
    # --- LOOCV For Baseline Comparison ---
    print("\n--- Running LOOCV (For Gap Comparison) ---")
    loo = LeaveOneOut()
    y_pred_loocv = []
    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train_c, y_test_c = y_class.iloc[train_idx], y_class.iloc[test_idx]
        clf.fit(X_train, y_train_c)
        y_pred_loocv.append(clf.predict(X_test)[0])
        
    acc_loocv = accuracy_score(y_class, y_pred_loocv)
    acc_wf = accuracy_score(overall_y_true_c, overall_y_pred_c) if len(overall_y_true_c) > 0 else 0.0
    
    msg_compare = f"\n## LOOCV vs Walk-Forward Gap\n"
    msg_compare += f"- LOOCV Accuracy (Implicitly sees future): {acc_loocv:.2f}\n"
    msg_compare += f"- Walk-Forward Accuracy (Honest real-world): {acc_wf:.2f}\n"
    msg_compare += f"- Gap (Overfitting Illusion): {(acc_loocv - acc_wf):.2f}\n"
    results_report.append(msg_compare)
    print(msg_compare)
    
    # Save validation report
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'validation_report.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(results_report))
        
    print(f"Saved validation report to {report_path}")
    
    # --- Train Final Models ---
    print("\n--- Training Final Models on 100% Real Scraped Data ---")
    clf.fit(X, y_class)
    reg.fit(X, y_reg)
    baseline.fit(X, y_class)
    
    # Save standard deviation of residuals for confidence intervals
    final_preds_r = reg.predict(X)
    residual_std = np.std(y_reg - final_preds_r)
    
    models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(clf, os.path.join(models_dir, 'ipo_xgb_classifier_v1.pkl'))
    joblib.dump(reg, os.path.join(models_dir, 'ipo_xgb_regressor_v1.pkl'))
    joblib.dump(baseline, os.path.join(models_dir, 'ipo_baseline_classifier_v1.pkl'))
    
    # Save residual std dev config
    joblib.dump(residual_std, os.path.join(models_dir, 'regressor_residual_std.pkl'))
    
    print("Saved final models and confidence interval specs.")

if __name__ == "__main__":
    train_models()
