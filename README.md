# PHYS 421 Assignment 2: Monte Carlo Volume Estimation

## Overview
This project implements a parallel Monte Carlo method using OpenMP to estimate the volume of n-dimensional p-spheres. The implementation includes both serial and parallel versions with comprehensive performance analysis.

## Files Structure
```
├── monte_carlo_sphere.c    # Main C implementation
├── Makefile               # Build configuration
├── run_experiments.sh     # Automated experiment runner
├── plot_results.py       # Python plotting script
├── README.md             # This file
├── results/              # Generated results directory
└── plots/                # Generated plots directory
```

## Building the Project

### Prerequisites
- GCC compiler with OpenMP support
- Python 3 with matplotlib, pandas, numpy (for plotting)
- bc calculator (for shell script calculations)

### Compilation
```bash
make clean
make
```

This creates the executable `monte_carlo_sphere`.

## Usage

### Basic Usage
```bash
./monte_carlo_sphere [options]
```

### Options
- `-n <int>`: Number of dimensions (default: 10)
- `-p <float>`: p-norm value (default: 4.0)
- `-R <float>`: Radius (default: 1.0)
- `-N <long>`: Number of samples (default: 1000000)
- `-seed <int>`: Random seed (default: 42)
- `-parallel`: Enable parallel mode
- `-threads <int>`: Number of threads (default: 1)
- `-schedule <string>`: OpenMP scheduling (static/dynamic)
- `-chunk <int>`: Chunk size for scheduling

### Example Commands

**Serial execution:**
```bash
./monte_carlo_sphere -n 10 -p 4 -R 1 -N 1000000
```

**Parallel execution:**
```bash
./monte_carlo_sphere -n 10 -p 4 -R 1 -N 1000000 -parallel -threads 4
```

**With custom scheduling:**
```bash
./monte_carlo_sphere -n 10 -p 4 -R 1 -N 1000000 -parallel -threads 4 -schedule dynamic -chunk 1000
```

## Running Experiments

### Automated Full Analysis
```bash
chmod +x run_experiments.sh
./run_experiments.sh
```

This runs all required experiments and saves results to CSV files in the `results/` directory.

### Individual Experiments
```bash
# Quick tests
make test_serial
make test_parallel

# Specific experiment types
make accuracy_test
make scaling_test
make validation_test
make schedule_test
```

## Generating Plots and Analysis

After running experiments:
```bash
python3 plot_results.py
```

This generates:
- `plots/accuracy_vs_n.png`: Error vs sample size
- `plots/scaling_analysis.png`: Speedup and efficiency analysis
- `plots/validation_comparison.png`: Monte Carlo vs exact values
- `plots/schedule_comparison.png`: Static vs dynamic scheduling
- `plots/high_dimensional_behavior.png`: High-dimensional analysis
- `results/summary.txt`: Key findings summary

## Implementation Details

### Thread Safety
- Uses `rand_r()` with per-thread seeds for thread-safe random number generation
- Each thread gets seed = base_seed + 1337 * thread_id
- Atomic reduction for hit counting

### Performance Optimizations
- Compiler optimizations: `-O3`
- Efficient power calculations using `pow()`
- Minimal memory allocation per thread
- Cache-friendly data access patterns

### Scheduling Options
- **Static**: Work divided equally among threads at compile time
- **Dynamic**: Work distributed dynamically at runtime
- Chunk sizes can be specified for load balancing

## Expected Results

### Part C.1: Accuracy vs N
- Error should decrease as ~1/√N
- Larger N gives more accurate estimates
- Log-log plot should show -1/2 slope

### Part C.2: Thread Scaling
- Near-linear speedup for low thread counts
- Efficiency typically 70-90% depending on system
- Diminishing returns beyond number of physical cores

### Part C.3: Validation (p=2 case)
- Monte Carlo estimates should match exact values within error bounds
- Relative errors typically < 1% for reasonable N
- Higher dimensions show larger volumes initially, then rapid decay

### Part C.4: Scheduling Comparison
- Static scheduling typically faster for balanced workloads
- Dynamic scheduling helps with load imbalances
- Chunk size affects cache performance

## Troubleshooting

### Common Issues
1. **Compilation errors**: Ensure OpenMP support (`gcc -fopenmp`)
2. **Permission denied**: Make scripts executable (`chmod +x run_experiments.sh`)
3. **Missing dependencies**: Install required Python packages
4. **Memory issues**: Reduce N for high-dimensional cases

### Performance Tips
- Use N ≥ 1M for stable timing measurements
- Test with different thread counts up to your CPU core count
- Monitor system load during experiments
- Use consistent seeds for reproducible results

## Mathematical Background

The n-dimensional p-sphere volume formula:
```
V_n^p(R) = [2Γ(1+1/p)]^n / Γ(1+n/p) * R^n
```

Monte Carlo estimation:
```
V ≈ (hits/N) * (2R)^n
```

Standard error: O(1/√N)

## Assignment Requirements Met

- ✅ **Part A**: Serial baseline implementation
- ✅ **Part B**: OpenMP parallelization with thread-safe RNG
- ✅ **Part C.1**: Accuracy vs N analysis
- ✅ **Part C.2**: Thread scaling analysis
- ✅ **Part C.3**: Validation against exact formula
- ✅ **Part C.4**: Scheduling comparison
- ✅ **Part D**: High-dimensional behavior analysis

## Notes

- All timing uses `omp_get_wtime()` for high precision
- Results are deterministic with fixed seeds
- Error estimates assume normal distribution (Central Limit Theorem)
- High-dimensional cases may require larger N for stability
