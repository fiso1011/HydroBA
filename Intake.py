import numpy as np
import RawMaterial as c_rm

class Intake:
    def __init__(self,input_data):
        self.intake_data=input_data.input_dict["intake_data"] ["dict"]
        self.intake_material=input_data.input_dict["intake_material"]["dict"]
        self.total_intake_cost

        #import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material=input_data.input_dict["raw_material"]["dict"]
        self.constants=input_data.input_dict["constants"]["dict"]

        # Dict to store Dimensions
        self.intake_dimensions= {}
        self.intake_storage = {}

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
        weir_over_height = ((1/((2/3)*np.sqrt(2*self.constants["gravitation"])))*q_worst)/\
                           (self.intake_data ['weir coefficient']*self.intake_data["river width"]) #weir formula Poleni

        wall_vol=(self.intake_data['weir height']+weir_over_height)*self.intake_data['river width']*self.intake_data['wall thickness']
        weir_vol=np.square(self.intake_data['weir height'])*(0.25+0.25/2)*self.intake_data['river width']
        foundation_vol=(self.intake_data['weir height']*1.5+self.intake_data['wall thickness'])*\
                       (self.intake_data['foundation thickness']*self.intake_data['river width'])
        intake_vol=wall_vol+weir_vol
        contact_sqm=((self.intake_data['weir height']+weir_over_height)+self.intake_data['weir height'])*self.intake_data['river width']*2

        self.intake_dimensions["intake_vol"] = intake_vol
        self.intake_dimensions["foundation_vol"]= foundation_vol
        self.intake_dimensions["structure_vol"]=intake_vol+foundation_vol
        self.intake_dimensions["contact_sqm"]=contact_sqm


    def calculate_intake_material(self):
        # calculate structure material material
        if self.intake_material["structural material"]=="RCC":
            intake_rcc =c_rm.Raw_Material(self.intake_dimensions,self.raw_material,self.constants)
            raw_mat_price=intake_rcc.calculate_rcc()
        elif self.intake_material["structural material"]=="MAS":
            intake_mas=c_rm.Raw_Material(self.intake_dimensions,self.raw_material,self.constants)
            raw_mat_price=intake_mas.calculate_masonry()
            self.intake_dimensions["structure_vol"]=self.intake_dimensions["structure_vol"]+\
                                                    self.intake_dimensions["contact_sqm"]*self.raw_material["surface_finish"] #cement finish vol for masonry walls
        self.intake_cost["raw material"] = raw_mat_price
        self.intake_cost["material"]=self.intake_material["coarse rake"] #average flow sized sluice gate

    def calculate_intake_labour(self):
        self.intake_cost["excavation labour"] = self.intake_dimensions["foundation_vol"] *\
                                                (1.1123*np.exp(0.4774*self.site_data["excavating_factor"])) * self.labour_cost["noskill_worker"]

        # calculate structure material work
        if self.intake_material["structural material"] =="RCC":
            formwork_labour=self.intake_dimensions["contact_sqm"]*self.labour_time["formwork"]*self.labour_cost["skill_worker"]
            concreting_labour= (self.intake_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
            hauling_cost = ((self.intake_dimensions["structure_vol"] * self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"]
            self.intake_cost["structure labour"] = formwork_labour+concreting_labour+hauling_cost
        elif self.intake_material["structural material"] =="MAS":
            surface_labour=self.intake_dimensions["contact_sqm"]*self.labour_time["plastering"]*self.labour_cost["skill_worker"]
            mas_labour=(self.intake_dimensions["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
            hauling_cost=((self.intake_dimensions["structure_vol"]*self.constants["p_structure"])/50)*2*self.labour_cost["hauling_cost"]
            self.intake_cost["structure labour"] = surface_labour+mas_labour+hauling_cost

        self.intake_storage["material"]=self.intake_cost["raw material"]+self.intake_cost["material"]
        self.intake_storage["labour"]=self.intake_cost["excavation labour"]+self.intake_cost["structure labour"]

