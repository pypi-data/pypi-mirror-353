import numpy as np
import pandas as pd
import time
import sys
import tsadmetrics
def compute_metrics(y_true: np.array,y_pred: np.array, metrics: list, metrics_params: dict, is_anomaly_score = False, verbose = False):
    """
    Computes the specified metrics for the given true and predicted values.

    Parameters:
        y_true (np.array):
            True labels.
        y_pred (np.array):
            Predicted labels or scores.
        metrics (list):
            List of metric names to compute.
        metrics_params (dict):
            Dictionary of parameters for each metric.
        is_anomaly_score (bool):
            Flag indicating if y_true and y_pred are anomaly scores. Otherwise, they are treated as binary labels.
        verbose (bool):
            Flag to print additional information.
    Returns:
        results (DataFrame): DataFrame containing the computed metrics and their values.
    """
    if not (np.array_equal(np.unique(y_true), [0, 1]) or np.array_equal(np.unique(y_true), [0]) or np.array_equal(np.unique(y_true), [1])):
        raise ValueError("y_true must be binary labels (0 or 1).")  
    if not is_anomaly_score:
        #Chech if y_true and y_pred are binary labels
        if not ( np.array_equal(np.unique(y_pred), [0, 1])):
            raise ValueError("y_true and y_pred must be binary labels (0 or 1) when is_anomaly_score is False. Which is the default.")
    else:
        # Check if y_true and y_pred are anomaly scores
        if not (np.all((y_pred >= 0) & (y_pred <= 1))):
            raise ValueError("y_true must be binary labels (0 or 1), and y_pred must be anomaly scores in the range [0, 1] when is_anomaly_score is True.")
    results = {}
    
    for metric in metrics:
        metric_name = metric[0]
        metric_func = metric[1]
        if verbose:
            print(f"Calculating metric: {metric_name}")
            t0 = time.time()
        metric_value = metric_func(y_true, y_pred, **metrics_params.get(metric_name, {}))
        if verbose:
            t1 = time.time()
            print(f"Metric {metric_name} calculated in {t1 - t0:.4f} seconds")
            print(f"Metric {metric_name} value: {metric_value}")
        # Store the result in the DataFrame
        results[metric_name] = metric_value

    metrics_df = pd.DataFrame(columns=['metric_name', 'metric_value'])
    metrics_df['metric_name'] = results.keys()
    metrics_df['metric_value'] = results.values()
    
    return metrics_df


def compute_metrics_from_file(results_file: str, conf_file: str, output_dir: str = '.'):
    """
    Computes metrics based on prediction results from a CSV file and configuration from a JSON file.

    Parameters:
        results_file (str):
            Path to CSV file containing y_true and y_pred columns.
        conf_file (str):
            Path to JSON configuration file with metrics and parameters.

    Returns:
        pd.DataFrame: DataFrame with computed metrics.
    """
    # Read results data
    res = pd.read_csv(results_file)
    y_true = res['y_true'].values
    y_pred = res['y_pred'].values
    
    # Determine if predictions are binary or scores
    is_anomaly_score = False
    unique_values = np.unique(y_pred)
    if not (np.array_equal(unique_values, [0, 1]) or 
            np.array_equal(unique_values, [0]) or 
            np.array_equal(unique_values, [1])):
        is_anomaly_score = True
        if not np.all((y_pred >= 0) & (y_pred <= 1)):
            raise ValueError("y_pred must be either binary (0/1) or anomaly scores in range [0, 1]")

    # Read configuration from JSON using pandas
    try:
        config_df = pd.read_json(conf_file, orient='records')
    except ValueError as e:
        raise ValueError(f"Invalid JSON format in configuration file: {str(e)}")

    # Convert pandas DataFrame to format expected by compute_metrics
    metrics = []
    metrics_params = {}
    
    for _, row in config_df.iterrows():
        metric_name = row['name']
        try:
            metric_func = getattr(tsadmetrics, metric_name)
        except AttributeError:
            raise ValueError(f"Metric function '{metric_name}' not found in tsadmetrics module")
        
        metrics.append((metric_name, metric_func))
        
        # Handle params (convert from pandas Series to dict if needed)
        params = row.get('params', {})
        if pd.notna(params) and params:  # Check for non-empty params
            if isinstance(params, pd.Series):
                metrics_params[metric_name] = params.to_dict()
            else:
                metrics_params[metric_name] = params

    # Compute metrics
    metrics_df = compute_metrics(
        y_true=y_true,
        y_pred=y_pred,
        metrics=metrics,
        metrics_params=metrics_params,
        is_anomaly_score=is_anomaly_score,
        verbose=False
    )
    metrics_df.to_csv(output_dir+'/computed_metrics.csv', index=False)

