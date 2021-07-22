import numpy as np
import RawMaterial as c_rm

class Penstock:
    def __init__(self,input_data):
        self.penstock_data=input_data.input_dict["penstock_data"]["dict"]
        self.penstock_material=input_data.input_dict["penstock_material"]["dict"]
        self.channel_material=input_data.input_dict["channel_material"]["dict"]
        self.total_penstock_cost

        #import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material = input_data.input_dict["raw_material"]["dict"]
        self.constants = input_data.input_dict["constants"]["dict"]
        self.powerhouse_data=input_data.input_dict["powerhouse_data"]["dict"]

        # Dict to store Dimensions
        self.penstock_dimensions= {}
        self.penstock_storage = {}

        #Dict to store the Material cost, the labour cost miscellaneous
        self.penstock_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_penstock_cost(self):
        self.calculate_penstock_dimensions()
        self.calculate_penstock_material()
        self.calculate_penstock_labour()
        self.total_penstock_cost=sum(self.penstock_cost.values())


    def calculate_penstock_dimensions(self):
        v_penstock=self.penstock_data["velocity"]
        di_penstock=((4*(self.site_data["used_flow"])/v_penstock)/np.pi)**(0.5)
        degree=np.deg2rad(self.penstock_data["cs_degree"])
        di_spillway=((self.site_data["used_flow"]/(111*((self.penstock_data["height drop"]/\
        self.penstock_data["penstock length"])**0.5)*(np.pi-0.5*(degree-np.sin(degree)))*(((np.pi-0.5*(degree-np.sin(degree)))/\
        ((2*np.pi-degree)))**(2/3))))**(1/2.66))*2
        #self.penstock_data["di_spillway"] #have to run macro in Excel before running
        v_anker=np.pi*((di_penstock/4)**2)*4*di_penstock*\
                ((self.penstock_data["penstock length"])/self.penstock_data["joint distance"]) #quarter diameter, 4 times lenght of diameter
        v_pressureblock=8 #to be changed later, minus diameter of penstock inside plus gravel
        v_tailrace_basin=3

        excavation_vol=(di_penstock**2)*2*self.penstock_data["penstock length"]+v_anker+0.5*v_pressureblock # 1d deep, 2d width + gravel
        gravel_sqm=2*di_penstock*self.penstock_data["penstock length"]+4 #to be edited later when v_pressureblock is available

        self.penstock_dimensions["excavation_vol"] = excavation_vol
        self.penstock_dimensions["structure_vol"] = v_anker+v_pressureblock+v_tailrace_basin
        self.penstock_dimensions["gravel_sqm"]=gravel_sqm
        self.penstock_dimensions["contact_sqm"]=8 #to be edited later when v_pressureblock is available

        self.penstock_storage["pipe volume"]=(np.pi*((di_penstock/2)**2)+np.pi*((di_spillway/2)**2))*self.penstock_data["penstock length"]
        self.penstock_storage["di_spillway"]=di_spillway

    def calculate_penstock_material(self):
        di_penstock=(((4 * (self.site_data["used_flow"]) / self.penstock_data["velocity"]) / np.pi) ** (0.5))
        penstock_rcc =c_rm.Raw_Material(self.penstock_dimensions,self.raw_material,self.constants)
        raw_mat_price=penstock_rcc.calculate_rcc()
        self.penstock_cost["raw material"] = raw_mat_price

        gravel=self.penstock_dimensions["gravel_sqm"]*self.raw_material["gravel_thickness"]*self.raw_material["gravel"]
        vlies=self.penstock_dimensions["gravel_sqm"]*self.channel_material["drainage vlies"]

        #calculate pipe cost for both penstock and spillway pipe
        if self.penstock_material["penstock material"] == "PVC":
            pipe1_cost= 0.00005*((self.penstock_data["height drop"]*1.5)*self.constants["bar_meter"]) * \
                        np.power((di_penstock*1000),1.98)*(self.penstock_data["penstock length"]+self.powerhouse_data["tailrace length"])# only pipe
            joint1_cost=0.0045*np.power((di_penstock*1000),1.98)*((self.penstock_data["penstock length"]+self.powerhouse_data["tailrace length"])/self.penstock_data["joint distance"])
            bolts1_cost=(pipe1_cost+joint1_cost)*0.05
            pipe2_cost = 0.00005*((self.penstock_data["height drop"]*1.5)*self.constants["bar_meter"])*\
                         np.power((self.penstock_storage["di_spillway"]*1000),1.98)*(self.penstock_data["penstock length"]+self.powerhouse_data["tailrace length"])
            joint2_cost = 0.0045*np.power((self.penstock_storage["di_spillway"]*1000),1.98)*\
                          ((self.penstock_data["penstock length"]+self.powerhouse_data["tailrace length"])/self.penstock_data["joint distance"])
            bolts2_cost = (pipe2_cost + joint2_cost) * 0.05
        elif self.penstock_material["penstock material"] == "HDPE":
            pipe1_cost = (0.00004*((self.penstock_data["height drop"]*1.5)*self.constants["bar_meter"])+0.00008)*\
                         np.power((di_penstock*1000),1.99)*(self.penstock_data["penstock length"]+self.powerhouse_data["tailrace length"])  # only pipe
            joint1_cost = 0.0018*np.power((di_penstock*1000),2.18)*(self.penstock_data["penstock length"]/self.penstock_data["joint distance"])
            bolts1_cost = (pipe1_cost + joint1_cost) * 0.05
            pipe2_cost = (0.00004*((self.penstock_data["height drop"]*1.5)*self.constants["bar_meter"])+0.00008)*\
                         np.power((self.penstock_storage["di_spillway"]*1000),1.99)*(self.penstock_data["penstock length"]+self.powerhouse_data["tailrace length"])
            joint2_cost = 0.0018*np.power((self.penstock_storage["di_spillway"]*1000),2.18)*\
                          (self.penstock_data["penstock length"]/self.penstock_data["joint distance"])
            bolts2_cost = (pipe2_cost + joint2_cost) * 0.05
        pipes_total_cost=pipe1_cost+pipe2_cost+joint1_cost+joint2_cost+bolts1_cost+bolts2_cost

        self.penstock_cost["material"]= gravel+vlies+pipes_total_cost
        self.penstock_storage["penstock pipe total"] = pipes_total_cost


    def calculate_penstock_labour(self):
        self.penstock_cost["excavation labour"] = (self.penstock_dimensions["excavation_vol"] *\
                                                   (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) *\
                                                  self.labour_cost["noskill_worker"]
        self.penstock_cost["laying"] = (self.penstock_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*\
                                       self.labour_cost["noskill_worker"]#gravel
        formwork_labour = self.penstock_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
        concreting_labour = (self.penstock_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
        hauling_cost = (((self.penstock_dimensions["structure_vol"] + self.penstock_dimensions["gravel_sqm"] *\
                          self.raw_material["surface_finish"]) * self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"]

        self.penstock_cost["structure labour"] = formwork_labour + concreting_labour+hauling_cost
        self.penstock_cost["installation labour"] = (self.penstock_data["penstock length"] / self.penstock_data["joint distance"])*\
                                                    8*(self.labour_cost["skill_worker"]+self.labour_cost["noskill_worker"]) #16 hours per 10m pipe

        self.penstock_storage["material"] = self.penstock_cost["raw material"] + self.penstock_cost["material"]
        self.penstock_storage["labour"] = self.penstock_cost["excavation labour"] + self.penstock_cost["structure labour"] +\
                                          self.penstock_cost["laying"] +self.penstock_cost["installation labour"]

