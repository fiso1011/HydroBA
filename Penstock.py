import pandas as pd
import numpy as np
import Raw_Material as c_rm
import data_input as c_di

class Penstock:
    def __init__(self,penstock_data,penstock_material):
        self.penstock_data=penstock_data
        self.penstock_material=penstock_material
        self.total_penstock_cost
        #import relevant Dicts
        c_di.data_storage.readingFunc()
        self.site_data = c_di.data_storage.readingFunc.inputdata.input_dict["site_data"]["dict"]
        self.labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]
        self.labour_time = c_di.data_storage.readingFunc.inputdata.input_dict["labour_time"]["dict"]
        self.raw_material = c_di.data_storage.readingFunc.inputdata.input_dict["raw_material"]["dict"]
        # Dict to store Dimensions
        self.penstock_dimensions= {}
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
        di_penstock=((4*(self.site_data["used flow"])/v_penstock)/np.pi)**(0.5)
        di_spillway=self.penstock_data["di_spillway"] #have to run macro in Excel before running
        v_anker=np.pi*((di_penstock/4)**2)*4*di_penstock*((self.penstock_data["penstock length"])/10) #viertel durchmesser, 4fache länge von Durchmesser
        v_pressureblock=8 #to be changed later, minus diameter of penstock inside plus gravel

        excavation_vol=di_spillway*2.2*self.penstock_data["penstock length"]+v_anker+0.5*v_pressureblock # 1d deep, 2d width + gravel
        gravel_sqm=2*di_penstock*self.penstock_data["penstock length"] #to be edited later when v_pressureblock is available

        self.penstock_dimensions["excavation_vol"] = excavation_vol
        self.penstock_dimensions["structure_vol"] = v_anker+v_pressureblock
        self.penstock_dimensions["gravel_sqm"]=gravel_sqm
        self.penstock_dimensions["contact_sqm"]=4 #to be edited later when v_pressureblock is available

    def calculate_penstock_material(self):
        diameter=(((4 * (self.site_data["used flow"]) / self.penstock_data["velocity"]) / np.pi) ** (0.5))
        penstock_rcc =c_rm.Raw_Material(self.penstock_dimensions)
        raw_mat_price=penstock_rcc.calculate_rcc()

        self.penstock_cost["raw material"] = raw_mat_price
        gravel=self.penstock_dimensions["gravel_sqm"]*0.1*self.raw_material["gravel"]
        mounting_bracket=self.penstock_material["mounting bracket"]*((self.penstock_data["penstock length"])/10)
        if self.penstock_material["structural_material"] == "PVC":
            pipe_cost=(self.penstock_data["height drop"]/10)*50+diameter*50 #to be changed later, only pipe
            joint_cost=(self.penstock_data["penstock length"]/10)*diameter*50 #to be changed later
            bolts_cost=(pipe_cost+joint_cost)*0.1
        elif self.penstock_material["structural_material"] == "HDPE":
            pipe_cost = (self.penstock_data["height drop"] / 10) * 50 + diameter * 50  # to be changed later, only pipe
            joint_cost = (self.penstock_data["penstock length"] / 10) * diameter * 50  # to be changed later
            bolts_cost = (pipe_cost + joint_cost) * 0.1
        pipe_total_cost=pipe_cost+joint_cost+bolts_cost
        self.penstock_cost["material"]= gravel+mounting_bracket+pipe_total_cost
        #HDPE und PVC vlt nur durch Faktor unterscheiden bei den Kosten??
    def calculate_penstock_labour(self):
        self.penstock_cost["excavation labour"] = (self.penstock_dimensions["excavation_vol"] * (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.penstock_cost["laying"] = (self.penstock_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel
        formwork_labour = self.penstock_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
        concreting_labour = (self.penstock_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
        self.penstock_cost["structure labour"] = formwork_labour + concreting_labour
        self.penstock_cost["installation labour"] = (self.penstock_data["penstock length"] / 10)*50 #change later
