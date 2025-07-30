#!/usr/bin/env python3
import argparse
from tsadmetrics.utils import compute_metrics_from_file


def main():
    
    parser = argparse.ArgumentParser(
        description='Compute metrics from anomaly detection results and configuration files.'
    )
    
    
    parser.add_argument(
        '--res_file', 
        type=str, 
        required=True,
        help='Path to the results CSV file (e.g., results.csv)'
    )
    parser.add_argument(
        '--conf_file', 
        type=str, 
        required=True,
        help='Path to the configuration JSON file (e.g., conf.json)'
    )
    parser.add_argument(
        '--output_dir', 
        type=str, 
        required=True,
        help='Directory where output files will be saved (e.g., ./output_dir)'
    )
    
    args = parser.parse_args()
    
    
    compute_metrics_from_file(
        results_file=args.res_file,
        conf_file=args.conf_file,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()