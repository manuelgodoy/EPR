import matplotlib.pyplot as plt
import numpy, random

# hl, = plt.plot([], [])

f, axarr = plt.subplots(3, sharex = True)
plt.ion()
axarr[0].set_xlim([0, 20])
axarr[1].set_xlim([0, 20])
axarr[2].set_xlim([0, 20])

def update_line(i,new_data):
    # hl.set_xdata(numpy.append(hl.get_xdata(), new_data))
    # hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    # ax.relim()
    # ax.autoscale_view()
    plt.scatter(i,new_data)
    plt.pause(0.5)

if __name__ == "__main__":
    for i in xrange(20):
        # update_line(i,random.randrange(1,100))
        axarr[0].scatter(i,random.randrange(1,100))
        axarr[1].scatter(i,random.randrange(1,100))
        axarr[2].scatter(i,random.randrange(1,100))
        plt.pause(0.5)
