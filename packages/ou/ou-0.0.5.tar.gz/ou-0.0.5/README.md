# ou
Window pairs of sequences

To install:	```pip install ou```

## Overview
The `ou` package provides tools for analyzing sequences by creating and manipulating pairs of sliding windows over data. This can be particularly useful in time series analysis, event sequence analysis, or any scenario where relationships between different segments of a dataset are of interest.

## Main Features
- **Window Pair Iterators**: Generate pairs of indices representing windows over a data range, which can be used to extract and analyze overlapping or consecutive segments of data.
- **Event Window Analysis**: Functions to handle timestamped event data, allowing analysis of events occurring within specified past and future windows relative to a present moment.
- **Feature Extraction**: Utilities to extract features from data within generated windows, which can be used for further statistical analysis or machine learning.
- **Aggregation and Counting**: Tools to aggregate and count occurrences across pairs of windows, useful for frequency analysis in categorical data.

## Usage Examples

### Window Pair Iteration
Generate sliding window pairs from a data sequence:
```python
from ou import wp_iter_with_sliding_discrete_step
data_range = 10
x_range = 2
y_range = 3
offset = 1

for window_pair in wp_iter_with_sliding_discrete_step(data_range, x_range, y_range, offset):
    print(window_pair)
```

### Event Window Analysis
Analyze events with past and future context:
```python
from ou import past_present_future_idx_and_duration_iter
timestamp_seq = [0, 5, 10, 15, 20]
past_range = 5
future_range = 5

for ppf_idx, duration, present_timestamp in past_present_future_idx_and_duration_iter(timestamp_seq, past_range, future_range):
    print(f"Past-Present-Future Index: {ppf_idx}, Duration: {duration}, Present Timestamp: {present_timestamp}")
```

### Feature Extraction from Data Windows
Extract features using predefined or custom functions applied to data windows:
```python
import pandas as pd
from ou import FeaturePairFactory, extract_series

# Sample data
data = pd.DataFrame({'timestamp': range(0, 100, 10), 'value': range(10)})

# Define feature extraction functions
def sum_values(df):
    return df['value'].sum()

# Setup feature pair factory
factory = FeaturePairFactory(past_feat_func=sum_values, past_range=30)

# Generate feature pairs
for feature_pair in factory.feature_pair_and_duration_iter(data):
    print(feature_pair)
```

### Aggregation of Windowed Data
Aggregate counts across pairs of windows:
```python
from ou import extract_series, agg_counts

# Using the same 'data' DataFrame from the previous example
window_iterator = wp_iter_with_sliding_discrete_step(data_range=len(data))
pairs_of_series = extract_series(data, window_iterator)

# Aggregate counts
aggregated_counts = agg_counts(pairs_of_series)
print(aggregated_counts)
```

## Documentation
Each function and class in the `ou` package is documented with docstrings, providing detailed usage instructions and examples. Users are encouraged to refer to these docstrings for more specific information on function parameters and expected data formats.