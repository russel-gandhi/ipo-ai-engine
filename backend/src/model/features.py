from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np

class RelativeIssueSizeTransformer(BaseEstimator, TransformerMixin):
    """
    Computes 'relative_issue_size' dynamically to prevent target leakage.
    Fits only on the training fold to calculate sector means, then transforms the test fold.
    """
    def __init__(self):
        self.sector_means_ = {}
        self.global_mean_ = 1.0

    def fit(self, X, y=None):
        if not isinstance(X, pd.DataFrame):
            # If for some reason it's not a dataframe, we can't group by sector easily. 
            # In our pipeline it will be a dataframe.
            pass
        else:
            if 'sector' in X.columns and 'issue_size' in X.columns:
                self.sector_means_ = X.groupby('sector')['issue_size'].mean().to_dict()
                self.global_mean_ = X['issue_size'].mean()
        return self

    def transform(self, X, y=None):
        X_out = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        
        if 'sector' in X_out.columns and 'issue_size' in X_out.columns:
            def get_mean(sector):
                return self.sector_means_.get(sector, self.global_mean_)
                
            sector_means = X_out['sector'].apply(get_mean)
            # Avoid division by zero
            sector_means = sector_means.replace(0, 1)
            X_out['relative_issue_size'] = X_out['issue_size'] / sector_means
        else:
            X_out['relative_issue_size'] = 1.0
            
        return X_out

def get_feature_pipeline():
    """
    Returns a scikit-learn ColumnTransformer that standardizes numeric features
    and one-hot encodes categorical features.
    """
    numeric_features = [
        'issue_size', 'sub_retail', 'sub_nii', 'sub_qib', 'sub_overall', 
        'price_band', 'fresh_vs_ofs_ratio', 'anchor_allocation_pct',
        'relative_issue_size', 'gmp_trajectory', 'market_regime_nifty_30d'
    ]
    categorical_features = ['sector', 'gmp_trend', 'is_sme']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='drop' # Drops any columns not explicitly defined above
    )
    
    return preprocessor
