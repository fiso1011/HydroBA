import numpy as np
import RawMaterial as c_rm

class Sandtrap:
    def __init__(self,input_data):
        self.sandtrap_data=input_data.input_dict["sandtrap_data"] ["dict"]
        self.sandtrap_material=input_data.input_dict["sandtrap_material"]["dict"]
        self.total_sandtrap_cost
        #import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.channel_data = input_data.input_dict["channel_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material = input_data.input_dict["raw_material"]["dict"]
        self.constants = input_data.input_dict["constants"]["dict"]
        # Dict to store Dimensions
        self.sandtrap_dimensions= {}
        self.sandtrap_storage = {}
        #Dict to store the Material cost, the labour cost miscellaneous
        self.sandtrap_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_sandtrap_cost(self):
        self.calculate_sandtrap_dimensions()
        self.calculate_sandtrap_material()
        self.calculate_sandtrap_labour()
        self.total_sandtrap_cost=sum(self.sandtrap_cost.values())
    def calculate_sandtrap_dimensions(self):
        slope=self.site_data["terrain_slope"]
        wall_width = self.sandtrap_data["wall width"]

        channel_width = (self.site_data["used_flow"] / (self.channel_data["channel roughness"] * 0.48 *\
                                                        np.power(self.channel_data["channel slope"],0.5))) ** (3 / 8)
        channel_perimeter = channel_width * (1 + 2 * self.channel_data["security height"])
        channel_area = channel_width ** 2

        basin_width = np.sqrt(self.site_data["used_flow"] / (1.05 * self.sandtrap_data["basin velocity"]))  # 0.15m/2 maximum suspension start Zanke
        basin_height = basin_width * 1.25
        v_channel = self.site_data["used_flow"] / channel_area
        v_basin = self.sandtrap_data["basin velocity"] #basin geschwindigkeit

        dyn_viscosity = (1 / (0.1 * ((self.site_data["water_temperature"] + self.constants["kelvin"]) ** 2) - 34.335 *\
                              (self.site_data["water_temperature"] + self.constants["kelvin"]) + 2472)) #Formel wiki
        kin_viscosity = dyn_viscosity / self.constants["p_water"]
        max_diameter = self.sandtrap_data["filtered diameter"]
        d_factor = (((((self.constants["p_stone"] / self.constants["p_water"]) - 1) * self.constants["gravitation"]) /\
                     (kin_viscosity ** 2)) ** (1 / 3)) * max_diameter
        v_wo = ((11 * kin_viscosity) / max_diameter) * (np.sqrt(1 + 0.01 * ((d_factor) ** 3)) - 1)
        k_factor = (1 / ((v_basin ** 0.4) * (v_channel ** 0.3))) * (1 / np.tan(np.deg2rad(5))) *\
                   (1 / ((self.constants["gravitation"] * (1.05 * (basin_width**2) / (2.98 * basin_width))) ** 0.15))
        v_w = v_wo - (0.21 / k_factor) #Formula Ortmann

        settling_lenght = (v_basin / v_w) * basin_height
        Uv_length = (basin_height - channel_width) / np.tan(np.deg2rad(5)) #5 degree opening slope
        spillway_length = (self.site_data["used_flow"] * self.channel_data["security height"] * 0.3564) /\
                          (0.5 * ((0.15) ** (3 / 2))) #15cm height

        # Dimensions of Part1
        a1 = (0.84 / 2.98) * channel_perimeter  # channel-sided side length of the truncated pyramid
        a2 = 0.84 * basin_width  # basin-sided side length of the truncated pyramid (idealized shape 0,84^2*1.5=1.05)
        #1:upper 2:lower part volume of channel/santrap opening
        v_1_1 = ((a1 ** 2) + a1 * a2 + (a2 ** 2)) * (Uv_length / 3)
        v_1_2 = (3 / 12) * ((a1 ** 2) + a1 * a2 + (a2 ** 2)) * (Uv_length * (1 / np.tan(np.pi / 3)))  # cotengens with radian
        #1:upper 2:lower part area of channel/santrap opening
        a_1_1 = (channel_width + (0.75 * basin_width - channel_width) * 0.5) * (np.sqrt(Uv_length**2+(basin_width-channel_width)**2)) * 2
        a_1_2 = ((0.5*basin_width) / np.cos(np.deg2rad(38.66))) * (np.sqrt(Uv_length**2+(basin_width-channel_width)**2)) * 0.5 * 2

        #Dimensions of Part2
        #lower part volume and 1: upper 2: lower part area of sandtrap settling part
        v_2_2 = 0.5 * basin_width * (0.4 + 0.2) * basin_width * settling_lenght
        a_2_1=(0.75*basin_width*settling_lenght+(settling_lenght**2)*0.04*0.5)*2
        a_2_2=((0.5/np.cos(np.deg2rad(38.66)))*2+0.2)*basin_width*settling_lenght

        # pressure basin Dimensions
        pbasin_width = basin_width # =pbasin_length
        pbasin_height = basin_height + settling_lenght * 0.04 #4% slope inside basin
        # lower part of pressure basin volume
        v_3_1 = (pbasin_height - 0.75 * pbasin_width) * (pbasin_width ** 2)
        #1: base 2:lower part 3:upper part (transition) area of pressure basin
        a_3_1=(pbasin_width+wall_width*2)**2
        a_3_2=(pbasin_height-0.75*pbasin_width)*(2*pbasin_width+2*wall_width)*2 #lower part
        a_3_3=0.75*pbasin_width*(pbasin_width*1.5+(pbasin_width+2+wall_width)*2) #upper part transition from sandtrap to pressure basin

        #Excavation Volume
        exc_vol1=v_1_2+a_1_2*((wall_width)+self.raw_material["gravel_thickness"])+\
                 ((((basin_width+2*wall_width)**2)*np.tan(np.deg2rad(slope))*0.5)/(((basin_width)**2)*0.75+(2*0.75*basin_width)*wall_width))*\
                 (v_1_1+a_1_1*wall_width)
        exc_vol2=v_2_2+(a_2_2+settling_lenght*settling_lenght*0.04)*(wall_width+self.raw_material["gravel_thickness"])+\
                 (settling_lenght*settling_lenght*0.04*0.5*basin_width)+\
                 ((((basin_width+2*wall_width)**2)*np.tan(np.deg2rad(slope))*0.5)/(((basin_width)**2)*0.75+(2*0.75*basin_width)*wall_width))*\
                 (0.75*(basin_width**2)*settling_lenght+0.75*basin_width*2*settling_lenght*wall_width)
        exc_vol3=v_3_1+a_3_1*(wall_width+self.raw_material["gravel_thickness"])+a_3_2*wall_width+\
                 ((pbasin_width+2*wall_width)**3)*(np.tan(np.deg2rad(slope))*0.5)

        #Gravel Area
        gravel_sqm1=(a_1_2+a_2_2+(settling_lenght**2)*0.04) #sandtrap, slope
        gravel_sqm2=a_3_1 #pressure basin

        #Structure Volume (with or without walls)
        if ((basin_width+2*wall_width)*np.tan(np.deg2rad(slope))) > 0.75*basin_width:
            hdiff1=((basin_width+2*wall_width)*(np.tan(np.deg2rad(slope))-0.75*basin_width))
            hdiff0=hdiff1*(channel_perimeter/(2.98*basin_width))
            wall1_vol=((hdiff0+0.5*(hdiff1-hdiff0))*Uv_length)*wall_width #first part of wall
            wall2_vol=hdiff1*(settling_lenght+pbasin_width) #second part of wall, constant basin width
            basin_volume=(a_1_1+a_1_2+a_2_1+a_2_2)*wall_width+spillway_length*1*0.2+(spillway_length+2)*(0.3*0.2) #v basin+catchment/spillway
            pbasin_volume=(a_3_1+a_3_2+a_3_3)*wall_width
            structure_vol=wall1_vol+wall2_vol+basin_volume+pbasin_volume
        else:
            basin_vol=(a_1_1+a_1_2+a_2_1+a_2_2)*wall_width+spillway_length*1*0.2+(spillway_length+2)*(0.3*0.2)
            pbasin_volume = (a_3_1 + a_3_2 + a_3_3) * wall_width
            structure_vol=basin_vol+pbasin_volume

        self.sandtrap_dimensions["excavation_vol"] = exc_vol1+exc_vol2+exc_vol3
        self.sandtrap_dimensions["structure_vol"] = structure_vol
        self.sandtrap_dimensions["gravel_sqm"]=gravel_sqm1+gravel_sqm2
        self.sandtrap_dimensions["contact_sqm"]=(a_1_1+a_1_2+a_2_1+a_2_2+a_3_1+a_3_2+a_3_3)*1.5 #formwork or surface finish area
        self.sandtrap_dimensions["basin width"]=basin_width

    def calculate_sandtrap_material(self):
        # calculate structure material price
        if self.sandtrap_material["structural material"]=="RCC":
            sandtrap_rcc =c_rm.Raw_Material(self.sandtrap_dimensions,self.raw_material,self.constants)
            raw_mat_price=sandtrap_rcc.calculate_rcc()
        elif self.sandtrap_material["structural material"]=="MAS":
            sandtrap_mas=c_rm.Raw_Material(self.sandtrap_dimensions,self.raw_material,self.constants)
            raw_mat_price=sandtrap_mas.calculate_masonry()
            self.sandtrap_dimensions["structure_vol"] = self.sandtrap_dimensions["structure_vol"] +\
                                                        self.sandtrap_dimensions["contact_sqm"] * self.raw_material["surface_finish"] # cement finish
        self.sandtrap_cost["raw material"] = raw_mat_price

        gravel=self.sandtrap_dimensions["gravel_sqm"]*self.raw_material["gravel_thickness"]*self.raw_material["gravel"]
        flush_gate=185.38*np.exp(2.3306*0.2*self.sandtrap_dimensions["basin width"])
        fine_rake=self.sandtrap_material["fine rake"]
        self.sandtrap_cost["material"]= gravel+flush_gate+fine_rake

    def calculate_sandtrap_labour(self):
        self.sandtrap_cost["excavation labour"] = (self.sandtrap_dimensions["excavation_vol"] *\
                                                   (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.sandtrap_cost["laying"] = (self.sandtrap_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel

        #calculate structure material work
        if self.sandtrap_material["structural material"] =="RCC":
            formwork_labour = self.sandtrap_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
            concreting_labour = (self.sandtrap_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
            hauling_cost = (((self.sandtrap_dimensions["structure_vol"]+self.sandtrap_dimensions["gravel_sqm"]*\
                              self.raw_material["gravel_thickness"]) * self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"]
            self.sandtrap_cost["structure labour"] = formwork_labour + concreting_labour+hauling_cost
        elif self.sandtrap_material["structural material"] =="MAS":
            surface_labour = self.sandtrap_dimensions["contact_sqm"] * self.labour_time["plastering"] * self.labour_cost["skill_worker"]  # cement finish
            mas_labour = (self.sandtrap_dimensions["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
            hauling_cost = (((self.sandtrap_dimensions["structure_vol"] + self.sandtrap_dimensions["gravel_sqm"] *\
                              self.raw_material["gravel_thickness"]*self.sandtrap_dimensions["contact_sqm"]*\
                              self.raw_material["surface_finish"]) * self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"]
            self.sandtrap_cost["structure labour"] = surface_labour + mas_labour+hauling_cost

        self.sandtrap_storage["material"] = self.sandtrap_cost["raw material"] + self.sandtrap_cost["material"]
        self.sandtrap_storage["labour"] = self.sandtrap_cost["excavation labour"] + self.sandtrap_cost["structure labour"] + self.sandtrap_cost["laying"]