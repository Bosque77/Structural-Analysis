from pyNastran.op2.op2 import OP2
from pyNastran.bdf.bdf import BDF
from typing import List
import numpy as np
import os
import pandas as pd
import main as mp
import math
from nasDataTypes import Property, Material, Element
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import openpyxl

def addBeamLoads(op2, elements: List[Element], maintain_directional_dependance=None):
    op2_file_location = op2.op2_filename
    split_string = str.split(op2_file_location, '/')
    op2_name = split_string[-1]
    cbeam_force = op2.cbeam_force # Extracting beam loads from output file



    # Looping through the List[dict] of the beam_forces for the output file.
    for case_id in cbeam_force:
        beam_data_current_case = cbeam_force.get(case_id)

        beam_force_type = beam_data_current_case.class_name

        if beam_force_type == "ComplexCBeamForceArray":  # Adding Frequency Dependent Loads
            freqs = beam_data_current_case.freqs

            for i in range(len(freqs)):
                freq = freqs[i]
                current_beam_loads_data = beam_data_current_case.data[i]
                current_beam_loads_element = beam_data_current_case.element
                for index, eid in enumerate(current_beam_loads_element, 0):
                    element = getElementByID(elements, eid)
                    if element:
                        load_vector = current_beam_loads_data[index]
                        element.addBeamLoads(op2_name, case_id, load_vector,freq,maintain_directional_dependance)


        else: # Adding Non-Frequency Dependent Loads
            current_beam_loads_data = beam_data_current_case.data[0]
            current_beam_loads_eid = beam_data_current_case.element


            for index, eid in enumerate(current_beam_loads_eid, 0):  # Code may break if the eid is not in the elements list that is created from the bdf file
                element = getElementByID(elements, eid)
                if element:
                    load_vector = current_beam_loads_data[index]
                    element.addBeamLoads(op2_name, case_id, load_vector)


    return elements

def extractModelElements(bdf_file_name,eids_to_analyze):  # Returns list of model elements
    print("inside extractModelElements")
    # Reading bdf file
    model = BDF()
    model.read_bdf(bdf_file_name, xref=True)
    model_element_ids = model.element_ids
    model_elements = model.elements

    # Creating a list of Material Objects
    # materials = []
    # for material in model.materials:
    #     material_object = Material()
    #     mat = model.materials.get(material)
    #     material_object.name = mat.comment
    #     material_object.mid = mat.mid
    #     material_object.E = mat.e
    #     material_object.v = mat.nu
    #     material_object.G = mat.g
    #     material_object.rho = mat.rho
    #     material_object.tref = mat.tref
    #     materials.append(material_object)
    #     print(material_object.name)

    # Creating a list of Property Objects
    properties = []
    for property in model.properties:
        property_object = Property()
        prop = model.properties.get(property)
        if prop.type == 'PBEAM':  # Only storing the beam properties
            prop_info_string = prop.comment
            start = ":"
            end = "\n"
            prop_name=prop_info_string.split(start)[1].split(end)[0]
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

            property_object.C1 = abs(property_object.C[1])
            property_object.C2 = abs(property_object.D[0])
            # Need to add the shear area ratio
            properties.append(property_object)


    # Extracting elements from bdf file
    elements = []
    for element_id in model_element_ids:
        if not eids_to_analyze:  # Adds all of the elements from the bdf file if eids_to_analyze is empty
            element = model_elements.get(element_id)
            element_object = Element()
            element_object.eid = element.eid
            element_object.property = getPropertyByID(properties,element.pid)
            if element_object.property:
                # mid = element_object.property.mid
                # element_object.material = getMaterialByID(materials,mid)
                elements.append(element_object)
        else:
            if element_id in eids_to_analyze: # Only adds the element ids that are in eids_to_analyze
                element = model_elements.get(element_id)
                element_object = Element()
                element_object.eid = element.eid
                element_object.property = getPropertyByID(properties, element.pid)
                if element_object.property:
                    # mid = element_object.property.mid
                    # element_object.material = getMaterialByID(materials, mid)
                    elements.append(element_object)
    return elements  # Returns list of model

def extractElementProperties(elements):
    properties = []
    for element in elements:
        element_property = element.property
        if element_property not in properties:
            properties.append(element_property)
    return properties

def extractModelProperties(bdf_file_name):
    model = BDF()
    model.read_bdf(bdf_file_name, xref=True)

    # Creating a list of Property Objects
    properties = []
    for property in model.properties:
        property_object = Property()
        prop = model.properties.get(property)
        if prop.type == 'PBEAM':  # Only storing the beam properties
            prop_info_string = prop.comment
            start = ":"
            end = "\n"
            prop_name=prop_info_string.split(start)[1].split(end)[0]
            property_object.name = prop_name
            property_object.mid = prop.mid
            property_object.pid = prop.pid
            property_object.A = prop.A[0]
            property_object.I1 = prop.i1[0]
            property_object.I2 = prop.i2[0]
            property_object.J = prop.j[0]
            property_object.C = [prop.c1[0], prop.c2[0]]  # Stress recovery point 1
            property_object.D = [prop.d1[0], prop.d2[0]]  # Stress recovery point 2
            property_object.E = [prop.e1[0], prop.e2[0]]  # Stress recovery point 3
            property_object.F = [prop.f1[0], prop.f2[0]]  # Stress recovery point 4

            property_object.C1 = abs(property_object.C[1])
            property_object.C2 = abs(property_object.D[0])
            # Need to add the shear area ratio
            properties.append(property_object)

    return properties

def getPropertyByID(properties: List[Property], pid:int):
    for property in properties:
        if property.pid==pid:
            return property
    return None

def getMaterialByID(materials: List[Material], mid:int):
    for material in materials:
        if material.mid==mid:
            return material

def getElementByID(elements: List[Element], eid:int):
    for element in elements:
        if element.eid == eid:
            return element

def loadConfigurationFile(App, file_name):
    print("Inside fileLoader-->loadConfigurationFile")
    # Import bdf file from the configuration file
    bdf_df = pd.read_excel(file_name, "Config", engine = 'openpyxl')

    local_path = file_name.rsplit('/', 1)[0]
    bdf_names = bdf_df['BDF']
    bdf_file_locations = bdf_df['BDF File Location']
    working_directory = bdf_df['Working Directory']

    # Importing the op2 file locations
    op2_file_names = bdf_df['OP2']
    op2_file_locations = bdf_df['OP2 File Location']
    op2_file_location_boolean = pd.isnull(op2_file_locations)

    # Importing the element ids that will be processed
    starting_element_ids = bdf_df["Element ID Start"].dropna()
    stopping_element_ids = bdf_df["Element ID Stop"].dropna()

    # ISSUE HERE IS THERE ARE NAN ENTRIES IN MY STARTING AND STOPPING ELEMENT ID CONFIG FILE



    list_element_ids=[]
    for index in range(len(starting_element_ids)):
        starting_element_id = int(starting_element_ids[index])
        stopping_element_id = int(stopping_element_ids[index])

        element_ids = list(range(starting_element_id, stopping_element_id))
        list_element_ids.append(element_ids)



        # if stopping_element_id != starting_element_id:
        #     stopping_element_id = stopping_element_ids[index]
        #     element_ids = list(range(starting_element_id,stopping_element_id))
        #     list_element_ids.append(element_ids)
        # else:
        #     element_ids.append(starting_element_id)

    analyzed_element_ids = []
    for element_list in list_element_ids:
        for element in element_list:
            if element not in analyzed_element_ids:
                analyzed_element_ids.append(element)



    bdf_name = bdf_names[0]
    bdf_file_path = bdf_file_locations[0]
    working_directory = working_directory[0]

    # Adding the bdf file to the App
    bdf_split_file_path = str.split(bdf_file_path, '/')
    bdf_file_name = bdf_split_file_path[-1]

    # deciding the file path for the bdf file (relative or absolute)
    if bdf_split_file_path[0] == ".":
        relative_file_path = bdf_file_path.rsplit('./', 1)[1]
        bdf_file_path = local_path + "/" + relative_file_path




    App.starting_element_ids = starting_element_ids
    App.ending_element_ids = stopping_element_ids
    App.analyzed_element_ids = analyzed_element_ids
    App.bdf_file_path = bdf_file_path
    App.bdf_file_name = bdf_file_name
    App.working_directory = working_directory
    App.bdf_label.setText(bdf_file_name)

    try:
        loaded_f06_model = QStandardItemModel()
        for index,op2_file_location in enumerate(op2_file_locations):
            op2_is_null = op2_file_location_boolean[index]
            if not op2_is_null:
                split_file_path = str.split(op2_file_location, '/')
                op2_model_name = split_file_path[-1]
                new_item = QStandardItem(op2_model_name)

                # deciding the file path for the op2 files (relative or absolute)
                if split_file_path[0] == ".":
                    relative_file_path = op2_file_location.rsplit('./', 1)[1]
                    file_path = local_path+"/"+relative_file_path
                else:
                    file_path = op2_file_location
                op2 = OP2()
                op2.read_op2(file_path)
                new_item.setCheckable(True)
                new_item.setCheckState(Qt.Unchecked)
                loaded_f06_model.appendRow(new_item)
                App.op2_models.append(op2)
    except FileNotFoundError as e:
        error_message = "OP2 File not Found. \n"
        error_message = error_message + "Error:\n" + str(e)
        msg = QMessageBox()
        msg.setText(error_message)
        msg.setText(error_message)
        msg.exec_()
        return
    except TypeError as e:
        error_message = "OP2 File not Found. \n"
        error_message = error_message + "Error:\n" + str(e)
        msg = QMessageBox()
        msg.setText(error_message)
        msg.exec_()
        return


    App.loaded_f06_list.setModel(loaded_f06_model)
    App.loaded_f06_list.checked.connect(App.onChecked)

    # Import Loadcases from the configuration file
    df = pd.read_excel(file_name,"Load_Cases", engine = 'openpyxl')
    load_case_ids = df['Case ID']
    types = df['Type']
    incs = df['Inc']
    coefs = df['coef']
    factors = df['factor']
    load_files = df['Load File']
    frequencies = df['Frequency']

    for index,freq in enumerate(frequencies):
        if np.isnan(freq):
            frequencies[index] = 'NA'

    op2_subcases = df['OP2 Subcase']

    unique_load_case_ids = []
    df2 = pd.isnull(load_case_ids)

    for index, case_id in enumerate(load_case_ids):
        if case_id == 'End':
            end_of_loads_index = index+1
    print(end_of_loads_index)

    clock_loads = []
    linear_combination_loads = []
    current_load_case_id = load_case_ids[0]
    grouped_load_cases = []

    # Grouping the loadcases from the configuratin file.  CODE WILL BREAK IF I HAVE MORE THAN 1 CLOCKED GROUP. NEED TO FIX THIS.
    for index in range(1,end_of_loads_index):
        if not df2[index]:
            load_case = {"id":current_load_case_id,"linear_combination_load_sets":linear_combination_loads,"clocked_load_sets":clock_loads}
            grouped_load_cases.append(load_case)
            load_case = []
            clock_loads = []
            linear_combination_loads = []
            current_load_case_id = load_case_ids[index]
        else:
            current_type = types[index]
            if current_type == "Clock":
                current_inc = incs[index]
                current_coef = coefs[index]
                current_factor = factors[index]
                op2_file_location = load_files[index]
                split_file_path = str.split(op2_file_location, '/')
                op2_model_name = split_file_path[-1]
                current_frequency = frequencies[index]
                current_case_id = int(op2_subcases[index])

                load_set =  {"op2_model_name":op2_model_name, "case_id": current_case_id, "scale_factor":current_factor,"inc":current_inc, "coef":current_coef,"frequency":current_frequency}
                clock_loads.append(load_set)
            elif current_type =="Linear Combination":
                print("Linear combination")
                current_inc = incs[index]
                current_coef = coefs[index]
                scale_factor = factors[index]
                op2_file_location = load_files[index]
                split_file_path = str.split(op2_file_location, '/')
                op2_model_name = split_file_path[-1]
                case_id = int(op2_subcases[index])

                load_set =  {"op2_model_name":op2_model_name,"case_id":case_id,"scale_factor":scale_factor}
                linear_combination_loads.append(load_set)
            else:
               raise Exception("The load case type is not recognized. It must be a Clocked load or a Linear Combination")


    # Convert the organized data above into the loadcase classes from main.py so I am working with the same data types. Kinda sloppy code should organize this better
    # I also have two classes named the same in two different modules and should probably re-organize the class name Loadcase
    load_cases = mp.LoadCases()
    load_case = mp.LoadCase()

    for current_load_case in grouped_load_cases:
        load_case.setName(current_load_case["id"])
        load_case.linear_combination_load_sets = current_load_case['linear_combination_load_sets']
        load_case.clocked_load_sets = current_load_case['clocked_load_sets']  # FOREST THIS IS WHERE YOU CAN SPLIT UP THE CLOCKED LOADS IF YOU WANT TO INCORPORATE THAT FUNCTIONALITY.
        load_cases.addLoadCase(load_case)
        load_case = mp.LoadCase()

        q_std_item = QStandardItem(current_load_case["id"])
        App.load_cases_list_model.appendRow(q_std_item)


    App.load_cases_object = load_cases

def printLoadsByElements(elements, file_path):
    print(file_path)
    try:
        if not os.path.isdir(file_path):
            os.makedirs(file_path)

        for element in elements:
            file_name = file_path + "/" + str(element.eid) + ".xlsx"
            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

            load_case_data_frame = {'P': [],
                                    'V1': [],
                                    'V2': [],
                                    'T': [],
                                    'M2A': [],
                                    'M1A': [],
                                    'M2B': [],
                                    'M1B': [],
                                    'Load Case ID': [],
                                    'Description': []
                                    }

            for count,data in enumerate(element.sorted_loads):

                load_vector = data['load_vector']
                load_case_id = data['loadcase_id']

                load_case_data_frame['P'].append(load_vector[0])
                load_case_data_frame['V1'].append(load_vector[1])
                load_case_data_frame['V2'].append(load_vector[2])
                load_case_data_frame['T'].append(load_vector[3])
                load_case_data_frame['M2A'].append(load_vector[4])
                load_case_data_frame['M1A'].append(load_vector[5])
                load_case_data_frame['M2B'].append(load_vector[6])
                load_case_data_frame['M1B'].append(load_vector[7])
                load_case_data_frame['Load Case ID'].append(load_case_id)

                if count == 0 :
                    load_case_data_frame['Description'].append("Max P")
                elif count ==1:
                    load_case_data_frame['Description'].append("Max V1")
                elif count==2:
                    load_case_data_frame['Description'].append("Max V2")
                elif count ==3:
                    load_case_data_frame['Description'].append("Max T")
                elif count==4:
                    load_case_data_frame['Description'].append("Max M2A")
                elif count==5:
                    load_case_data_frame['Description'].append("Max M1A")
                elif count==6:
                    load_case_data_frame['Description'].append("Max M2B")
                elif count==7:
                    load_case_data_frame['Description'].append("Max M1B")
                elif count>=8:
                    load_case_data_frame['Description'].append("Max Stress")

            lc_df = pd.DataFrame(load_case_data_frame)
            lc_df.to_excel(writer, "Load_Cases", index=False)
            writer.save()
    except:
        error_message = "Error Saving the Configuration File. \n"
        error_message = error_message + "Error:\n" + str(e)
        msg = QMessageBox()
        msg.setText(error_message)
        msg.setText(error_message)
        msg.exec_()
        return



    print("Finished printing element loads")

def printLoadsByProperty(property_loads, file_path):
    print(file_path)
    if not os.path.isdir(file_path):
        os.makedirs(file_path)


    for data in property_loads:

        file_name = file_path+"/" + str(data["Property"]) + ".xlsx"
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        load_case_data_frame = {'P': [],
                                'V1': [],
                                'V2': [],
                                'T': [],
                                'M2A': [],
                                'M1A': [],
                                'M2B': [],
                                'M1B': [],
                                'Load Case ID': [],
                                'description':[]
                                }



        load_data = data["Load Data"]
        load_vector = load_data["max_p_load"]
        load_case_id = load_data["max_p_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max P')


        load_vector = load_data["max_v1_load"]
        load_case_id = load_data["max_v1_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max V1')

        load_vector = load_data["max_v2_load"]
        load_case_id = load_data["max_v2_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max V2')


        load_vector = load_data["max_t_load"]
        load_case_id = load_data["max_t_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max T')

        load_vector = load_data["max_m2a_load"]
        load_case_id = load_data["max_m2a_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max M2A')

        load_vector = load_data["max_m1a_load"]
        load_case_id = load_data["max_m1a_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max M1A')

        load_vector = load_data["max_m2b_load"]
        load_case_id = load_data["max_m2b_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max M2B')

        load_vector = load_data["max_m1b_load"]
        load_case_id = load_data["max_m1b_load_id"]

        load_case_data_frame['P'].append(load_vector[0])
        load_case_data_frame['V1'].append(load_vector[1])
        load_case_data_frame['V2'].append(load_vector[2])
        load_case_data_frame['T'].append(load_vector[3])
        load_case_data_frame['M2A'].append(load_vector[4])
        load_case_data_frame['M1A'].append(load_vector[5])
        load_case_data_frame['M2B'].append(load_vector[6])
        load_case_data_frame['M1B'].append(load_vector[7])
        load_case_data_frame['Load Case ID'].append(load_case_id)
        load_case_data_frame['description'].append('Max M1B')

        sigma_loads = load_data["max_sigma_loads"]
        sigma_vector = load_data["max_sigma_vector"]
        sigma_loads_id = load_data["max_sigma_loads_id"]
        for index,load_vector in enumerate(sigma_loads):
            load_case_id = sigma_loads_id[index]

            load_case_data_frame['P'].append(load_vector[0])
            load_case_data_frame['V1'].append(load_vector[1])
            load_case_data_frame['V2'].append(load_vector[2])
            load_case_data_frame['T'].append(load_vector[3])
            load_case_data_frame['M2A'].append(load_vector[4])
            load_case_data_frame['M1A'].append(load_vector[5])
            load_case_data_frame['M2B'].append(load_vector[6])
            load_case_data_frame['M1B'].append(load_vector[7])
            load_case_data_frame['Load Case ID'].append(load_case_id)
            load_case_data_frame['description'].append('Max Sigma')

        tau_loads = load_data["max_tau_loads"]
        tau_vector = load_data["max_tau_vector"]
        tau_loads_id = load_data["max_tau_loads_id"]
        for index,load_vector in enumerate(tau_loads):
            load_case_id = tau_loads_id[index]

            load_case_data_frame['P'].append(load_vector[0])
            load_case_data_frame['V1'].append(load_vector[1])
            load_case_data_frame['V2'].append(load_vector[2])
            load_case_data_frame['T'].append(load_vector[3])
            load_case_data_frame['M2A'].append(load_vector[4])
            load_case_data_frame['M1A'].append(load_vector[5])
            load_case_data_frame['M2B'].append(load_vector[6])
            load_case_data_frame['M1B'].append(load_vector[7])
            load_case_data_frame['Load Case ID'].append(load_case_id)
            load_case_data_frame['description'].append('Max Tau')

        lc_df = pd.DataFrame(load_case_data_frame)
        lc_df.to_excel(writer, "Load_Cases", index=False)
        writer.save()

    print("Finished printing property loads")

def saveConfigurationFile(load_case_data_frame, config_data_frame, file_name):
    try:
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        lc_df = pd.DataFrame(load_case_data_frame)
        config_df = pd.DataFrame(config_data_frame)
        lc_df.to_excel(writer,"Load_Cases", index=False)
        config_df.to_excel(writer, "Config", index=False)
        writer.save()
        print("Saved Configuration File")
    except:
        error_message = "Error Saving the Configuration File. \n"
        error_message = error_message + "Error:\n" + str(e)
        msg = QMessageBox()
        msg.setText(error_message)
        msg.setText(error_message)
        msg.exec_()
        return

def sortLoadsByElements(elements, number_of_stress_vectors):
    print("inside sort loads by elements")
    for element in elements:
        max_sigma_loads = []
        max_sigma_vector = []
        max_sigma_loads_id = []

        max_tau_loads = []
        max_tau_vector = []
        max_tau_loads_id = []

        max_p_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_p_load_id = None
        max_v1_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_v1_load_id = None
        max_v2_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_v2_load_id = None
        max_t_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_t_load_id = None
        max_m2a_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_m2a_load_id = None
        max_m1a_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_m1a_load_id = None
        max_m2b_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_m2b_load_id = None
        max_m1b_load = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        max_m1b_load_id = None

        load_cases = element.load_case_data
        for load_case in load_cases:

            load_case_id = load_case.unique_id
            P = load_case.P
            V1 = load_case.V1
            V2 = load_case.V2

            VRSS = np.sqrt(V1**2+V2**2)
            T = load_case.T
            M2A = load_case.M2A
            M1A = load_case.M1A
            M2B = load_case.M2B
            M1B = load_case.M1B

            property = element.property
            A = property.A
            I1 = property.I1
            I2 = property.I2
            J = property.J
            C1 = property.C1
            C2 = property.C2

            sigma_A = abs(P)/A+abs(M1A)*C1/I1+abs(M2A)*C2/I2
            sigma_B = abs(P) / A + abs(M1B) * C1 / I1 + abs(M2B) * C2 / I2

            sigma = max(sigma_A, sigma_B)
            tau = VRSS/A+abs(T)*C1/J

            load_vector = [P, V1, V2, T, M2A, M1A, M2B, M1B]

            if abs(P) > abs(max_p_load[0]):
                max_p_load = load_vector
                max_p_load_id = load_case_id

            if abs(V1) > abs(max_v1_load[1]):
                max_v1_load = load_vector
                max_v1_load_id = load_case_id

            if abs(V2) > abs(max_v2_load[2]):
                max_v2_load = load_vector
                max_v2_load_id = load_case_id

            if abs(T) > abs(max_t_load[3]):
                max_t_load = load_vector
                max_t_load_id = load_case_id

            if abs(M2A) > abs(max_m2a_load[4]):
                max_m2a_load = load_vector
                max_m2a_load_id = load_case_id

            if abs(M1A) > abs(max_m1a_load[5]):
                max_m1a_load = load_vector
                max_m1a_load_id = load_case_id

            if abs(M2B) > abs(max_m2b_load[6]):
                max_m2b_load = load_vector
                max_m2b_load_id = load_case_id

            if abs(M1B) > abs(max_m1b_load[7]):
                max_m1b_load = load_vector
                max_m1b_load_id = load_case_id


            # Adding the loads to the max sigma vector of loads
            end_of_list = len(max_sigma_vector) - 1
            if not max_sigma_vector:
                max_sigma_loads.append(load_vector)
                max_sigma_vector.append(sigma)
                max_sigma_loads_id.append(load_case_id)
            else:
                for i in range(len(max_sigma_vector)):
                    value = max_sigma_vector[i]
                    if sigma > value:
                        max_sigma_vector.insert(i,sigma)
                        max_sigma_loads.insert(i,load_vector)
                        max_sigma_loads_id.insert(i,load_case_id)
                        break
                    elif i==end_of_list and len(max_sigma_vector)<6:
                        max_sigma_vector.append(sigma)
                        max_sigma_loads.append(load_vector)
                        max_sigma_loads_id.append(load_case_id)

            if len(max_sigma_vector) > number_of_stress_vectors:
                max_sigma_vector=max_sigma_vector[0:number_of_stress_vectors]
                max_sigma_loads = max_sigma_loads[0:number_of_stress_vectors]
                max_sigma_loads_id = max_sigma_loads_id[0:number_of_stress_vectors]

            # Adding the loads to the max shear vector of loads
            end_of_list = len(max_tau_vector) - 1
            if not max_tau_vector:
                max_tau_loads.append(load_vector)
                max_tau_vector.append(tau)
                max_tau_loads_id.append(load_case_id)
            else:
                for i in range(len(max_tau_vector)):
                    value = max_tau_vector[i]
                    if tau > value:
                        max_tau_vector.insert(i,tau)
                        max_tau_loads.insert(i,load_vector)
                        max_tau_loads_id.insert(i,load_case_id)
                        break
                    elif i==end_of_list and len(max_tau_vector)<6:
                        max_tau_vector.append(tau)
                        max_tau_loads.append(load_vector)
                        max_tau_loads_id.append(load_case_id)


            if len(max_tau_vector) > number_of_stress_vectors:
                max_tau_vector=max_tau_vector[0:number_of_stress_vectors]
                max_tau_loads = max_tau_loads[0:number_of_stress_vectors]
                max_tau_loads_id = max_tau_loads_id[0:number_of_stress_vectors]


        load_case_p_block = {'loadcase_id':max_p_load_id,'load_vector':max_p_load}
        element.sorted_loads.append(load_case_p_block)
        load_case_v1_block = {'loadcase_id': max_v1_load_id, 'load_vector': max_v1_load}
        element.sorted_loads.append(load_case_v1_block)
        load_case_v2_block = {'loadcase_id': max_v2_load_id, 'load_vector': max_v2_load}
        element.sorted_loads.append(load_case_v2_block)
        load_case_t_block = {'loadcase_id': max_t_load_id, 'load_vector': max_t_load}
        element.sorted_loads.append(load_case_t_block)
        load_case_m2a_block = {'loadcase_id': max_m2a_load_id, 'load_vector': max_m2a_load}
        element.sorted_loads.append(load_case_m2a_block)
        load_case_m1a_block = {'loadcase_id': max_m1a_load_id, 'load_vector': max_m1a_load}
        element.sorted_loads.append(load_case_m1a_block)
        load_case_m2b_block = {'loadcase_id': max_m2b_load_id, 'load_vector': max_m2b_load}
        element.sorted_loads.append(load_case_m2b_block)
        load_case_m1b_block = {'loadcase_id': max_m1b_load_id, 'load_vector': max_m1b_load}
        element.sorted_loads.append(load_case_m1b_block)

        for index,load in enumerate(max_sigma_loads):
            load_vector = load
            load_case_id = max_sigma_loads_id[index]
            data_block = {'loadcase_id': load_case_id,'load_vector':load_vector,'max_stress':max_sigma_vector[index]}
            element.sorted_loads.append(data_block)

        for index,load in enumerate(max_tau_loads):
            load_vector = load
            load_case_id = max_tau_loads_id[index]
            data_block = {'loadcase_id': load_case_id,'load_vector':load_vector,'max_stress':max_tau_vector[index]}
            element.sorted_loads.append(data_block)

    print("finished sorting element loads")

    return elements

def sortLoadsByProperty(elements, properties, number_of_stress_vectors):
    print("inside sort loads by property")

    property_loads = []

    for property in properties:
        max_sigma_loads = []
        max_sigma_vector = []
        max_sigma_loads_id = []

        max_tau_loads = []
        max_tau_vector = []
        max_tau_loads_id = []

        max_p_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_p_load_id = None
        max_v1_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_v1_load_id = None
        max_v2_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_v2_load_id = None
        max_t_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_t_load_id = None
        max_m2a_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_m2a_load_id = None
        max_m1a_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_m1a_load_id = None
        max_m2b_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_m2b_load_id = None
        max_m1b_load = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        max_m1b_load_id = None

        load_data = {"max_sigma_loads":max_sigma_loads,"max_sigma_vector":max_sigma_vector,"max_sigma_loads_id":max_sigma_loads_id,
                              "max_tau_loads":max_tau_loads,"max_tau_vector":max_tau_vector,"max_tau_loads_id":max_tau_loads_id,"max_p_load":max_p_load,"max_p_load_id":max_p_load_id,
                              "max_v1_load":max_v1_load,"max_v1_load_id":max_v1_load_id,"max_v2_load":max_v2_load,"max_v2_load_id":max_v2_load_id,"max_t_load":max_t_load,
                              "max_t_load_id":max_t_load_id,"max_m2a_load":max_m2a_load,"max_m2a_load_id":max_m2a_load_id,"max_m1a_load":max_m1a_load,"max_m1a_load_id":max_m1a_load_id,
                              "max_m2b_load":max_m2b_load,"max_m2b_load_id":max_m2b_load_id,"max_m1b_load":max_m1b_load,"max_m1b_load_id":max_m1b_load_id}

        property_load_data = {"Property":property.name,"Load Data":load_data}
        property_loads.append(property_load_data)

    for element in elements:

        property_name = element.property.name

        loads = []

        for current_loads in property_loads:
            if current_loads["Property"]==property_name:
                loads = current_loads['Load Data']



        max_sigma_loads = loads['max_sigma_loads']
        max_sigma_vector = loads['max_sigma_vector']
        max_sigma_loads_id = loads["max_sigma_loads_id"]

        max_tau_loads = loads["max_tau_loads"]
        max_tau_vector = loads["max_tau_vector"]
        max_tau_loads_id = loads["max_tau_loads_id"]

        max_p_load = loads["max_p_load"]
        max_p_load_id = loads["max_p_load_id"]
        max_v1_load = loads["max_v1_load"]
        max_v1_load_id = loads["max_v1_load_id"]
        max_v2_load = loads["max_v2_load"]
        max_v2_load_id = loads["max_v2_load_id"]
        max_t_load = loads["max_t_load"]
        max_t_load_id = loads["max_t_load_id"]
        max_m2a_load = loads["max_m2a_load"]
        max_m2a_load_id = loads["max_m2a_load_id"]
        max_m1a_load = loads["max_m1a_load"]
        max_m1a_load_id = loads["max_m1a_load_id"]
        max_m2b_load = loads["max_m2b_load"]
        max_m2b_load_id = loads["max_m2b_load_id"]
        max_m1b_load = loads["max_m1b_load"]
        max_m1b_load_id = loads["max_m1b_load_id"]

        load_cases = element.load_case_data
        for load_case in load_cases:

            load_case_id = load_case.unique_id
            P = load_case.P
            V1 = load_case.V1
            V2 = load_case.V2

            VRSS = np.sqrt(V1**2+V2**2)
            T = load_case.T
            M2A = load_case.M2A
            M1A = load_case.M1A
            M2B = load_case.M2B
            M1B = load_case.M1B

            property = element.property
            A = property.A
            I1 = property.I1
            I2 = property.I2
            J = property.J
            C1 = property.C1
            C2 = property.C2

            sigma_A = abs(P)/A+abs(M1A)*C1/I1+abs(M2A)*C2/I2
            sigma_B = abs(P) / A + abs(M1B) * C1 / I1 + abs(M2B) * C2 / I2

            sigma = max(sigma_A, sigma_B)
            tau = VRSS/A+abs(T)*C1/J

            load_vector = [P, V1, V2, T, M2A, M1A, M2B, M1B]

            if abs(P) > abs(max_p_load[0]):
                max_p_load = load_vector
                max_p_load_id = load_case_id

            if abs(V1) > abs(max_v1_load[1]):
                max_v1_load = load_vector
                max_v1_load_id = load_case_id

            if abs(V2) > abs(max_v2_load[2]):
                max_v2_load = load_vector
                max_v2_load_id = load_case_id

            if abs(T) > abs(max_t_load[3]):
                max_t_load = load_vector
                max_t_load_id = load_case_id

            if abs(M2A) > abs(max_m2a_load[4]):
                max_m2a_load = load_vector
                max_m2a_load_id = load_case_id

            if abs(M1A) > abs(max_m1a_load[5]):
                max_m1a_load = load_vector
                max_m1a_load_id = load_case_id

            if abs(M2B) > abs(max_m2b_load[6]):
                max_m2b_load = load_vector
                max_m2b_load_id = load_case_id

            if abs(M1B) > abs(max_m1b_load[7]):
                max_m1b_load = load_vector
                max_m1b_load_id = load_case_id


            # Adding the loads to the max sigma vector of loads
            end_of_list = len(max_sigma_vector) - 1
            if not max_sigma_vector:
                max_sigma_loads.append(load_vector)
                max_sigma_vector.append(sigma)
                max_sigma_loads_id.append(load_case_id)
            else:
                for i in range(len(max_sigma_vector)):
                    value = max_sigma_vector[i]
                    if sigma > value:
                        max_sigma_vector.insert(i,sigma)
                        max_sigma_loads.insert(i,load_vector)
                        max_sigma_loads_id.insert(i,load_case_id)
                        break
                    elif i==end_of_list and len(max_sigma_vector)<6:
                        max_sigma_vector.append(sigma)
                        max_sigma_loads.append(load_vector)
                        max_sigma_loads_id.append(load_case_id)

            if len(max_sigma_vector) > 6:
                max_sigma_vector=max_sigma_vector[0:6]
                max_sigma_loads = max_sigma_loads[0:6]
                max_sigma_loads_id = max_sigma_loads_id[0:6]

            # Adding the loads to the max shear vector of loads
            end_of_list = len(max_tau_vector) - 1
            if not max_tau_vector:
                max_tau_loads.append(load_vector)
                max_tau_vector.append(tau)
                max_tau_loads_id.append(load_case_id)
            else:
                for i in range(len(max_tau_vector)):
                    value = max_tau_vector[i]
                    if tau > value:
                        max_tau_vector.insert(i,tau)
                        max_tau_loads.insert(i,load_vector)
                        max_tau_loads_id.insert(i,load_case_id)
                        break
                    elif i==end_of_list and len(max_tau_vector)<6:
                        max_tau_vector.append(tau)
                        max_tau_loads.append(load_vector)
                        max_tau_loads_id.append(load_case_id)


            if len(max_tau_vector) > 6:
                max_tau_vector=max_tau_vector[0:6]
                max_tau_loads = max_tau_loads[0:6]
                max_tau_loads_id = max_tau_loads_id[0:6]

            updated_load_data = {"max_sigma_loads": max_sigma_loads, "max_sigma_vector": max_sigma_vector,
                         "max_sigma_loads_id": max_sigma_loads_id,
                         "max_tau_loads": max_tau_loads, "max_tau_vector": max_tau_vector,
                         "max_tau_loads_id": max_tau_loads_id, "max_p_load": max_p_load, "max_p_load_id": max_p_load_id,
                         "max_v1_load": max_v1_load, "max_v1_load_id": max_v1_load_id, "max_v2_load": max_v2_load,
                         "max_v2_load_id": max_v2_load_id, "max_t_load": max_t_load,
                         "max_t_load_id": max_t_load_id, "max_m2a_load": max_m2a_load,
                         "max_m2a_load_id": max_m2a_load_id, "max_m1a_load": max_m1a_load,
                         "max_m1a_load_id": max_m1a_load_id,
                         "max_m2b_load": max_m2b_load, "max_m2b_load_id": max_m2b_load_id, "max_m1b_load": max_m1b_load,
                         "max_m1b_load_id": max_m1b_load_id}

            for index, current_loads in enumerate(property_loads):
                if current_loads["Property"] == property_name:
                    updated_data = {"Property":property_name,"Load Data":updated_load_data}
                    property_loads[index] = updated_data


    return property_loads


class LoadCase:
    def __init__(self):
        self.op2_name = "XXXXXX"
        self.case_id = 9999
        self.unique_id = 999
        self.P = 999
        self.V1 = 999
        self.V2 = 999
        self.T = 999
        self.M2A = 999
        self.M1A = 999
        self.M2B = 999
        self.M1B = 999

