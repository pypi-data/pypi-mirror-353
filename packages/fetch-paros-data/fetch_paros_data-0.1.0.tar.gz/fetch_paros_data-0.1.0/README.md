# fetch-paros-data

A Python library for fetching and processing sensor data from an InfluxDB instance used with PAROS boxes.

## Install (local)

```bash
pip install ./dist/fetch_paros_data-0.1.0-py3-none-any.whl

# EXAMPLE USAGE
import os
import parosdata 
import numpy as np  # Import NumPy for array handling

creds_path = os.path.expanduser("~/Desktop/paros-tools/influx-creds.pickle")
output_path = os.path.expanduser("~/Desktop/DroneData_test.csv")

# Fetch data as a dictionary of Pandas DataFrames
data = parosdata.query_influx_data(
    start_time="2025-02-25T17:30:00",
    end_time="2025-02-25T18:15:00",
    box_id="parosD",
    sensor_id="142180",
    creds=creds_path
)

# Convert each DataFrame into a NumPy array, store in a new dictionary
data_arrays = {key: df.values for key, df in data.items()}

# Example usage: print shape of arrays
for key, arr in data_arrays.items():
    print(f"Data for {key} has shape {arr.shape}")

# Print the first 100 rows of each DataFrame
for key, df in data.items():
    print(f"First 100 rows for {key}:")
    print(df.head(100))
    print("\n")  # Add some spacing between outputs


# Save the original DataFrames as CSV files
parosdata.save_data(data, output_path)
