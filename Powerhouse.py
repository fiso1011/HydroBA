import pandas as pd
import numpy as np
import Raw_Material as c_rm
import data_input as c_di

class Powerhouse:
    def __init__(self,powerhouse_data,powerhouse_material):
        self.powerhouse_data=powerhouse_data
        self.powerhouse_material=powerhouse_material
        self.total_powerhouse_cost
        #import relevant Dicts
        c_di.data_storage.readingFunc()
        self.site_data = c_di.data_storage.readingFunc.inputdata.input_dict["site_data"]["dict"]
        self.penstock_data = c_di.data_storage.readingFunc.inputdata.input_dict["penstock_data"]["dict"]
        self.labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]
        self.labour_time = c_di.data_storage.readingFunc.inputdata.input_dict["labour_time"]["dict"]
        self.raw_material = c_di.data_storage.readingFunc.inputdata.input_dict["raw_material"]["dict"]
        # Dict to store Dimensions
        self.powerhouse_dimensions= {}
        self.help1={} #help to store different volume for brick and concrete parts
        self.help2={} #help to store different volume for brick and concrete parts
        #Dict to store the Material cost, the labour cost miscellaneous
        self.powerhouse_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_powerhouse_cost(self):
        self.calculate_powerhouse_dimensions()
        self.calculate_powerhouse_material()
        self.calculate_powerhouse_labour()
        self.total_powerhouse_cost=sum(self.powerhouse_cost.values())
    def calculate_powerhouse_dimensions(self):
        exc_1=((5+2)*10**2)*np.tan(np.deg2rad(self.penstock_data["height drop"]/self.penstock_data["penstock length"]))*0.5 #slope excavation
        exc_2=5*10*(0.5+0.1)+(1.5+2*self.powerhouse_data["wall_width"])*1.5*5 #Foundation and Channel under powerhouse
        foundation_vol=5*10*0.5
        wall_vol=(2*(5+8)*2.5+(1.5*5*2+(1.5**2)))*self.powerhouse_data["wall_width"]
        gravel_sqm=5*10
        self.powerhouse_dimensions["excavation_vol"] = exc_1+exc_2
        self.powerhouse_dimensions["structure_vol"] = foundation_vol+wall_vol
        self.powerhouse_dimensions["gravel_sqm"]=gravel_sqm
        self.help1["structure_vol"]=foundation_vol
        self.help2["structure_vol"]=wall_vol

    def calculate_powerhouse_material(self):
        powerhouse_rcc =c_rm.Raw_Material(self.help1)
        raw_mat_price1=powerhouse_rcc.calculate_rcc()
        powerhouse_mas = c_rm.Raw_Material(self.help2)
        raw_mat_price2 = powerhouse_mas.calculate_masonry()
        raw_mat_price=raw_mat_price1+raw_mat_price2

        self.powerhouse_cost["raw material"] = raw_mat_price
        gravel=self.powerhouse_dimensions["gravel_sqm"]*0.1*self.raw_material["gravel"]

        #tailrace pipe
        if self.powerhouse_material["structural_material"] == "PVC":
            pipe_cost=(self.powerhouse_data["tailrace drop"]/10)*50+self.powerhouse_data["di_tailrace"]*50 #to be changed later, only pipe
            joint_cost=(self.powerhouse_data["tailrace length"]/10)*self.powerhouse_data["di_tailrace"]*50 #to be changed later
            bolts_cost=(pipe_cost+joint_cost)*0.1
        elif self.powerhouse_material["structural_material"] == "HDPE":
            pipe_cost = (self.penstock_data["tailrace drop"] / 10) * 50 + self.powerhouse_data["di_tailrace"] * 50  # to be changed later, only pipe
            joint_cost = (self.penstock_data["tailrace length"] / 10) * self.powerhouse_data["di_tailrace"] * 50  # to be changed later
            bolts_cost = (pipe_cost + joint_cost) * 0.1
        tailrace_total_cost=pipe_cost+joint_cost+bolts_cost

        #Turbine price
        if self.powerhouse_material["turbine_type"]=="FR":
            turbine_cost=(self.penstock_data["height drop"])*50+self.site_data["power"]*50 #to be edited later
        elif self.powerhouse_material["turbine_type"]=="PE":
            turbine_cost = (self.penstock_data["height drop"]) * 50 + self.site_data["power"] * 50  # to be edited later
        elif self.powerhouse_material["turbine_type"]=="CR":
            turbine_cost = (self.penstock_data["height drop"]) * 50 + self.site_data["power"] * 50  # to be edited later

        load_regulator=self.powerhouse_material["load_regulator"]*(self.site_data["power"]/10)
        lightning_protection=self.powerhouse_material["lightning protection"]
        electrics_equipment=self.powerhouse_material["electrics material"]*self.site_data["power"] # to be edited later

        self.powerhouse_cost["material"]= gravel+tailrace_total_cost+turbine_cost+load_regulator+lightning_protection+electrics_equipment

    def calculate_powerhouse_labour(self):
        self.powerhouse_cost["excavation labour"] = (self.powerhouse_dimensions["excavation_vol"] * (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.powerhouse_cost["laying"] = (self.powerhouse_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel

        concreting_labour = (self.help1["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
        masonry_labour=(self.help2["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
        building_installation=50 # to be edited later roof, lightning protection
        tailrace_installation=50 # to be edited later
        turbine_installation=50 # to be edited later
        electrical_installation=50 # to be edited later switch cabinet and load control
        self.powerhouse_cost["structure labour"] = concreting_labour+masonry_labour
        self.powerhouse_cost["installation labour"] =building_installation+tailrace_installation+turbine_installation+electrical_installation
