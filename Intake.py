import pandas as pd
import numpy as np
class: Intake
    def __init__(self,river_length,q_mean,q_use,q_max,weir_height)
        self.river_length=river_length
        self.q_mean=q_mean
        self.q_use=q_use
        self.q_max=q_max
        self.weir_height=weir_height

        #Dicts to store the Material cost, the labour cost miscellaneous
        self.intake_material={}
        self.intake_labour={}
        self.intake_misc={}
    #calls all other methods and returns the total intake cost
    def total_intake_cost(self):
         calculate_intake_dimensions()
         calculate_intake_material()
         calculate_intake_labour()
        calculate_intake_dimensions()

    def calculate_intake_dimensions(self):
        #Dict to store Dimensions
        global intake_dimensions
        intake_dimensions= dict{}

        q_worst=self.q_max*50                                                                           #Assumption in Micro Hydro Design manual
        intake_coeff=1.9                                                                                #for sharp edged weir
        weir_over_height = ((1/((2/3)*np.sqrt(2*9.81)))*q_worst)/(intake_coeff*river_length)                 #weir formula of Poleni
        weir_width=0.5*self.weir_height
        wall_width=0.4
        wall_length=self.river_length
        wall_height=self.weir_height+weir_over_height

        weir_evol=


    def calculate_intake_material(self,)
    def calculate_intake_labour(self)
    def calculate_intake_misc(self)
total_intake_cost()
