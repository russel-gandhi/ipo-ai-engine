import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error, r2_score, mean_squared_error
import os

from backend.src.model.features import get_feature_pipeline, RelativeIssueSizeTransformer

def train_models():
    print("Loading historical IPO data...")
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical_ipos.csv')
    df = pd.read_csv(csv_path)
    
    # Sort by listing_date for walk-forward validation
    df['listing_date'] = pd.to_datetime(df['listing_date'])
    df = df.sort_values(by='listing_date').reset_index(drop=True)
    
    # Clean NaNs in critical columns (Notice relative_issue_size is not strictly required here if it's derived, but issue_size is)
    critical_cols = [
        'issue_size', 'sub_retail', 'sub_nii', 'sub_qib', 'sub_overall', 
        'price_band', 'fresh_vs_ofs_ratio', 'sector', 'gmp_trend', 
        'listing_gain_bucket', 'actual_listing_gain_pct', 'anchor_allocation_pct',
        'gmp_trajectory', 'market_regime_nifty_30d', 'is_sme'
    ]
    df = df.dropna(subset=critical_cols)
    
    # Strictly isolate real_scraped data for the honest baseline per user request
    # If source_conflict_flag exists, we might want to exclude it, but for now we just use real_scraped
    if 'source_conflict_flag' in df.columns:
        df_real = df[(df['data_source'] == 'real_scraped') & (df['source_conflict_flag'] != True)].copy()
    else:
        df_real = df[df['data_source'] == 'real_scraped'].copy()
        
    print(f"Data shape (All valid real scraped rows): {df_real.shape}")
    
    feature_cols = [
        'issue_size', 'sub_retail', 'sub_nii', 'sub_qib', 'sub_overall', 
        'price_band', 'fresh_vs_ofs_ratio', 'sector', 'gmp_trend',
        'anchor_allocation_pct', 'gmp_trajectory', 
        'market_regime_nifty_30d', 'is_sme'
    ]
    
    X = df_real[feature_cols]
    y_class = df_real['listing_gain_bucket']
    y_reg = df_real['actual_listing_gain_pct']
    
    # Models with the new RelativeIssueSizeTransformer at the start
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
    
    # Baseline pipelines
    baseline_clf = Pipeline([
        ('relative_size', RelativeIssueSizeTransformer()),
        ('preprocessor', get_feature_pipeline()),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    naive_reg = DummyRegressor(strategy="mean")
    naive_clf = DummyClassifier(strategy="most_frequent")
    
    # --- Walk-Forward Validation (Dynamic N >= 15) ---
    print("\n--- Running Walk-Forward (Time-Based) Validation ---")
    
    results_report = ["# ML Pipeline V2 Validation Report\n"]
    
    overall_y_true_c = []
    overall_y_pred_c = []
    overall_y_true_r = []
    overall_y_pred_r = []
    
    # We will slice the dataframe dynamically
    test_start_idx = int(len(X) * 0.3) # Start testing after giving the model at least 30% of data to train on initially
    
    current_test_start = test_start_idx
    min_test_size = 15
    
    while current_test_start < len(X):
        # Determine the end of this test fold
        current_test_end = current_test_start + min_test_size
        
        # If the remaining tail is less than 15, we either extend the current fold or just stop.
        # We will extend the current fold to include the tail if it's too small.
        if len(X) - current_test_end < min_test_size:
            current_test_end = len(X)
            
        # Extract train and test (Strictly non-overlapping, strictly chronological)
        X_train = X.iloc[:current_test_start]
        y_train_c = y_class.iloc[:current_test_start]
        y_train_r = y_reg.iloc[:current_test_start]
        
        X_test = X.iloc[current_test_start:current_test_end]
        y_test_c = y_class.iloc[current_test_start:current_test_end]
        y_test_r = y_reg.iloc[current_test_start:current_test_end]
        
        # Fit models
        clf.fit(X_train, y_train_c)
        reg.fit(X_train, y_train_r)
        
        naive_clf.fit(X_train, y_train_c)
        naive_reg.fit(X_train, y_train_r)
        
        # Predict
        preds_c = clf.predict(X_test)
        preds_r = reg.predict(X_test)
        
        naive_preds_c = naive_clf.predict(X_test)
        naive_preds_r = naive_reg.predict(X_test)
        
        # Metrics
        acc = accuracy_score(y_test_c, preds_c)
        naive_acc = accuracy_score(y_test_c, naive_preds_c)
        
        rmse = np.sqrt(mean_squared_error(y_test_r, preds_r))
        mae = mean_absolute_error(y_test_r, preds_r)
        naive_mae = mean_absolute_error(y_test_r, naive_preds_r)
        
        cm = confusion_matrix(y_test_c, preds_c, labels=['loss', 'flat', 'moderate', 'high'])
        
        overall_y_true_c.extend(y_test_c)
        overall_y_pred_c.extend(preds_c)
        overall_y_true_r.extend(y_test_r)
        overall_y_pred_r.extend(preds_r)
        
        # Get date ranges for report
        train_start_date = df_real['listing_date'].iloc[0].strftime('%Y-%m-%d')
        train_end_date = df_real['listing_date'].iloc[current_test_start - 1].strftime('%Y-%m-%d')
        test_start_date = df_real['listing_date'].iloc[current_test_start].strftime('%Y-%m-%d')
        test_end_date = df_real['listing_date'].iloc[current_test_end - 1].strftime('%Y-%m-%d')
        
        msg = f"## Test Window: {test_start_date} to {test_end_date}\n"
        msg += f"- **Train Window:** {train_start_date} to {train_end_date} (N={len(X_train)})\n"
        msg += f"- **Test Size:** N={len(X_test)}\n"
        msg += f"- **Classifier Accuracy:** {acc:.2f} (Naive Majority: {naive_acc:.2f})\n"
        msg += f"- **Confusion Matrix (loss, flat, moderate, high):**\n```\n{cm}\n```\n"
        msg += f"- **Regressor MAE:** {mae:.2f}% (Naive Mean: {naive_mae:.2f}%)\n"
        msg += f"- **Regressor RMSE:** {rmse:.2f}%\n"
        
        results_report.append(msg)
        print(msg)
        
        # Advance rolling window
        current_test_start = current_test_end

    # --- Overall Accuracy ---
    acc_wf = accuracy_score(overall_y_true_c, overall_y_pred_c) if len(overall_y_true_c) > 0 else 0.0
    
    msg_overall = f"\n## Overall Walk-Forward Accuracy: {acc_wf:.2f}\n"
    results_report.append(msg_overall)
    print(msg_overall)
    
    # Save validation report
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'validation_report.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(results_report))
        
    print(f"Saved validation report to {report_path}")
    
    # --- Train Final Models ---
    print("\n--- Training Final Models on 100% Real Scraped Data ---")
    clf.fit(X, y_class)
    reg.fit(X, y_reg)
    baseline_clf.fit(X, y_class)
    
    # Save standard deviation of residuals for confidence intervals
    final_preds_r = reg.predict(X)
    residual_std = np.std(y_reg - final_preds_r)
    
    models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(clf, os.path.join(models_dir, 'ipo_xgb_classifier_v1.pkl'))
    joblib.dump(reg, os.path.join(models_dir, 'ipo_xgb_regressor_v1.pkl'))
    joblib.dump(baseline_clf, os.path.join(models_dir, 'ipo_baseline_classifier_v1.pkl'))
    joblib.dump(residual_std, os.path.join(models_dir, 'regressor_residual_std.pkl'))
    
    print("Saved final models and confidence interval specs.")

if __name__ == "__main__":
    train_models()
