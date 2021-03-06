import numpy as np
import RawMaterial as c_rm


class Powerhouse:
    def __init__(self, input_data):
        self.powerhouse_data = input_data.input_dict["powerhouse_data"]["dict"]
        self.powerhouse_material = input_data.input_dict["powerhouse_material"]["dict"]
        self.total_powerhouse_cost

        # import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.penstock_data = input_data.input_dict["penstock_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material = input_data.input_dict["raw_material"]["dict"]
        self.constants = input_data.input_dict["constants"]["dict"]
        self.usd_conversion=input_data.input_dict["currency"]["dict"]

        # Dict to store Dimensions
        self.powerhouse_dimensions = {}
        self.powerhouse_storage = {}
        self.help1 = {}  # help to store different volume for brick and concrete parts
        self.help2 = {}  # help to store different volume for brick and concrete parts

        # Dict to store the Material cost, the labour cost miscellaneous
        self.powerhouse_cost = {}

        # calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_powerhouse_cost(self):
        self.calculate_powerhouse_dimensions()
        self.calculate_powerhouse_material()
        self.calculate_powerhouse_labour()
        self.total_powerhouse_cost = sum(self.powerhouse_cost.values())

    def calculate_powerhouse_dimensions(self):
        exc_1 = (5 ** 2) * np.tan(np.arcsin(self.penstock_data["height drop"] / self.penstock_data["penstock length"])) *\
                0.5 * 10 #building 5*10m slope excavation
        exc_2 = 5 * 10 * (0.5 + self.raw_material["gravel_thickness"]) + (1.5 + 2 * self.powerhouse_data["wall_width"]) * 1.5 *\
                5  # Foundation and Channel under powerhouse
        foundation_vol = 5 * 10 * 0.5
        wall_vol = (2 * (5 + 8) * 2.5 + (1.5 * 5 * 2 + (1.5 ** 2))) * self.powerhouse_data[
            "wall_width"]  # walls of house and water channel
        gravel_sqm = 5 * 10

        self.powerhouse_dimensions["excavation_vol"] = exc_1 + exc_2
        self.powerhouse_dimensions["gravel_sqm"] = gravel_sqm
        self.help1["structure_vol"] = foundation_vol
        self.help2["structure_vol"] = wall_vol
        self.help2["contact_sqm"] = (2 * (5 + 8) * 2.5 + (1.5 * 5 * 2 + (1.5 ** 2)))  # walls area of house and water channel
        self.powerhouse_dimensions["structure_vol"] = self.help1["structure_vol"] + self.help2["structure_vol"] + \
                                                      self.help2["contact_sqm"] * self.raw_material["surface_finish"]

    def calculate_powerhouse_material(self):
        powerhouse_rcc = c_rm.Raw_Material(self.help1, self.raw_material,self.constants)
        raw_mat_price1 = powerhouse_rcc.calculate_rcc()
        powerhouse_mas = c_rm.Raw_Material(self.help2, self.raw_material,self.constants)
        raw_mat_price2 = powerhouse_mas.calculate_masonry()
        raw_mat_price = raw_mat_price1 + raw_mat_price2
        self.powerhouse_cost["raw material"] = raw_mat_price

        gravel = self.powerhouse_dimensions["gravel_sqm"] * self.raw_material["gravel_thickness"] * self.raw_material["gravel"]
        roofing = self.powerhouse_material["roofing"]

        # tailrace pipe
        di_tailrace=(((4*self.site_data["used_flow"])/(self.penstock_data["velocity"]*np.pi))**(0.5))
        if self.powerhouse_material["tailrace material"] == "PVC":
            pipe_cost = 0.00005 * (6) *np.power((di_tailrace * 1000), 1.98)*self.powerhouse_data["tailrace length"]  # only pipe
            joint_cost = 0.0045 * np.power((di_tailrace * 1000), 1.98)*\
                         (self.powerhouse_data["tailrace length"] / self.penstock_data["joint distance"])
            bolts_cost = (pipe_cost + joint_cost) * 0.05
        elif self.powerhouse_material["tailrace material"] == "HDPE":
            pipe_cost = (0.00004 * (6) + 0.00008) * np.power((di_tailrace * 1000), 1.99) *self.powerhouse_data["tailrace length"]  # only pipe
            joint_cost = 0.0018 * np.power((di_tailrace* 1000), 2.18) *\
                         (self.powerhouse_data["tailrace length"] / self.penstock_data["joint distance"])
            bolts_cost = (pipe_cost + joint_cost) * 0.05
        tailrace_total_cost = (pipe_cost + joint_cost + bolts_cost)

        # Turbine price
        if self.powerhouse_material["turbine type"] == "FR":
            turbine_cost = (190.37 * np.power(self.penstock_data["height drop"], 1.27963) + 1441610.56*\
                            np.power((self.site_data["used_flow"] * 1000), 0.03064) +\
                            9.62402 * np.power(self.site_data["power"], 1.28487) - 1621571.28)*1.05*self.usd_conversion["eur_usd"]#1.05 inflation since 2016
        elif self.powerhouse_material["turbine type"] == "PE":
            turbine_cost = (1358677.67 * np.power(self.penstock_data["height drop"], 0.014) + 8489.85 *\
                            np.power((self.site_data["used_flow"] * 1000), 0.515) +\
                            3382.1 * np.power(self.site_data["power"], 0.416) - 1479160.63)*1.05*self.usd_conversion["eur_usd"]#1.05 inflation since 2016

        lightning_protection = self.powerhouse_material["lightning protection"]
        electrics_fix = self.powerhouse_material["electrics fix"]
        electrics_var = self.site_data["power"]*30 #30 USD kWh
        self.powerhouse_cost["material"] = round(roofing + gravel + tailrace_total_cost + turbine_cost + lightning_protection +\
                                           electrics_fix + electrics_var,0)

        self.powerhouse_storage["tailrace pipe total"] = round(tailrace_total_cost,0)
        self.powerhouse_storage["turbine_cost"] = round(turbine_cost,0)
        self.powerhouse_storage["electric_equipment_cost"] = round(lightning_protection + electrics_fix + electrics_var,0)
        self.powerhouse_storage["powerhouse_cost"]=round(self.powerhouse_cost["raw material"]+self.powerhouse_cost["material"]-\
                                                   turbine_cost-self.powerhouse_storage["electric_equipment_cost"],0)
        self.powerhouse_storage["pipe volume"] = round(np.pi * ((di_tailrace / 2) ** 2) * \
                                                     self.powerhouse_data["tailrace length"],0)
        self.powerhouse_storage["tailrace total cost"]=round(tailrace_total_cost,0)

    def calculate_powerhouse_labour(self):
        self.powerhouse_cost["excavation labour"] = (self.powerhouse_dimensions["excavation_vol"] *\
                                                     (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) *\
                                                    self.labour_cost["noskill_worker"]
        self.powerhouse_cost["laying"] = (self.powerhouse_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*\
                                         self.labour_cost["noskill_worker"]#gravel

        concreting_labour = (self.help1["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
        masonry_labour = (self.help2["structure_vol"] * self.labour_time["bricklaying"]) * self.labour_cost["skill_worker"]

        building_installation = round(8 * (self.labour_cost["skill_worker"] + self.labour_cost["noskill_worker"]),0) # 16h: roof, lightning protection
        tailrace_installation = round((self.powerhouse_data["tailrace length"] / self.penstock_data["joint distance"]) * 4 *\
                                (self.labour_cost["skill_worker"] + self.labour_cost["noskill_worker"]),0)
        turbine_installation = round(50 * (self.labour_cost["skill_worker"] + self.labour_cost["noskill_worker"]),0)
        electrical_installation = round(100 * (self.labour_cost["skill_worker"] + self.labour_cost["noskill_worker"]),0)

        hauling_cost = round((((self.help1["structure_vol"] + self.help2["structure_vol"] + self.powerhouse_dimensions["gravel_sqm"] *\
                          self.raw_material["gravel_thickness"] + self.help2["contact_sqm"] * self.raw_material["surface_finish"])*\
                         self.constants["p_structure"]) / 50) * 2 * self.labour_cost["hauling_cost"],0)

        self.powerhouse_cost["structure labour"] = round(concreting_labour + masonry_labour + hauling_cost,0)
        self.powerhouse_cost["installation labour"] = round(building_installation + tailrace_installation + \
                                                      turbine_installation + electrical_installation,0)
        self.powerhouse_storage["material"] = round(self.powerhouse_cost["raw material"] + self.powerhouse_cost["material"],0)
        self.powerhouse_storage["labour"] = round(self.powerhouse_cost["excavation labour"] + self.powerhouse_cost["structure labour"] +\
                                            self.powerhouse_cost["laying"]+self.powerhouse_cost["installation labour"],0)
        self.powerhouse_storage["turbine install"]=round(turbine_installation,0)
        self.powerhouse_storage["electrics install"]=round(electrical_installation,0)
        self.powerhouse_storage["powerhouse install"]=round(tailrace_installation+building_installation,0)
