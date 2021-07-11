import os
import numpy as np
import pandas as pd

class DataReader:
    
    def __init__(self, inputname, isFolder=False):
        self.data = pd.DataFrame()
        if (isFolder):
            for fname in os.listdir(inputname):
                self.data = self.data.append(pd.read_csv(os.path.join(inputname, fname), parse_dates=True))
        else:
            self.data = pd.read_csv(inputname, parse_dates=True)
        self.data["Date"] = pd.to_datetime(self.data["Date"], infer_datetime_format=True)
        self.data.sort_values(by="Date", inplace=True, ascending=True)
        self.data.set_index("Date", inplace=True, drop=False)