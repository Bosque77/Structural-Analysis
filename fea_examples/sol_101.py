from typing import TextIO
import numpy as np
from pyNastran.bdf.bdf import BDF
from sympy import *

class SOL_101:
    BIN1 = 0
    BIN2 = 8
    BIN3 = 16
    BIN4 = 24
    BIN5 = 32
    BIN6 = 40
    BIN7 = 48
    BIN8 = 56
    BIN9 = 64


    def __init__(self,dmig_file, model_bdf):
        self.dmig_file = dmig_file
        self.model = BDF()
        self.model.read_bdf(model_bdf,xref=True)
        self.node_dof_list = []
        self.nodal_displacements=[]
        self.elemental_strain=[]

    # Generating the mass, stiffness, and loads matrices from the DMIG
    def getDmigVariables(self):
        node_dof_list=[]
        file = open(self.dmig_file, "r")  # type: TextIO

        # Forming the stiffness matrix.
        # This code goes the the KAAX section in the DMIG and formulates the stiffness matrix
        line_1 = file.readline()
        matrix_size = int(line_1[self.BIN9:])
        s = (matrix_size,matrix_size)
        stiffness_matrix = np.zeros(s)
        current_line = file.readline()
        line_type_indicator = current_line[self.BIN2:self.BIN3]
        while line_type_indicator != "MAAX    ":
            if line_type_indicator == "KAAX    ":
                node = int(current_line[self.BIN5:self.BIN6])
                dof = int(current_line[self.BIN7:self.BIN8])
                node_dof = (node,dof)
                node_dof_list.append(node_dof)
                if 'row' in locals():
                    row = row+1
                else:
                    row = 0
            else:
                # finding the position of the stiffness matrix position using the node_dof and column
                node = int(current_line[self.BIN3:self.BIN4])
                dof = int(current_line[self.BIN5:self.BIN6])
                current_stiffness = float(current_line[self.BIN6:self.BIN8])
                current_node_dof = (node,dof)
                col = node_dof_list.index(current_node_dof)
                stiffness_matrix[row,col] = current_stiffness
                try:
                    stiffness_matrix[col,row] = current_stiffness
                except:
                    continue
            current_line = file.readline()
            line_type_indicator = current_line[self.BIN2:self.BIN3]

        # Forming the mass matrix
        # This code goes the the MAAX section in the DMIG and formulates the mass matrix
        matrix_size = int(current_line[self.BIN9:])
        s = (matrix_size,matrix_size)
        mass_matrix = np.zeros(s)
        current_line = file.readline()
        while line_type_indicator != "PAX     ":
            if line_type_indicator == "MAAX    ":
                node_row = int(current_line[self.BIN5:self.BIN6])
                dof_row = int(current_line[self.BIN7:self.BIN8])
            else:
                # finding the position of the mass matrix position using the node_dof and column
                node_col = int(current_line[self.BIN3:self.BIN4])
                dof_col = int(current_line[self.BIN5:self.BIN6])
                current_mass = float(current_line[self.BIN6:self.BIN8])
                current_node_dof_row = (node_row, dof_row)
                current_node_dof_col = (node_col, dof_col)
                row = node_dof_list.index(current_node_dof_row)
                col = node_dof_list.index(current_node_dof_col)
                mass_matrix[row, col] = current_mass
            current_line = file.readline()
            line_type_indicator = current_line[self.BIN2:self.BIN3]

        # Forming the load vector
        # This code goes the the PAX section in the DMIG and formulates the load vector
        vector_size = len(node_dof_list)
        s=(vector_size,1)
        load_vector = np.zeros(s)
        current_line = file.readline()
        current_line = file.readline()
        while line_type_indicator != "TUG1    ":
            node_row = int(current_line[self.BIN3:self.BIN4])
            dof_row = int(current_line[self.BIN5:self.BIN6])
            current_load = float(current_line[self.BIN6:self.BIN8])
            current_node_dof_row = (node_row, dof_row)
            row = node_dof_list.index(current_node_dof_row)
            load_vector[row] = current_load
            current_line = file.readline()
            line_type_indicator = current_line[self.BIN2:self.BIN3]
            self.node_dof_list = node_dof_list
        return [mass_matrix,stiffness_matrix,load_vector]

    # Getting the nodal displacements given the force and stiffness matrix
    def getNodalDisplacements(self,K,F):
        nodal_displacements = np.linalg.solve(K,F)
        self.nodal_displacements = nodal_displacements
        return nodal_displacements

    def getElementStrain(self, nodal_displacements):
        element_strain_list=[]
        all_nodes = solver.model.nodes
        for eid, element in sorted(solver.model.elements.items()):
            solver.model.elements
            if element.type=="CQUAD4":
                # Getting the original global coordinates of the 4 nodes that correspond to this element
                element_nodes = element.nodes
                node_1_id = element_nodes[3]
                node_1_pos_o = all_nodes.get(node_1_id).get_position()
                node_2_id = element_nodes[2]
                node_2_pos_o = all_nodes.get(node_2_id).get_position()
                node_3_id = element_nodes[1]
                node_3_pos_o = all_nodes.get(node_3_id).get_position()
                node_4_id = element_nodes[0]
                node_4_pos_o = all_nodes.get(node_4_id).get_position()
                # Getting the new global coordinates of the 4 nodes that correspond to the DEFORMED element
                # by adding the displacements of the deformed nodes to the original nodes
                try:
                    node_1_T1_index = self.node_dof_list.index((node_1_id,1))
                    node_1_T2_index = self.node_dof_list.index((node_1_id,2))
                    node_1_T3_index = self.node_dof_list.index((node_1_id, 3))

                    node_1_T1 = self.nodal_displacements[node_1_T1_index]
                    node_1_T2 = self.nodal_displacements[node_1_T2_index]
                    node_1_T3 = self.nodal_displacements[node_1_T3_index]

                    node_1_pos_n = [node_1_pos_o[0]+node_1_T1, node_1_pos_o[1]+node_1_T2, node_1_pos_o[2]+node_1_T3]
                except:
                    node_1_pos_n = node_1_pos_o
                # Not all of the coordinates are in the stiffness matrix sense we are given the symmetric matrix,
                # therefore i am using a try catch to set the new coordinates equal to the old coordinates if they were
                # not transformed in the stiffness matrix
                try:
                    node_2_T1_index = self.node_dof_list.index((node_2_id,1))
                    node_2_T2_index = self.node_dof_list.index((node_2_id,2))
                    node_2_T3_index = self.node_dof_list.index((node_2_id, 3))

                    node_2_T1 = self.nodal_displacements[node_2_T1_index]
                    node_2_T2 = self.nodal_displacements[node_2_T2_index]
                    node_2_T3 = self.nodal_displacements[node_2_T3_index]

                    node_2_pos_n = [node_2_pos_o[0] + node_2_T1, node_2_pos_o[1] + node_2_T2, node_2_pos_o[2] + node_2_T3]
                except:
                    node_2_pos_n = node_2_pos_o
                try:
                    node_3_T1_index = self.node_dof_list.index((node_3_id,1))
                    node_3_T2_index = self.node_dof_list.index((node_3_id,2))
                    node_3_T3_index = self.node_dof_list.index((node_3_id, 3))

                    node_3_T1 = self.nodal_displacements[node_3_T1_index]
                    node_3_T2 = self.nodal_displacements[node_3_T2_index]
                    node_3_T3 = self.nodal_displacements[node_3_T3_index]

                    node_3_pos_n = [node_3_pos_o[0] + node_3_T1, node_3_pos_o[1] + node_3_T2, node_3_pos_o[2] + node_3_T3]
                except:
                    node_3_pos_n = node_3_pos_o
                try:
                    node_4_T1_index = self.node_dof_list.index((node_4_id,1))
                    node_4_T2_index = self.node_dof_list.index((node_4_id,2))
                    node_4_T3_index = self.node_dof_list.index((node_4_id, 3))

                    node_4_T1 = self.nodal_displacements[node_4_T1_index]
                    node_4_T2 = self.nodal_displacements[node_4_T2_index]
                    node_4_T3 = self.nodal_displacements[node_4_T3_index]

                    node_4_pos_n = [node_4_pos_o[0] + node_4_T1, node_4_pos_o[1] + node_4_T2, node_4_pos_o[2] + node_4_T3]
                except:
                    node_4_pos_n = node_4_pos_o

                # After getting the old and transformed nodes for each element in the global coordinate system, we need
                #     to transform the information into the elemental coordinate system I THINK THIS FUNCTION WILL NOT WORK FOR A NOT PERFECTLY SQUARE ELEMENT!!!!
                H = self.getHomogenousMatrix(node_1_pos_o, node_2_pos_o,node_4_pos_o)

                node_1_pos_o = np.append(node_1_pos_o,[1])
                node_1_transposed_o = np.transpose(node_1_pos_o)
                n1_to = np.matmul(H,node_1_transposed_o)


                node_1_pos_n = np.append(node_1_pos_n,[1])
                node_1_transposed_n = np.transpose(node_1_pos_n)
                n1_tn = np.matmul(H,node_1_transposed_n)

                node_2_pos_o = np.append(node_2_pos_o, [1])
                node_2_transposed_o = np.transpose(node_2_pos_o)
                n2_to = np.matmul(H, node_2_transposed_o)

                node_2_pos_n = np.append(node_2_pos_n, [1])
                node_2_transposed_n = np.transpose(node_2_pos_n)
                n2_tn = np.matmul(H, node_2_transposed_n)

                node_3_pos_o = np.append(node_3_pos_o, [1])
                node_3_transposed_o = np.transpose(node_3_pos_o)
                n3_to = np.matmul(H, node_3_transposed_o)

                node_3_pos_n = np.append(node_3_pos_n, [1])
                node_3_transposed_n = np.transpose(node_3_pos_n)
                n3_tn = np.matmul(H, node_3_transposed_n)

                node_4_pos_o = np.append(node_4_pos_o, [1])
                node_4_transposed_o = np.transpose(node_4_pos_o)
                n4_to = np.matmul(H, node_4_transposed_o)

                node_4_pos_n = np.append(node_4_pos_n, [1])
                node_4_transposed_n = np.transpose(node_4_pos_n)
                n4_tn = np.matmul(H, node_4_transposed_n)


                # Defining the old nodes variables used in the shape function (i.e. the global node locations before displacement)
                x1_o, x2_o, x3_o, x4_o, y1_o, y2_o, y3_o, y4_o = symbols('x1_o x2_o x3_o x4_o y1_o y2_o y3_o y4_o', real=True)
                # Defining the new node variables used in the shape function (i.e. the golbal node locations after displacement)
                x1_n, x2_n, x3_n, x4_n, y1_n, y2_n, y3_n, y4_n = symbols('x1_n x2_n x3_n x4_n y1_n y2_n y3_n y4_n', real=True)
                x, y = symbols('x y', real=True)
                # Defining the shape functions
                a = (x1_o-x2_o)/2
                b = (y1_o-y4_o)/2
                N1 = 1/(4*a*b)*(x-x2_o)*(y-y4_o)
                N2 =-1/(4*a*b)*(x-x1_o)*(y-y3_o)
                N3 = 1/(4*a*b)*(x-x4_o)*(y-y2_o)
                N4 =-1/(4*a*b)*(x-x3_o)*(y-y1_o)



                # Taking the derivative of the shape functions
                N1_dx = diff(N1,x)
                N1_dy = diff(N1,y)
                N2_dx = diff(N2,x)
                N2_dy = diff(N2,y)
                N3_dx = diff(N3,x)
                N3_dy = diff(N3,y)
                N4_dx = diff(N4,x)
                N4_dy = diff(N4,y)

                # Forming the strain-displacement matrix
                B = Matrix([[N1_dx, 0, N2_dx, 0, N3_dx, 0, N4_dx, 0],[ 0, N1_dy, 0, N2_dy, 0, N3_dy, 0, N4_dy],[ N1_dy, N1_dx, N2_dy, N2_dx, N3_dy, N3_dx, N4_dy, N4_dx]])
                B = B.subs({x1_o:n1_to[0,0], x2_o:n2_to[0,0], x3_o:n3_to[0,0], x4_o:n4_to[0,0], y1_o:n1_to[0,1], y2_o:n2_to[0,1], y3_o:n3_to[0,1], y4_o:n4_to[0,1]})

                # Solving for the strain at the center of the element
                a = a.subs(
                    {x1_o: n1_to[0, 0], x2_o: n2_to[0, 0], x3_o: n3_to[0, 0], x4_o: n4_to[0, 0], y1_o: n1_to[0, 1],
                     y2_o: n2_to[0, 1], y3_o: n3_to[0, 1], y4_o: n4_to[0, 1]})
                b = b.subs(
                    {x1_o: n1_to[0, 0], x2_o: n2_to[0, 0], x3_o: n3_to[0, 0], x4_o: n4_to[0, 0], y1_o: n1_to[0, 1],
                     y2_o: n2_to[0, 1], y3_o: n3_to[0, 1], y4_o: n4_to[0, 1]})
                B = B.subs({x: -a, y:-b})
                B = np.matrix(B)
                # Finding the nodal displacements in the elemental coordinate system for each node in the element
                print(n1_to)
                print(n1_tn)
                T1 = (n1_tn-n1_to)
                u1 = T1[0,0]
                v1 = T1[0,1]
                T2 = (n2_tn-n2_to)
                u2 = T2[0,0]
                v2 = T2[0,1]
                T3 = (n3_tn-n3_to)
                u3 = T3[0,0]
                v3 = T3[0,1]
                T4 = (n4_tn-n4_to)
                u4 = T4[0,0]
                v4 = T4[0,1]
                current_nodal_displacements = np.matrix([u1,v1,u2,v2,u3,v3,u4,v4])
                current_nodal_displacements = current_nodal_displacements.astype(float)
                current_nodal_displacements = np.transpose(current_nodal_displacements)
                B = B.astype(float)
                elemental_strain = B*current_nodal_displacements
                # elemental_strain = np.matmul(B,current_nodal_displacements)
                Ex = elemental_strain[0,0]
                sigma_x = 29100000*Ex
                Ey = elemental_strain[1,0]
                G = elemental_strain[2,0]
                print(eid)
                print(elemental_strain)
                element_strain_list.append(elemental_strain)


        self.elemental_strain = element_strain_list
        return element_strain_list

    def getHomogenousMatrix(self,node_1, node_2, node_3):
        uv_1 = node_2 - node_1
        uv_1_mag = np.linalg.norm(uv_1)
        UV_1 = uv_1 / uv_1_mag

        uv_2 = node_3 - node_1
        uv_2_mag = np.linalg.norm(uv_2)
        UV_2 = uv_2 / uv_2_mag

        UV_3 = np.cross(uv_1, uv_2)

        T = np.matrix([[UV_1[0], UV_2[0], UV_3[0], node_1[0]], [UV_1[1], UV_2[1], UV_3[1], node_1[1]],
                       [UV_1[2], UV_2[2], UV_3[2], node_1[2]], [0, 0, 0, 1]])

        H = np.linalg.inv(T)
        return H




    def getBin(self,line,bin_number):
        start = bin_number*8
        end = start+9
        info = line[start:end]
        return info

from sol_101 import *
solver = SOL_101('./1_Element/DMIG.pch','./1_Element/1.bdf')
[M,K,F] = solver.getDmigVariables()
nodal_displacements = solver.getNodalDisplacements(K,F)
elemental_strain = solver.getElementStrain(nodal_displacements)
print("placeholder")