import numpy as np
import RawMaterial as c_rm

class Channel:
    def __init__(self,input_data):
        self.channel_data=input_data.input_dict["channel_data"] ["dict"]
        self.channel_material=input_data.input_dict["channel_material"]["dict"]
        self.total_channel_cost
        #import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material = input_data.input_dict["raw_material"]["dict"]
        self.constants = input_data.input_dict["constants"]["dict"]

        # Dict to store Dimensions
        self.channel_dimensions= {}
        self.channel_storage = {}

        #Dict to store the Material cost, the labour cost miscellaneous
        self.channel_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_channel_cost(self):
        self.calculate_channel_dimensions()
        self.calculate_channel_material()
        self.calculate_channel_labour()
        self.total_channel_cost=sum(self.channel_cost.values())

    def calculate_channel_dimensions(self):
        channel_width=(self.site_data["used_flow"]/(self.channel_data["channel roughness"]*0.48*\
                                                    np.power(self.channel_data["channel slope"],0.5)))**(3/8)
        excavation_width=channel_width+2*self.channel_data["wall thickness"]
        excavation_height=excavation_width*np.tan(self.site_data["terrain_slope"])
        channel_height=channel_width*self.channel_data["security height"]

        #determine the height of the base of the basin to match wall heights
        if excavation_height > channel_height:
            foundation_thickness=self.channel_data["foundation thickness"]+excavation_height-channel_height
        else:
            foundation_thickness=self.channel_data["foundation thickness"]
        excavation_vol=self.channel_data["channel length"]*(excavation_width*(foundation_thickness+self.raw_material["gravel_thickness"])+\
                                                             np.power(excavation_width, 2) *0.5 * np.tan(np.deg2rad(self.site_data["terrain_slope"])))
        structure_vol=self.channel_data["channel length"]*(excavation_width*foundation_thickness+2*channel_height*self.channel_data["wall thickness"])
        gravel_sqm=self.channel_data["channel length"]*excavation_width
        contact_sqm=channel_width*(self.channel_data["security height"]*2+1)*self.channel_data["channel length"]

        self.channel_dimensions["excavation_vol"] = excavation_vol
        self.channel_dimensions["structure_vol"] = structure_vol
        self.channel_dimensions["gravel_sqm"]=gravel_sqm
        self.channel_dimensions["vlies_sqm"]= self.channel_data["channel length"]*(excavation_width+excavation_height+foundation_thickness)
        self.channel_dimensions["contact_sqm"]=contact_sqm
        self.channel_dimensions["excavation_width"] = excavation_width
        self.channel_dimensions["channel_height"]=channel_height


    def calculate_channel_material(self):
        # calculate structure material price
        if self.channel_material["structural material"]=="RCC":
            channel_rcc =c_rm.Raw_Material(self.channel_dimensions,self.raw_material,self.constants)
            raw_mat_price=channel_rcc.calculate_rcc()
        elif self.channel_material["structural material"]=="MAS":
            channel_mas=c_rm.Raw_Material(self.channel_dimensions,self.raw_material,self.constants)
            raw_mat_price=channel_mas.calculate_masonry()
            self.channel_dimensions["structure_vol"] = self.channel_dimensions["structure_vol"] +\
                                                       self.channel_dimensions["contact_sqm"] * self.raw_material["surface_finish"]  # cement finish vol for masonry walls
        self.channel_cost["raw material"] = raw_mat_price

        drainage_vlies=self.channel_dimensions["vlies_sqm"]*self.channel_material["drainage vlies"]
        drainage_pipe=self.channel_material["drainage pipe"]*(self.channel_data["channel length"]/10)*\
                      (2*1.3*self.channel_dimensions["excavation_width"])
        gravel=self.channel_dimensions["gravel_sqm"]*self.raw_material["gravel_thickness"]*self.raw_material["gravel"]
        self.channel_cost["material"]= drainage_pipe+drainage_vlies+gravel

    def calculate_channel_labour(self):
        self.channel_cost["excavation labour"] = (self.channel_dimensions["excavation_vol"] *\
                                                  (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.channel_cost["laying"] = (self.channel_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"] #gravel,vlies und rohr

        # calculate structure material work
        if self.channel_material["structural material"] =="RCC":
            formwork_labour = self.channel_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
            concreting_labour = (self.channel_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
            hauling_cost = (((self.channel_dimensions["structure_vol"]+self.channel_dimensions["gravel_sqm"]*\
                              self.raw_material["gravel_thickness"]) * self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"]
            self.channel_cost["structure labour"] = formwork_labour + concreting_labour+hauling_cost
        elif self.channel_material["structural material"] =="MAS":
            surface_labour=self.channel_dimensions["contact_sqm"] * self.labour_time["plastering"] * self.labour_cost["skill_worker"]#cement finish
            mas_labour=(self.channel_dimensions["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
            hauling_cost = (((self.channel_dimensions["structure_vol"]+self.channel_dimensions["gravel_sqm"]*\
                              self.raw_material["gravel_thickness"]+self.channel_dimensions["contact_sqm"]*\
                              self.raw_material["surface_finish"]) * self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"]
            self.channel_cost["structure labour"] = surface_labour+mas_labour+hauling_cost

        self.channel_storage["material"] = self.channel_cost["raw material"] + self.channel_cost["material"]
        self.channel_storage["labour"] = self.channel_cost["excavation labour"] + self.channel_cost["structure labour"]+self.channel_cost["laying"]