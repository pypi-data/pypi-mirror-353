import numpy as np

def check_gt_binary_array(arr):
    if len(arr.shape) != 1:
        raise ValueError("Ground truth input must be a 1D binary array.")
    if not np.all(np.isin(arr, [0, 1])):
        raise ValueError("Ground truth input array must contain only binary values (0 or 1).")
    return True

def check_pred_binary_array(arr):
    if len(arr.shape) != 1:
        raise ValueError("Prediction input must be a 1D binary array.")
    if not np.all(np.isin(arr, [0, 1])):
        raise ValueError("Prediction input array must contain only binary values (0 or 1).")
    return True
def check_same_length(arr1, arr2):
    if len(arr1) != len(arr2):
        raise ValueError("Ground truth and prediction arrays must have the same length.")
    return True

def check_pred_continuous_array(arr):
    if len(arr.shape) != 1:
        raise ValueError("Prediction input must be a 1D continuous array.")
    if not np.all((arr >= 0) & (arr <= 1)):
        raise ValueError("All values in the array must be in the range [0, 1].")
    return True

def validate_binary_inputs(y_true, y_pred):
    check_gt_binary_array(y_true)
    check_pred_binary_array(y_pred)
    check_same_length(y_true, y_pred)

def validate_non_binary_inputs(y_true, y_anomaly_scores):
    check_gt_binary_array(y_true)
    check_same_length(y_true, y_anomaly_scores)