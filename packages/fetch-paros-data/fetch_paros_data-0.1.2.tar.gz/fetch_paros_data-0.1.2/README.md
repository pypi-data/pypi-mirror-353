# fetch-paros-data

**fetch-paros-data** is a Python library for querying and processing environmental sensor data from an InfluxDB instance, specifically designed for use with PAROS box deployments.

---

## Installation

Install the latest release from PyPI:

```bash
pip install fetch-paros-data

## Usage 
import os
import numpy as np
from fetch_paros_data import query_influx_data, save_data

# Path to your InfluxDB credentials file
creds_path = os.path.expanduser("~/Desktop/paros-tools/influx-creds.pickle")

# Where to save output
output_path = os.path.expanduser("~/Desktop/DroneData_test.csv")

# Fetch sensor data
data = query_influx_data(
    start_time="2025-02-25T17:30:00",
    end_time="2025-02-25T18:15:00",
    box_id="parosD",
    sensor_id="142180",
    creds=creds_path
)

# Convert to NumPy arrays if needed
data_arrays = {key: df.values for key, df in data.items()}

# Print shape and a preview of each result
for key, arr in data_arrays.items():
    print(f"Data for {key} has shape {arr.shape}")

for key, df in data.items():
    print(f"First 100 rows for {key}:")
    print(df.head(100))
    print("\n")

# Save to file
save_data(data, output_path)
