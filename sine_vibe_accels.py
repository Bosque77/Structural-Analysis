from pyNastran.bdf.bdf import BDF
from pyNastran.op2.op2 import OP2
import pickle
import numpy as np
from matplotlib.ticker import MaxNLocator, AutoMinorLocator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import xlsxwriter


# 1) re-organize the acceleration information in a more easy to use format
def get_nodal_accelerations(op2: object, node_ids: set):
    """
    takes in a op2 object and a list of node ids and returns a dictionary that contains
    node_ids as keys and a list of tuples (frequency , ax, ay, az) as values

    :param op2: op2 object
    :param node_ids: list of node ids
    :return: dictionary that contains node_ids:num as keys and a list of tuples (frequency:num , ax:num, ay:num, az:num) as values

    ex: {node_id:num : [(freq:num, ax:num, ay:num, az:num), (freq:num, ax:num, ay:num, az:num), ...]}
    }
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

# 2) read in the nodal limits file to determine your acceleration limits
def read_nodal_limits(file_name: str):
    """
    takes in a file name and returns a dictionary that contains node_ids as keys and a list of tuples (freq, ax, ay, az) as values.
    the limits file is a text file that contains the node ids and the acceleration limits for each node id
    the format of the limits file must be as follows:



    ex: 
        Node 1 X  # to start recording data for node 1 in the x direction (capitalizaiton does not matter)
        5   10    # frequency 5 has an acceleration limit of 10
        10  15    # frequency 10 has an acceleration limit of 15 
        15  15    # ...
        16  5
        100 5

    

    :param file_name: file name of the nodal limits file
    :return: dictionary that contains node_ids:num as keys and a list of tuples (freq, ax, ay, az) as values

    ex: {node_id:num : [(freq:num, ax:num, ay:num, az:num), (freq:num, ax:num, ay:num, az:num), ...]}
    }
    """


    nodal_limits = {}

    # open the file
    with open(file_name, 'r') as file:
        lines = file.readlines()


    record_data = False

    # create a dictionary that contains node_ids as keys and a list of tuples (freq, ax, ay, az) as values
    node_id_to_limits = {}
    for line in lines:
        line = line.strip()
        if line == '' or line.startswith('#'):
            record_data = False
            continue
        


        line = line.split(' ')
        line = [_ for _ in line if _ != '']
        if line[0].lower() == 'node':
            record_data = True
            node_id = int(line[1])
            direction = line[2].lower()

            if node_id not in node_id_to_limits:
                node_id_to_limits[node_id] = {}

            continue


        if record_data:
            freq = float(line[0])
            acc_limit = float(line[1])

            limits = node_id_to_limits.get(node_id)
            freq_limits = limits.get(freq)
            if freq_limits is None:
                if direction == 'x':
                    freq_limits = {'x': acc_limit, 'y': 0, 'z': 0}
                elif direction == 'y':
                    freq_limits = {'x': 0, 'y': acc_limit, 'z': 0}
                elif direction == 'z':
                    freq_limits = {'x': 0, 'y': 0, 'z': acc_limit}
                else:
                    raise ValueError('direction must be x, y, or z')
            else:
                if direction == 'x':
                    freq_limits['x'] = acc_limit
                elif direction == 'y':
                    freq_limits['y'] = acc_limit
                elif direction == 'z':
                    freq_limits['z'] = acc_limit
                else:
                    raise ValueError('direction must be x, y, or z')

            limits[freq] = freq_limits
            node_id_to_limits[node_id] = limits


    # convert the dictionary to a list of tuples
    for node_id in node_id_to_limits:
        limits = node_id_to_limits[node_id]
        freq_limits = []
        for freq in limits:
            freq_limits.append((freq, limits[freq]['x'], limits[freq]['y'], limits[freq]['z']))
        node_id_to_limits[node_id] = freq_limits

    return node_id_to_limits











    return node_id_to_limits

# 3) plot nodal accelerations
def plot_nodal_accelerations(nodal_accelerations: dict, nodal_limits: dict = {}, nodal_names:dict = {}):
    """
    takes in a dictionary that contains node_ids as keys and a list of tuples (frequency , ax, ay, az) as values
    and plots the accelerations  ax vs. frequency, ay vs. frequency, az vs. frequency in a pdf file.  

    :param_1 nodal_accelerations: dictionary that contains node_ids as keys and a list of tuples (frequency , ax, ay, az) as values 
        ex: {node_id:num : [(freq:num, ax:num, ay:num, az:num), (freq:num, ax:num, ay:num, az:num), ...]}
    :param_2 nodal_limits: dictionary that contains node_ids as keys and a list of tuples (min_freq, max_freq, min_accel, max_accel) as values
        ex: {node_id:num : [(freq:num, ax:num, ay:num, az:num), (freq:num, ax:num, ay:num, az:num), ...]}
    :param_3 nodal_names: dictionary that contains the node_ids and there corresponding names {node_id:num: name:str}
    :return: None


    """
    

    # create a pdf file to store the plots
    pdf = PdfPages('nodal_accelerations.pdf')





    # plot the accelerations for each node
    for node_id in nodal_accelerations:

        # nodal name
        nodal_name = nodal_names.get(node_id)

        # limit accels
        limit_accels = nodal_limits.get(node_id)
        if limit_accels is not None:
            limit_freqs = [accel[0] for accel in limit_accels]
            ax_limits = [accel[1] for accel in limit_accels]
            ay_limits = [accel[2] for accel in limit_accels]
            az_limits = [accel[3] for accel in limit_accels]

        
        # extract the nodal accelerations and frequencies for the specified node id
        accels = nodal_accelerations.get(node_id)
        if accels is None:
            print('node id {} not found in nodal_accelerations dictionary'.format(node_id))
            continue
        freqs = [accel[0] for accel in accels]
        ax = [accel[1] for accel in accels]
        ay = [accel[2] for accel in accels]
        az = [accel[3] for accel in accels]


        # interpolate the limit accelerations to the frequencies of the accelerations
        if limit_accels is not None:
            ax_limits = np.interp(freqs, limit_freqs, ax_limits)
            ay_limits = np.interp(freqs, limit_freqs, ay_limits)
            az_limits = np.interp(freqs, limit_freqs, az_limits)
            ax_limits = [ax_limit if ax_limit > 0 else 0 for ax_limit in ax_limits]
            ay_limits = [ay_limit if ay_limit > 0 else 0 for ay_limit in ay_limits]
            az_limits = [az_limit if az_limit > 0 else 0 for az_limit in az_limits]
        


        # plot the accelerations
        fig, axs = plt.subplots(3, 1, sharex=True)




        max_ax_val = max(ax)
        max_ay_val = max(ay)
        max_az_val = max(az)



        axs[0].plot(freqs, ax, label='ax')
        if limit_accels is not None:
            axs[0].plot(freqs, ax_limits, label='ax limits', linestyle='--', color='red')

        if nodal_name is not None:
            title = 'Nodal Accelerations at Node {} ({})'.format(node_id, nodal_name)
        else:
            title = 'Nodal Accelerations at Node {}'.format(node_id)

        axs[0].set_title(title, family='serif', fontsize=10)
        axs[0].autoscale(enable=True, axis='y', tight=None)
        if max_ax_val > 1:
            axs[0].yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            axs[0].yaxis.set_minor_locator(AutoMinorLocator(4))


        axs[0].tick_params(axis='both', which='major', labelsize=8)
        axs[0].set_ylabel('Acceleration (G)', fontsize=8, family='serif')
        axs[0].legend()
        axs[0].grid()
        axs[0].grid(which='minor', alpha=0.2)



        axs[1].plot(freqs, ay, label='ay')
        if limit_accels is not None:
            axs[1].plot(freqs, ay_limits, label='ay limits', linestyle='--', color='red')
        axs[1].autoscale(enable=True, axis='y', tight=None)
        if max_ay_val > 1:
            axs[1].yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            axs[1].yaxis.set_minor_locator(AutoMinorLocator(4))


        axs[1].tick_params(axis='both', which='major', labelsize=8)
        axs[1].set_ylabel('Acceleration (G)', fontsize=8, family='serif')
        axs[1].legend()
        axs[1].grid()
        axs[1].grid(which='minor', alpha=0.2)


        axs[2].plot(freqs, az, label='az')
        if limit_accels is not None:
            axs[2].plot(freqs, az_limits, label='az limits', linestyle='--', color='red')
        axs[2].autoscale(enable=True, axis='y', tight=None)
        if max_az_val > 1:
            axs[2].yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            axs[2].yaxis.set_minor_locator(AutoMinorLocator(4))


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


# 4) write nodal accelerations to excel file
def write_nodal_accelerations_to_excel(output_file_name:str, nodal_accelerations:dict, limit_accels:dict = {}, nodal_names:dict = {}):
    """
    Write the nodal accelerations to an excel file
    
    Parameters
    ----------
    output_file_name : str
        The name of the output file   "output.xlsx"
    nodal_accelerations : dict
        A dictionary of nodal accelerations  {node_id: [(freq, ax, ay, az)]]}
    limit_accels : dict
        A dictionary of limit accelerations {node_id: [(freq, ax, ay, az)]]}
    nodal_name: dict
        A dictionary containing the node names   {node_id: nod_name}


    """

    # create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output_file_name)
    worksheet = workbook.add_worksheet()

    # add a bold format to use to highlight cells
    bold = workbook.add_format({'bold': True})




    # write the data
    row = 2
    col = 0

    for node_id in nodal_accelerations:


        # write the header

        center_format = workbook.add_format({'align': 'center'})

        nodal_name = nodal_names.get(node_id)

        if nodal_name is not None:
            data_name = f'{node_id} - {nodal_name}'
        else:
            data_name = f'{node_id}'
        
        worksheet.merge_range(0, 0, 0, 6, data_name,center_format)
        worksheet.write('A2', 'Frequency (Hz)', bold)
        worksheet.write('B2', 'Ax (G)', bold)
        worksheet.write('C2', 'Ay (G)', bold)
        worksheet.write('D2', 'Az (G)', bold)

        # extract the nodal accelerations
        accels = nodal_accelerations.get(node_id)
        if accels is None:
            print('node id {} not found in nodal_accelerations dictionary'.format(node_id))
            continue
        freqs = [round(accel[0],3) for accel in accels]
        ax = [round(accel[1],2) for accel in accels]
        ay = [round(accel[2],2) for accel in accels]
        az = [round(accel[3],2) for accel in accels]

        # extract and interpolate the limit accels for the node if it exists
        nodal_limit_accels = limit_accels.get(node_id) if limit_accels is not None else None

        if nodal_limit_accels:
            worksheet.write('E2', 'Ax Limit (G)', bold)
            worksheet.write('F2', 'Ay Limit (G)', bold)
            worksheet.write('G2', 'Az Limit (G)', bold)
            limit_freqs = [accel[0] for accel in nodal_limit_accels]
            ax_limits = [accel[1] for accel in nodal_limit_accels]
            ay_limits = [accel[2] for accel in nodal_limit_accels]
            az_limits = [accel[3] for accel in nodal_limit_accels]
            ax_limits = np.interp(freqs, limit_freqs, ax_limits)
            ay_limits = np.interp(freqs, limit_freqs, ay_limits)
            az_limits = np.interp(freqs, limit_freqs, az_limits)
            ax_limits = [round(ax_limit,2) if ax_limit > 0 else 0 for ax_limit in ax_limits]
            ay_limits = [round(ay_limit,2) if ay_limit > 0 else 0 for ay_limit in ay_limits]
            az_limits = [round(az_limit,2) if az_limit > 0 else 0 for az_limit in az_limits]


        # write the data to the excel file
        for i in range(len(freqs)):
            worksheet.write(row, col, freqs[i])
            worksheet.write(row, col + 1, ax[i])
            worksheet.write(row, col + 2, ay[i])
            worksheet.write(row, col + 3, az[i])
            if nodal_limit_accels:
                worksheet.write(row, col + 4, ax_limits[i])
                worksheet.write(row, col + 5, ay_limits[i])
                worksheet.write(row, col + 6, az_limits[i])
            worksheet.write
            row += 1

    workbook.close()




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






if __name__ == "__main__":


    # op2_file_name = './FEA_Model_Examples/sine/frf.op2'
    # pickle_op2(op2_file_name)

    # op2 = load_pickled_op2()
    # node_ids = {181, 182}
    # op2 = load_pickled_op2()

    # nodal_accels = get_nodal_accelerations(op2, node_ids)

    # pickle_nodal_accelerations(nodal_accels)

    nodal_accels = load_pickled_nodal_accelerations()
    nodal_limits = read_nodal_limits('limits.txt')
    # limit = [(5,1,15,1), (10,1,15,1),(25,1,15,1),(20,1,5,1),(100,1,5,1)]
    # nodal_limits = {181:limit}
    nodal_names = {181:'Lower Bar', 182:'Node 2'}
    plot_nodal_accelerations(nodal_accels, nodal_limits, nodal_names)
    # write_nodal_accelerations_to_excel('nodal_accels.xlsx', nodal_accels,nodal_limits, nodal_names)




