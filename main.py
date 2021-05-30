import pandas as pd
import numpy as np
from openpyxl import load_workbook
import data_input as c_di
import Intake as c_in
import Channel as c_ch
import Sandtrap as c_st
import Penstock as c_ps
import Powerhouse as c_ph

# Read input files
c_di.data_storage.readingFunc()
input_data=c_di.data_storage.readingFunc.inputdata

#calculate cost for each part

intake_data=input_data.input_dict["intake_data"] ["dict"]
intake_material=input_data.input_dict["intake_material"]["dict"]

Intake = c_in.Intake(intake_data,intake_material)
Intake.total_intake_cost()
print("total intake cost")
print(Intake.total_intake_cost)  #total cost, detailed cost is stored in dict intake_cost

channel_data=input_data.input_dict["channel_data"] ["dict"]
channel_material=input_data.input_dict["channel_material"]["dict"]

Channel = c_ch.Channel(channel_data,channel_material)
Channel.total_channel_cost()
print("total channel cost")
print(Channel.total_channel_cost)  #total cost, detailed cost is stored in dict

sandtrap_data=input_data.input_dict["sandtrap_data"] ["dict"]
sandtrap_material=input_data.input_dict["sandtrap_material"]["dict"]

Sandtrap = c_st.Sandtrap(sandtrap_data,sandtrap_material)
Sandtrap.total_sandtrap_cost()
print("total sandtrap cost")
print(Sandtrap.total_sandtrap_cost)  #total cost, detailed cost is stored in dict

penstock_data=input_data.input_dict["penstock_data"] ["dict"]
penstock_material=input_data.input_dict["penstock_material"]["dict"]

Penstock = c_ps.Penstock(penstock_data,penstock_material)
Penstock.total_penstock_cost()
print("total penstock cost")
print(Penstock.total_penstock_cost)  #total cost, detailed cost is stored in dict

powerhouse_data=input_data.input_dict["powerhouse_data"] ["dict"]
powerhouse_material=input_data.input_dict["powerhouse_material"]["dict"]

Powerhouse = c_ph.Powerhouse(powerhouse_data,powerhouse_material)
Powerhouse.total_powerhouse_cost()
print("total powerhouse cost")
print(Powerhouse.total_powerhouse_cost)  #total cost, detailed cost is stored in dict

#dicts for country specific cost
country_data=input_data.input_dict["country_data"]["dict"]
site_data = c_di.data_storage.readingFunc.inputdata.input_dict["site_data"]["dict"]
labour_cost = c_di.data_storage.readingFunc.inputdata.input_dict["labour_cost"]["dict"]


#Calculate Miscellaneous cost for building structure (tools etc)
structure_misc_cost=(Intake.intake_cost["raw material"]+Channel.channel_cost["raw material"]+Sandtrap.sandtrap_cost["raw material"]+Penstock.penstock_cost["raw material"]+Powerhouse.powerhouse_cost["raw material"])*0.08#8% material for total masonry or concrete
#Calculate Miscellaneous cost for installations of penstock and powerhouse
installation_misc_cost=50 #to be edited later
print("misc material cost")
print(structure_misc_cost+installation_misc_cost)

#calculate import cost
Powerhouse.powerhouse_helpstorage["turbine_cost"]+Powerhouse.powerhouse_helpstorage["electric_equipment_cost"]*country_data["import tax"]
#calculate delivery to site (international port: turbine, pipes)
flight_cost =50*(0.05*site_data["used flow"]) #50 and 0.05 factor be edited later, dependent on used flow volume turbine and pipe size

    #transport cost for 1 truck 1 way international port
    #turbine: 1 truck, 35m^3 volume
if country_data["road_condition"]=="paved":
    int_vehicle_cost = (country_data["int_port_distance"])*((labour_cost["skill_worker"]*2*(1/70))+0.3*country_data["petrol_price"])*(0.05 * site_data["used flow"])*1.1 #1 way trip 1 vehicle 70km/h,40l/100km,*weight factor+10% marge
elif country_data["road_condition"]=="unpaved":
    int_vehicle_cost = (country_data["int_port_distance"])*((labour_cost["skill_worker"]*2*(1/30))+0.45*country_data["petrol_price"])*(0.05 * site_data["used flow"])*1.1 #30km/h,60l/100km,*weight factor+10% marge

pipes_transport_vol=Penstock.penstock_helpstorage["pipe volume"]+Powerhouse.powerhouse_helpstorage["pipe volume"]

int_transport_cost=int_vehicle_cost*(1+pipes_transport_vol/(35*0.8))*1.5 #1 vehicle for turbine, 0.8% of storage volume are used, 1.5 journeys per vehicle to pay

#calculate delivery to site (national port:building material)
if country_data["road_condition"]=="paved":
    nat_vehicle_cost = (country_data["nat_port_distance"])*((labour_cost["skill_worker"]*2*(1/70))+0.3*country_data["petrol_price"])*(0.05 * site_data["used flow"])*1.1 #70km/h,30l/100km,*weight factor+10% marge
elif country_data["road_condition"]=="unpaved":
    nat_vehicle_cost = (country_data["nat_port_distance"])*((labour_cost["skill_worker"]*2*(1/30))+0.45*country_data["petrol_price"])*(0.05 * site_data["used flow"])*1.1 #30km/h,45l/100km,*weight factor+10% marge

material_transport_vol=Intake.intake_dimensions["structure_vol"]+Channel.channel_dimensions["structure_vol"]+Sandtrap.sandtrap_dimensions["structure_vol"]+Penstock.penstock_dimensions["structure_vol"]+Powerhouse.powerhouse_dimensions["structure_vol"]
gravel_transport_vol=(Channel.channel_dimensions["gravel_sqm"]+Sandtrap.sandtrap_dimensions["gravel_sqm"]+Penstock.penstock_dimensions["gravel_sqm"]+Powerhouse.powerhouse_dimensions["gravel_sqm"])*0.1
total_transport_weight=(material_transport_vol+gravel_transport_vol)*2300 #estimated 2300kg/m^3 density

nat_transport_cost=nat_vehicle_cost*(1+total_transport_weight/3000)*1.5 #1 vehicle for rest of material, 3t per vehicle heavy material,1.5 journeys per vehicle to pay

#calculate transportation at site
hauling_cost=(country_data["walking_distance"]/0.85)*labour_cost["noskill_worker"]
transport_by_foot=hauling_cost*(total_transport_weight/40)*2 #40kg, walking speed 3km/h, 2 way

print("import and transport cost")
print(int_transport_cost)
print(flight_cost+int_transport_cost+nat_transport_cost+transport_by_foot)

#calculate risk on top for each division
#planning, währung,rohr,turbine,...
#=total investing cost

#calculate running cost labour
#calculate running cost material

#calculate running cost abbreviation
    #Intake+Channel+Sandtrap:50 years
waterway_depreciation=(Intake.total_intake_cost+Channel.total_channel_cost+Sandtrap.total_sandtrap_cost)/50
    #Penstock:30
penstock_depreciation=Penstock.total_penstock_cost/30
    #Powerhouse,TG-Gruppe:30
tg_group_depreciation=Powerhouse.powerhouse_helpstorage["turbine cost"]/30
    #Regler,electrical:20
electrical_depreciation=Powerhouse.powerhouse_helpstorage["electric_equipment_cost"]

#calculate totall.......
#wirtschaftlichkeit rechnung, annuitäten...

