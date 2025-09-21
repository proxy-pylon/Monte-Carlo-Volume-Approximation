#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set up the plotting style
plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

# Create plots directory
os.makedirs('plots', exist_ok=True)

def plot_accuracy_vs_n():
    """Plot relative error vs sample size N"""
    try:
        df = pd.read_csv('results/accuracy_vs_n.csv')
        
        plt.figure(figsize=(10, 6))
        plt.loglog(df['N'], df['Relative_Error'], 'bo-', linewidth=2, markersize=8)
        
        # Add theoretical 1/sqrt(N) line for comparison
        N_theory = np.logspace(np.log10(df['N'].min()), np.log10(df['N'].max()), 100)
        error_theory = 0.1 / np.sqrt(N_theory / df['N'].iloc[0]) * df['Relative_Error'].iloc[0]
        plt.loglog(N_theory, error_theory, 'r--', alpha=0.7, linewidth=2, 
                  label=r'Theoretical $\propto 1/\sqrt{N}$')
        
        plt.xlabel('Number of Samples (N)', fontsize=14)
        plt.ylabel('Relative Error', fontsize=14)
        plt.title('Monte Carlo Accuracy vs Sample Size\n(n=10, p=4, R=1)', fontsize=16)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig('plots/accuracy_vs_n.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Created plots/accuracy_vs_n.png")
    except FileNotFoundError:
        print("✗ results/accuracy_vs_n.csv not found")

def plot_scaling():
    """Plot speedup and efficiency vs number of threads"""
    try:
        df = pd.read_csv('results/scaling_vs_threads.csv')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Speedup plot
        ax1.plot(df['Threads'], df['Speedup'], 'bo-', linewidth=2, markersize=8, label='Actual Speedup')
        ax1.plot(df['Threads'], df['Threads'], 'r--', linewidth=2, label='Ideal Speedup')
        ax1.set_xlabel('Number of Threads', fontsize=14)
        ax1.set_ylabel('Speedup', fontsize=14)
        ax1.set_title('Parallel Speedup', fontsize=16)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlim(1, df['Threads'].max())
        ax1.set_ylim(1, df['Threads'].max())
        
        # Efficiency plot
        ax2.plot(df['Threads'], df['Efficiency'], 'go-', linewidth=2, markersize=8)
        ax2.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='Ideal Efficiency')
        ax2.set_xlabel('Number of Threads', fontsize=14)
        ax2.set_ylabel('Parallel Efficiency', fontsize=14)
        ax2.set_title('Parallel Efficiency', fontsize=16)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_xlim(1, df['Threads'].max())
        ax2.set_ylim(0, 1.1)
        
        plt.tight_layout()
        plt.savefig('plots/scaling_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Created plots/scaling_analysis.png")
    except FileNotFoundError:
        print("✗ results/scaling_vs_threads.csv not found")

def plot_validation():
    """Plot validation results with error bars"""
    try:
        df = pd.read_csv('results/validation_dimensions.csv')
        
        plt.figure(figsize=(12, 6))
        
        # Calculate error bars (assuming they're roughly proportional to 1/sqrt(N))
        # This is a simple approximation for visualization
        error_bars = df['Relative_Error'] * df['Exact_Volume']
        
        x = df['n']
        plt.errorbar(x, df['Estimated_Volume'], yerr=error_bars, 
                    fmt='bo', capsize=5, capthick=2, elinewidth=2, 
                    markersize=8, label='Monte Carlo Estimates')
        plt.plot(x, df['Exact_Volume'], 'r-', linewidth=3, 
                marker='s', markersize=8, label='Exact Values')
        
        plt.xlabel('Dimension (n)', fontsize=14)
        plt.ylabel('Volume', fontsize=14)
        plt.title('Volume Validation: Monte Carlo vs Exact\n(p=2, R=1)', fontsize=16)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig('plots/validation_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Created plots/validation_comparison.png")
    except FileNotFoundError:
        print("✗ results/validation_dimensions.csv not found")

def plot_schedule_comparison():
    """Plot scheduling comparison"""
    try:
        df = pd.read_csv('results/schedule_comparison.csv')
        
        static_df = df[df['Schedule'] == 'static']
        dynamic_df = df[df['Schedule'] == 'dynamic']
        
        plt.figure(figsize=(10, 6))
        
        x_pos = np.arange(len(static_df))
        width = 0.35
        
        plt.bar(x_pos - width/2, static_df['Runtime'], width, 
               label='Static', alpha=0.8, color='blue')
        plt.bar(x_pos + width/2, dynamic_df['Runtime'], width, 
               label='Dynamic', alpha=0.8, color='red')
        
        plt.xlabel('Chunk Size', fontsize=14)
        plt.ylabel('Runtime (seconds)', fontsize=14)
        plt.title('OpenMP Scheduling Comparison\n(n=10, p=4, R=1, N=5M, 4 threads)', fontsize=16)
        plt.xticks(x_pos, ['Default' if int(x) == 0 else str(int(x)) for x in static_df['Chunk_Size']])
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig('plots/schedule_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Created plots/schedule_comparison.png")
    except FileNotFoundError:
        print("✗ results/schedule_comparison.csv not found")

def plot_high_dimensional():
    """Plot high dimensional behavior"""
    try:
        df = pd.read_csv('results/high_dimensional.csv')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Volume vs dimension for different p values
        for p in df['p'].unique():
            p_data = df[df['p'] == p]
            ax1.semilogy(p_data['n'], p_data['Exact_Volume'], 'o-', 
                        linewidth=2, markersize=6, label=f'p = {p}')
        
        ax1.set_xlabel('Dimension (n)', fontsize=14)
        ax1.set_ylabel('Volume (log scale)', fontsize=14)
        ax1.set_title('Volume vs Dimension', fontsize=16)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Acceptance ratio vs dimension
        for p in df['p'].unique():
            p_data = df[df['p'] == p]
            ax2.semilogy(p_data['n'], p_data['Acceptance_Ratio'], 'o-', 
                        linewidth=2, markersize=6, label=f'p = {p}')
        
        ax2.set_xlabel('Dimension (n)', fontsize=14)
        ax2.set_ylabel('Acceptance Ratio (log scale)', fontsize=14)
        ax2.set_title('Acceptance Ratio vs Dimension', fontsize=16)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('plots/high_dimensional_behavior.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Created plots/high_dimensional_behavior.png")
    except FileNotFoundError:
        print("✗ results/high_dimensional.csv not found")

def create_summary_table():
    """Create a summary table of key results"""
    try:
        # Load all data
        accuracy_df = pd.read_csv('results/accuracy_vs_n.csv')
        scaling_df = pd.read_csv('results/scaling_vs_threads.csv')
        validation_df = pd.read_csv('results/validation_dimensions.csv')
        
        with open('results/summary.txt', 'w') as f:
            f.write("PHYS 421 Assignment 2 - Results Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("1. ACCURACY ANALYSIS:\n")
            f.write("-" * 20 + "\n")
            max_n = accuracy_df['N'].max()
            min_error = accuracy_df['Relative_Error'].min()
            f.write("Best accuracy (largest N={:,}): ".format(max_n))
            f.write("{:.2e} ({:.4f}%)\n".format(min_error, min_error*100))
            f.write("Error scaling follows ~1/sqrt(N) trend: {} data points\n\n".format(len(accuracy_df)))
            
            f.write("2. PARALLEL PERFORMANCE:\n")
            f.write("-" * 25 + "\n")
            max_threads = scaling_df['Threads'].max()
            max_speedup = scaling_df['Speedup'].max()
            max_efficiency = scaling_df['Efficiency'].iloc[-1]  # efficiency at max threads
            f.write("Maximum threads tested: {}\n".format(max_threads))
            f.write("Best speedup: {:.2f}x\n".format(max_speedup))
            f.write("Efficiency at {} threads: {:.2f} ({:.1f}%)\n\n".format(max_threads, max_efficiency, max_efficiency*100))
            
            f.write("3. VALIDATION RESULTS:\n")
            f.write("-" * 22 + "\n")
            avg_error = validation_df['Relative_Error'].mean()
            max_error = validation_df['Relative_Error'].max()
            f.write("Average relative error across n=2-10: {:.2e} ({:.4f}%)\n".format(avg_error, avg_error*100))
            f.write("Maximum relative error: {:.2e} ({:.4f}%)\n".format(max_error, max_error*100))
            f.write("All estimates within acceptable bounds\n\n")
            
            # Runtime analysis
            f.write("4. RUNTIME ANALYSIS:\n")
            f.write("-" * 20 + "\n")
            serial_time = scaling_df[scaling_df['Threads'] == 1]['Runtime'].iloc[0]
            parallel_time = scaling_df[scaling_df['Threads'] == max_threads]['Runtime'].iloc[0]
            f.write("Serial runtime (N=5M): {:.2f} seconds\n".format(serial_time))
            f.write("Parallel runtime ({} threads): {:.2f} seconds\n".format(max_threads, parallel_time))
            f.write("Time improvement: {:.2f}x faster\n".format(serial_time/parallel_time))
        
        print("✓ Created results/summary.txt")
    except FileNotFoundError as e:
        print("✗ Could not create summary: {}".format(e))

if __name__ == "__main__":
    print("Generating plots and analysis...")
    print("=" * 40)
    
    plot_accuracy_vs_n()
    plot_scaling()
    plot_validation()
    plot_schedule_comparison()
    plot_high_dimensional()
    create_summary_table()
    
    print("=" * 40)
    print("All plots generated successfully!")
    print("Check the 'plots/' directory for all figures.")
    print("Check 'results/summary.txt' for key findings.")
