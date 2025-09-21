#!/bin/bash

echo "============================================"
echo "PHYS 421 Assignment 2: Monte Carlo Experiments"
echo "============================================"

# Make sure the program is compiled
make clean
make

# Create results directory
mkdir -p results

echo ""
echo "Part C.1: Accuracy vs N experiments"
echo "===================================="
echo "N,Estimated_Volume,Exact_Volume,Relative_Error,Runtime" > results/accuracy_vs_n.csv

for N in 100000 200000 400000 800000 1600000 3200000 6400000
do
    echo "Testing N = $N"
    result=$(./monte_carlo_sphere -n 10 -p 4 -R 1 -N $N -seed 42 2>/dev/null | tail -4)
    
    estimated=$(echo "$result" | grep "Estimated volume:" | awk '{print $3}')
    exact=$(echo "$result" | grep "Exact volume:" | awk '{print $3}')
    error=$(echo "$result" | grep "Relative error:" | awk '{print $3}')
    runtime=$(echo "$result" | grep "Runtime:" | awk '{print $2}')
    
    echo "$N,$estimated,$exact,$error,$runtime" >> results/accuracy_vs_n.csv
done

echo ""
echo "Part C.2: Thread scaling experiments"
echo "====================================="
echo "Threads,Estimated_Volume,Exact_Volume,Relative_Error,Runtime,Speedup,Efficiency" > results/scaling_vs_threads.csv

# First run serial to get baseline
echo "Testing serial (1 thread)"
serial_result=$(./monte_carlo_sphere -n 10 -p 4 -R 1 -N 5000000 -seed 42 2>/dev/null | tail -4)
serial_runtime=$(echo "$serial_result" | grep "Runtime:" | awk '{print $2}')

estimated=$(echo "$serial_result" | grep "Estimated volume:" | awk '{print $3}')
exact=$(echo "$serial_result" | grep "Exact volume:" | awk '{print $3}')
error=$(echo "$serial_result" | grep "Relative error:" | awk '{print $3}')

echo "1,$estimated,$exact,$error,$serial_runtime,1.0,1.0" >> results/scaling_vs_threads.csv

# Test parallel versions
max_threads=$(nproc)
for t in $(seq 2 $max_threads)
do
    echo "Testing $t threads"
    result=$(./monte_carlo_sphere -n 10 -p 4 -R 1 -N 5000000 -parallel -threads $t -seed 42 2>/dev/null | tail -4)
    
    estimated=$(echo "$result" | grep "Estimated volume:" | awk '{print $3}')
    exact=$(echo "$result" | grep "Exact volume:" | awk '{print $3}')
    error=$(echo "$result" | grep "Relative error:" | awk '{print $3}')
    runtime=$(echo "$result" | grep "Runtime:" | awk '{print $2}')
    
    speedup=$(echo "scale=4; $serial_runtime / $runtime" | bc -l)
    efficiency=$(echo "scale=4; $speedup / $t" | bc -l)
    
    echo "$t,$estimated,$exact,$error,$runtime,$speedup,$efficiency" >> results/scaling_vs_threads.csv
done

echo ""
echo "Part C.3: Validation experiments (p=2, different dimensions)"
echo "============================================================"
echo "n,Estimated_Volume,Exact_Volume,Relative_Error,Runtime" > results/validation_dimensions.csv

for n in $(seq 2 10)
do
    echo "Testing n = $n dimensions"
    result=$(./monte_carlo_sphere -n $n -p 2 -R 1 -N 2000000 -parallel -threads 4 -seed 42 2>/dev/null | tail -4)
    
    estimated=$(echo "$result" | grep "Estimated volume:" | awk '{print $3}')
    exact=$(echo "$result" | grep "Exact volume:" | awk '{print $3}')
    error=$(echo "$result" | grep "Relative error:" | awk '{print $3}')
    runtime=$(echo "$result" | grep "Runtime:" | awk '{print $2}')
    
    echo "$n,$estimated,$exact,$error,$runtime" >> results/validation_dimensions.csv
done

echo ""
echo "Part C.4: Schedule comparison"
echo "============================="
echo "Schedule,Chunk_Size,Estimated_Volume,Exact_Volume,Relative_Error,Runtime" > results/schedule_comparison.csv

for schedule in "static" "dynamic"
do
    for chunk in 0 100 1000 10000
    do
        echo "Testing $schedule scheduling with chunk size $chunk"
        if [ $chunk -eq 0 ]; then
            result=$(./monte_carlo_sphere -n 10 -p 4 -R 1 -N 5000000 -parallel -threads 4 -schedule $schedule -seed 42 2>/dev/null | tail -4)
        else
            result=$(./monte_carlo_sphere -n 10 -p 4 -R 1 -N 5000000 -parallel -threads 4 -schedule $schedule -chunk $chunk -seed 42 2>/dev/null | tail -4)
        fi
        
        estimated=$(echo "$result" | grep "Estimated volume:" | awk '{print $3}')
        exact=$(echo "$result" | grep "Exact volume:" | awk '{print $3}')
        error=$(echo "$result" | grep "Relative error:" | awk '{print $3}')
        runtime=$(echo "$result" | grep "Runtime:" | awk '{print $2}')
        
        echo "$schedule,$chunk,$estimated,$exact,$error,$runtime" >> results/schedule_comparison.csv
    done
done

echo ""
echo "Part D (Optional): High dimensional behavior"
echo "==========================================="
echo "n,p,Estimated_Volume,Exact_Volume,Relative_Error,Acceptance_Ratio,Runtime" > results/high_dimensional.csv

for p in 0.5 2 8
do
    for n in $(seq 2 15)
    do
        echo "Testing n = $n, p = $p"
        result=$(./monte_carlo_sphere -n $n -p $p -R 1 -N 1000000 -parallel -threads 4 -seed 42 2>/dev/null)
        
        estimated=$(echo "$result" | grep "Estimated volume:" | awk '{print $3}')
        exact=$(echo "$result" | grep "Exact volume:" | awk '{print $3}')
        error=$(echo "$result" | grep "Relative error:" | awk '{print $3}')
        runtime=$(echo "$result" | grep "Runtime:" | awk '{print $2}')
        
        # Calculate acceptance ratio (estimated volume / hypercube volume)
        hypercube_vol=$(echo "scale=10; 2^$n" | bc -l)
        acceptance_ratio=$(echo "scale=10; $estimated / $hypercube_vol" | bc -l)
        
        echo "$n,$p,$estimated,$exact,$error,$acceptance_ratio,$runtime" >> results/high_dimensional.csv
    done
done

echo ""
echo "============================================"
echo "All experiments completed!"
echo "Results saved in the 'results/' directory:"
echo "- accuracy_vs_n.csv"
echo "- scaling_vs_threads.csv"
echo "- validation_dimensions.csv"
echo "- schedule_comparison.csv"
echo "- high_dimensional.csv"
echo "============================================"
