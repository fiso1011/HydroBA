import numpy as np
import RawMaterial as c_rm

class Powerhouse:
    def __init__(self,input_data):
        self.powerhouse_data=input_data.input_dict["powerhouse_data"] ["dict"]
        self.powerhouse_material=input_data.input_dict["powerhouse_material"]["dict"]
        self.total_powerhouse_cost
        #import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.penstock_data = input_data.input_dict["penstock_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material = input_data.input_dict["raw_material"]["dict"]
        # Dict to store Dimensions
        self.powerhouse_dimensions= {}
        self.powerhouse_helpstorage={}
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
        exc_1=((5+2)**2)*np.tan(np.arcsin(self.penstock_data["height drop"]/self.penstock_data["penstock length"]))*0.5*10*0.5 #slope excavation
        exc_2=5*10*(0.5+0.1)+(1.5+2*self.powerhouse_data["wall_width"])*1.5*5 #Foundation and Channel under powerhouse
        foundation_vol=5*10*0.5
        wall_vol=(2*(5+8)*2.5+(1.5*5*2+(1.5**2)))*self.powerhouse_data["wall_width"] #walls of house and water channel
        gravel_sqm=5*10
        self.powerhouse_dimensions["excavation_vol"] = exc_1+exc_2
        self.powerhouse_dimensions["structure_vol"] = foundation_vol+wall_vol
        self.powerhouse_dimensions["gravel_sqm"]=gravel_sqm
        self.help1["structure_vol"]=foundation_vol
        self.help2["structure_vol"]=wall_vol
        self.help2["contact_sqm"]=(2*(5+8)*2.5+(1.5*5*2+(1.5**2)))#walls area of house and water channel

    def calculate_powerhouse_material(self):
        powerhouse_rcc =c_rm.Raw_Material(self.help1,self.raw_material)
        raw_mat_price1=powerhouse_rcc.calculate_rcc()
        powerhouse_mas = c_rm.Raw_Material(self.help2,self.raw_material)
        raw_mat_price2 = powerhouse_mas.calculate_masonry()
        raw_mat_price=raw_mat_price1+raw_mat_price2
        self.powerhouse_dimensions["structure_vol"] = self.powerhouse_dimensions["structure_vol"] + self.help2["contact_sqm"] * 0.02  # cement finish vol for masonry walls

        self.powerhouse_cost["raw material"] = raw_mat_price

        gravel=self.powerhouse_dimensions["gravel_sqm"]*0.1*self.raw_material["gravel"]

        #tailrace pipe
        if self.powerhouse_material["tailrace material"] == "PVC":
            pipe_cost = 0.00005 * ((self.powerhouse_data["tailrace drop"] * 1.5) / 10) * np.power((self.powerhouse_data["di_tailrace"] * 1000),1.98)  # only pipe
            joint_cost = 0.0045 * np.power((self.powerhouse_data["di_tailrace"] * 1000), 1.98)
            bolts_cost = (pipe_cost + joint_cost) * 0.1
        elif self.powerhouse_material["tailrace material"] == "HDPE":
            pipe_cost = (0.00004 * ((self.powerhouse_data["tailrace drop"]  * 1.5) / 10) + 0.00008) * np.power((self.powerhouse_data["di_tailrace"]* 1000), 1.99)*self.powerhouse_data["tailrace length"]  # only pipe
            joint_cost = 0.0018 * np.power((self.powerhouse_data["di_tailrace"]* 1000),2.18)*(self.powerhouse_data["tailrace length"]/10)
            bolts_cost = (pipe_cost + joint_cost) * 0.1
        tailrace_total_cost=pipe_cost+joint_cost+bolts_cost


        #Turbine price
        if self.powerhouse_material["turbine type"]=="FR":
            turbine_cost=190.37*np.power(self.penstock_data["height drop"],1.27963)+1441610*np.power((self.site_data["used_flow"]*1000),0.03064)+\
                         9.62402*np.power(self.site_data["power"],1.28487)-1621571.28
        elif self.powerhouse_material["turbine type"]=="PE":
            turbine_cost = 1358677.67*np.power(self.penstock_data["height drop"],0.014)+8489.85*np.power((self.site_data["used_flow"]*1000),0.515)+\
                           3382.1*np.power(self.site_data["power"],0.416)-1479160.63
        elif self.powerhouse_material["turbine type"]=="CR":
            turbine_cost = 139318.161*np.power(self.penstock_data["height drop"],0.02156)+0.06372*np.power((self.site_data["used_flow"]*1000),1.45636)+\
                           155227.37*np.power(self.site_data["power"],0.11053)-302038.27

        roofing=self.powerhouse_material["roofing"] #fixed price to be edited later
        #load_regulator=self.powerhouse_material["load regulator"]*(self.site_data["power"]/10) #already included in the turbine formula
        lightning_protection=self.powerhouse_material["lightning protection"]
        electrics_fix=self.powerhouse_material["electrics fix"]
        electrics_var= self.powerhouse_material["electrics var"]

        self.powerhouse_cost["material"]= roofing+gravel+tailrace_total_cost+turbine_cost+lightning_protection+electrics_fix+electrics_var

        self.powerhouse_helpstorage["turbine_cost"]=turbine_cost
        self.powerhouse_helpstorage["electric_equipment_cost"] = lightning_protection+electrics_fix+electrics_var
        self.powerhouse_helpstorage["pipe volume"] =np.pi*((self.powerhouse_data["di_tailrace"]/2)**2)*self.powerhouse_data["tailrace length"]

    def calculate_powerhouse_labour(self):
        self.powerhouse_cost["excavation labour"] = (self.powerhouse_dimensions["excavation_vol"] *\
                                                     (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.powerhouse_cost["laying"] = (self.powerhouse_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel

        concreting_labour = (self.help1["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
        masonry_labour=(self.help2["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]
        building_installation=8*(self.labour_cost["skill_worker"]+self.labour_cost["noskill_worker"]) # 16h: roof, lightning protection
        tailrace_installation=(self.powerhouse_data["tailrace length"] / 10)*4*(self.labour_cost["skill_worker"]+self.labour_cost["noskill_worker"]) # to be edited later
        turbine_installation=16*(self.labour_cost["skill_worker"]+self.labour_cost["noskill_worker"])  #32h
        electrical_installation=8*(self.labour_cost["skill_worker"]+self.labour_cost["noskill_worker"])  #16h switch cabinet
        hauling_cost = (((self.help1["structure_vol"] +self.help2["structure_vol"]+ self.powerhouse_dimensions["gravel_sqm"] * 0.1+\
                          self.help2["contact_sqm"]*0.02) * 2300) / 50) * 2 * self.labour_cost["hauling_cost"]
        self.powerhouse_cost["structure labour"] = concreting_labour+masonry_labour+hauling_cost
        self.powerhouse_cost["installation labour"] =building_installation+tailrace_installation+\
                                                     turbine_installation+electrical_installation