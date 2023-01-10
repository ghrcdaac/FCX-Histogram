import numpy as np
# 100% of data can be used to show
# 50% of data can be used to show
# 25% of data can be used to show

# many algorithms can be used to sample data based off density
# for now I will just take the data in an equal intervals.

def sample_data(data):
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
    return np_data[::5].tolist()
    