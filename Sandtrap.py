import pandas as pd
import numpy as np
import Raw_Material as c_rm
import data_input as c_di

class Sandtrap:
    def __init__(self,sandtrap_data,sandtrap_material):
        self.sandtrap_data=sandtrap_data
        self.sandtrap_material=sandtrap_material
        self.total_sandtrap_cost
        #import relevant Dicts
        c_di.data_storage.readingFunc()
        self.site_data = c_di.data_storage.readingFunc.inputdata.input_dict["hydro_data"]["dict"]
        self.channel_data = c_di.data_storage.readingFunc.inputdata.input_dict["channel_data"]["dict"]
        self.labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]
        self.labour_time = c_di.data_storage.readingFunc.inputdata.input_dict["labour_time"]["dict"]
        self.raw_material = c_di.data_storage.readingFunc.inputdata.input_dict["raw_material"]["dict"]
        # Dict to store Dimensions
        self.sandtrap_dimensions= {}
        #Dict to store the Material cost, the labour cost miscellaneous
        self.sandtrap_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_sandtrap_cost(self):
        self.calculate_sandtrap_dimensions()
        self.calculate_sandtrap_material()
        self.calculate_sandtrap_labour()
        self.total_sandtrap_cost=sum(self.sandtrap_cost.values())
    def calculate_sandtrap_dimensions(self):
        slope=self.channel_data["terrain slope"]
        channel_width = (self.site_data["used flow"] / (self.channel_data["channel roughness"] * 0.48 * np.power(self.channel_data["channel slope"],0.5))) ** (3 / 8)
        channel_perimeter=channel_width*(1+2*1.3)
        channel_area=channel_width**2
        basin_width=self.site_data["used flow"]/(1.05*0.2) #0.2m/2 maximum suspension start Zanke
        basin_height=basin_width*1.25
        v_channel=self.site_data["used flow"]/channel_area
        v_basin=0.2
        dyn_viscosity=(1/(0.1*((self.site_data["water_temperature"]+273.15)**2)-34.335*(self.site_data["water_temperature"]+273.15)+2472))
        kin_viscosity=dyn_viscosity/1000
        max_diameter=0.0002
        d_factor=(((((2650/1000)-1)*9.81)/(kin_viscosity**2))**(1/3))*max_diameter
        v_wo=((11*kin_viscosity)/max_diameter)*(np.sqrt(1+0.01*((d_factor)**3))-1)
        k_factor=(1/((v_basin**0.4)*(v_channel**0.3)))*(1/np.sin(np.deg2rad(15)))*(1/((9.81*(1.05*basin_width/2.98*basin_width))**0.15))
        v_w=v_wo-(0.21/k_factor)
        settling_lenght=(v_basin/v_w)*basin_height
        Uv_length=(basin_height-channel_width)/np.tan(np.deg2rad(15))
        spillway_length=(self.site_data["used flow"]*1.3*0.3564)/(0.5*((0.15)**(3/2)))
        #Dimensions of Part1
        a1=(0.84/2.98)*channel_perimeter  #channel-sided side length of the truncated pyramid
        a2=0.84*basin_width               #basin-sided side length of the truncated pyramid
        v_1_1=((a1**2)+a1*a2+(a2**2))*(Uv_length/3)
        v_1_2=(3/12)*((a1**2)+a1*a2+(a2**2))*(Uv_length*(1/np.tan(np.pi/3))) #cotengens with radian
        a_1_1=(channel_width+(0.75*basin_width-channel_width)*0.5)*Uv_length*2
        a_1_2=(0.5/np.cos(np.deg2rad(38.66)))*Uv_length*0.5*2
        #Dimensions of Part2
        v_2_1=0.75*basin_width*settling_lenght+settling_lenght*settling_lenght*0.04*0.5*basin_width
        v_2_2=0.5*basin_width*(0.4+0.2)*basin_width*settling_lenght
        a_2_1=(0.75*basin_width*settling_lenght+settling_lenght*settling_lenght*0.04*0.5)*2
        a_2_2=((0.5/np.cos(np.deg2rad(38.66)))*2+0.2)*basin_width*settling_lenght
        #Excavation Volume
        wall_width=self.sandtrap_data["wall_width"]
        exc_vol1=v_1_2+a_1_2*((wall_width)+0.1)+((((basin_width+2*wall_width)**2)*np.tan(np.deg2rad(slope))*0.5)/(((basin_width)**2)*0.75+(2*0.75*basin_width)*wall_width))*(v_1_1+a_1_1*wall_width)
        exc_vol2=v_2_2+(a_2_2+settling_lenght*settling_lenght*0.04)*(wall_width+0.1)+(settling_lenght*settling_lenght*0.04*0.5*basin_width)+((((basin_width+2*wall_width)**2)*np.tan(np.deg2rad(slope))*0.5)/(((basin_width)**2)*0.75+(2*0.75*basin_width)*wall_width))*(0.75*(basin_width**2)*settling_lenght+0.75*basin_width*2*settling_lenght*wall_width)
        #Gravel Area
        gravel_sqm=(a_1_2+a_2_2+(settling_lenght**2)*0.04)
        #Structure Volume
        if ((basin_width+2*wall_width)*np.tan(np.deg2rad(slope))) > 0.75*basin_width:
            hdiff1=((basin_width+2*wall_width)*(np.tan(np.deg2rad(slope))-0.75*basin_width))
            hdiff0=hdiff1*(channel_perimeter/(2.98*basin_width))
            wall1_vol=((hdiff0+0.5*(hdiff1-hdiff0))*Uv_length)*wall_width
            wall2_vol=hdiff1*settling_lenght
            basin_volume=(a_1_1+a_1_2+a_2_1+a_2_2)*wall_width+spillway_length*(1*0.3)+(spillway_length+2)*(0.3*0.2) #volume of basin+catchment for spillway
            structure_vol=wall1_vol+wall2_vol+basin_volume
        else:structure_vol=(a_1_1+a_1_2+a_2_1+a_2_2)*wall_width+spillway_length*(1*0.3)+(spillway_length+2)*(0.3*0.2)

        self.sandtrap_dimensions["excavation_vol"] = exc_vol1+exc_vol2
        self.sandtrap_dimensions["structure_vol"] = structure_vol
        self.sandtrap_dimensions["gravel_sqm"]=gravel_sqm
        self.sandtrap_dimensions["contact_sqm"]=(a_1_1+a_1_2+a_2_1+a_2_2)*1.5 #formwork or surface finish area

    def calculate_sandtrap_material(self):
        if self.sandtrap_material["structural_material"]=="RCC":
            sandtrap_rcc =c_rm.Raw_Material(self.sandtrap_dimensions)
            raw_mat_price=sandtrap_rcc.calculate_rcc()
        elif self.sandtrap_material["structural_material"]=="MAS":
            sandtrap_mas=c_rm.Raw_Material(self.sandtrap_dimensions)
            raw_mat_price=sandtrap_mas.calculate_masonry()
        self.sandtrap_cost["raw material"] = raw_mat_price

        gravel=self.sandtrap_dimensions["gravel_sqm"]*0.1*self.raw_material["gravel"]
        flush_gate=self.sandtrap_material["flush gate"]
        fine_rake=self.sandtrap_material["fine rake"]
        self.sandtrap_cost["material"]= gravel+flush_gate+fine_rake

    def calculate_sandtrap_labour(self):
        self.sandtrap_cost["excavation labour"] = (self.sandtrap_dimensions["excavation_vol"] * (1.1123*np.exp(0.4774*self.labour_time["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.sandtrap_cost["laying"] = (self.sandtrap_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel, vlies und rohr
        if self.sandtrap_material["structural_material"] =="RCC":
            formwork_labour = self.sandtrap_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
            concreting_labour = (self.sandtrap_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
            self.sandtrap_cost["structure labour"] = formwork_labour + concreting_labour
        elif self.sandtrap_material["structural_material"] =="MAS":
            surface_labour = self.sandtrap_dimensions["contact_sqm"] * self.labour_time["plastering"] * self.labour_cost["skill_worker"]  # cement finish
            mas_labour = (self.sandtrap_dimensions["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
            self.sandtrap_cost["structure labour"] = surface_labour + mas_labour