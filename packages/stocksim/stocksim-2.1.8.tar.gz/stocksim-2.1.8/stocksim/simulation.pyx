# filepath: c:\Users\storage\StockSim\stocksim\simulation.pyx
import numpy as np
cimport numpy as np

np.import_array()  # Ensure numpy C-API is initialized

def simulate_batch(float start_price, float mean_return, float volatility, float years, int batch_len):
    """
    Run a batch of Monte Carlo simulations for geometric Brownian motion.
    Returns an array of simulated ending prices.
    """
    cdef int n_steps = int(252 * years)
    cdef float dt = years / n_steps
    cdef float drift = (mean_return - 0.5 * volatility ** 2) * dt
    cdef float vol = volatility * np.sqrt(dt)
    cdef np.ndarray[np.float32_t, ndim=2] rand_norm = np.random.normal(0, 1, (batch_len, n_steps)).astype(np.float32)
    cdef np.ndarray[np.float32_t, ndim=2] increments = drift + vol * rand_norm
    cdef np.ndarray[np.float32_t, ndim=1] log_returns = increments.sum(axis=1)
    return start_price * np.exp(log_returns)