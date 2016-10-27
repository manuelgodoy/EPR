import numpy as np
import pandas as pd
import sys

def find_error(values):
    return values.std()

def find_average(values):
    return values.mean()

if __name__ == "__main__":
    data = []
    # headers = ['']
    # Rs = {key: [] for key in headers}
    df = pd.DataFrame()

    if len(sys.argv) > 1:
        filename = sys.argv[-1]
        for i in xrange(1,len(sys.argv)-1):
            file_data = pd.read_csv(sys.argv[i])
            data.append(file_data['R pp'][0])
            df['R {0}'.format(str(i))] = file_data['R']

        df['Error'] = find_error(pd.DataFrame(data))
        df['Average'] = find_average(pd.DataFrame(data))
        print "error: %.6g" % find_error(pd.DataFrame(data))
        print "Average: %.6g" % find_average(pd.DataFrame(data))
        df.to_csv(filename, index = False)
    else:
        print "Give me a file"
