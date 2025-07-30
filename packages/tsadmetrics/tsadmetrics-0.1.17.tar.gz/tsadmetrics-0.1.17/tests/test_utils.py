import unittest
from tsadmetrics import *
import os
import numpy as np
import random

class TestComputeMetrics(unittest.TestCase):
    def setUp(self):
        self.y_true  = np.array([0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1])
        self.y_pred_binary = np.array([0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) 
        self.y_pred_non_binary = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.12, 0.11, 0.21, 0.13, 0.4, 0.3, 0.2, 0.1, 0.32, 0.98, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

    
    def test_compute_metrics_binary(self):
        metrics = [
            ('point_wise_f_score', point_wise_f_score),
            ('segment_wise_f_score', segment_wise_f_score),
        ]
        metrics_params = {}
        
        results = compute_metrics(self.y_true, self.y_pred_binary, metrics, metrics_params)
        
        self.assertTrue('point_wise_f_score' in results['metric_name'].values)
        self.assertTrue('segment_wise_f_score' in results['metric_name'].values)
        
    def test_compute_metrics_non_binary(self):
        metrics = [
            ('vus_roc', vus_roc),
            ('vus_pr', vus_pr),
        ]
        metrics_params = { 
        'vus_roc': {'window': 3},
        'vus_pr': {'window': 3}}

        results = compute_metrics(self.y_true, self.y_pred_non_binary, metrics, metrics_params, is_anomaly_score=True)

        self.assertTrue('vus_roc' in results['metric_name'].values)
        self.assertTrue('vus_pr' in results['metric_name'].values)

class TestComputeMetricsFromFile(unittest.TestCase):
    def setUp(self):
        self.y_true  = np.array([0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1])
        self.y_pred_binary = np.array([0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        self.results_file = 'tests/test_data/results.csv'
        self.conf_file = 'tests/test_data/config.json'

    def test_compute_metrics_from_file(self):
        results_df = compute_metrics_from_file(self.results_file, self.conf_file, output_dir='tests/test_data')
        assert os.path.exists('tests/test_data/computed_metrics.csv'), f"Error: The file 'computed_metrics.csv' was not created."
