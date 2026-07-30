from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

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
