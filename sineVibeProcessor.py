# Name: Forest Schwartz
# Date: 10/27/2022
# Summary:  This module is used to determine the max loadcases for elements in a sine vibe analysis
#  It will come up with the max load based on maximum [P, V1, V2, T, M2, M1, VRSS, MRSS, Sigma_Bending ]

from enum import Enum
import numpy as np
import math
from pyNastran.bdf.bdf import BDF
from pyNastran.op2.op2 import OP2
from nasDataTypes import Property
import pickle
import os
from my_types import ElementSummary


class LoadCaseId(Enum):
    P = 'P'
    V1 = 'V1'
    V2 = 'V2'
    T = 'T'
    M2 = 'M2'
    M1 = 'M1'
    VRSS = 'VRSS'
    MRSS = 'MRSS'


# 1) Extract model properties from your model
def extractModelProperties(bdf_model: BDF) -> dict:
    """
    extracts the properties from a bdf file and organizes it in a dictionary

    param_1: file name of bdf to extract
    returns: dictionary of properties  {pid: property_object defined in nasDataTypes}
    """

    model = bdf_model

    # Creating a list of Property Objects
    properties = {}
    for property in model.properties:
        property_object = Property()
        prop = model.properties.get(property)
        if prop.type == 'PBEAM':  # Only storing the beam properties
            prop_info_string = prop.comment
            start = ":"
            end = "\n"
            prop_name = prop_info_string.split(start)[1].split(end)[0]
            property_object.name = prop_name
            # property_object.mid = prop.mid
            property_object.pid = prop.pid
            property_object.A = prop.A[0]
            property_object.I1 = prop.i1[0]
            property_object.I2 = prop.i2[0]
            property_object.J = prop.j[0]
            property_object.C = [prop.c1[0], prop.c2[0]]  # Stress recovery point 1
            property_object.D = [prop.d1[0], prop.d2[0]]  # Stress recovery point 2
            property_object.E = [prop.e1[0], prop.e2[0]]  # Stress recovery point 3
            property_object.F = [prop.f1[0], prop.f2[0]]  # Stress recovery point 4

            Y_Coord = [abs(prop.c1[0]), abs(prop.d1[0]), abs(prop.e1[0]), abs(prop.f1[0])]
            Z_Coord = [abs(prop.c2[0]), abs(prop.d2[0]), abs(prop.e2[0]), abs(prop.f2[0])]

            property_object.C1 = max(Y_Coord)
            property_object.C2 = max(Z_Coord)
            # Need to add the shear area ratio
            properties[property_object.pid] = property_object

    return properties


# 2) Determine the properties of the elements you are analyzing
def determineElementProperties(bdf_model: BDF, element_ids: set = None) -> dict:
    """
    this function determines the properties for a set of element ids and stores it in a dictionary

    param_1: bdf_model    a pynastran bdf object
    param_2: set of elements
    returns: a dictionary matching the element id to its property   {element_id: pid}
    """

    model = bdf_model
    model_elements = model.elements

    # Creating a list of Property Objects
    element_properties = {}

    if element_ids is None:
        for element_id in model_elements:
            element = model_elements.get(element_id)
            element_properties[element_id] = element.pid
    else:
        for element_id in element_ids:
            element = model_elements.get(element_id)
            element_properties[element_id] = element.pid
    return element_properties


# 3) Re-Organize the load information in a more easy to use format
def organizeElementLoadsFromOP2(op2_model: OP2, element_ids: set) -> dict:
    """
    takes in the op2 file and organizes the beam load information in a more easy to use format.

    param_1: op2_file_name
    param_2: element_ids to analyze
    returns:  dictionary    {element_id : {freq_1 : [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque],
                                                    [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
                                           freq_2:  [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque],
                                                    [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
                                                     }
                             element_id_2: ...
                                                    }
    """
    op2 = op2_model

    # the beam forces is a ndarry : (frequencies, elements , forces)  the forces are 8 forces
    # 8 = [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
    beam_forces = op2.cbeam_force[1].data  # {ndarray: (frequencies, elements, forces)}
    element_order = op2.cbeam_force[1].element
    freq_order = op2.cbeam_force[1].freqs

    element_location_dict = {}
    for element_id in element_ids:

        positions = []
        for index, element in enumerate(element_order):
            if element == element_id:
                positions.append(index)
        element_location_dict[element_id] = positions

    element_load_dict = {}
    for element_id in element_ids:

        load_positions = element_location_dict[element_id]
        freq_data = {}
        for index, freq in enumerate(freq_order):
            current_frequency_beam_forces = beam_forces[index]
            loads = []
            for position in load_positions:
                load = current_frequency_beam_forces[position]
                loads.append(load)
            freq_data[freq] = loads
        element_load_dict[element_id] = freq_data

    return element_load_dict


# 4) Save/Pickle all of this information for easy access
def saveAndPickleImportantInfo(bdf_file_name: str, op2_file_name: str, element_ids: set):
    """
    this functions takes in the bdf_file_name op2_file_name and a set of elements and reorganizes the important
    information needed for the stress run analysis and then pickles those objects for use later on.

    param_1: bdf_file_name
    param_2: op2_file_name
    param_3: set of element_ids
    returns:  None  (Creates bdf_model.pkl, op2_model.pkl, model_properties.pkl, element_properties.pkl, element_loads.pkl)
    """
    # extract and pickle important information
    bdf_model = BDF()
    bdf_model.read_bdf(bdf_file_name, xref=True)
    with open('bdf_model.pkl', 'wb') as outfile:
        pickle.dump(bdf_model, outfile)

    op2 = OP2()
    op2.read_op2(op2_file_name)
    with open('op2_model.pkl', 'wb') as outfile:
        pickle.dump(op2, outfile)

    properties = extractModelProperties(bdf_model)
    with open('model_properties.pkl', 'wb') as outfile:
        pickle.dump(properties, outfile)

    element_properties = determineElementProperties(bdf_model, element_ids)
    with open('element_properties.pkl', 'wb') as outfile:
        pickle.dump(element_properties, outfile)

    element_loads = organizeElementLoadsFromOP2(op2, element_ids)
    with open('element_loads.pkl', 'wb') as outfile:
        pickle.dump(element_loads, outfile)


# 5) Determine the critical frequencies for each element
def determineCriticalFrequencies(element_loads, element_properties, model_properties):
    """
    this function determines the critical frequencies for each element.

    param_1:  element_loads - this is the dictionary that was created by organizeElementLoads
    param_2: element_properties - this is a dictionary that maps the element id to the property id
    param_3: model_properties - this is a dicitonary that maps the property id to the Property Class defined in nasDataTypes
    returns:  dict { element_id : critical_frequencies }
              critical_frequencies: dict = { 'P': frequency_value, 'V1':... }
              The keys are  'P', 'V1', 'V2', 'T', 'M2' , 'M1', 'VRSS', 'MRSS'
    """

    element_critical_frequencies = {}

    for element_id in element_loads:
        element = element_loads.get(element_id)
        property_id = element_properties[element_id]
        property = model_properties[property_id]

        freq_keys = list(element.keys())

        first_freq = freq_keys[0]

        # keeps track of the max loadcase for each of the cases shown below
        freq_index = {
            'P': first_freq,
            'V1': first_freq,
            'V2': first_freq,
            'T': first_freq,
            'M2A': first_freq,
            'M1A': first_freq,
            'M2B': first_freq,
            'M1B': first_freq,
            'VRSS': first_freq,
            'MRSS': first_freq,
            # 'Max_Sigma': first_freq
        }

        # update the freq_index so it references  the frequencies with the max loads
        for freq in freq_keys:
            current_freq_loadcase = getLoadMagnitude(element, freq)

            # Now i will update my frequency index based on the max loads.

            # Max P
            max_freq = freq_index['P']
            current_max_p_loadcase = getLoadMagnitude(element, max_freq)
            P_max_freq = current_max_p_loadcase[0]
            P_current_loadcase = current_freq_loadcase[0]
            if P_current_loadcase > P_max_freq:
                freq_index['P'] = freq

            # Max V1
            max_freq = freq_index['V1']
            current_max_v1_loadcase = getLoadMagnitude(element, max_freq)
            V1_max_freq = current_max_v1_loadcase[1]
            V1_current_loadcase = current_freq_loadcase[1]
            if V1_current_loadcase > V1_max_freq:
                freq_index['V1'] = freq

            # Max V2
            max_freq = freq_index['V2']
            current_max_v2_loadcase = getLoadMagnitude(element, max_freq)
            V2_max_freq = current_max_v2_loadcase[2]
            V2_current_loadcase = current_freq_loadcase[2]
            if V2_current_loadcase > V2_max_freq:
                freq_index['V2'] = freq

            # Max T
            max_freq = freq_index['T']
            current_max_T_loadcase = getLoadMagnitude(element, max_freq)
            T_max_freq = current_max_T_loadcase[3]
            T_current_loadcase = current_freq_loadcase[3]
            if T_current_loadcase > T_max_freq:
                freq_index['T'] = freq

            # Max M2A
            max_freq = freq_index['M2A']
            current_max_M2A_loadcase = getLoadMagnitude(element, max_freq)
            M2A_max_freq = current_max_M2A_loadcase[4]
            M2A_current_loadcase = current_freq_loadcase[4]
            if M2A_current_loadcase > M2A_max_freq:
                freq_index['M2A'] = freq

            # Max M1A
            max_freq = freq_index['M1A']
            current_max_M1A_loadcase = getLoadMagnitude(element, max_freq)
            M1A_max_freq = current_max_M1A_loadcase[5]
            M1A_current_loadcase = current_freq_loadcase[5]
            if M1A_current_loadcase > M1A_max_freq:
                freq_index['M1A'] = freq

            # Max M2B
            max_freq = freq_index['M2B']
            current_max_M2B_loadcase = getLoadMagnitude(element, max_freq)
            M2B_max_freq = current_max_M2B_loadcase[6]
            M2B_current_loadcase = current_freq_loadcase[6]
            if M2B_current_loadcase > M2B_max_freq:
                freq_index['M2B'] = freq

            # Max M1B
            max_freq = freq_index['M1B']
            current_max_M1B_loadcase = getLoadMagnitude(element, max_freq)
            M1B_max_freq = current_max_M1B_loadcase[7]
            M1B_current_loadcase = current_freq_loadcase[7]
            if M1B_current_loadcase > M1B_max_freq:
                freq_index['M1B'] = freq

            # VRSS
            max_freq = freq_index['VRSS']
            current_max_VRSS_loadcase = getLoadMagnitude(element, max_freq)
            V1_max_freq = current_max_VRSS_loadcase[1]
            V2_max_freq = current_max_VRSS_loadcase[2]
            VRSS_max_freq = (V1_max_freq ** 2 + V2_max_freq ** 2) ** 0.5

            V1_current_loadcase = current_freq_loadcase[1]
            V2_current_loadcase = current_freq_loadcase[2]
            VRSS_current_loadcase = (V1_current_loadcase ** 2 + V2_current_loadcase ** 2) ** 0.5
            if VRSS_current_loadcase > VRSS_max_freq:
                freq_index['VRSS'] = freq

            # MRSS
            max_freq = freq_index['MRSS']
            current_max_MRSS_loadcase = getLoadMagnitude(element, max_freq)

            M2A_max_freq = current_max_MRSS_loadcase[4]
            M1A_max_freq = current_max_MRSS_loadcase[5]
            MRSSA_max_freq = (M2A_max_freq ** 2 + M1A_max_freq ** 2) ** 0.5

            M2B_max_freq = current_max_MRSS_loadcase[6]
            M1B_max_freq = current_max_MRSS_loadcase[7]
            MRSSB_max_freq = (M2B_max_freq ** 2 + M1B_max_freq ** 2) ** 0.5

            MRSS_max_freq = max(MRSSA_max_freq, MRSSB_max_freq)

            M2A_current_loadcase = current_freq_loadcase[4]
            M1A_current_loadcase = current_freq_loadcase[5]
            MRSSA_current_loadcase = (M2A_current_loadcase ** 2 + M1A_current_loadcase ** 2) ** 0.5

            M2B_current_loadcase = current_freq_loadcase[6]
            M1B_current_loadcase = current_freq_loadcase[7]
            MRSSB_current_loadcase = (M2B_current_loadcase ** 2 + M1B_current_loadcase ** 2) ** 0.5

            MRSS_current_loadcase = max(MRSSA_current_loadcase, MRSSB_current_loadcase)

            if MRSS_current_loadcase > MRSS_max_freq:
                freq_index['MRSS'] = freq

        element_critical_frequencies[element_id] = freq_index

    return element_critical_frequencies


# 6 - Option 1) Write critical frequencies to a csv file (Magnitude of Force)
def writeCriticalFrequenciesMagnitude(element_critical_frequencies: object, element_loads: object):
    """
      takes in a dictionary or element critical frequencies and the element loads at different
    frequencies and writes them to a CSV file

    param_1: element_critical_frequencies
    param_2: element_loads dictionary of element loads that correspond to each frequency {freq: [load case A side], [load case B side] }
    returns: None (Writes element loads to a csv file) it will also pickle all of the element loads and store them in a dictionary
    to use later if i wanted them.  The format will be

    {element_id: [ [load_case_ids: str] ,
    """

    cwd = os.getcwd()
    target_dir = cwd + '/Element_Loads'
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    element_summary: ElementSummary = {}

    for element_id in element_critical_frequencies:
        element_freq = element_critical_frequencies[element_id]

        # storing the important information in arrays to use later
        load_case_ids = []
        loads = []
        freqs = []

        file_name = f"./Element_Loads/{element_id}.txt"

        with open(file_name, 'w') as outfile:
            line = f"P\tV1\tV2\tT\tM2A\tM1A\tM2B\tM1B\t\n"
            outfile.write(line)

            for load_case_id in element_freq:
                freq = element_freq[load_case_id]
                element_freq_loads = element_loads[element_id]
                mag_of_loads = getLoadMagnitude(element_freq_loads, freq)

                freqs.append(freq)
                load_case_ids.append(load_case_id)
                loads.append(mag_of_loads)

                [P, V1, V2, T, M2A, M1A, M2B, M1B] = mag_of_loads

                line = f"{P:.2f}\t{V1:.2f}\t{V2:.2f}\t{T:.2f}\t{M2A:.2f}\t{M1A:.2f}\t{M2B:.2f}\t{M1B:.2f}\t{freq:.2f}Hz\n"
                outfile.write(line)

        element_summary[element_id] = {'load_case_ids': load_case_ids, 'loads': loads, 'freq': freqs}

    file_name = "./Element_Loads/element_data.pkl"
    with open(file_name, 'wb') as outfile:
        pickle.dump(element_summary, outfile)


# 6 - Option 2) Write critical frequencies to a csv file  (Maintains Direction Dependence)
def writeCriticalFrequenciesWithPhase(element_critical_frequencies: object, element_loads: object):
    """
    takes in a dictionary or element critical frequencies and the element loads at different
    frequencies and writes them to a CSV file

    param_1: element_critical_frequencies
    param_2: element_loads dictionary of element loads that correspond to each frequency {freq: [load case A side], [load case B side] }
    returns: None (Writes element loads to a csv file)
    """

    cwd = os.getcwd()
    target_dir = cwd + '/Element_Loads'
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    element_summary: ElementSummary = {}

    for element_id in element_critical_frequencies:
        element_freq = element_critical_frequencies[element_id]

        # storing the important information in arrays to use later
        load_case_ids = []
        loads = []
        freqs = []

        file_name = f"./Element_Loads/{element_id}.txt"

        with open(file_name, 'w') as outfile:
            line = f"P\tV1\tV2\tT\tM2A\tM1A\tM2B\tM1B\t\n"
            outfile.write(line)

            for load_case_id in element_freq:
                freq = element_freq[load_case_id]
                element_freq_loads = element_loads[element_id]
                complex_load_vector = getLoadComplex(element_freq_loads, freq)

                # need to find the max phase angle for specified loadcase

                max_phase_angle = calculateMaxPhaseAngle(complex_load_vector, load_case_id)
                max_phase_angle_deg = max_phase_angle * 360 / (2 * np.pi)

                [P, V1, V2, T, M2A, M1A, M2B, M1B] = [getPhaseAdjustedLoad(load, max_phase_angle) for load in
                                                      complex_load_vector]

                line = f"{P:.2f}\t{V1:.2f}\t{V2:.2f}\t{T:.2f}\t{M2A:.2f}\t{M1A:.2f}\t{M2B:.2f}\t{M1B:.2f}\t{freq:.2f}Hz {max_phase_angle_deg:.2f} Phase Angle {load_case_id}\n"
                outfile.write(line)

            element_summary[element_id] = {'load_case_ids': load_case_ids, 'loads': loads, 'freq': freqs}

    file_name = "./Element_Loads/element_data.pkl"
    with open(file_name, 'wb') as outfile:
        pickle.dump(element_summary, outfile)


# 7)  Run your Vibe Processor!
def runVibeProcessor(bdf_file_name: str, op2_file_name: str, element_ids: set, info_pickled: bool = False, phase_data: bool = False):
    """
    takes in the bdf file name, op2 file name and a set of element ids and determines if
    param_1:
    """

    if not info_pickled:
        saveAndPickleImportantInfo(bdf_file_name, op2_file_name, element_ids)

    with open('model_properties.pkl', 'rb') as infile:
        model_properties = pickle.load(infile)

    with open('element_properties.pkl', 'rb') as infile:
        element_properties = pickle.load(infile)

    with open('element_loads.pkl', 'rb') as infile:
        element_loads = pickle.load(infile)

    element_critical_frequencies = determineCriticalFrequencies(element_loads, element_properties, model_properties)


    if not phase_data:
        writeCriticalFrequenciesMagnitude(element_critical_frequencies, element_loads)
    else:
        writeCriticalFrequenciesWithPhase(element_critical_frequencies, element_loads)


###--------------------------- HELPER FUNCTIONS ------------------------------------------ #

class IncorrectLoadCaseId(Exception):
    pass


def reformatLoadCase(load_case):
    """
    this function reformats the load case which is provided in the pyNastran format of
    [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
    to my format of [P, V1, V2, T, M2, M1].

    param_1: load_case which is a list of complex values that represent
        [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
    returns: load_case [P, V1, V2, T, M2, M1] (Complex Form)
    """
    M1 = load_case[1]
    M2 = load_case[2]
    V1 = load_case[3]
    V2 = load_case[4]
    P = load_case[5]
    T = load_case[6]

    LC = [P, V1, V2, T, M2, M1]

    return LC


def reformatLoadCaseMag(load_case):
    """
    this function reformats the load case which is provided in the pyNastran format of
    [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
    to my format of [P, V1, V2, T, M2, M1].  It also converts the load value from a complex value into the magnitude of
    the complex value

    param_1: load_case which is a list of complex values that represent
        [sd, bending_moment1, bending_moment2, shear1, shear2, axial_force, total_torque, warping_torque]
    returns: load_case [P, V1, V2, T, M2, M1] (Magnitude)
    """
    M1 = abs(load_case[1])
    M2 = abs(load_case[2])
    V1 = abs(load_case[3])
    V2 = abs(load_case[4])
    P = abs(load_case[5])
    T = abs(load_case[6])

    LC = [P, V1, V2, T, M2, M1]

    return LC


def findMaxSide(a_load_case_mag, b_load_case_mag):
    """
    this function take the magnitude of the a side load and the magnitude of the b side load and returns
    the max magnitude from either side.
    """
    # finding the max moment from either the A or B Side of the beam and putting that into 1 loadcase.
    M2_Max = max(a_load_case_mag[4], b_load_case_mag[4])
    M1_Max = max(a_load_case_mag[5], b_load_case_mag[5])
    load_case = a_load_case_mag
    load_case[4] = M2_Max
    load_case[5] = M1_Max
    return load_case


def getLoadMagnitude(element_freq_loads: object, freq: float):
    """
    takes in a dictionary of element loads by frequency and the frequency of the load we are looking at.
    It then takes the complex load array which holds the A and B side of the beam and returns the magnitude of the load
    at the A  and B side of the beam

    param_1: element_freq_loads  { freq_id: [ [ load case A side ], [load case B side] ]
    param_2: freq  the freq_id that we are looking at
    returns: [magnitude of loads A or B side]  magnitude of loads at either the A and B side of the beam
    """

    load_case = element_freq_loads.get(freq)
    a_side_load = load_case[0]
    b_side_load = load_case[1]

    a_side_load = reformatLoadCaseMag(a_side_load)  # [P, V1, V2, T, M2, M1 ]
    b_side_load = reformatLoadCaseMag(b_side_load)

    combined_load = a_side_load + b_side_load[4:6]

    return combined_load  # [P, V1, V2, T, M2A, M1A, M2B, M1B ]


def getLoadComplex(element_freq_loads: object, freq: float):
    """
    takes in a dictionary of element loads by frequency and the frequency of the load we are looking at.
    It then takes the complex load array which holds the A and B side of the beam and returns the complex force of the load
    at the A or B side of the beam (whichever has a greater MRSS)

    param_1: element_freq_loads  { freq_id: [ [ load case A side ], [load case B side] ]
    param_2: freq  the freq_id that we are looking at
    returns: [magnitude of loads A or B side]  complex loads at either the A and B side of the beam
    """

    load_case = element_freq_loads.get(freq)
    a_side_load = load_case[0]
    b_side_load = load_case[1]

    a_side_load = reformatLoadCase(a_side_load)  # [P, V1, V2, T, M2, M1 ]
    b_side_load = reformatLoadCase(b_side_load)

    combined_load = a_side_load + b_side_load[4:6]

    return combined_load  # [P, V1, V2, T, M2A, M1A, M2B, M1B ]


def calculateMaxPhaseAngle(complex_load_vector: list, load_case_id: LoadCaseId):
    """
    the complex load load vector is a list of complex numbers. Therefore each number
    has a magnitude and phase. This is information that is needed to maintain the directional dependence of the
    sine vibe load vector.  But the current phase may not be the max value for the load vector. For example, if we
    are trying to maximize the P load case we need to fine the phase angle below that will maximize P.

    P_Mag*cos(P_phase+phase_angle)

    Load Case IDs

     'P': first_freq,
     'V1': first_freq,
     'V2': first_freq,
     'T': first_freq,
     'M2': first_freq,
     'M1': first_freq,
     'VRSS': first_freq,
     'MRSS': first_freq,

    param_1: complex load vector [P, V1, V2, T, M2A, M1A, M2B, M1B]
    returns: phase_angle that maximizes the load specified by the load case
    """

    if load_case_id == 'P':
        load_id = 0
    elif load_case_id == 'V1':
        load_id = 1
    elif load_case_id == 'V2':
        load_id = 2
    elif load_case_id == 'T':
        load_id = 3
    elif load_case_id == 'M2A':
        load_id = 4
    elif load_case_id == 'M1A':
        load_id = 5
    elif load_case_id == 'M2B':
        load_id = 6
    elif load_case_id == 'M1B':
        load_id = 7
    elif load_case_id == 'VRSS':
        load_id = 8
    elif load_case_id == 'MRSS':
        load_id = 9
    else:
        raise IncorrectLoadCaseId

    if load_id < 8:
        theta_range = np.linspace(0, 1, 50) * np.pi * 2
        load_complex = complex_load_vector[load_id]
        mag = abs(load_complex)
        phase = np.angle(load_complex)
        max_p = 0
        max_phase = 0
        for theta in theta_range:
            adjusted_phase = phase + theta
            p = mag * math.cos(adjusted_phase)

            mag_p = np.linalg.norm(p)
            if mag_p > max_p:
                max_p = mag_p
                max_phase = theta

        return max_phase
    elif load_id == 8:
        theta_range = np.linspace(0, 1, 50) * np.pi * 2
        v1_load_complex = complex_load_vector[1]
        v2_load_complex = complex_load_vector[2]
        v1_mag = abs(v1_load_complex)
        v1_phase = np.angle(v1_load_complex)
        v2_mag = abs(v2_load_complex)
        v2_phase = np.angle(v2_load_complex)

        max_phase_angle = 0
        max_vrss = 0
        for theta in theta_range:
            v1_adjusted_phase = v1_phase + theta
            v2_adjusted_phase = v2_phase + theta
            v1 = v1_mag * math.cos(v1_adjusted_phase)
            v2 = v2_mag * math.cos(v2_adjusted_phase)
            v_vector = [v1, v2]
            vrss = np.linalg.norm(v_vector)
            if vrss > max_vrss:
                max_phase_angle = theta
                max_vrss = vrss
        return max_phase_angle
    elif load_id == 9:
        theta_range = np.linspace(0, 1, 50) * np.pi * 2
        # A side of beam
        m2a_load_complex = complex_load_vector[4]
        m1a_load_complex = complex_load_vector[5]
        m2a_mag = abs(m2a_load_complex)
        m2a_phase = np.angle(m2a_load_complex)
        m1a_mag = abs(m1a_load_complex)
        m1a_phase = np.angle(m1a_load_complex)

        # B side of beam
        m2b_load_complex = complex_load_vector[6]
        m1b_load_complex = complex_load_vector[7]
        m2b_mag = abs(m2b_load_complex)
        m2b_phase = np.angle(m2b_load_complex)
        m1b_mag = abs(m1b_load_complex)
        m1b_phase = np.angle(m1b_load_complex)

        max_phase_angle = 0
        max_mrss = 0
        for theta in theta_range:
            m2a_adjusted_phase = m2a_phase + theta
            m1a_adjusted_phase = m1a_phase + theta
            m2a = m2a_mag * math.cos(m2a_adjusted_phase)
            m1a = m1a_mag * math.cos(m1a_adjusted_phase)
            ma_vector = [m1a, m2a]
            mrssa = np.linalg.norm(ma_vector)

            m2b_adjusted_phase = m2b_phase + theta
            m1b_adjusted_phase = m1b_phase + theta
            m2b = m2b_mag * math.cos(m2b_adjusted_phase)
            m1b = m1b_mag * math.cos(m1b_adjusted_phase)
            mb_vector = [m1b, m2b]
            mrssb = np.linalg.norm(mb_vector)

            mrss = max(mrssa, mrssb)

            if mrss > max_mrss:
                max_phase_angle = theta
                max_mrss = mrss
        return max_phase_angle


def getPhaseAdjustedLoad(complex_load, phase_angle):
    complex_load_abs = abs(complex_load)
    complex_angle = np.angle(complex_load)
    adjusted_angle = complex_angle + phase_angle
    new_load = complex_load_abs * math.cos(adjusted_angle)
    return new_load


if __name__ == "__main__":
    # model input information
    cwd = os.getcwd()
    bdf_file_name = './Example/04_sine_vibe_models/sine_Z.bdf'
    op2_file_name = './Example/04_sine_vibe_models/sine_Z.op2'
    element_ids = {31376,31378,31419,31422,78069,78117,78126,78137}

    runVibeProcessor(bdf_file_name,op2_file_name,element_ids,False,True)
