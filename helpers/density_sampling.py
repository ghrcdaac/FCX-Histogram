import numpy as np
import math
# 100% of data can be used to show
# 50% of data can be used to show
# 25% of data can be used to show

# many algorithms can be used to sample data based off density
# for now I will just take the data in an equal intervals.

class DensitySampling:
    def __init__(self, density=1.0):
        """
        Args:
            density (float): Density ranges from 0 to 1. Defaults to 1.
                If 1, samples all the data.
                If .5, samples 50% of the data.
        """
        self.density = density
        
    def sample_data(self, data):
        """
        Samples the data set, by picking the data in equal intervals. 
        Currently takes 1 out of 5 data sets
        TODO: Explore other algorithms to sample the data.

        Args:
            data (array): The data set that is to be sampled

        Returns:
            data (array): The sampled data set 
        """
        np_data = np.array(data)
        
        #  using the density value and total length of input data, find the skip rate.
        skip_rate = math.floor(np_data.size * self.density)
        print(">>>>>>>", skip_rate)
        return np_data[::skip_rate].tolist()
    