from pyNastran.bdf.bdf import BDF
from pyNastran.op2.op2 import OP2
import pickle
import numpy as np
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# 1) re-organize the acceleration information in a more easy to use format
def get_nodal_accelerations(op2: object, node_ids: set):
    """
    takes in a op2 object and a list of node ids and returns a dictionary that contains
    node_ids as keys and a list of tuples (frequency , ax, ay, az) as values

    :param op2: op2 object
    :param node_ids: list of node ids
    :return: dictionary that contains node_ids as keys and a list of tuples (frequency , ax, ay, az) as values
    """


    # extract the accelerations, freqs, and node ids from the op2 object
    accelerations = op2.accelerations[1].data
    freqs = op2.accelerations[1].freqs
    op2_node_ids = op2.accelerations[1].node_gridtype[:, 0]

    # convert numpy array of op2 node ids to a list
    op2_node_ids = op2_node_ids.tolist()


    # find the mapping between the node ids in the op2 object and the node ids in the node_ids list
    node_id_map = {}
    for  node_id in node_ids:
        try:
            op2_node_id = op2_node_ids.index(node_id)
            node_id_map[node_id] = op2_node_id
        except ValueError:
            print('node id {} not found in op2 object'.format(node_id))
            continue


    # create a dictionary that contains node_ids as keys and a list of frequency and acceleration pairs as values
    node_id_to_accels = {}
    for node_id in node_id_map:
        accel_index = node_id_map[node_id]
        mag_of_accelerations = []

        for i in range(len(accelerations)):
            acceleration = accelerations[i][accel_index]
            ax = np.abs(acceleration[0])
            ay = np.abs(acceleration[1])
            az = np.abs(acceleration[2])
            freq = freqs[i]
            mag_of_accelerations.append((freq, ax, ay, az))

        node_id_to_accels[node_id] = mag_of_accelerations

    return node_id_to_accels




# 2) plot nodal accelerations
def plot_nodal_accelerations(nodal_accelerations: dict, nodal_limits: dict = None):
    """
    takes in a dictionary that contains node_ids as keys and a list of tuples (frequency , ax, ay, az) as values
    and plots the accelerations  ax vs. frequency, ay vs. frequency, az vs. frequency in a pdf file.  

    :param nodal_accelerations: dictionary that contains node_ids as keys and a list of tuples (frequency , ax, ay, az) as values
    :return: None


    """
    

    # create a pdf file to store the plots
    pdf = PdfPages('nodal_accelerations.pdf')





    # plot the accelerations for each node
    for node_id in nodal_accelerations:
        # extract the accelerations and frequencies
        accels = nodal_accelerations[node_id]
        freqs = [accel[0] for accel in accels]
        ax = [accel[1] for accel in accels]
        ay = [accel[2] for accel in accels]
        az = [accel[3] for accel in accels]

        # plot the accelerations
        fig, axs = plt.subplots(3, 1, sharex=True)




        max_ax_val = max(ax)
        max_ay_val = max(ay)
        max_az_val = max(az)



        axs[0].plot(freqs, ax, label='ax')
        axs[0].set_title('Nodal Accelerations at Node {}'.format(node_id), family='serif', fontsize=10)
        axs[0].autoscale(enable=True, axis='y', tight=None)
        if max_ax_val > 1:
            axs[0].yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            axs[0].set_ylim(bottom=0, top=max_ax_val*1.1)

        axs[0].tick_params(axis='both', which='major', labelsize=8)
        axs[0].set_ylabel('Acceleration (G)', fontsize=8, family='serif')
        axs[0].legend()
        axs[0].grid()
        axs[0].grid(which='minor', alpha=0.2)



        axs[1].plot(freqs, ay, label='ay')
        axs[1].autoscale(enable=True, axis='y', tight=None)
        if max_ay_val > 1:
            axs[1].yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            axs[1].set_ylim(bottom=0, top=max_ay_val*1.1)

        axs[1].tick_params(axis='both', which='major', labelsize=8)
        axs[1].set_ylabel('Acceleration (G)', fontsize=8, family='serif')
        axs[1].legend()
        axs[1].grid()
        axs[1].grid(which='minor', alpha=0.2)


        axs[2].plot(freqs, az, label='az')

        axs[2].autoscale(enable=True, axis='y', tight=None)
        if max_az_val > 1:
            axs[2].yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            axs[2].set_ylim(bottom=0, top=max_az_val*1.1)

        axs[2].tick_params(axis='both', which='major', labelsize=8)
        axs[2].set_ylabel('Acceleration (G)', fontsize=8, family='serif')
        axs[2].legend()


        axs[2].set_xlim(left=0, right=100)
        axs[2].set_xlabel('Frequency (Hz)', fontsize=8)
        axs[2].set_xticks(np.arange(0, max(freqs), 10))
        axs[2].set_xticks(np.arange(0, max(freqs), 5), minor=True)
        axs[2].grid()
        axs[2].grid(which='minor', alpha=0.2)
  
        pdf.savefig(fig)
        plt.close()

    pdf.close()



# -------------------- Helper Functions--------------------#
def pickle_op2(op2_file_name):
    op2 = OP2()
    op2.read_op2(op2_file_name)
    with open('op2_model.pkl', 'wb') as outfile:
        pickle.dump(op2, outfile)


def load_pickled_op2():
    with open('op2_model.pkl', 'rb') as infile:
        op2 = pickle.load(infile)
    return op2

def pickle_nodal_accelerations(nodal_accelerations):
    with open('nodal_accelerations.pkl', 'wb') as outfile:
        pickle.dump(nodal_accelerations, outfile)

def load_pickled_nodal_accelerations():
    with open('nodal_accelerations.pkl', 'rb') as infile:
        nodal_accelerations = pickle.load(infile)
    return nodal_accelerations








    print('pause here')


if __name__ == "__main__":


    # op2_file_name = './FEA_Model_Examples/sine/frf.op2'
    # pickle_op2(op2_file_name)

    # op2 = load_pickled_op2()
    # node_ids = {181, 182}
    # op2 = load_pickled_op2()

    # nodal_accels = get_nodal_accelerations(op2, node_ids)

    # pickle_nodal_accelerations(nodal_accels)

    nodal_accels = load_pickled_nodal_accelerations()
    plot_nodal_accelerations(nodal_accels)





    print('pause here')



