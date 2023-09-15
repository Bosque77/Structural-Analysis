import sys
from copy import copy

import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, pyqtSlot
from fileLoader import *
import random
import math


class Delegate(QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        checked = index.data(Qt.CheckStateRole)
        ret = QStyledItemDelegate.editorEvent(self, event, model, option, index)
        if checked != index.data(Qt.CheckStateRole):
            self.parent().checked.emit(index)
        return ret

class ListView(QListView):
    checked = pyqtSignal(QModelIndex)
    def __init__(self, *args, **kwargs):
        super(ListView, self).__init__(*args, **kwargs)
        self.setItemDelegate(Delegate(self))

class App(QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)

        # Defining window and geometry info
        self.title = 'Stressrun'
        self.logo = 'window_icon.png'
        self.left = 400
        self.top = 350
        self.width = 1200
        self.height = 600

        # Creating Global Widgets
        self.selected_f06_list = QListView()
        self.loaded_f06_list = ListView()
        self.loaded_f06_model = QStandardItemModel()
        self.f06_cases_list = QListView()
        self.scaled_cases = QListView()
        self.scaled_cases_model = QStandardItemModel()
        self.load_case_name = QLineEdit()
        self.load_case_name_list = []

        self.bdf_file_path = ""
        self.bdf_file_name = ""
        self.bdf_label = QLabel()

        self.working_directory = ""

        self.load_cases_list_model = QStandardItemModel()
        self.load_cases_list_view = QListView()
        self.load_cases_list_view.setModel(self.load_cases_list_model)

        self.op2_models = []
        self.scale_factor_line_edit = QLineEdit()
        self.scale_factor_clock_x = QLineEdit()
        self.scale_factor_clock_y = QLineEdit()
        self.scale_factor_clock_z = QLineEdit()
        self.clock_inc = QLineEdit()
        self.clock_freq = QLineEdit()

        self.number_of_stress_cases_line_edit = QLineEdit()
        self.number_of_stress_vectors = 6

        self.x_clock_label = QLabel()
        self.y_clock_label = QLabel()
        self.z_clock_label = QLabel()

        self.x_clock_model = ""
        self.x_clock_subcase = None
        self.y_clock_model = ""
        self.y_clock_subcase = None
        self.z_clock_model = ""
        self.z_clock_subcase = None

        self.load_scaling_case = [] # Contains an individual load scaling case
        self.load_scaling_cases = [] # Contains all of the load scaling cases
        self.load_case = LoadCase()
        self.load_cases_object = LoadCases()

        self.starting_element_ids = []
        self.ending_element_ids = []
        self.analyzed_element_ids = []

        self.sort_by_property_checkbox = QCheckBox("Property")
        self.sort_by_property_checkbox.setCheckable(True)
        self.sort_by_element_checkbox = QCheckBox("Element")
        self.sort_by_element_checkbox.setCheckable(True)

        self.maintain_directional_dependence = "No"

        # Setting Window and Geometry Info
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(self.logo))
        self.initUI()

    def initUI(self):
        # Loading the L3Harris Logo into the QLabel object
        logo = QLabel()
        qimg = QImage()
        qimg.load('test.jpg')
        l3harris_logo = QPixmap.fromImage(qimg)
        logo.setPixmap(l3harris_logo)


        # Creating Main Horizontal Layout
        MainLayout = QHBoxLayout()
        layout_1 = self.setupVerticalLayout1()
        layout_2 = self.setupVerticalLayout2()
        layout_3 = self.setupVerticalLayout3()
        # Addings Layouts to Main Layout
        layout_1_widget = QWidget()
        layout_1_widget.setLayout(layout_1)
        MainLayout.addWidget(layout_1_widget)
        layout_2_widget = QWidget()
        layout_2_widget.setLayout(layout_2)
        MainLayout.addWidget(layout_2_widget)
        layout_3_widget = QWidget()
        layout_3_widget.setLayout((layout_3))
        MainLayout.addWidget(layout_3_widget)

        widget = QWidget()
        widget.setLayout(MainLayout)
        self.w = ElementSelectorWindow(self)
        self.a = AdvancedSettingsWindow(self)
        self.setCentralWidget(widget)
        self.show()

    def addClockedXSubcase(self):
        print("Inside add Clocked X Subcase")
        # Get the currently selected model
        model = self.loaded_f06_list.model()
        for i in range(model.rowCount()):
            item = model.item(i)
            check_state = item.checkState()
            op2_model_name = item.text()
            # If a model is checked
            if check_state ==2:
                # now lets select all of the checked cases in the model
                list_view_model = self.f06_cases_list.model()
                num_of_cases = list_view_model.rowCount() # Determining the number of cases
                for index in range(num_of_cases): # looping through the cases
                    item = list_view_model.item(index)
                    if item.isCheckable() and item.checkState() == Qt.Checked:
                        print("This case is checked: " + str(index))
                        case_id = item.text()
                        description = "Model: " + op2_model_name + " Subcase: " + case_id
                        self.x_clock_label.setText(description)
                        self.x_clock_model = op2_model_name
                        self.x_clock_subcase = int(case_id)

    def addClockedYSubcase(self):
        print("Inside add Clocked Y Subcase")
        # Get the currently selected model
        model = self.loaded_f06_list.model()
        for i in range(model.rowCount()):
            item = model.item(i)
            check_state = item.checkState()
            op2_model_name = item.text()
            # If a model is checked
            if check_state ==2:
                # now lets select all of the checked cases in the model
                list_view_model = self.f06_cases_list.model()
                num_of_cases = list_view_model.rowCount() # Determining the number of cases
                for index in range(num_of_cases): # looping through the cases
                    item = list_view_model.item(index)
                    if item.isCheckable() and item.checkState() == Qt.Checked:
                        print("This case is checked: " + str(index))
                        case_id = item.text()
                        description = "Model: " + op2_model_name + " Subcase: " + case_id
                        self.y_clock_label.setText(description)
                        self.y_clock_model = op2_model_name
                        self.y_clock_subcase = int(case_id)

    def addClockedZSubcase(self):
        print("Inside add Clocked Y Subcase")
        # Get the currently selected model
        model = self.loaded_f06_list.model()
        for i in range(model.rowCount()):
            item = model.item(i)
            check_state = item.checkState()
            op2_model_name = item.text()
            # If a model is checked
            if check_state ==2:
                # now lets select all of the checked cases in the model
                list_view_model = self.f06_cases_list.model()
                num_of_cases = list_view_model.rowCount() # Determining the number of cases
                for index in range(num_of_cases): # looping through the cases
                    item = list_view_model.item(index)
                    if item.isCheckable() and item.checkState() == Qt.Checked:
                        print("This case is checked: " + str(index))
                        case_id = item.text()
                        description = "Model: " + op2_model_name + " Subcase: " + case_id
                        self.z_clock_label.setText(description)
                        self.z_clock_model = op2_model_name
                        self.z_clock_subcase = int(case_id)

    def addClockLoads(self):
        print("Inside Add Clock Loads")
        inc = float(self.clock_inc.text())
        x_scale_factor = float(self.scale_factor_clock_x.text())
        y_scale_factor = float(self.scale_factor_clock_y.text())
        z_scale_factor = float(self.scale_factor_clock_z.text())

        freq_str = self.clock_freq.text()
        if freq_str != "":
            freq = float(freq_str)
            load_set_x = {"op2_model_name": self.x_clock_model, "case_id": self.x_clock_subcase, "scale_factor": x_scale_factor, "inc": inc, "coef": 'x',"frequency":freq}
            load_set_y = {"op2_model_name": self.y_clock_model, "case_id": self.y_clock_subcase, "scale_factor": y_scale_factor, "inc": inc, "coef": 'y',"frequency":freq}
            load_set_z = {"op2_model_name": self.z_clock_model, "case_id": self.z_clock_subcase, "scale_factor": z_scale_factor, "inc": inc, "coef": 'z',"frequency":freq}
        else:
            load_set_x = {"op2_model_name": self.x_clock_model, "case_id": self.x_clock_subcase, "scale_factor": x_scale_factor, "inc": inc, "coef": 'x',"frequency":'NA'}
            load_set_y = {"op2_model_name": self.y_clock_model, "case_id": self.y_clock_subcase, "scale_factor": y_scale_factor, "inc": inc, "coef": 'y',"frequency":'NA'}
            load_set_z = {"op2_model_name": self.z_clock_model, "case_id": self.z_clock_subcase, "scale_factor": z_scale_factor, "inc": inc, "coef": 'z',"frequency":'NA'}


        self.load_case.addClockedLoadSet(load_set_x)
        self.load_case.addClockedLoadSet(load_set_y)
        self.load_case.addClockedLoadSet(load_set_z)


        data_text = "Clock [ X ( {x_scale_factor} * {x_clock_model},{x_clock_subcase} ) \n Y ( {y_scale_factor} * {y_clock_model},{y_clock_subcase} ) \n Z ( {z_scale_factor} * {z_clock_model},{z_clock_subcase} )] \n"
        data_text = data_text.format(x_scale_factor = x_scale_factor, x_clock_model = self.x_clock_model, x_clock_subcase = self.x_clock_subcase, y_scale_factor = y_scale_factor, y_clock_model = self.y_clock_model, y_clock_subcase = self.y_clock_subcase, z_scale_factor = z_scale_factor, z_clock_model = self.z_clock_model, z_clock_subcase = self.z_clock_subcase)
        data_qstd_item = QStandardItem(data_text)
        self.scaled_cases_model.appendRow(data_qstd_item)

    def addLinearCombination(self):
        print("Inside add combination")
        scalar_value = self.scale_factor_line_edit.text()
        scale_factor = str(scalar_value)
        model = self.loaded_f06_list.model()

        # Get the currently selected model
        for i in range(model.rowCount()):
            item = model.item(i)
            check_state = item.checkState()
            op2_model_name = item.text()
            # If a model is checked
            if check_state ==2:
                # now lets select all of the checked cases in the model
                list_view_model = self.f06_cases_list.model()
                num_of_cases = list_view_model.rowCount() # Determining the number of cases
                for index in range(num_of_cases): # looping through the cases
                    item = list_view_model.item(index)
                    if item.isCheckable() and item.checkState() == Qt.Checked:
                        print("This case is checked: " + str(index))
                        case_id = item.text()
                        data_object = {"op2_model_name": op2_model_name, "case_id": case_id, "scale_factor": scale_factor}
                        self.load_case.addLinearCombinationLoadSet(data_object)
                        data_text = "Model Name: " + op2_model_name + ", Case Name: " + case_id + ", Scale Factor: " + scale_factor
                        data_qstd_item = QStandardItem(data_text)
                        self.scaled_cases_model.appendRow(data_qstd_item)

    def addLoadCase(self):
        print("Inside Add Load Case")
        load_case_name = self.load_case_name.text()
        if load_case_name != "":
            if load_case_name not in self.load_case_name_list:
                self.load_case.setName(load_case_name)
                self.load_case_name_list.append(load_case_name)
            else:
                error_message = "This load case already exists. The name must be unique. Please enter another name \n"
                msg = QMessageBox()
                msg.setText(error_message)
                msg.exec_()
                return
        else:
            print("making custom loadcase name")
            random_number = random.randint(0,10000)
            load_case_name = "LC_"+str(random_number)
            self.load_case.setName(load_case_name)
            self.load_case_name_list.append(load_case_name)

        load_case = copy(self.load_case)
        self.load_cases_object.addLoadCase(load_case)
        self.load_case.reset()
        self.scaled_cases_model.clear()
        q_std_item = QStandardItem(load_case.name)
        self.load_cases_list_model.appendRow(q_std_item)

    def getOP2Model(self,model_name):
        for op2_model in self.op2_models:
            file_name = op2_model.op2_filename
            split_str = str.split(file_name, '/')
            current_model_name = split_str[-1]
            if current_model_name == model_name:
                return op2_model

# forest this is where the error is occuring. You are only showing the f06_model_view loaded output files but need to show all of the loaded output files.
    def loadOP2Files(self):
        print("Inside Load OP2 files")
        f06_model_view = self.selected_f06_list.model() #Getting the f06 list model

        for index in range(f06_model_view.rowCount()):
            item = f06_model_view.item(index)
            if item.isCheckable() and item.checkState() == Qt.Checked:
                new_item = QStandardItem(item.text())
                file_path = item.file_path
                op2 = OP2()
                op2.read_op2(file_path)
                new_item.setCheckable(True)
                new_item.setCheckState(Qt.Unchecked)
                self.loaded_f06_model.appendRow(new_item)
                self.op2_models.append(op2)
        self.loaded_f06_list.setModel(self.loaded_f06_model)
        self.loaded_f06_list.checked.connect(self.onChecked)

    def loadConfigFile(self):
        print("Inside Load Configuration File")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "*.xlsx"
                                            , options=options)

        if file:
            file_path = file[0]
            loadConfigurationFile(self,file_path)
            print("Checking Spot Here")
        else:
            return

    @pyqtSlot(QModelIndex)
    def onChecked(self, index):
        print("Inside On Checked")
        model = self.loaded_f06_list.model()
        checked_item = model.itemFromIndex(index)
        cases_model = QStandardItemModel()
        for i in range(model.rowCount()):
            item = model.item(i)
            if item != checked_item:
                item.setCheckState(Qt.Unchecked)
            else:
                op2_index = index.row()
                print(op2_index)
                op2 = self.op2_models[op2_index]
                cbeam_force = op2.cbeam_force
                for case_id in cbeam_force:
                    case_item = QStandardItem(str(case_id))
                    case_item.setCheckState(Qt.Unchecked)
                    case_item.setCheckable(True)
                    cases_model.appendRow(case_item)
                self.f06_cases_list.setModel(cases_model)
                print(item.text(), "was checked")

    def openAdvancedSettings(self):
        print("inside open advanced settings")
        self.a.show()

    def openElementSelector(self):
        print("inside open element selector")
        self.w.updateRows(self.starting_element_ids,self.ending_element_ids)
        self.w.show()



    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def resetLoadCase(self):
        self.load_case.reset()
        self.scaled_cases_model.clear()

    def resetLoadCases(self):
        print("Inside Reset Load Cases")
        self.load_cases_object.reset()
        self.load_cases_list_model.clear()

    def runLoadCases(self):
        print("Inside Run Load Cases")
        try:
            eids_to_analyze = self.analyzed_element_ids
            elements = extractModelElements(self.bdf_file_path,eids_to_analyze)
            properties = extractElementProperties(elements)
            # properties = extractModelProperties(self.bdf_file_path)
        except Exception as e:
            error_message = "Error occured while trying to extract model elements. Is the BDF file defined? \n"
            error_message = error_message + "Error:\n" + str(e)
            msg = QMessageBox()
            msg.setText(error_message)
            msg.exec_()
            return

        # Loading the beam loads for all of the op2 models into each element

        for op2_model in self.op2_models:
            elements = addBeamLoads(op2_model,elements, self.maintain_directional_dependence) # only adds the beam loads to elements that are in the op2 file

        # loading the beam loads for each loadcase into the element.
        load_cases = self.load_cases_object.getLoadCases()
        for element in elements:

            for load_case in load_cases:
                M1A = 0.0
                M1B = 0.0
                M2A = 0.0
                M2B = 0.0
                P = 0.0
                T = 0.0
                V1 = 0.0
                V2 = 0.0
                load_case_name = load_case.name

                # CREATING THE LINEAR COMBINATION LOAD VECTOR
                linear_combination_load_sets = load_case.linear_combination_load_sets
                if linear_combination_load_sets:
                    for load_set in linear_combination_load_sets:
                        op2_name = load_set['op2_model_name']
                        case_id = load_set['case_id']
                        try:
                            scale_factor = float(load_set['scale_factor'])
                        except:   # FOREST YOU SHOULD UPDATE THIS TO ONLY ACCEPT NO VALUE ERRORS
                            scale_factor = 0
                        load_vector = element.getBeamLoads(op2_name,case_id)  # if one of the elements is not in the op2 file data then it may through the error below.
                        if not load_vector:
                            error_message = "A load vector for this subcase could not be generated. Please check you have a subcase selected. \n" \
                                            " Case ID: " + load_case_name + " Subcase: " + str(
                                case_id) + "\n"
                            msg = QMessageBox()
                            msg.setText(error_message)
                            msg.exec_()
                            return


                        M1A = M1A + load_vector.M1A*scale_factor
                        M1B = M1B + load_vector.M1B*scale_factor
                        M2A = M2A + load_vector.M2A*scale_factor
                        M2B = M2B + load_vector.M2B*scale_factor
                        P = P + load_vector.P*scale_factor
                        T = T + load_vector.T*scale_factor
                        V1 = V1 + load_vector.V1*scale_factor
                        V2 = V2 + load_vector.V2*scale_factor
                    linearly_combined_load_vector = {'P': P, 'V1': V1, 'V2': V2, 'T': T, 'M2A': M2A, 'M1A': M1A, 'M2B': M2B, 'M1B': M1B}
                else:
                    linearly_combined_load_vector = {'P': 0.0, 'V1': 0.0, 'V2': 0.0, 'T': 0.0, 'M2A': 0.0, 'M1A': 0.0,
                                                     'M2B': 0.0, 'M1B': 0.0}

                # CREATING THE CLOCKED LOAD VECTOR
                clocked_load_sets = load_case.clocked_load_sets
                if clocked_load_sets:
                    inc = float(clocked_load_sets[0]['inc'])
                    if inc != 0:
                        num_of_angles = math.floor(360/inc)
                    else:
                        num_of_angles = 1
                    for i in range(0,num_of_angles):

                        load_case_name = load_case.name
                        M1A = 0.0
                        M1B = 0.0
                        M2A = 0.0
                        M2B = 0.0
                        P = 0.0
                        T = 0.0
                        V1 = 0.0
                        V2 = 0.0
                        sub_inc = i*inc
                        theta = math.radians(sub_inc)
                        for load_set in clocked_load_sets:
                            try:
                                op2_name = load_set['op2_model_name']
                                case_id = load_set['case_id']
                                scale_factor = load_set['scale_factor']
                                coef = load_set['coef']
                                frequency = load_set['frequency']
                            except:
                                error_message = "The scale factor is not defined properly for the clocked load set under case id: " + str(case_id) + "\n"
                                error_message = error_message + "Error:\n" + str(e)
                                msg = QMessageBox()
                                msg.setText(error_message)
                                msg.exec_()

                    # There is an issue with the if statement here.
                            if frequency =='NA':
                                load_vector = element.getBeamLoads(op2_name, case_id)
                            else:
                                load_vector = element.getBeamLoads(op2_name, case_id,frequency)



                            if not load_vector:
                                error_message = "A load vector for this subcase could not be generated. Please check you have a subcase selected. \n" \
                                                " Case ID: " +load_case_name+" Subcase: "+ str(
                                    case_id) + "\n"
                                msg = QMessageBox()
                                msg.setText(error_message)
                                msg.exec_()
                                return

                            if coef=="x":
                                M1A = M1A + load_vector.M1A*scale_factor*math.cos(theta)
                                M1B = M1B + load_vector.M1B*scale_factor*math.cos(theta)
                                M2A = M2A + load_vector.M2A*scale_factor*math.cos(theta)
                                M2B = M2B + load_vector.M2B*scale_factor*math.cos(theta)
                                P = P + load_vector.P*scale_factor*math.cos(theta)
                                T = T + load_vector.T*scale_factor*math.cos(theta)
                                V1 = V1 + load_vector.V1*scale_factor*math.cos(theta)
                                V2 = V2 + load_vector.V2*scale_factor*math.cos(theta)
                            elif coef=="y":
                                M1A = M1A + load_vector.M1A*scale_factor*math.sin(theta)
                                M1B = M1B + load_vector.M1B*scale_factor*math.sin(theta)
                                M2A = M2A + load_vector.M2A*scale_factor*math.sin(theta)
                                M2B = M2B + load_vector.M2B*scale_factor*math.sin(theta)
                                P = P + load_vector.P*scale_factor*math.sin(theta)
                                T = T + load_vector.T*scale_factor*math.sin(theta)
                                V1 = V1 + load_vector.V1*scale_factor*math.sin(theta)
                                V2 = V2 + load_vector.V2*scale_factor*math.sin(theta)
                            elif coef=="z":   # NEED TO INCORPORATE A NEGATIVE Z LOAD AS WELL AS A POSITIVE Z LOAD.
                                M1A_p = M1A + load_vector.M1A*scale_factor
                                M1B_p = M1B + load_vector.M1B*scale_factor
                                M2A_p = M2A + load_vector.M2A*scale_factor
                                M2B_p = M2B + load_vector.M2B*scale_factor
                                P_p = P + load_vector.P*scale_factor
                                T_p = T + load_vector.T*scale_factor
                                V1_p = V1 + load_vector.V1*scale_factor
                                V2_p = V2 + load_vector.V2*scale_factor

                                M1A_n = M1A - load_vector.M1A*scale_factor
                                M1B_n = M1B - load_vector.M1B*scale_factor
                                M2A_n = M2A - load_vector.M2A*scale_factor
                                M2B_n = M2B - load_vector.M2B*scale_factor
                                P_n = P - load_vector.P*scale_factor
                                T_n = T - load_vector.T*scale_factor
                                V1_n = V1 - load_vector.V1*scale_factor
                                V2_n = V2 - load_vector.V2*scale_factor

                        clocked_load_vector_p = {'P': P_p, 'V1': V1_p, 'V2': V2_p, 'T': T_p, 'M2A': M2A_p, 'M1A': M1A_p, 'M2B': M2B_p, 'M1B': M1B_p}
                        clocked_load_vector_n = {'P': P_n, 'V1': V1_n, 'V2': V2_n, 'T': T_n, 'M2A': M2A_n, 'M1A': M1A_n, 'M2B': M2B_n, 'M1B': M1B_n}


                        # Adding the +Z Clocked Load Case + Linear Combination
                        P = linearly_combined_load_vector['P']+clocked_load_vector_p['P']
                        V1 = linearly_combined_load_vector['V1']+clocked_load_vector_p['V1']
                        V2 = linearly_combined_load_vector['V2'] + clocked_load_vector_p['V2']
                        T = linearly_combined_load_vector['T']+clocked_load_vector_p['T']
                        M2A = linearly_combined_load_vector['M2A']+clocked_load_vector_p['M2A']
                        M1A = linearly_combined_load_vector['M1A']+clocked_load_vector_p['M1A']
                        M2B = linearly_combined_load_vector['M2B']+clocked_load_vector_p['M2B']
                        M1B = linearly_combined_load_vector['M1B']+clocked_load_vector_p['M1B']

                        P = round(P,2)
                        V1 = round(V1,2)
                        V2 = round(V2,2)
                        T = round(T,2)
                        M2A = round(M2A,2)
                        M1A = round(M1A,2)
                        M2B = round(M2B,2)
                        M1B = round(M1B,2)

                        load_vector = {'P': P, 'V1': V1, 'V2': V2, 'T': T, 'M2A': M2A, 'M1A': M1A, 'M2B': M2B, 'M1B': M1B}

                        if frequency == 'NA':
                            load_case_name_id = load_case_name+"_Clocked_"+str(sub_inc)+"_+Z"
                        else:
                            load_case_name_id = load_case_name + "_Clocked_" + str(sub_inc) + "_+Z"+"_Freq_"+str(frequency)+"_Hz"

                        element.addLoadCase(load_case_name_id , load_vector)

                        # Adding the -Z Clocked Load Case + Linear Combination

                        P = linearly_combined_load_vector['P']+clocked_load_vector_n['P']
                        V1 = linearly_combined_load_vector['V1']+clocked_load_vector_n['V1']
                        V2 = linearly_combined_load_vector['V2'] + clocked_load_vector_n['V2']
                        T = linearly_combined_load_vector['T']+clocked_load_vector_n['T']
                        M2A = linearly_combined_load_vector['M2A']+clocked_load_vector_n['M2A']
                        M1A = linearly_combined_load_vector['M1A']+clocked_load_vector_n['M1A']
                        M2B = linearly_combined_load_vector['M2B']+clocked_load_vector_n['M2B']
                        M1B = linearly_combined_load_vector['M1B']+clocked_load_vector_n['M1B']

                        P = round(P,2)
                        V1 = round(V1,2)
                        V2 = round(V2,2)
                        T = round(T,2)
                        M2A = round(M2A,2)
                        M1A = round(M1A,2)
                        M2B = round(M2B,2)
                        M1B = round(M1B,2)

                        load_vector = {'P': P, 'V1': V1, 'V2': V2, 'T': T, 'M2A': M2A, 'M1A': M1A, 'M2B': M2B, 'M1B': M1B}

                        if frequency=='NA':
                            load_case_name_id = load_case_name + "_Clocked_" + str(sub_inc) + "_-Z"
                        else:
                            load_case_name_id = load_case_name + "_Clocked_" + str(sub_inc) + "_-Z" + "_Freq_" + str(
                                frequency) + "_Hz"

                        element.addLoadCase(load_case_name_id , load_vector)
                else:
                    P = linearly_combined_load_vector['P']
                    V1 = linearly_combined_load_vector['V1']
                    V2 = linearly_combined_load_vector['V2']
                    T = linearly_combined_load_vector['T']
                    M2A = linearly_combined_load_vector['M2A']
                    M1A = linearly_combined_load_vector['M1A']
                    M2B = linearly_combined_load_vector['M2B']
                    M1B = linearly_combined_load_vector['M1B']
                    load_vector = {'P': P, 'V1': V1, 'V2': V2, 'T': T, 'M2A': M2A, 'M1A': M1A, 'M2B': M2B, 'M1B': M1B}
                    load_case_name = load_case_name
                    element.addLoadCase(load_case_name, load_vector)




        if self.sort_by_element_checkbox.checkState() == Qt.Checked:
            elements = sortLoadsByElements(elements, self.number_of_stress_vectors)
            parent_dir = self.working_directory
            sorted_load_dir = '/Sorted_Loads/Elements'
            file_path = parent_dir + sorted_load_dir
            printLoadsByElements(elements, file_path)

        if self.sort_by_property_checkbox.checkState() == Qt.Checked:
            property_loads = sortLoadsByProperty(elements,properties, self.number_of_stress_vectors)
            parent_dir = self.working_directory
            sorted_load_dir = '/Sorted_Loads/Properties'
            file_path =  parent_dir+sorted_load_dir
            printLoadsByProperty(property_loads,file_path)

    def saveConfigFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "Excel File (*.xlsx)", options=options)
        if file_name:

            split_string = file_name.split(".")
            end_string = split_string[-1]
            if end_string !="xlsx":
                file_name = file_name + ".xlsx"

            load_cases = self.load_cases_object.getLoadCases()


            bdf_file_location = self.bdf_file_path
            bdf_file_name = self.bdf_file_name
            working_directory = self.working_directory

            if bdf_file_location == '':
                error_message = "BDF File must be defined before saving the configuration file \n"
                msg = QMessageBox()
                msg.setText(error_message)
                msg.exec_()
                return

            if working_directory == '':
                error_message = "A working directory must be defined before saving the configuration file \n"
                msg = QMessageBox()
                msg.setText(error_message)
                msg.exec_()
                return

            config_data_frame = {  'BDF': [],
                            'BDF File Location': [],
                            'OP2': [],
                            'OP2 File Location' : [],
                            'Element ID Start': [],
                            'Element ID Stop': [],
                            'Working Directory':[]
                          }

            # Adding the BDF file to the config file
            config_data_frame['BDF'].append(bdf_file_name)
            config_data_frame['BDF File Location'].append(bdf_file_location)
            config_data_frame['Working Directory'].append(working_directory)

            # Adding the OP2 files to the config file
            op2_models = self.op2_models
            # finding the op2 file name from the shortened name
            for index, op2_model in enumerate(op2_models):
                current_file_name = op2_model.op2_filename
                split_string = current_file_name.split("/")
                op2_name = split_string[-1]
                if index ==0:
                    config_data_frame['OP2'].append(op2_name)
                    config_data_frame['OP2 File Location'].append(current_file_name)
                else:
                    config_data_frame['BDF'].append('')
                    config_data_frame['BDF File Location'].append('')
                    config_data_frame['Working Directory'].append('')
                    config_data_frame['OP2'].append(op2_name)
                    config_data_frame['OP2 File Location'].append(current_file_name)

            element_table = self.w.table_widget
            num_of_element_table_rows = element_table.rowCount()
            for i in range(num_of_element_table_rows):
                starting_eid = element_table.item(i, 0).text()
                stopping_eid = element_table.item(i, 1).text()

                if starting_eid != "":
                    try:
                        starting_eid = int(starting_eid)
                        stopping_eid = int(stopping_eid)
                        config_data_frame['Element ID Start'].append(starting_eid)
                        config_data_frame['Element ID Stop'].append(stopping_eid)
                    except Exception as e:
                        error_message = "Error occured while saving configuraiton file. \n Make sure the starting and ending element are both integers in the element limiting table \n"
                        error_message = error_message + "Error:\n" + str(e)
                        msg = QMessageBox()
                        msg.setText(error_message)
                        msg.exec_()
                        return

            # ERROR IS OCCURING HERE. NEED TO MAKE SURE WHEN I SAVE THE CONFIG FILE THE DATA FRAME ARRAYS ARE ALL THE SAME LENGTH.
            num_of_op2_files = len(config_data_frame['OP2 File Location'])
            num_of_limit_element_rows = len(config_data_frame['Element ID Start'])

            if num_of_op2_files > num_of_limit_element_rows:
                difference_in_rows = num_of_op2_files-num_of_limit_element_rows
                for i in range(difference_in_rows):
                    config_data_frame['Element ID Start'].append('')
                    config_data_frame['Element ID Stop'].append('')
            elif num_of_limit_element_rows > num_of_op2_files:
                difference_in_rows = num_of_limit_element_rows - num_of_op2_files
                for i in range(difference_in_rows):
                    config_data_frame['BDF'].append('')
                    config_data_frame['BDF File Location'].append('')
                    config_data_frame['OP2'].append('')
                    config_data_frame['OP2 File Location'].append('')


            load_case_data_frame = {  'Case ID': [],
                            'Type': [],
                            'Inc': [],
                            'coef' : [],
                            'factor': [],
                            'Load File': [],
                            'Frequency': [],
                            'OP2 Subcase': [],
                          }
            for load_case in load_cases:
                load_case_name = load_case.name
                clocked_load_sets = load_case.clocked_load_sets
                linear_combination_load_set = load_case.linear_combination_load_sets

                load_case_data_frame['Case ID'].append(load_case_name)
                load_case_data_frame['Type'].append('')
                load_case_data_frame['Inc'].append('')
                load_case_data_frame['coef'].append('')
                load_case_data_frame['factor'].append('')
                load_case_data_frame['Load File'].append('')
                load_case_data_frame['Frequency'].append('')
                load_case_data_frame['OP2 Subcase'].append('')

                for load_set in clocked_load_sets:
                    type = "Clock"
                    inc = load_set['inc']
                    coef = load_set['coef']
                    scale_factor = load_set['scale_factor']
                    op2_name = load_set['op2_model_name']
                    op2_models = self.op2_models
                    load_file = ""
                    # finding the op2 file name from the shortened name
                    for op2_model in op2_models:
                        current_file_name = op2_model.op2_filename

                        split_string = current_file_name.split("/")
                        end_string = split_string[-1]

                        if op2_name == end_string:
                            load_file = current_file_name
                            break
                    if load_set['frequency']:
                        frequency = load_set['frequency']
                    else:
                        frequency = 'NA'
                    op2_subcase = load_set['case_id']

                    load_case_data_frame['Case ID'].append('')
                    load_case_data_frame['Type'].append(type)
                    load_case_data_frame['Inc'].append(inc)
                    load_case_data_frame['coef'].append(coef)
                    load_case_data_frame['factor'].append(scale_factor)
                    load_case_data_frame['Load File'].append(load_file)
                    load_case_data_frame['Frequency'].append(frequency)
                    load_case_data_frame['OP2 Subcase'].append(op2_subcase)

                for load_set in linear_combination_load_set:
                    type = "Linear Combination"
                    op2_subcase = load_set['case_id']
                    scale_factor = load_set['scale_factor']
                    op2_name = load_set['op2_model_name']
                    load_file = ""
                    # finding the op2 file name from the shortened name
                    for op2_model in op2_models:
                        current_file_name = op2_model.op2_filename

                        split_string = current_file_name.split("/")
                        end_string = split_string[-1]

                        if op2_name == end_string:
                            load_file = current_file_name
                            break

                    load_case_data_frame['Case ID'].append('')
                    load_case_data_frame['Type'].append(type)
                    load_case_data_frame['Inc'].append('')
                    load_case_data_frame['coef'].append('')
                    load_case_data_frame['factor'].append(scale_factor)
                    load_case_data_frame['Load File'].append(load_file)
                    load_case_data_frame['Frequency'].append('')
                    load_case_data_frame['OP2 Subcase'].append(op2_subcase)

            load_case_data_frame['Case ID'].append('End')
            load_case_data_frame['Type'].append('')
            load_case_data_frame['Inc'].append('')
            load_case_data_frame['coef'].append('')
            load_case_data_frame['factor'].append('')
            load_case_data_frame['Load File'].append('')
            load_case_data_frame['Frequency'].append('')
            load_case_data_frame['OP2 Subcase'].append('')

            saveConfigurationFile(load_case_data_frame,config_data_frame,file_name)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

    def selectBDF(self):
        print("Inside Select BDF")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "Python Files (*.bdf)", options=options)
        file_path = file[0]
        split_file_path = str.split(file_path, '/')
        file_name = split_file_path[-1]
        self.bdf_file_path = file_path
        self.bdf_file_name = file_name
        self.bdf_label.setText(file_name)

    def selectWorkingDirectory(self):
        print("Inside Select Working Directory")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.working_directory = QFileDialog.getExistingDirectory(self, "Select Your Working Directory")


    def selectOP2Files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "OP2 Files (*.op2)", options=options)
        if files:
            num_of_files = len(files)
            model = QStandardItemModel()
            for i in range(num_of_files):
                file_path = files[i]
                split_file_path = str.split(file_path, '/')
                file_name = split_file_path[-1]
                item = QStandardItem(file_name)
                item.addFile(file_path)
                check = Qt.Unchecked
                item.setCheckState(check)
                item.setCheckable(True)
                model.appendRow(item)
            self.selected_f06_list.setModel(model)

    def setDirectionalDependence(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.maintain_directional_dependence = radioButton.text
            print(self.maintain_directional_dependence)

    def setupVerticalLayout1(self):
        # Creating 1st Vertical Layout that will reside inside the Main Horizontal Layout
        layout_1 = QVBoxLayout()
        label = QLabel()
        label.setText("Output Reference Files")
        layout_1.addWidget(label)
        layout_1.addWidget(self.selected_f06_list)
        load_buttons_layout = QHBoxLayout()

        # Creating Button to Select Files
        select_f06_files = QPushButton()
        select_f06_files.setText("Select OP2 Files")
        select_f06_files.clicked.connect(self.selectOP2Files)
        # Creating button to Load Files
        load_f06_files = QPushButton()
        load_f06_files.setText("Load OP2 Files")
        load_f06_files.clicked.connect(self.loadOP2Files)
        # Adding buttons to horizontal layout
        load_buttons_layout.addWidget(select_f06_files)
        load_buttons_layout.addWidget(load_f06_files)

        buttons_widget = QWidget()
        buttons_widget.setLayout(load_buttons_layout)
        layout_1.addWidget(buttons_widget)

        return layout_1

    def setupVerticalLayout2(self):
        # Creating the 2nd Vertical Layout that will reside inside the Main Horizontal Layout
        layout_2 = QVBoxLayout()
        ####################### Sublayout 1 #################
        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        tabs.resize(400, 200)
        tabs.addTab(tab1, "Linear Combination")
        tabs.addTab(tab2, "Clock")

        # Setting up Linear Combination Tab
        tab1.layout = QVBoxLayout()
        row_1 = QHBoxLayout()
        # line_edit = QLineEdit()
        pushButton1 = QPushButton("Add Linear Combination")
        pushButton1.clicked.connect(self.addLinearCombination)
        row_1.addWidget(self.scale_factor_line_edit, 35)
        row_1.addWidget(pushButton1, 15)
        horizontal_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        row_1.addItem(horizontal_spacer)
        row_1_widget = QWidget()
        row_1_widget.setLayout(row_1)
        tab1.layout.addWidget(row_1_widget)
        tab1.setLayout(tab1.layout)

        # Setting up Clock Tab FOREST NEED TO FINISH THIS CODE
        tab2.layout = QVBoxLayout()

        # title row
        title_row = QHBoxLayout()
        label1 = QLabel()
        label1.setText("Clocking Angle")
        label2 = QLabel()
        label2.setText("Scale Factor")
        title_row.addWidget(label1)
        title_row.addWidget(self.clock_inc)
        title_row.addStretch()
        title_row.addWidget(label2)
        # row 1
        row_1 = QHBoxLayout()
        pushButton1 = QPushButton("Add X-Subcase")
        pushButton1.clicked.connect(self.addClockedXSubcase)
        scale_factor = self.scale_factor_clock_x
        row_1.addWidget(pushButton1)
        self.x_clock_label.setText("Select X Subcase")
        row_1.addWidget(self.x_clock_label)
        row_1.addStretch()
        row_1.addItem(horizontal_spacer)
        row_1.addWidget(scale_factor)

        # row 2
        row_2 = QHBoxLayout()
        pushButton1 = QPushButton("Add Y-Subcase")
        pushButton1.clicked.connect(self.addClockedYSubcase)
        scale_factor = self.scale_factor_clock_y
        row_2.addWidget(pushButton1)
        self.y_clock_label.setText("Select Y Subcase")
        row_2.addWidget(self.y_clock_label)
        row_2.addStretch()
        row_2.addItem(horizontal_spacer)
        row_2.addWidget(scale_factor)

        # row 3
        row_3 = QHBoxLayout()
        pushButton1 = QPushButton("Add Z-Subcase")
        pushButton1.clicked.connect(self.addClockedZSubcase)
        scale_factor = self.scale_factor_clock_z
        row_3.addWidget(pushButton1)
        self.z_clock_label.setText("Select Z Subcase")
        row_3.addWidget(self.z_clock_label)
        row_3.addStretch()
        row_3.addItem(horizontal_spacer)
        row_3.addWidget(scale_factor)

        # row 4
        submit_row = QHBoxLayout()
        pushButton1 = QPushButton("Add Clocked Loads")
        pushButton1.clicked.connect(self.addClockLoads)
        label = QLabel()
        label.setText("Frequency")
        submit_row.addWidget(label)
        submit_row.addWidget(self.clock_freq)
        submit_row.addStretch()
        submit_row.addWidget(pushButton1)


        tab2.layout.addLayout(title_row)
        tab2.layout.addLayout(row_1)
        tab2.layout.addLayout(row_2)
        tab2.layout.addLayout(row_3)
        tab2.layout.addLayout(submit_row)
        tab2.setLayout(tab2.layout)

        sublayout_1 = QVBoxLayout()
        linear_combination = QLineEdit()
        select_all = QPushButton()
        select_all.setText("Select All")
        sublayout_1.addWidget(tabs)
        sublayout_1_widget = QWidget()
        sublayout_1_widget.setLayout(sublayout_1)
        ####################### Sublayout 2 #################
        sublayout_2 = QHBoxLayout()
        vertical_layout = QVBoxLayout()
        label = QLabel()
        label.setText("Loaded Output Files")
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(self.loaded_f06_list)
        sublayout_2.addLayout(vertical_layout, 33)

        vertical_layout = QVBoxLayout()
        label = QLabel()
        label.setText("Cases")
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(self.f06_cases_list)
        sublayout_2.addLayout(vertical_layout,66)
        sublayout_2_widget = QWidget()
        sublayout_2_widget.setLayout(sublayout_2)

        ####################### Sublayout 3 #################
        sublayout_3 = QHBoxLayout()

        vertical_layout = QVBoxLayout()
        label = QLabel()
        label.setText("Load Case")
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(self.scaled_cases)
        self.scaled_cases.setModel(self.scaled_cases_model)
        sublayout_3.addLayout(vertical_layout)
        sublayout_3_widget = QWidget()
        sublayout_3_widget.setLayout(sublayout_3)

        ####################### Sublayout 4 #################
        sublayout_4 = QHBoxLayout()

        reset_button = QPushButton("Reset Load Case")
        reset_button.clicked.connect(self.resetLoadCase)
        sublayout_4.addWidget(reset_button)
        sublayout_4.addStretch()
        lc_button = QPushButton("Add Load Case")
        lc_button.clicked.connect(self.addLoadCase)
        sublayout_4.addWidget(lc_button)
        sublayout_4.addWidget(self.load_case_name)
        sublayout_4_widget = QWidget()
        sublayout_4_widget.setLayout(sublayout_4)

        ############ Organizing Sublayouts ##################
        layout_2.addWidget(sublayout_1_widget, 30)
        layout_2.addWidget(sublayout_2_widget, 45)
        layout_2.addWidget(sublayout_3_widget, 20)
        layout_2.addWidget(sublayout_4_widget, 5)

        return layout_2

    def setupVerticalLayout3(self):
        print("Inside Setup VerticalLayout 3")
        layout_3 = QVBoxLayout()
        ####################### Sublayout 1 #################
        label = QLabel("Load Cases")
        layout_3.addWidget(label)
        layout_3.addWidget(self.load_cases_list_view)

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        reset_button = QPushButton("Reset Load Cases")
        reset_button.clicked.connect(self.resetLoadCases)
        h_layout.addWidget(reset_button)
        layout_3.addLayout(h_layout)

        ####################### Sublayout 2 #################
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        label = QLabel("# of Processors")
        h_layout.addWidget(label)
        line_edit = QLineEdit("1")
        line_edit.setAlignment(Qt.AlignRight)
        h_layout.addWidget(line_edit)
        layout_3.addLayout(h_layout)

        ####################### Sublayout 3 #################
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.bdf_label)
        select_bdf_button = QPushButton("Select BDF File")
        select_bdf_button.clicked.connect(self.selectBDF)
        h_layout.addWidget(select_bdf_button)
        select_working_directory_button = QPushButton("Select Working Diretory")
        select_working_directory_button.clicked.connect(self.selectWorkingDirectory)
        h_layout.addWidget(select_bdf_button)
        h_layout.addWidget(select_working_directory_button)
        layout_3.addLayout(h_layout)
        ####################### Sublayout 4 #################
        label_2 = QLabel("Vibe - Maintain Directional Dependence:")
        layout_3.addWidget(label_2)
        h_layout = QHBoxLayout()

        radiobutton_1 = QRadioButton("Yes")
        radiobutton_1.setChecked(False)
        radiobutton_1.text = "Yes"
        radiobutton_1.toggled.connect(self.setDirectionalDependence)
        h_layout.addWidget(radiobutton_1)

        radiobutton_2 = QRadioButton("No")
        radiobutton_2.setChecked(True)
        radiobutton_2.text = "No"
        radiobutton_2.toggled.connect(self.setDirectionalDependence)
        h_layout.addWidget(radiobutton_2)

        layout_3.addLayout(h_layout)
        ####################### Sublayout 5 #################
        label_2 = QLabel("Sort By:")
        layout_3.addWidget(label_2)

        h_layout = QHBoxLayout()
        item_model = QStandardItemModel()

        push_button = QPushButton("Limit Elements")
        push_button.clicked.connect(self.openElementSelector)

        h_layout.addWidget(self.sort_by_property_checkbox)
        h_layout.addWidget(self.sort_by_element_checkbox)
        h_layout.addWidget(push_button)

        layout_3.addLayout(h_layout)
        ####################### Sublayout 6 #################
        h_layout = QHBoxLayout()
        button_1 = QPushButton("Load Config. File")
        button_1.clicked.connect(self.loadConfigFile)
        button_2 = QPushButton("Save Config. File")
        button_2.clicked.connect(self.saveConfigFile)
        h_layout.addWidget(button_1)
        h_layout.addWidget(button_2)
        layout_3.addLayout(h_layout)
        ####################### Sublayout 7 #################
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.runLoadCases)
        layout_3.addWidget(run_button)

        advanced_settings_button = QPushButton("Advanced Settings")
        advanced_settings_button.clicked.connect(self.openAdvancedSettings)
        layout_3.addWidget(advanced_settings_button)

        layout_3


        return layout_3

class ElementTableWidget(QTableWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()


        # Defining window and geometry info
        self.title = 'Element Selector'
        self.logo = 'window_icon.png'
        self.left = 800
        self.top = 750
        self.width = 800
        self.height = 400



        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(self.logo))
        # self.horizontalHeader().setStretchLastSection(True)

        self.setColumnCount(2)
        self.setRowCount(4)
        self.setItem(0, 0, QTableWidgetItem("Starting EID"))
        self.setItem(0, 1, QTableWidgetItem("Ending EID"))
        self.setItem(1, 0, QTableWidgetItem(""))
        self.setItem(1, 1, QTableWidgetItem(""))
        self.setItem(2, 0, QTableWidgetItem(""))
        self.setItem(2, 1, QTableWidgetItem(""))
        self.setItem(3, 0, QTableWidgetItem(""))
        self.setItem(3, 1, QTableWidgetItem(""))
        self.move(0, 0)
        # table selection change
        self.doubleClicked.connect(self.on_table_click)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        header = self.verticalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

    def updateRows(self,starting_element_ids,ending_element_ids):
        print("inside update rows")
        self.setColumnCount(2)
        num_of_starting_element_ids = len(starting_element_ids)
        if num_of_starting_element_ids > 0:
            self.setColumnCount(2)
            self.setRowCount(num_of_starting_element_ids)

            for i in range(num_of_starting_element_ids):
                starting_element_id = starting_element_ids[i]
                ending_element_id = ending_element_ids[i]
                self.setItem(i, 0, QTableWidgetItem(str(starting_element_id)))
                self.setItem(i, 1, QTableWidgetItem(str(ending_element_id)))
        self.move(0, 0)
        # table selection change
        self.doubleClicked.connect(self.on_table_click)

    @pyqtSlot()
    def on_table_click(self):
        print("\n")
        for currentQTableWidgetItem in self.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

class ElementSelectorWindow(QWidget):
    print("inside element selector window")
    # Defining window and geometry info
    def __init__(self, Main_App):
        super().__init__()
        self.Main_App = Main_App

        self.title = 'Element Selector'
        self.logo = 'window_icon.png'
        self.left = 650
        self.top = 450
        self.width = 600
        self.height = 400

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(self.logo))
        self.analyzed_element_ids=[]


        label = QLabel()
        label.setText("Select the elements you want to limit the load processing to.\n  \nWhen entering the elements to include"
                      "the first element ID will be included in the selected elements, but the last element ID will not be included.\n"
                      "\nTherefore if you want to process loads on elements 1-10 you need to enter 1 in the first column and 11 in the second column\n")
        label.setWordWrap(True)
        self.table_widget = ElementTableWidget()

        button_layout = QHBoxLayout()
        button_1 = QPushButton("Add Row")
        button_1.clicked.connect(self.addRow)
        button_2 = QPushButton("Save")
        button_2.clicked.connect(self.saveElementSelection)

        button_layout.addWidget(button_1)
        button_layout.addWidget(button_2)

        layout = QVBoxLayout()


        layout.addWidget(label)
        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def addRow(self):
        print("inside add row")
        row_number = self.table_widget.rowCount()
        self.table_widget.insertRow(row_number)
        self.table_widget.setItem(row_number, 0, QTableWidgetItem(""))
        self.table_widget.setItem(row_number, 1, QTableWidgetItem(""))

    def updateRows(self,starting_element_ids,ending_element_ids):
        self.table_widget.updateRows(starting_element_ids,ending_element_ids)

    def saveElementSelection(self):
        num_of_rows = self.table_widget.rowCount()

        starting_element_ids = []
        stopping_element_ids = []
        for i in range(num_of_rows):
            starting_eid = self.table_widget.item(i, 0).text()
            stopping_eid = self.table_widget.item(i, 1).text()

            if starting_eid !="":
                try:
                    starting_eid = int(starting_eid)
                    stopping_eid = int(stopping_eid)
                    starting_element_ids.append(starting_eid)
                    stopping_element_ids.append(stopping_eid)
                except Exception as e:
                    error_message = "Error occured while trying to save the element IDs. \n Make sure the starting and ending element are both integers \n"
                    error_message = error_message + "Error:\n" + str(e)
                    msg = QMessageBox()
                    msg.setText(error_message)
                    msg.exec_()
                    return


        list_element_ids = []
        for index in range(len(starting_element_ids)):
            starting_element_id = starting_element_ids[index]
            stopping_element_id = stopping_element_ids[index]
            if stopping_element_id != starting_element_id:
                stopping_element_id = stopping_element_ids[index]
                element_ids = list(range(starting_element_id, stopping_element_id))
                list_element_ids.append(element_ids)
            else:
                element_ids.append(starting_element_id)

        self.analyzed_element_ids = []
        for element_list in list_element_ids:
            for element in element_list:
                if element not in self.analyzed_element_ids:
                    self.analyzed_element_ids.append(element)

        self.Main_App.starting_element_ids = starting_element_ids
        self.Main_App.ending_element_ids = stopping_element_ids
        self.Main_App.analyzed_element_ids = self.analyzed_element_ids
        self.close()

class AdvancedSettingsWindow(QWidget):
    def __init__(self, Main_App):
        super().__init__()
        self.Main_App = Main_App

        self.title = 'Advanced Settings'
        self.logo = 'window_icon.png'
        self.left = 650
        self.top = 450
        self.width = 600
        self.height = 400

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(self.logo))
        self.analyzed_element_ids=[]

        layout = QVBoxLayout()
        label = QLabel()

        # Creating the input for setting the number of stress cases to compute per element/property loads write out
        input_box = QVBoxLayout()
        label.setText(
            "Number of Stress Results to Compute\n")
        label.setWordWrap(True)
        input_box.addWidget(label)
        input_box.addWidget(Main_App.number_of_stress_cases_line_edit, 35)
        layout.addLayout(input_box)



        # button_layout = QHBoxLayout()
        button = QPushButton("Save")
        button.clicked.connect(self.saveAdvancedSettings)

        layout.addWidget(button)

        self.setLayout(layout)

    def saveAdvancedSettings(self):
        print('inside save advanced settings')
        number_of_stress_vectors = int(self.Main_App.number_of_stress_cases_line_edit.text())
        self.Main_App.number_of_stress_vectors = number_of_stress_vectors
        self.close()

class QStandardItem(QStandardItem):
    def __init__(self,data):
        super().__init__(data)
        self.data = data

    def addFile(self,file_path):
        self.file_path = file_path

# Represents a Linear Combination, RSS, or Clocked Loadcase
class LoadCase:
    def __init__(self):
        self.linear_combination_load_sets=[]
        self.clocked_load_sets=[]
        self.name = "LC_Generic"

    def setName(self,load_case_name):
        self.name = load_case_name

    def addLinearCombinationLoadSet(self,load_set):
        self.linear_combination_load_sets.append(load_set)

    def addClockedLoadSet(self,load_set):
        self.clocked_load_sets.append(load_set)



    def reset(self):
        self.linear_combination_load_sets = []
        self.clocked_load_sets = []
        self.name = "LC_Generic"

# Holds a list of all of the combination sets that will be ran
class LoadCases:
    def __init__(self):
        self.loadcases = []

    def addLoadCase(self,load_case:LoadCase):
        self.loadcases.append(load_case)

    def getLoadCases(self):
        return self.loadcases;

    def reset(self):
        self.loadcases = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    ex = App()
    sys.exit(app.exec_())


