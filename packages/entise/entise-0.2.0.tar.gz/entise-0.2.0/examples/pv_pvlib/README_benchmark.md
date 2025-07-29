# PVLib Benchmark

This directory contains a benchmark script for testing the performance of the PVLib method with 100 PV objects.

## Benchmark Description

The benchmark script `benchmark_pvlib.py` performs the following tasks:

1. Generates 100 PV objects with varying parameters:
   - Latitude and longitude with small random variations around a base location
   - Power ratings between 1kW and 20kW
   - Azimuth angles between 0° and 360°
   - Tilt angles between 0° and 90°

2. Uses the PVLib method to generate time series for all objects

3. Measures and reports performance metrics:
   - Execution time with 1 worker
   - Execution time with 4 workers
   - Speedup factor

4. Visualizes the results with:
   - Histogram of maximum generation
   - Histogram of total generation
   - Sample daily profiles for a few systems

## Running the Benchmark

To run the benchmark, navigate to the `examples/pv_pvlib` directory and run:

```bash
python benchmark_pvlib.py
```

## Benchmark Results

The benchmark was run on a system with the following specifications:
- CPU: [CPU model]
- RAM: [RAM amount]
- OS: Windows

### Performance Metrics

| Configuration | Execution Time | Speedup |
|---------------|---------------|---------|
| 1 worker      | 28.07 seconds | 1.00x   |
| 4 workers     | 12.49 seconds | 2.25x   |

### Summary Statistics

The benchmark generated PV time series for 100 objects with varying parameters. Here are the summary statistics for a few example objects:

| Object ID | Generation (kWh/a) | Maximum Generation (W) | Full Load Hours (h) |
|-----------|-------------------|------------------------|---------------------|
| pv_1      | 11,130            | 8,348                  | 1,047               |
| pv_2      | 4,220             | 3,162                  | 1,114               |
| pv_3      | 15,251            | 11,538                 | 766                 |
| pv_4      | 17,030            | 13,830                 | 915                 |
| pv_5      | 4,485             | 3,490                  | 631                 |

### Observations

1. **Parallelization Efficiency**: Using 4 workers provides a 2.25x speedup compared to using 1 worker. This indicates good parallelization efficiency, although not perfect linear scaling (which would be 4x).

2. **Generation Variability**: The PV objects show significant variability in generation, maximum power, and full load hours due to the random variations in parameters (azimuth, tilt, power rating).

3. **Performance Considerations**: The PVLib method is computationally intensive but provides accurate results. For large-scale simulations with hundreds or thousands of objects, parallel processing is essential for reasonable execution times.

## Conclusion

The benchmark demonstrates that the PVLib method can efficiently generate time series for 100 PV objects in a reasonable amount of time, especially when using parallel processing. The method produces realistic PV generation profiles with appropriate variability based on the input parameters.