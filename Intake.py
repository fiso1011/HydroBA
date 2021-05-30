import pandas as pd
import numpy as np
import Raw_Material as c_rm
import data_input as c_di

class Intake:
    def __init__(self,intake_data,intake_material):
        self.intake_data=intake_data
        self.intake_material=intake_material
        self.total_intake_cost
        #import relevant Dicts
        c_di.data_storage.readingFunc()
        self.site_data = c_di.data_storage.readingFunc.inputdata.input_dict["site_data"]["dict"]
        self.labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]
        self.labour_time = c_di.data_storage.readingFunc.inputdata.input_dict["labour_time"]["dict"]
        # Dict to store Dimensions
        self.intake_dimensions= {}
        #Dict to store the Material cost, the labour cost miscellaneous
        self.intake_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_intake_cost(self):
        self.calculate_intake_dimensions()
        self.calculate_intake_material()
        self.calculate_intake_labour()
        self.total_intake_cost=sum(self.intake_cost.values())
    def calculate_intake_dimensions(self):
        q_worst=self.site_data["maximum_flow"]*20   #Assumption in Micro Hydro Design manual
        weir_over_height = ((1/((2/3)*np.sqrt(2*9.81)))*q_worst)/(self.intake_data ['weir coefficient']*self.intake_data["river length"])       #weir formula of Poleni

        wall_vol=(self.intake_data['weir height']+weir_over_height)*self.intake_data['river length']*self.intake_data['wall thickness']
        weir_vol=np.square(self.intake_data['weir height'])*(0.25+0.25/2)*self.intake_data['river length']
        foundation_vol=(self.intake_data['weir height']+self.intake_data['wall thickness'])*(self.intake_data['foundation thickness']*self.intake_data['river length'])
        intake_vol=wall_vol+weir_vol
        contact_sqm=((self.intake_data['weir height']+weir_over_height)+self.intake_data['weir height'])*self.intake_data['river length']*2

        self.intake_dimensions["intake_vol"] = intake_vol
        self.intake_dimensions["foundation_vol"]= foundation_vol
        self.intake_dimensions["structure_vol"]=intake_vol+foundation_vol
        self.intake_dimensions["contact_sqm"]=contact_sqm


    def calculate_intake_material(self):
        if self.intake_material["structural_material"]=="RCC":
            intake_rcc =c_rm.Raw_Material(self.intake_dimensions)
            raw_mat_price=intake_rcc.calculate_rcc()
        elif self.intake_material["structural_material"]=="MAS":
            intake_mas=c_rm.Raw_Material(self.intake_dimensions)
            raw_mat_price=intake_mas.calculate_masonry()
        self.intake_cost["raw material"] = raw_mat_price
        self.intake_cost["material"]=self.intake_material["coarse rake"]+self.intake_material["sluice gate"]

    def calculate_intake_labour(self):
        self.intake_cost["excavation labour"] = self.intake_dimensions["foundation_vol"] * (1.1123*np.exp(0.4774*self.site_data["excavating_factor"])) * self.labour_cost["noskill_worker"]
        if self.intake_material["structural_material"] =="RCC":
            formwork_labour=self.intake_dimensions["contact_sqm"]*self.labour_time["formwork"]*self.labour_cost["skill_worker"]
            concreting_labour= (self.intake_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
            self.intake_cost["structure labour"] = formwork_labour+concreting_labour
        elif self.intake_material["structural_material"] =="MAS":
            surface_labour=self.intake_dimensions["contact_sqm"]*self.labour_time["plastering"]*self.labour_cost["skill_worker"]
            mas_labour=(self.intake_dimensions["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
            self.intake_cost["structure labour"] = surface_labour+mas_labour

