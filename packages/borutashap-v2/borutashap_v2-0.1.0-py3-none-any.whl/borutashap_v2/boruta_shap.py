# --- Core Dependencies ---
import pandas as pd
import numpy as np
import shap
import warnings
from tqdm.auto import tqdm

# --- Scikit-learn Core Components ---
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split

# --- Scipy Stats Function ---
from scipy.stats import binomtest

# --- Other ---
import inspect
from collections import defaultdict

warnings.filterwarnings("ignore")


class BorutaShap(BaseEstimator, TransformerMixin):
    """
    BorutaShap: A wrapper feature selection method that combines the ideas of both SHAP and Boruta.
    """

    def __init__(self, model=None, importance_measure='shap',
                 classification=True, percentile=100, p_value=0.05):
        self.model = model
        self.importance_measure = importance_measure.lower()
        self.classification = classification
        self.percentile = percentile
        self.p_value = p_value


    def _check_model(self):
        """Checks if the model is compliant and sets a default if not provided."""
        if self.model is None:
            self.model = RandomForestClassifier() if self.classification else RandomForestRegressor()
            print("No model was provided. Using a default RandomForest.")
        
        if not (hasattr(self.model, 'fit') and hasattr(self.model, 'predict')):
            raise AttributeError('Model must have both fit() and predict() methods.')

        if self.importance_measure == 'gini' and not hasattr(self.model, 'feature_importances_'):
            raise AttributeError('Model must have feature_importances_ for Gini importance.')


    def _check_X_y(self, X, y):
        """Checks the type and for missing values in the input data."""
        if not isinstance(X, pd.DataFrame):
            raise TypeError('X must be a pandas DataFrame.')
        
        if isinstance(y, (pd.Series, pd.DataFrame)):
            if y.isnull().any().any():
                raise ValueError('y contains missing values.')
        elif isinstance(y, np.ndarray):
            if np.isnan(y).any():
                raise ValueError('y contains missing values.')
        else:
            raise TypeError('y must be a pandas Series, DataFrame, or a numpy array.')
        
        if X.isnull().any().any():
            # Modern GBM models can handle NaNs, so we only print a warning.
            model_name = str(type(self.model)).lower()
            if any(m in model_name for m in ('xgb', 'catboost', 'lgbm', 'lightgbm')):
                print('Warning: Missing values found in X. Make sure your model can handle them.')
            else:
                raise ValueError('Missing values found in X. Please impute them before using BorutaShap.')
        
        return X, y


    def fit(self, X, y, n_trials=20, random_state=0, sample=False,
            train_or_test='test', normalize=True, verbose=True, stratify=None):
        
        """Main fit function to perform the Boruta-Shap feature selection process."""
        self.random_state = random_state
        self.rng = np.random.default_rng(self.random_state) # Use the modern random number generator
        
        X, y = self._check_X_y(X, y)
        self.X_original = X.copy()
        self.y_original = y.copy()
        
        self._check_model()

        self.n_trials = n_trials
        self.all_columns = X.columns.to_numpy()
        self.hits = np.zeros(len(self.all_columns))
        
        self.accepted = []
        self.rejected = []
        
        # Main iterative loop
        for trial in tqdm(range(self.n_trials), desc="BorutaShap Trials"):
            
            X_boruta = self._create_shadow_features(X)

            # Train the model
            if train_or_test.lower() == 'test':
                X_train, X_test, y_train, _ = train_test_split(
                    X_boruta, y, test_size=0.3, random_state=self.random_state, stratify=stratify
                )
                self.model.fit(X_train, y_train)
                importances = self._get_feature_importance(X_test, normalize)
            else:
                self.model.fit(X_boruta, y)
                importances = self._get_feature_importance(X_boruta, normalize)

            # Calculate hits
            self._update_hits(importances, X.columns)
            
            # Make decisions
            self._test_features(current_trial=trial + 1)
            
            # If all features are assigned, stop early
            if len(self.accepted) + len(self.rejected) == len(self.all_columns):
                print(f"All features assigned. Early stopping at trial {trial + 1}.")
                break
        
        self._finalize_decisions(verbose)
        return self

    
    def _create_shadow_features(self, X):
        """Creates shadow features using efficient NumPy operations."""
        X_shadow_np = X.to_numpy(copy=True)
        # Shuffle each column independently to maintain column integrity
        for i in range(X_shadow_np.shape[1]):
            self.rng.shuffle(X_shadow_np[:, i])
        
        X_shadow = pd.DataFrame(X_shadow_np, columns=['shadow_' + col for col in X.columns], index=X.index)
        return pd.concat([X, X_shadow], axis=1)


    def _get_feature_importance(self, X_boruta, normalize):
        """Gets the feature importance scores."""
        if self.importance_measure == 'shap':
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_boruta)
            
            if isinstance(shap_values, list): # Multi-class classification case
                importances = np.abs(shap_values).mean(axis=1).sum(axis=0)
            else:
                importances = np.abs(shap_values).mean(axis=0)
        
        elif self.importance_measure == 'gini':
            importances = self.model.feature_importances_
            
        else:
            raise ValueError("importance_measure must be 'shap' or 'gini'.")
            
        if normalize:
            importances = (importances - importances.mean()) / (importances.std() + 1e-8)
        
        return importances


    def _update_hits(self, importances, original_columns):
        """Updates the hit counts for each feature."""
        num_original_features = len(original_columns)
        original_importances = importances[:num_original_features]
        shadow_importances = importances[num_original_features:]
        
        shadow_threshold = np.percentile(shadow_importances, self.percentile)
        
        # Get indices of features whose importance is greater than the shadow threshold
        hit_indices = np.where(original_importances > shadow_threshold)[0]
        
        # Update these hits in the main hits array
        # A mapping is needed because the columns of X might change during iterations
        current_col_indices = [list(self.all_columns).index(c) for c in original_columns]
        hits_in_all_cols = np.zeros_like(self.hits, dtype=bool)
        hits_in_all_cols[current_col_indices] = original_importances > shadow_threshold
        self.hits[hits_in_all_cols] += 1
        

    def _test_features(self, current_trial):
        """Uses the binomial test to decide whether to accept or reject features."""
        p_values = np.array([
            binomtest(int(hit_count), n=current_trial, p=0.5, alternative='greater').pvalue
            for hit_count in self.hits
        ])
        
        # Multiple testing correction (Bonferroni)
        alpha_corrected = self.p_value / len(self.all_columns)
        
        # Update accepted and rejected lists based on the corrected p-value
        self.accepted = list(self.all_columns[p_values < alpha_corrected])
        
        # For rejection, we use a less strict standard, just checking if the p-value indicates it's no better than random
        p_values_less = np.array([
            binomtest(int(hit_count), n=current_trial, p=0.5, alternative='less').pvalue
            for hit_count in self.hits
        ])
        self.rejected = list(self.all_columns[p_values_less < alpha_corrected])
        
        # Ensure that accepted features are not also in the rejected list
        self.rejected = [f for f in self.rejected if f not in self.accepted]


    def _finalize_decisions(self, verbose):
        """Finalizes the decisions for all features, especially tentative ones."""
        self.tentative = [f for f in self.all_columns if f not in self.accepted and f not in self.rejected]

        # TentativeRoughFix: Make a final decision on tentative features
        if self.tentative:
            # A simple heuristic: accept a tentative feature if its average hit rate is > 0.5
            final_hit_rate = self.hits / self.n_trials
            tentative_indices = [list(self.all_columns).index(c) for c in self.tentative]
            
            newly_accepted = [self.tentative[i] for i, idx in enumerate(tentative_indices) if final_hit_rate[idx] > 0.5]
            self.accepted.extend(newly_accepted)
            self.tentative = [f for f in self.tentative if f not in newly_accepted]
            self.rejected.extend(self.tentative) # The remaining tentative features are rejected
            self.tentative = [] # Clear the tentative list
        
        if verbose:
            print(f"{len(self.accepted)} attributes confirmed important: {sorted(self.accepted)}")
            print(f"{len(self.rejected)} attributes confirmed unimportant: {sorted(self.rejected)}")


    def transform(self, X, tentative=False):
        """
        Returns a DataFrame containing only the selected features.
        This method complies with the scikit-learn Transformer API.
        """
        if tentative:
            features_to_keep = self.accepted + self.tentative
        else:
            features_to_keep = self.accepted
            
        return X[features_to_keep]


if __name__ == '__main__':
    # Example usage (if this file is run directly)
    from sklearn.datasets import load_diabetes
    
    # 1. Load data
    db = load_diabetes()
    X = pd.DataFrame(db.data, columns=db.feature_names)
    y = pd.Series(db.target)

    # 2. Initialize a model
    model = RandomForestRegressor(n_jobs=-1, random_state=42)

    # 3. Create and run BorutaShap
    feature_selector = BorutaShap(model=model, importance_measure='shap', classification=False, p_value=0.05)
    feature_selector.fit(X=X, y=y, n_trials=50, random_state=42)

    # 4. Get the results
    X_filtered = feature_selector.transform(X)
    print("\nOriginal number of features:", X.shape[1])
    print("Number of selected features:", X_filtered.shape[1])
    print("Selected features:", X_filtered.columns.tolist())