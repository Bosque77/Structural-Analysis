import numpy as np

class Material:
    def __init__(self):
        self.name = "empty_material"
        self.mid = 9999
        self.E = 9000000
        self.v = 0.33
        self.G = 999999
        self.rho = 0.098
        self.tref = 70

class Property:
    def __init__(self):
        self.name = "empty_property"
        self.mid = 9999
        self.pid = 99999
        self.A = 0.0
        self.I1 = 0.0
        self.I2 = 0.0
        self.J = 0.0
        self.C = 0.0
        self.shear_area_ratio = 0.0

class Element:
    def __init__(self):
        self.eid = 9999
        self.property = Property
        self.material = Material
        self.beam_loads_data=[]
        self.load_case_data = []
        self.sorted_loads = []

    def addBeamLoads(self,op2_name,case_id, load_vector,freq=None, maintain_directional_dependance = None):
        if freq is not None:
            rounded_freq = str(round(freq,2))
            unique_id = op2_name+"_case_"+str(case_id)+"_freq_"+rounded_freq
        else:
            unique_id = op2_name + "_case_" + str(case_id)

        beam_loads = self.getBeamLoads(op2_name,case_id,freq)
        beam_side = load_vector[0]

        if freq is not None:  # Frequency based loads will be complex and therefore need separate computation
            beam_side = np.abs(beam_side)
            if maintain_directional_dependance=="Yes":
                if beam_loads is not None:
                    if beam_side == 0:
                        beam_loads.M1A = np.abs(load_vector[1])*np.cos(np.angle(load_vector[1]))
                        beam_loads.M2A = np.abs(load_vector[2])*np.cos(np.angle(load_vector[2]))
                        beam_loads.V1 = np.abs(load_vector[3])*np.cos(np.angle(load_vector[3]))
                        beam_loads.V2 = np.abs(load_vector[4])*np.cos(np.angle(load_vector[4]))
                        beam_loads.P = np.abs(load_vector[5])*np.cos(np.angle(load_vector[5]))
                        beam_loads.T = np.abs(load_vector[6])*np.cos(np.angle(load_vector[6]))
                    elif beam_side == 1:
                        beam_loads.M1B = np.abs(load_vector[1])*np.cos(np.angle(load_vector[1]))
                        beam_loads.M2B = np.abs(load_vector[2])*np.cos(np.angle(load_vector[2]))
                        beam_loads.V1 = np.abs(load_vector[3])*np.cos(np.angle(load_vector[3]))
                        beam_loads.V2 = np.abs(load_vector[4])*np.cos(np.angle(load_vector[4]))
                        beam_loads.P = np.abs(load_vector[5])*np.cos(np.angle(load_vector[5]))
                        beam_loads.T = np.abs(load_vector[6])*np.cos(np.angle(load_vector[6]))
                else:
                    beam_loads = BeamLoads()
                    beam_loads.op2_name = op2_name
                    beam_loads.case_id = case_id
                    beam_loads.freq = rounded_freq
                    beam_loads.unique_id = unique_id
                    if beam_side == 0:
                        beam_loads.M1A = np.abs(load_vector[1])*np.cos(np.angle(load_vector[1]))
                        beam_loads.M2A = np.abs(load_vector[2])*np.cos(np.angle(load_vector[2]))
                        beam_loads.V1 = np.abs(load_vector[3])*np.cos(np.angle(load_vector[3]))
                        beam_loads.V2 = np.abs(load_vector[4])*np.cos(np.angle(load_vector[4]))
                        beam_loads.P = np.abs(load_vector[5])*np.cos(np.angle(load_vector[5]))
                        beam_loads.T = np.abs(load_vector[6])*np.cos(np.angle(load_vector[6]))
                    elif beam_side == 1:
                        beam_loads.M1B = np.abs(load_vector[1])*np.cos(np.angle(load_vector[1]))
                        beam_loads.M2B = np.abs(load_vector[2])*np.cos(np.angle(load_vector[2]))
                        beam_loads.V1 = np.abs(load_vector[3])*np.cos(np.angle(load_vector[3]))
                        beam_loads.V2 = np.abs(load_vector[4])*np.cos(np.angle(load_vector[4]))
                        beam_loads.P = np.abs(load_vector[5])*np.cos(np.angle(load_vector[5]))
                        beam_loads.T = np.abs(load_vector[6])*np.cos(np.angle(load_vector[6]))
                    self.beam_loads_data.append(beam_loads)
            else:
                if beam_loads is not None:
                    if beam_side == 0:
                        beam_loads.M1A = np.abs(load_vector[1])
                        beam_loads.M2A = np.abs(load_vector[2])
                        beam_loads.V1 = np.abs(load_vector[3])
                        beam_loads.V2 = np.abs(load_vector[4])
                        beam_loads.P = np.abs(load_vector[5])
                        beam_loads.T = np.abs(load_vector[6])
                    elif beam_side == 1:
                        beam_loads.M1B = np.abs(load_vector[1])
                        beam_loads.M2B = np.abs(load_vector[2])
                        beam_loads.V1 = np.abs(load_vector[3])
                        beam_loads.V2 = np.abs(load_vector[4])
                        beam_loads.P = np.abs(load_vector[5])
                        beam_loads.T = np.abs(load_vector[6])
                else:
                    beam_loads = BeamLoads()
                    beam_loads.op2_name = op2_name
                    beam_loads.case_id = case_id
                    beam_loads.unique_id = unique_id
                    beam_loads.freq = rounded_freq
                    if beam_side == 0:
                        beam_loads.M1A = np.abs(load_vector[1])
                        beam_loads.M2A = np.abs(load_vector[2])
                        beam_loads.V1 = np.abs(load_vector[3])
                        beam_loads.V2 = np.abs(load_vector[4])
                        beam_loads.P = np.abs(load_vector[5])
                        beam_loads.T = np.abs(load_vector[6])
                    elif beam_side == 1:
                        beam_loads.M1B = np.abs(load_vector[1])
                        beam_loads.M2B = np.abs(load_vector[2])
                        beam_loads.V1 = np.abs(load_vector[3])
                        beam_loads.V2 = np.abs(load_vector[4])
                        beam_loads.P = np.abs(load_vector[5])
                        beam_loads.T = np.abs(load_vector[6])
                    self.beam_loads_data.append(beam_loads)

        else:  #There is no frequency data
            if beam_loads is not None:
                if beam_side ==0:
                    beam_loads.M1A = load_vector[1]
                    beam_loads.M2A = load_vector[2]
                    beam_loads.V1 = load_vector[3]
                    beam_loads.V2 = load_vector[4]
                    beam_loads.P = load_vector[5]
                    beam_loads.T = load_vector[6]
                elif beam_side ==1:
                    beam_loads.M1B = load_vector[1]
                    beam_loads.M2B = load_vector[2]
                    beam_loads.V1 = load_vector[3]
                    beam_loads.V2 = load_vector[4]
                    beam_loads.P = load_vector[5]
                    beam_loads.T = load_vector[6]
            else:
                beam_loads = BeamLoads()
                beam_loads.op2_name = op2_name
                beam_loads.case_id = case_id
                beam_loads.freq = "None"
                beam_loads.unique_id = unique_id
                if beam_side == 0:
                    beam_loads.M1A = load_vector[1]
                    beam_loads.M2A = load_vector[2]
                    beam_loads.V1 = load_vector[3]
                    beam_loads.V2 = load_vector[4]
                    beam_loads.P = load_vector[5]
                    beam_loads.T = load_vector[6]
                elif beam_side == 1:
                    beam_loads.M1B = load_vector[1]
                    beam_loads.M2B = load_vector[2]
                    beam_loads.V1 = load_vector[3]
                    beam_loads.V2 = load_vector[4]
                    beam_loads.P = load_vector[5]
                    beam_loads.T = load_vector[6]
                self.beam_loads_data.append(beam_loads)

    def addLoadCase(self,load_case_name,load_vector):
        load_case = BeamLoads()
        load_case.unique_id = load_case_name
        load_case.P = load_vector['P']
        load_case.V1 = load_vector['V1']
        load_case.V2 = load_vector['V2']
        load_case.T = load_vector['T']
        load_case.M2A = load_vector['M2A']
        load_case.M1A = load_vector['M1A']
        load_case.M2B = load_vector['M2B']
        load_case.M1B = load_vector['M1B']
        self.load_case_data.append(load_case)

    def getBeamLoads(self,op2_name,case_id,freq=None):
        if freq is not None:
            rounded_freq = str(round(freq,2))
            unique_id = op2_name+"_case_"+str(case_id)+"_freq_"+rounded_freq
        else:
            unique_id = op2_name + "_case_" + str(case_id)
        for beam_loads in self.beam_loads_data:
            if unique_id == beam_loads.unique_id:
                return beam_loads
        return None




class BeamLoads:
    def __init__(self):
        self.op2_name = "XXXXXX"
        self.case_id = 9999
        self.unique_id = 999
        self.freq = 'None'
        self.P = 999
        self.V1 = 999
        self.V2 = 999
        self.T = 999
        self.M2A = 999
        self.M1A = 999
        self.M2B = 999
        self.M1B = 999


