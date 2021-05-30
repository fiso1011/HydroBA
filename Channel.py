import pandas as pd
import numpy as np
import Raw_Material as c_rm
import data_input as c_di

class Channel:
    def __init__(self,channel_data,channel_material):
        self.channel_data=channel_data
        self.channel_material=channel_material
        self.total_channel_cost
        #import relevant Dicts
        c_di.data_storage.readingFunc()
        self.site_data = c_di.data_storage.readingFunc.inputdata.input_dict["site_data"]["dict"]
        self.labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]
        self.labour_time = c_di.data_storage.readingFunc.inputdata.input_dict["labour_time"]["dict"]
        self.raw_material = c_di.data_storage.readingFunc.inputdata.input_dict["raw_material"]["dict"]
        # Dict to store Dimensions
        self.channel_dimensions= {}
        #Dict to store the Material cost, the labour cost miscellaneous
        self.channel_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_channel_cost(self):
        self.calculate_channel_dimensions()
        self.calculate_channel_material()
        self.calculate_channel_labour()
        self.total_channel_cost=sum(self.channel_cost.values())
    def calculate_channel_dimensions(self):
        channel_width=(self.site_data["used flow"]/(self.channel_data["channel roughness"]*0.48*np.power(self.channel_data["channel slope"],0.5)))**(3/8)
        excavation_width=channel_width+2*self.channel_data["wall thickness"]
        excavation_height=excavation_width*np.tan(self.site_data["terrain slope"])
        channel_height=channel_width*1.3

        if excavation_height > channel_height:
            foundation_thickness=self.channel_data["foundation thickness"]+excavation_height-channel_height
        else:
            foundation_thickness=self.channel_data["foundation thickness"]
        excavation_vol=self.channel_data["channel length"]*(excavation_width*(foundation_thickness+0.1)+np.power(excavation_width, 2) * 0.5 * np.tan(np.deg2rad(self.site_data["terrain slope"])))
        structure_vol=self.channel_data["channel length"]*(excavation_width*foundation_thickness+2*channel_height*self.channel_data["wall thickness"])
        gravel_sqm=self.channel_data["channel length"]*excavation_width*0.1
        contact_sqm=channel_height*1.3*3*self.channel_data["channel length"]

        self.channel_dimensions["excavation_vol"] = excavation_vol
        self.channel_dimensions["structure_vol"] = structure_vol
        self.channel_dimensions["gravel_sqm"]=gravel_sqm
        self.channel_dimensions["vlies_sqm"]= self.channel_data["channel length"]*(excavation_width+excavation_height+foundation_thickness)
        self.channel_dimensions["wet_surface"]=self.channel_data["channel length"]*channel_width*(1+2*1.3)
        self.channel_dimensions["contact_sqm"]=contact_sqm

    def calculate_channel_material(self):
        if self.channel_material["structural_material"]=="RCC":
            channel_rcc =c_rm.Raw_Material(self.channel_dimensions)
            raw_mat_price=channel_rcc.calculate_rcc()
        elif self.channel_material["structural_material"]=="MAS":
            channel_mas=c_rm.Raw_Material(self.channel_dimensions)
            raw_mat_price=channel_mas.calculate_masonry()
        self.channel_cost["raw material"] = raw_mat_price
        drainage_vlies=self.channel_dimensions["vlies_sqm"]*self.channel_material["drainage vlies"]
        drainage_pipe=self.channel_material["drainage pipe"]*(self.channel_data["channel length"]/10)
        gravel=self.channel_dimensions["gravel_sqm"]*0.1*self.raw_material["gravel"]
        self.channel_cost["material"]= drainage_pipe+drainage_vlies+gravel

    def calculate_channel_labour(self):
        self.channel_cost["excavation labour"] = (self.channel_dimensions["excavation_vol"] * (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.channel_cost["laying"] = (self.channel_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel, vlies und rohr
        if self.channel_material["structural_material"] =="RCC":
            formwork_labour = self.channel_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
            concreting_labour = (self.channel_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
            self.channel_cost["structure labour"] = formwork_labour + concreting_labour
        elif self.channel_material["structural_material"] =="MAS":
            surface_labour=self.channel_dimensions["wet_surface"] * self.labour_time["plastering"] * self.labour_cost["skill_worker"]#cement finish
            mas_labour=(self.channel_dimensions["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
            self.channel_cost["structure labour"] = surface_labour+mas_labour

