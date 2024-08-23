import numpy as np

def init_lattice(size=8):
    lattice = np.random.choice([1, -1], size=(size, size))
    return np.pad(lattice, pad_width=1, mode='constant', constant_values=0)

def update_spin(lattice, beta, i, j):
    neighbor_sum = lattice[i-1, j] + lattice[i+1, j] + lattice[i, j-1] + lattice[i, j+1]
    exponent = beta * neighbor_sum
    pos_prob = np.exp(exponent)
    neg_prob = np.exp(-exponent)
    prob = pos_prob / (pos_prob + neg_prob)
    lattice[i, j] = np.random.choice([1, -1], p=[prob, 1 - prob])

def run_sweeps(lattice, beta, sweeps):
    size = lattice.shape[0] - 2
    for _ in range(sweeps):
        for i in range(1, size + 1):
            for j in range(1, size + 1):
                update_spin(lattice, beta, i, j)
    return lattice

def generate_sample(T, size=8, sweeps=25):
    beta = 1 / T
    lattice = init_lattice(size)
    return run_sweeps(lattice, beta, sweeps)

def calc_empirical_expectations(T, samples=10000, size=8):
    sum_12, sum_18 = 0, 0
    for idx in range(samples):
        if idx % 500 == 0:
            print(f"Processing sample {idx}")
        sample = generate_sample(T, size)
        sum_12 += sample[1, 1] * sample[2, 2]
        sum_18 += sample[1, 1] * sample[8, 8]
    return sum_12 / samples, sum_18 / samples

def ergodic_expectations(T, size=8, total_sweeps=25000, burn_in=100):
    beta = 1 / T
    lattice = init_lattice(size)
    avg_corr_1_2, avg_corr_1_8 = 0, 0
    lattice = run_sweeps(lattice, beta, burn_in)
    for idx in range(1, total_sweeps - burn_in + 1):
        lattice = run_sweeps(lattice, beta, 1)
        avg_corr_1_2 = ((idx - 1) * avg_corr_1_2 + lattice[1, 1] * lattice[2, 2]) / idx
        avg_corr_1_8 = ((idx - 1) * avg_corr_1_8 + lattice[1, 1] * lattice[8, 8]) / idx
    return avg_corr_1_2, avg_corr_1_8

def main():
    temps = [1, 1.5, 2]
    print("Method 1 - Independent samples")
    for temp in temps:
        expectations = calc_empirical_expectations(temp)
        print(f"For temperature {temp}: E(x[1,1] * x[2,2]) = {expectations[0]}, E(x[1,1] * x[8,8]) = {expectations[1]}")

    print("Method 2 - Ergodicity")
    for temp in temps:
        results = ergodic_expectations(temp)
        print(f"For temperature {temp}: E(x[1,1] * x[2,2]) = {results[0]}, E(x[1,1] * x[8,8]) = {results[1]}")

if __name__ == "__main__":
    main()
