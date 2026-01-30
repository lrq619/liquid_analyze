import pandas as pd

import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt
import json
from tqdm import tqdm
import time
from typing import Tuple, List

TRACE_TIME_SPAN = 3600 * 1000 # trace is one hour 3600 * 1000 milliseconds
TIME_DELTA = 0.001 # the value changes in a very short time to simulate pulse function

class EventTimestamp:
    def __init__(self, ts, event):
        self.ts = ts
        self.event = event

class TimeSeriesFunction:
    def __init__(self, timestamps, values):
        """
        keypoints: List of (timestamp, value) tuples.
        """
        self.timestamps = np.asarray(timestamps)    
        self.values = np.asarray(values)
        self.interpolator = scipy.interpolate.interp1d(self.timestamps, self.values, kind='linear', fill_value="extrapolate")

    def evaluate(self, t):
        return float(self.interpolator(t))
        
    def get_nearest_value(self, t):
        """
        Get the nearest value to the given timestamp t.
        """
        idx = np.searchsorted(self.timestamps, t)
        if idx == 0:
            return self.values[0]
        elif idx == len(self.timestamps):
            return self.values[-1]
        else:
            left_value = self.values[idx - 1]
            return left_value

    def sample(self,num_points=100):
        min_timestamp = min(self.timestamps)
        max_timestamp = max(self.timestamps)
        delta_time = (max_timestamp - min_timestamp) / num_points
        sampled_timestamps = [min_timestamp + delta_time * (i+1) for i in range(num_points)]
        sampled_values = [self.evaluate(t) for t in sampled_timestamps]
        return sampled_timestamps, sampled_values


    def plot(self, num_points=100):
        """Plot the interpolated function and return a matplotlib.figure.Figure instance."""
        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(self.timestamps, self.values, color="red", label="Key Points", zorder=3)

        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.grid(True)

        return fig  # Return the figure instance

    def __repr__(self):
        return repr(self.data)
        

