import skrf as rf
import numpy as np
import pandas as pd
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    nw = rf.Network(filename)
    nw.plot_s_smith()
    s_par = nw.s
