import numpy as np
import math

class DensitySampling:
    def __init__(self, density=1.0):
        """
        Args:
            density (float): Density ranges from 0 to 1. Defaults to 1.
                If 1, samples all the data.
                If .5, samples 50% of the data.
        """
        self.density = float(density)
        
    def sample_data(self, data):
        """
        Samples the data set, by picking the data in equal intervals. 
        Note: density and skip_rate are inversly proportional to each other
        So, applying -ve linear relation between them, we come with an equation
        Say, L = length of array, d = density wanted, g = skip_interval(gap)
        We have, g = (1-L)*d + L

        Args:
            data (array): The data set that is to be sampled

        Returns:
            data (array): The sampled data set 
        """
        np_data = np.array(data)
        total_size = np_data.size

        skip_rate = math.floor(((1 - total_size) * self.density) + total_size)
        return np_data[::skip_rate].tolist()
    