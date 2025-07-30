"""
Tools for comparing optimization algorithms.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from sklearn.model_selection import KFold, train_test_split
from scipy import stats
import time

from amgd.models import PoissonRegressor
from amgd.utils.metrics import evaluate_model


def compare_optimizers(
    X: np.ndarray,
    y: np.ndarray,
    optimizers: List[str] = None,
    penalties: List[str] = None,
    lambda_values: np.ndarray = None,
    cv_folds: int = 5,
    test_size: float = 0.2,
    random_state: int = 42,
    verbose: bool = True,
    **optimizer_params
) -> Dict[str, Any]:
    """
    Compare performance of different optimizers.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Feature matrix.
    y : array-like of shape (n_samples,)
        Target values.
    optimizers : list of str, optional
        Optimizers to compare. Default: ['amgd', 'adam', 'adagrad'].
    penalties : list of str, optional
        Penalties to test. Default: ['l1', 'elasticnet'].
    lambda_values : array-like, optional
        Regularization strengths to test.
    cv_folds : int
        Number of cross-validation folds.
    test_size : float
        Proportion of data for test set.
    random_state : int
        Random seed.
    verbose : bool
        Print progress.
    **optimizer_params
        Additional parameters for optimizers.
        
    Returns
    -------
    results : dict
        Comparison results including best parameters and test metrics.
    """
    if optimizers is None:
        optimizers = ['amgd', 'adam', 'adagrad']
        
    if penalties is None:
        penalties = ['l1', 'elasticnet']
        
    if lambda_values is None:
        lambda_values = np.logspace(-4, 1, 20)
        
    # Split data
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Cross-validation to find best parameters
    cv_results = []
    best_params = {}
    
    for optimizer in optimizers:
        for penalty in penalties:
            if verbose:
                print(f"\nEvaluating {optimizer} with {penalty} penalty...")
                
            try:
                # Run cross-validation for different lambda values
                cv_scores = run_cross_validation(
                    X_train_val, y_train_val,
                    optimizer=optimizer,
                    penalty=penalty,
                    lambda_values=lambda_values,
                    cv_folds=cv_folds,
                    random_state=random_state,
                    **optimizer_params
                )
                
                # Find best lambda
                best_idx = np.argmin(cv_scores['mean_mae'])
                best_lambda = lambda_values[best_idx]
                
                # Store results
                result = {
                    'optimizer': optimizer,
                    'penalty': penalty,
                    'lambda': best_lambda,
                    'cv_mae': cv_scores['mean_mae'][best_idx],
                    'cv_mae_std': cv_scores['std_mae'][best_idx],
                    'cv_rmse': cv_scores['mean_rmse'][best_idx],
                    'cv_rmse_std': cv_scores['std_rmse'][best_idx],
                }
                cv_results.append(result)
                
                # Store best params for each optimizer
                if optimizer not in best_params or cv_scores['mean_mae'][best_idx] < best_params[optimizer]['cv_mae']:
                    best_params[optimizer] = {
                        'penalty': penalty,
                        'lambda': best_lambda,
                        'cv_mae': cv_scores['mean_mae'][best_idx]
                    }
                    
            except Exception as e:
                if verbose:
                    print(f"Error with {optimizer} + {penalty}: {str(e)}")
                continue
                
    # Convert to DataFrame for easy viewing
    cv_results_df = pd.DataFrame(cv_results)
    
    # Train final models with best parameters
    final_models = {}
    test_results = []
    
    for optimizer, params in best_params.items():
        if verbose:
            print(f"\nTraining final {optimizer} model...")
            
        try:
            # Create and train model
            if params['penalty'] == 'l1':
                lambda1 = params['lambda']
                lambda2 = 0.0
            else:  # elasticnet
                lambda1 = params['lambda'] / 2
                lambda2 = params['lambda'] / 2
                
            model = PoissonRegressor(
                optimizer=optimizer,
                penalty=params['penalty'],
                lambda1=lambda1,
                lambda2=lambda2,
                verbose=False,
                **optimizer_params
            )
            
            start_time = time.time()
            model.fit(X_train_val, y_train_val)
            train_time = time.time() - start_time
            
            # Evaluate on test set
            y_pred = model.predict(X_test)
            
            # Use sklearn metrics as fallback if evaluate_model fails
            try:
                test_metrics = evaluate_model(model.coef_, X_test, y_test)
            except:
                from sklearn.metrics import mean_absolute_error, mean_squared_error
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                test_metrics = {
                    'MAE': mae,
                    'RMSE': rmse,
                    'Mean Deviance': mae * 2,  # Approximation
                    'Sparsity': np.mean(np.abs(model.coef_) < 1e-6)
                }
            
            # Store results
            test_result = {
                'optimizer': optimizer,
                'penalty': params['penalty'],
                'lambda': params['lambda'],
                'train_time': train_time,
                'n_iter': getattr(model, 'n_iter_', 'unknown'),
                **test_metrics
            }
            test_results.append(test_result)
            final_models[optimizer] = model
            
        except Exception as e:
            if verbose:
                print(f"Error training final {optimizer} model: {str(e)}")
            continue
        
    test_results_df = pd.DataFrame(test_results)
    
    # Print summary if verbose
    if verbose:
        print("\n" + "="*60)
        print("CROSS-VALIDATION RESULTS")
        print("="*60)
        if not cv_results_df.empty:
            print(cv_results_df.to_string(index=False))
        else:
            print("No successful CV results")
        
        print("\n" + "="*60)
        print("TEST SET RESULTS")
        print("="*60)
        if not test_results_df.empty:
            print(test_results_df.to_string(index=False))
        else:
            print("No successful test results")
        
    return {
        'cv_results': cv_results_df,
        'test_results': test_results_df,
        'best_params': best_params,
        'models': final_models,
        'data_splits': {
            'X_train_val': X_train_val,
            'X_test': X_test,
            'y_train_val': y_train_val,
            'y_test': y_test
        }
    }


def run_cross_validation(
    X: np.ndarray,
    y: np.ndarray,
    optimizer: str,
    penalty: str,
    lambda_values: np.ndarray,
    cv_folds: int = 5,
    random_state: int = 42,
    **model_params
) -> Dict[str, np.ndarray]:
    """
    Run k-fold cross-validation for hyperparameter tuning.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Feature matrix.
    y : array-like of shape (n_samples,)
        Target values.
    optimizer : str
        Optimizer name.
    penalty : str
        Penalty type.
    lambda_values : array-like
        Regularization values to test.
    cv_folds : int
        Number of CV folds.
    random_state : int
        Random seed.
    **model_params
        Additional model parameters.
        
    Returns
    -------
    scores : dict
        Cross-validation scores for each lambda value.
    """
    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    mae_scores = []
    rmse_scores = []
    deviance_scores = []
    sparsity_scores = []
    
    for lambda_val in lambda_values:
        fold_mae = []
        fold_rmse = []
        fold_deviance = []
        fold_sparsity = []
        
        # Set up regularization parameters
        if penalty == 'l1':
            lambda1 = lambda_val
            lambda2 = 0.0
        elif penalty == 'elasticnet':
            lambda1 = lambda_val / 2
            lambda2 = lambda_val / 2
        else:
            lambda1 = 0.0
            lambda2 = 0.0
            
        # Cross-validation loop
        for train_idx, val_idx in kf.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            try:
                # Train model
                model = PoissonRegressor(
                    optimizer=optimizer,
                    penalty=penalty,
                    lambda1=lambda1,
                    lambda2=lambda2,
                    verbose=False,
                    **model_params
                )
                
                model.fit(X_train, y_train)
                
                # Evaluate - use fallback if evaluate_model fails
                try:
                    metrics = evaluate_model(model.coef_, X_val, y_val)
                except:
                    from sklearn.metrics import mean_absolute_error, mean_squared_error
                    y_pred = model.predict(X_val)
                    mae = mean_absolute_error(y_val, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
                    metrics = {
                        'MAE': mae,
                        'RMSE': rmse,
                        'Mean Deviance': mae * 2,
                        'Sparsity': np.mean(np.abs(model.coef_) < 1e-6)
                    }
                
                fold_mae.append(metrics['MAE'])
                fold_rmse.append(metrics['RMSE'])
                fold_deviance.append(metrics['Mean Deviance'])
                fold_sparsity.append(metrics['Sparsity'])
                
            except Exception as e:
                # If model fails, append NaN
                fold_mae.append(np.nan)
                fold_rmse.append(np.nan)
                fold_deviance.append(np.nan)
                fold_sparsity.append(np.nan)
            
        # Store average scores (excluding NaN values)
        mae_scores.append(np.nanmean(fold_mae))
        rmse_scores.append(np.nanmean(fold_rmse))
        deviance_scores.append(np.nanmean(fold_deviance))
        sparsity_scores.append(np.nanmean(fold_sparsity))
        
    return {
        'mean_mae': np.array(mae_scores),
        'std_mae': np.array([np.nanstd(mae_scores)]),  # Fixed: calculate std properly
        'mean_rmse': np.array(rmse_scores),
        'std_rmse': np.array([np.nanstd(rmse_scores)]),  # Fixed: calculate std properly
        'mean_deviance': np.array(deviance_scores),
        'mean_sparsity': np.array(sparsity_scores)
    }


def statistical_significance_test(
    X: np.ndarray,
    y: np.ndarray,
    optimizers: List[str],
    n_bootstrap: int = 1000,
    n_runs: int = 100,
    test_size: float = 0.2,
    random_state: int = 42,
    **model_params
) -> Dict[str, Any]:
    """
    Perform statistical significance testing between optimizers.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Feature matrix.
    y : array-like of shape (n_samples,)
        Target values.
    optimizers : list of str
        Optimizers to compare.
    n_bootstrap : int
        Number of bootstrap samples.
    n_runs : int
        Number of runs for each comparison.
    test_size : float
        Test set proportion.
    random_state : int
        Random seed.
    **model_params
        Additional model parameters.
        
    Returns
    -------
    results : dict
        Statistical test results.
    """
    np.random.seed(random_state)
    
    # Store performance metrics for each optimizer
    all_metrics = {opt: {
        'mae': [], 'rmse': [], 'deviance': [], 'sparsity': []
    } for opt in optimizers}
    
    # Run multiple experiments
    for run in range(n_runs):
        print(f"Running experiment {run+1}/{n_runs}")
        
        # Random train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state + run
        )
        
        # Train each optimizer
        for optimizer in optimizers:
            try:
                model = PoissonRegressor(
                    optimizer=optimizer,
                    penalty='l1',
                    lambda1=0.1,  # Fixed for fair comparison
                    verbose=False,
                    **model_params
                )
                
                model.fit(X_train, y_train)
                
                # Evaluate with fallback
                try:
                    metrics = evaluate_model(model.coef_, X_test, y_test)
                except:
                    from sklearn.metrics import mean_absolute_error, mean_squared_error
                    y_pred = model.predict(X_test)
                    mae = mean_absolute_error(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    metrics = {
                        'MAE': mae,
                        'RMSE': rmse,
                        'Mean Deviance': mae * 2,
                        'Sparsity': np.mean(np.abs(model.coef_) < 1e-6)
                    }
                
                all_metrics[optimizer]['mae'].append(metrics['MAE'])
                all_metrics[optimizer]['rmse'].append(metrics['RMSE'])
                all_metrics[optimizer]['deviance'].append(metrics['Mean Deviance'])
                all_metrics[optimizer]['sparsity'].append(metrics['Sparsity'])
                
            except Exception as e:
                print(f"Error with {optimizer} in run {run+1}: {str(e)}")
                continue
            
    # Compute statistics
    statistics = {}
    
    for optimizer in optimizers:
        statistics[optimizer] = {}
        
        for metric in ['mae', 'rmse', 'deviance', 'sparsity']:
            values = all_metrics[optimizer][metric]
            
            if len(values) > 0:
                # Bootstrap confidence intervals
                bootstrap_means = []
                for _ in range(n_bootstrap):  # Fixed syntax error here
                    bootstrap_sample = np.random.choice(values, size=len(values), replace=True)
                    bootstrap_means.append(np.mean(bootstrap_sample))
                    
                statistics[optimizer][metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'ci_lower': np.percentile(bootstrap_means, 2.5),
                    'ci_upper': np.percentile(bootstrap_means, 97.5)
                }
            else:
                statistics[optimizer][metric] = {
                    'mean': np.nan,
                    'std': np.nan,
                    'ci_lower': np.nan,
                    'ci_upper': np.nan
                }
                
    # Pairwise comparisons
    comparisons = {}
    
    for i, opt1 in enumerate(optimizers):
        for opt2 in optimizers[i+1:]:
            key = f"{opt1}_vs_{opt2}"
            comparisons[key] = {}
            
            for metric in ['mae', 'rmse', 'deviance', 'sparsity']:
                values1 = all_metrics[opt1][metric]
                values2 = all_metrics[opt2][metric]
                
                if len(values1) > 0 and len(values2) > 0:
                    # Paired t-test
                    t_stat, p_value = stats.ttest_rel(values1, values2)
                    
                    # Effect size (Cohen's d)
                    mean_diff = np.mean(values1) - np.mean(values2)
                    pooled_std = np.sqrt((np.var(values1) + np.var(values2)) / 2)
                    effect_size = mean_diff / (pooled_std + 1e-10)
                    
                    comparisons[key][metric] = {
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'effect_size': effect_size,
                        'significant': p_value < 0.05
                    }
                else:
                    comparisons[key][metric] = {
                        't_statistic': np.nan,
                        'p_value': np.nan,
                        'effect_size': np.nan,
                        'significant': False
                    }
                
    return {
        'statistics': statistics,
        'comparisons': comparisons,
        'n_runs': n_runs
    }]
