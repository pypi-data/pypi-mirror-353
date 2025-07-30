import numpy as np
from ._tsadeval.metrics import pointwise_to_full_series, segmentwise_to_full_series

def is_full_series(length: int, anomalies: np.array):
    # [1 0 1 1 0]
    return len(anomalies.shape) == 1 and len(anomalies) == length

def is_pointwise(length: int, anomalies: np.array):
    # [0 2 3]
    return len(anomalies.shape) == 1 and len(anomalies) < length

def is_segmentwise(length: int, anomalies: np.array):
    # [[0 0] [2 3]]
    return len(anomalies.shape) == 2


def transform_to_full_series(length: int, anomalies: np.array):
    if is_full_series(length, anomalies):
        return anomalies
    elif is_pointwise(anomalies):
        return pointwise_to_full_series(anomalies, length)
    elif is_segmentwise(length, anomalies):
        return segmentwise_to_full_series(anomalies, length)
    else:
        raise ValueError(f"Illegal shape of anomalies:\n{anomalies}")

def counting_method(y_true: np.array, y_pred: np.array, k: int):
    em,da,ma,fa = 0,0,0,0
    for i_gt in range(len(y_true)):
        i_pa = i_gt
        gt = y_true[i_gt]
        pa = y_pred[i_pa]
        if gt==1 and pa==1:
            em+=1
        elif gt==0 and pa==1:
            fa+=1
        elif gt==1 and pa==0:
            anom_range = y_pred[i_gt-k:i_pa+k+1]
            detected = False
            for r in anom_range:
                if r==1:
                    em+=1
                    detected=True
                    break
            if not detected:
                ma+=1
        elif gt==0 and pa==0:
            pass
    # b = DelayThresholdedPointAdjust(len(y_true),y_true,y_pred,k=k)
    # da = b.tp-em
    # ma = b.fn

    return em,da,ma,fa


#Range Based utils

def cardinality(n_intersections,mode):
    if mode == 'one':
        return 1
    elif mode == 'reciprocal':
        if n_intersections==0:
            return 1
        else:
            return float(1/n_intersections)
    else:
        raise Exception("Error, wrong cardinality mode.")
    
    
def size(anomaly_range, overlap_set, position, bias):
    if overlap_set == None:
        return 0
    
    my_value = 0
    max_value = 0
    anomaly_length = anomaly_range[1] - anomaly_range[0] + 1
    for i in range(1,anomaly_length+1):
        bias_value = position(i, anomaly_length,bias)
        max_value += bias_value
        if  anomaly_range[0]+i-1 >= overlap_set[0] and anomaly_range[0]+i-1 <= overlap_set[1]:
            my_value += bias_value
    return my_value / max_value

def position(i, anomaly_length,bias):
    if bias == 'flat':
        return 1
    elif bias == 'front-end':
        return anomaly_length - i + 1
    elif bias == 'back-end':
        return i
    elif bias == 'middle':
        if i <= anomaly_length / 2:
            return i
        else:
            return anomaly_length - i + 1
    else:
        raise Exception("Error, wrong bias value.")
    
