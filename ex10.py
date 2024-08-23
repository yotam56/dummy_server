import numpy as np
import matplotlib.pyplot as plt

def init_lattice(size=100):
    lattice = np.random.choice([1, -1], size=(size, size))
    return np.pad(lattice, pad_width=1, mode='constant', constant_values=0)

def update_spin(lattice, beta, i, j):
    neighbor_sum = lattice[i-1, j] + lattice[i+1, j] + lattice[i, j-1] + lattice[i, j+1]
    exponent = beta * neighbor_sum
    positive_prob = np.exp(exponent)
    negative_prob = np.exp(-exponent)
    prob = positive_prob / (positive_prob + negative_prob)
    lattice[i, j] = np.random.choice([1, -1], p=[prob, 1 - prob])

def perform_sweeps(lattice, beta, num_sweeps):
    size = lattice.shape[0] - 2
    for _ in range(num_sweeps):
        for i in range(1, size + 1):
            for j in range(1, size + 1):
                update_spin(lattice, beta, i, j)
    return lattice

def sample_ising(T, size=100, sweeps=50):
    beta = 1 / T
    lattice = init_lattice(size)
    return perform_sweeps(lattice, beta, sweeps)

def sample_posterior(y, T, size=100, sweeps=50, variance=4):
    beta = 1 / T
    lattice = init_lattice(size)
    sz = lattice.shape[0] - 2
    for _ in range(sweeps):
        for i in range(1, sz + 1):
            for j in range(1, sz + 1):
                neighbor_sum = lattice[i-1, j] + lattice[i+1, j] + lattice[i, j-1] + lattice[i, j+1]
                exponent = beta * neighbor_sum
                positive_term = -1 / (2 * variance)
                positive_difference = y[i, j] - 1
                positive_reg = positive_term * (positive_difference ** 2)
                negative_difference = y[i, j] + 1
                negative_reg = positive_term * (negative_difference ** 2)
                pos_prob = np.exp(exponent + positive_reg)
                neg_prob = np.exp(-exponent + negative_reg)
                prob = pos_prob / (pos_prob + neg_prob)
                lattice[i, j] = np.random.choice([1, -1], p=[prob, 1 - prob])
    return lattice

def icm(y, T, size=100, sweeps=50, variance=4):
    beta = 1 / T
    lattice = init_lattice(size)
    sz = lattice.shape[0] - 2
    for _ in range(sweeps):
        for i in range(1, sz + 1):
            for j in range(1, sz + 1):
                neighbor_sum = lattice[i-1, j] + lattice[i+1, j] + lattice[i, j-1] + lattice[i, j+1]
                exponent = beta * neighbor_sum
                positive_term = -1 / (2 * variance)
                positive_difference = y[i, j] - 1
                positive_reg = positive_term * (positive_difference ** 2)
                negative_difference = y[i, j] + 1
                negative_reg = positive_term * (negative_difference ** 2)
                pos_prob = np.exp(exponent + positive_reg)
                neg_prob = np.exp(-exponent + negative_reg)
                prob = pos_prob / (pos_prob + neg_prob)
                lattice[i, j] = 1 if prob > 0.5 else -1
    return lattice

def sign_random_zero(x):
    return np.random.choice([-1, 1]) if x == 0 else np.sign(x)

def main():
    temperatures = [1, 1.5, 2]
    grid_size = 100
    sweeps = 50
    noise_variance = 4

    fig, axs = plt.subplots(len(temperatures), 5, figsize=(15, 9), gridspec_kw={'width_ratios': [1, 1, 1, 1.2, 1.2]})

    for temp in temperatures:
        original_sample = sample_ising(temp, grid_size, sweeps)
        noise = 2 * np.random.standard_normal(size=(grid_size, grid_size))
        noise = np.pad(noise, ((1, 1), (1, 1)), 'constant', constant_values=0)
        corrupted_sample = original_sample + noise
        restored_sample = sample_posterior(corrupted_sample, temp, grid_size, sweeps, noise_variance)
        icm_sample = icm(corrupted_sample, temp, grid_size, sweeps, noise_variance)
        ml_estimate = np.vectorize(sign_random_zero)(corrupted_sample)

        row = temperatures.index(temp)
        axs[row, 0].imshow(original_sample[1:-1, 1:-1], cmap='gray', vmin=-1, vmax=1)
        axs[row, 0].set_title(f'Original (Temp={temp})')

        axs[row, 1].imshow(corrupted_sample[1:-1, 1:-1], cmap='gray')
        axs[row, 1].set_title('Corrupted')

        axs[row, 2].imshow(restored_sample[1:-1, 1:-1], cmap='gray', vmin=-1, vmax=1)
        axs[row, 2].set_title('Restored')

        axs[row, 3].imshow(icm_sample[1:-1, 1:-1], cmap='gray', vmin=-1, vmax=1)
        axs[row, 3].set_title('ICM')

        axs[row, 4].imshow(ml_estimate[1:-1, 1:-1], cmap='gray')
        axs[row, 4].set_title('ML Estimate')

    fig.suptitle('Binary Image Restoration at Various Temperatures')
    plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95, hspace=0.3, wspace=0.3)
    plt.show()

if __name__ == "__main__":
    main()
