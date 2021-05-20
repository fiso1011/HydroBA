import pandas as pd
import numpy as np
import Raw_Material as c_rm
import data_input as c_di

class Intake:
    def __init__(self,intake_data,intake_material)
        self.intake_data=intake_data
        self.intake_material=intake_material
        self.total_intake_cost=sum(self.intake_cost.values())
        #import relevant Dicts
        c_di.data_storage.readingFunc()
        self.site_data = c_di.data_storage.readingFunc.inputdata.input_dict["hydro_data"]["dict"]
        self.labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]
        self.labour_time = c_di.data_storage.readingFunc.inputdata.input_dict["labour_time"]["dict"]
        # Dict to store Dimensions
        self.intake_dimensions= {}
        #Dict to store the Material cost, the labour cost miscellaneous
        self.intake_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_intake_cost(self):
        calculate_intake_dimensions()
        calculate_intake_material()
        calculate_intake_labour()

    def calculate_intake_dimensions(self):
        q_worst=self.site_data["maximum flow"]*20                                                                         #Assumption in Micro Hydro Design manual
        weir_over_height = ((1/((2/3)*np.sqrt(2*9.81)))*q_worst)/(intake_data ['weir coefficient']*river_length)                 #weir formula of Poleni
        wall_height=self.weir_height+weir_over_height

        wall_vol=(intake_data['weir height']+weir_over_height)*intake_data['river length']*intake_data['wall thickness']
        weir_vol=np.square(intake_data['weir height'])*(0.25+0.25/2)*intake_data['river length']
        foundation_vol=(intake_data['weir height']+intake_data['wall thickness'])*(intake_data['foundation thickness']*intake_data['river length'])
        structure_vol=wall_vol+weir_vol

        self.intake_dimensions["sum_vol"] = structure_vol
        self.intake_dimensions["foundation_vol"]=foundation_vol
        self.intake_dimensions["total_vol"]=structure_vol+foundation_vol


    def calculate_intake_material(self):
        if self.intake_material["structural_material"]=="RCC":
            intake_rcc =c_rm(self.intake_dimensions)
            raw_mat_price=intake_rcc.calculate_concrete()
        elif self.intake_material["structural_material"]=="MAS":
            intake_mas=c_rm(self.intake_dimensions)
            raw_mat_price=intake_mas.calculate_masonry()
        self.intake_cost["raw material"] = raw_mat_price
        self.intake_cost["material"]=self.intake_material["coarse rake"]+self.intake_material["sluice gate"]

    def calculate_intake_labour(self):
        self.intake_dimensions["foundation_vol"]
