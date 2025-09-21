#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include <string.h>

// Function to compute gamma function for our specific needs
double compute_gamma(double x) {
    return tgamma(x);
}

// Function to compute exact volume of n-dimensional p-sphere
double exact_volume(int n, double p, double R) {
    double gamma_term = compute_gamma(1.0 + 1.0/p);
    double numerator = pow(2.0 * gamma_term, n);
    double denominator = compute_gamma(1.0 + n/p);
    return (numerator / denominator) * pow(R, n);
}

// Function to check if a point is inside the p-sphere
int is_inside_sphere(double *point, int n, double p, double R) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += pow(fabs(point[i]), p);
    }
    return sum <= pow(R, p);
}

// Serial Monte Carlo estimation
double monte_carlo_serial(int n, double p, double R, long N, unsigned int seed) {
    long hits = 0;
    double *point = malloc(n * sizeof(double));
    
    // Set seed for serial version
    srand(seed);
    
    for (long i = 0; i < N; i++) {
        // Generate random point in [-R, R]^n
        for (int j = 0; j < n; j++) {
            double u = (double)rand() / RAND_MAX;
            point[j] = (2.0 * u - 1.0) * R;
        }
        
        if (is_inside_sphere(point, n, p, R)) {
            hits++;
        }
    }
    
    free(point);
    double hypercube_volume = pow(2.0 * R, n);
    return (double)hits / N * hypercube_volume;
}

// Parallel Monte Carlo estimation with OpenMP
double monte_carlo_parallel(int n, double p, double R, long N, unsigned int seed, 
                           const char* schedule_type, int chunk_size) {
    long hits = 0;
    double hypercube_volume = pow(2.0 * R, n);
    
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        unsigned int thread_seed = seed + 1337 * thread_id;
        double *point = malloc(n * sizeof(double));
        long local_hits = 0;
        
        if (strcmp(schedule_type, "static") == 0) {
            if (chunk_size > 0) {
                #pragma omp for schedule(static, chunk_size)
                for (long i = 0; i < N; i++) {
                    for (int j = 0; j < n; j++) {
                        double u = (double)rand_r(&thread_seed) / RAND_MAX;
                        point[j] = (2.0 * u - 1.0) * R;
                    }
                    if (is_inside_sphere(point, n, p, R)) {
                        local_hits++;
                    }
                }
            } else {
                #pragma omp for schedule(static)
                for (long i = 0; i < N; i++) {
                    for (int j = 0; j < n; j++) {
                        double u = (double)rand_r(&thread_seed) / RAND_MAX;
                        point[j] = (2.0 * u - 1.0) * R;
                    }
                    if (is_inside_sphere(point, n, p, R)) {
                        local_hits++;
                    }
                }
            }
        } else {  // dynamic
            if (chunk_size > 0) {
                #pragma omp for schedule(dynamic, chunk_size)
                for (long i = 0; i < N; i++) {
                    for (int j = 0; j < n; j++) {
                        double u = (double)rand_r(&thread_seed) / RAND_MAX;
                        point[j] = (2.0 * u - 1.0) * R;
                    }
                    if (is_inside_sphere(point, n, p, R)) {
                        local_hits++;
                    }
                }
            } else {
                #pragma omp for schedule(dynamic)
                for (long i = 0; i < N; i++) {
                    for (int j = 0; j < n; j++) {
                        double u = (double)rand_r(&thread_seed) / RAND_MAX;
                        point[j] = (2.0 * u - 1.0) * R;
                    }
                    if (is_inside_sphere(point, n, p, R)) {
                        local_hits++;
                    }
                }
            }
        }
        
        #pragma omp atomic
        hits += local_hits;
        
        free(point);
    }
    
    return (double)hits / N * hypercube_volume;
}

int main(int argc, char *argv[]) {
    // Default values
    int n = 10;
    double p = 4.0;
    double R = 1.0;
    long N = 1000000;
    unsigned int seed = 42;
    int num_threads = 1;
    char schedule_type[20] = "static";
    int chunk_size = 0;
    int parallel_mode = 0;
    
    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
            n = atoi(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            p = atof(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-R") == 0 && i + 1 < argc) {
            R = atof(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-N") == 0 && i + 1 < argc) {
            N = atol(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-seed") == 0 && i + 1 < argc) {
            seed = atoi(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-threads") == 0 && i + 1 < argc) {
            num_threads = atoi(argv[i + 1]);
            parallel_mode = 1;
            i++;
        } else if (strcmp(argv[i], "-schedule") == 0 && i + 1 < argc) {
            strcpy(schedule_type, argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-chunk") == 0 && i + 1 < argc) {
            chunk_size = atoi(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-parallel") == 0) {
            parallel_mode = 1;
        }
    }
    
    printf("Monte Carlo Volume Estimation\n");
    printf("==============================\n");
    printf("Dimensions (n): %d\n", n);
    printf("p-norm: %.2f\n", p);
    printf("Radius (R): %.2f\n", R);
    printf("Sample size (N): %ld\n", N);
    printf("Seed: %u\n", seed);
    
    if (parallel_mode) {
        omp_set_num_threads(num_threads);
        printf("Threads: %d\n", num_threads);
        printf("Schedule: %s", schedule_type);
        if (chunk_size > 0) printf(" (chunk size: %d)", chunk_size);
        printf("\n");
    } else {
        printf("Mode: Serial\n");
    }
    printf("==============================\n");
    
    // Compute exact volume
    double exact_vol = exact_volume(n, p, R);
    
    // Run Monte Carlo estimation
    double start_time = omp_get_wtime();
    double estimated_vol;
    
    if (parallel_mode) {
        estimated_vol = monte_carlo_parallel(n, p, R, N, seed, schedule_type, chunk_size);
    } else {
        estimated_vol = monte_carlo_serial(n, p, R, N, seed);
    }
    
    double end_time = omp_get_wtime();
    double runtime = end_time - start_time;
    
    // Calculate relative error
    double relative_error = fabs(estimated_vol - exact_vol) / exact_vol;
    
    // Print results
    printf("Results:\n");
    printf("--------\n");
    printf("Estimated volume: %.10f\n", estimated_vol);
    printf("Exact volume:     %.10f\n", exact_vol);
    printf("Relative error:   %.6e (%.4f%%)\n", relative_error, relative_error * 100);
    printf("Runtime:          %.4f seconds\n", runtime);
    
    return 0;
}
