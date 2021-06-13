import numpy as np
import RawMaterial as c_rm

class Penstock:
    def __init__(self,input_data):
        self.penstock_data=input_data.input_dict["penstock_data"]["dict"]
        self.penstock_material=input_data.input_dict["penstock_material"]["dict"]
        self.channel_material=input_data.input_dict["channel_material"]["dict"]
        self.total_penstock_cost
        #import relevant Dicts
        self.site_data = input_data.input_dict["site_data"]["dict"]
        self.labour_cost = input_data.input_dict["labour_cost"]["dict"]
        self.labour_time = input_data.input_dict["labour_time"]["dict"]
        self.raw_material = input_data.input_dict["raw_material"]["dict"]
        # Dict to store Dimensions
        self.penstock_dimensions= {}
        self.penstock_helpstorage = {}
        #Dict to store the Material cost, the labour cost miscellaneous
        self.penstock_cost={}

        #calls all other methods and returns the total intake cost and material volume in 2 dicts
    def total_penstock_cost(self):
        self.calculate_penstock_dimensions()
        self.calculate_penstock_material()
        self.calculate_penstock_labour()
        self.total_penstock_cost=sum(self.penstock_cost.values())
    def calculate_penstock_dimensions(self):
        v_penstock=self.penstock_data["velocity"]
        di_penstock=((4*(self.site_data["used_flow"])/v_penstock)/np.pi)**(0.5)
        di_spillway=self.penstock_data["di_spillway"] #have to run macro in Excel before running
        v_anker=np.pi*((di_penstock/4)**2)*4*di_penstock*((self.penstock_data["penstock length"])/10) #viertel durchmesser, 4fache länge von Durchmesser
        v_pressureblock=8 #to be changed later, minus diameter of penstock inside plus gravel

        excavation_vol=di_spillway*2.2*self.penstock_data["penstock length"]+v_anker+0.5*v_pressureblock # 1d deep, 2d width + gravel
        gravel_sqm=2*di_penstock*self.penstock_data["penstock length"] #to be edited later when v_pressureblock is available

        self.penstock_dimensions["excavation_vol"] = excavation_vol
        self.penstock_dimensions["structure_vol"] = v_anker+v_pressureblock
        self.penstock_dimensions["gravel_sqm"]=gravel_sqm
        self.penstock_dimensions["contact_sqm"]=4 #to be edited later when v_pressureblock is available

        self.penstock_helpstorage["pipe volume"]=(np.pi*((di_penstock/2)**2)+np.pi*((di_spillway/2)**2))*self.penstock_data["penstock length"]

    def calculate_penstock_material(self):
        di_penstock=(((4 * (self.site_data["used_flow"]) / self.penstock_data["velocity"]) / np.pi) ** (0.5))
        penstock_rcc =c_rm.Raw_Material(self.penstock_dimensions,self.raw_material)
        raw_mat_price=penstock_rcc.calculate_rcc()
        self.penstock_cost["raw material"] = raw_mat_price

        gravel=self.penstock_dimensions["gravel_sqm"]*0.1*self.raw_material["gravel"]
        vlies=self.penstock_dimensions["gravel_sqm"]*self.channel_material["drainage vlies"]
        mounting_bracket=self.penstock_material["mounting bracket"]*((self.penstock_data["penstock length"])/10)
        #calculate pipe cost for both penstock and spillway pipe
        if self.penstock_material["penstock material"] == "PVC":
            pipe1_cost= 0.00005*((self.penstock_data["height drop"]*1.5)/10)*np.power((di_penstock*1000),1.98)*self.penstock_data["penstock length"]# only pipe
            joint1_cost=0.0045*np.power((di_penstock*1000),1.98)*(self.penstock_data["penstock length"]/10)
            bolts1_cost=(pipe1_cost+joint1_cost)*0.1
            pipe2_cost = 0.00005*((self.penstock_data["height drop"]*1.5)/10)*np.power((self.penstock_data["di_spillway"]*1000),1.98)*self.penstock_data["penstock length"]
            joint2_cost = 0.0045*np.power((self.penstock_data["di_spillway"]*1000),1.98)*(self.penstock_data["penstock length"]/10)
            bolts2_cost = (pipe2_cost + joint2_cost) * 0.1
        elif self.penstock_material["penstock material"] == "HDPE":
            pipe1_cost = (0.00004*((self.penstock_data["height drop"]*1.5)/10)+0.00008)*np.power((di_penstock*1000),1.99)  # only pipe
            joint1_cost = 0.0018*np.power((di_penstock*1000),2.18)
            bolts1_cost = (pipe1_cost + joint1_cost) * 0.1
            pipe2_cost = (0.00004*((self.penstock_data["height drop"]*1.5)/10)+0.00008)*np.power((self.penstock_data["di_spillway"]*1000),1.99)
            joint2_cost = 0.0018*np.power((self.penstock_data["di_spillway"]*1000),2.18)
            bolts2_cost = (pipe2_cost + joint2_cost) * 0.1
        pipes_total_cost=pipe1_cost+pipe2_cost+joint1_cost+joint2_cost+bolts1_cost+bolts2_cost
        self.penstock_cost["material"]= gravel+vlies+mounting_bracket+pipes_total_cost
        #HDPE und PVC vlt nur durch Faktor unterscheiden bei den Kosten??
    def calculate_penstock_labour(self):
        self.penstock_cost["excavation labour"] = (self.penstock_dimensions["excavation_vol"] *\
                                                   (1.1123*np.exp(0.4774*self.site_data["excavating_factor"]))) * self.labour_cost["noskill_worker"]
        self.penstock_cost["laying"] = (self.penstock_dimensions["gravel_sqm"])*3*self.labour_time["laying"]*self.labour_cost["noskill_worker"]#gravel
        formwork_labour = self.penstock_dimensions["contact_sqm"] * self.labour_time["formwork"] * self.labour_cost["skill_worker"]
        concreting_labour = (self.penstock_dimensions["structure_vol"] * self.labour_time["concreting"]) * self.labour_cost["skill_worker"]
        hauling_cost = (((self.penstock_dimensions["structure_vol"] + self.penstock_dimensions["gravel_sqm"] * 0.1) * 2300) / 50) * 2 * self.labour_cost["hauling_cost"]
        self.penstock_cost["structure labour"] = formwork_labour + concreting_labour+hauling_cost
        self.penstock_cost["installation labour"] = (self.penstock_data["penstock length"] / 10)*4*(self.labour_cost["skill_worker"]+self.labour_cost["noskill_worker"]) #8 hours per 10m pipe
