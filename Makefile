CC = gcc
CFLAGS = -Wall -O3 -fopenmp -std=c99
LDFLAGS = -lm -fopenmp
TARGET = monte_carlo_sphere
SOURCE = monte_carlo_sphere.c

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)

clean:
	rm -f $(TARGET)

# Test targets
test_serial:
	./$(TARGET) -n 10 -p 4 -R 1 -N 1000000

test_parallel:
	./$(TARGET) -n 10 -p 4 -R 1 -N 1000000 -parallel -threads 4

# Experiment scripts will call these
accuracy_test:
	@echo "Running accuracy vs N experiments..."
	@for N in 100000 200000 400000 800000 1600000 3200000; do \
		echo "N = $$N"; \
		./$(TARGET) -n 10 -p 4 -R 1 -N $$N -seed 42; \
		echo ""; \
	done

scaling_test:
	@echo "Running thread scaling experiments..."
	@for t in 1 2 3 4 5 6 7 8; do \
		echo "Threads = $$t"; \
		./$(TARGET) -n 10 -p 4 -R 1 -N 5000000 -parallel -threads $$t -seed 42; \
		echo ""; \
	done

validation_test:
	@echo "Running validation experiments (n=2 to 10, p=2)..."
	@for n in 2 3 4 5 6 7 8 9 10; do \
		echo "n = $$n"; \
		./$(TARGET) -n $$n -p 2 -R 1 -N 2000000 -parallel -threads 4 -seed 42; \
		echo ""; \
	done

schedule_test:
	@echo "Comparing static vs dynamic scheduling..."
	@echo "Static scheduling:"; \
	./$(TARGET) -n 10 -p 4 -R 1 -N 5000000 -parallel -threads 4 -schedule static -seed 42; \
	echo ""; \
	echo "Dynamic scheduling:"; \
	./$(TARGET) -n 10 -p 4 -R 1 -N 5000000 -parallel -threads 4 -schedule dynamic -seed 42; \
	echo ""

.PHONY: all clean test_serial test_parallel accuracy_test scaling_test validation_test schedule_test
