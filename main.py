import DataInput as c_di
import Intake as c_in
import Channel as c_ch
import Sandtrap as c_st
import Penstock as c_ps
import Powerhouse as c_ph

# Read input files from DataInput Class
input_data_path = 'C:/Users/soere/PycharmProjects/HydroBA/HydroBA_Input.xlsm'
input_data = c_di.data_input(input_data_path)  # class with all dicts from Excel

#Calculate cost for each division
Intake = c_in.Intake(input_data)
Intake.total_intake_cost()
print("total intake cost")
print(Intake.total_intake_cost)  #total cost of Intake, detailed cost is stored in dict intake_cost

Channel = c_ch.Channel(input_data)
Channel.total_channel_cost()
print("total channel cost")
print(Channel.total_channel_cost)  #total cost of Channel, detailed cost is stored in dict

Sandtrap = c_st.Sandtrap(input_data)
Sandtrap.total_sandtrap_cost()
print("total sandtrap cost")
print(Sandtrap.total_sandtrap_cost)  #total cost of Sandtrap, detailed cost is stored in dict

Penstock = c_ps.Penstock(input_data)
Penstock.total_penstock_cost()
print("total penstock cost")
print(Penstock.total_penstock_cost)  #total cost of Penstock, detailed cost is stored in dict

Powerhouse = c_ph.Powerhouse(input_data)
Powerhouse.total_powerhouse_cost()
print("total powerhouse cost")
print(Powerhouse.total_powerhouse_cost)  #total cost of Powerhouse, detailed cost is stored in dict

#Import dicts for country specific cost calculation
country_data=input_data.input_dict["country_data"]["dict"]
site_data = input_data.input_dict["site_data"]["dict"]
labour_cost = input_data.input_dict["labour_cost"]["dict"]


#Calculate Miscellaneous cost for building structure (tools etc)
structure_misc_cost=(Intake.intake_cost["raw material"]+Channel.channel_cost["raw material"]+Sandtrap.sandtrap_cost["raw material"]+\
Penstock.penstock_cost["raw material"]+Powerhouse.powerhouse_cost["raw material"])*0.08#8% material for total masonry or concrete

#Calculate Miscellaneous cost of tools&material for installations of penstock and powerhouse
installation_misc_cost=50 #to be edited later
print("misc material cost")
print(structure_misc_cost+installation_misc_cost)

#calculate import cost
Powerhouse.powerhouse_helpstorage["turbine_cost"]+Powerhouse.powerhouse_helpstorage["electric_equipment_cost"]*country_data["import tax"]

#calculate delivery to site (international port: turbine, pipes)
flight_cost =50*(0.05*site_data["used_flow"]) #50 and 0.05 factor be edited later, dependent on used flow volume turbine and pipe size

#calculate delivery cost of 1 truckload to building site of goods that arrive in international port/airport: 1 truck 35m^3 volume 1 way from international port
if country_data["road_condition"]=="paved":
    int_vehicle_cost = (country_data["int_port_distance"])*((labour_cost["skill_worker"]*2*(1/70))+0.3*country_data["petrol_price"])*\
    (0.05 * site_data["used_flow"])*1.1 #1 way trip 1 vehicle 70km/h,40l/100km petrol,*weight factor+10% marge
elif country_data["road_condition"]=="unpaved":
    int_vehicle_cost = (country_data["int_port_distance"])*((labour_cost["skill_worker"]*2*(1/30))+0.45*country_data["petrol_price"])*\
    (0.05 * site_data["used flow"])*1.1 #30km/h,60l/100km petrol,*weight factor+10% marge

#calculate total pipe volume to be transported
pipes_transport_vol=Penstock.penstock_helpstorage["pipe volume"]+Powerhouse.powerhouse_helpstorage["pipe volume"]
#calculate the total transport cost for pipes and turbine from international port destination
int_transport_cost=int_vehicle_cost*(1+pipes_transport_vol/(35*0.8))*1.5 #1 vehicle for turbine, 0.8% of storage volume are used, 1.5 journeys per vehicle to pay

#calculate delivery cost of 1 truckload to building site from next big city where building material can be purchased (building material and other material)
if country_data["road_condition"]=="paved":
    nat_vehicle_cost = (country_data["nat_port_distance"])*((labour_cost["skill_worker"]*2*(1/70))+0.3*country_data["petrol_price"])*\
                       (0.05 * site_data["used_flow"])*1.1 #70km/h,30l/100km,*weight factor+10% marge
elif country_data["road_condition"]=="unpaved":
    nat_vehicle_cost = (country_data["nat_port_distance"])*((labour_cost["skill_worker"]*2*(1/30))+0.45*country_data["petrol_price"])*\
                       (0.05 * site_data["used flow"])*1.1 #30km/h,45l/100km,*weight factor+10% marge
#calculate total volume building material, estimate total weight
material_transport_vol=Intake.intake_dimensions["structure_vol"]+Channel.channel_dimensions["structure_vol"]+Sandtrap.sandtrap_dimensions["structure_vol"]+\
                       Penstock.penstock_dimensions["structure_vol"]+Powerhouse.powerhouse_dimensions["structure_vol"]
gravel_transport_vol=(Channel.channel_dimensions["gravel_sqm"]+Sandtrap.sandtrap_dimensions["gravel_sqm"]+Penstock.penstock_dimensions["gravel_sqm"]+\
                      Powerhouse.powerhouse_dimensions["gravel_sqm"])*0.1
total_transport_weight=(material_transport_vol+gravel_transport_vol)*2300 #estimated 2300kg/m^3 density
#calculate the total transport cost for building material from next city
nat_transport_cost=nat_vehicle_cost*(1+total_transport_weight/3000)*1.5 #1 vehicle for rest of material, 3t per vehicle heavy material,1.5 journeys per vehicle to pay

#calculate transportation at site by workers
hauling_cost=(site_data["walking_distance"]/0.85)*labour_cost["noskill_worker"]
transport_by_foot=hauling_cost*(total_transport_weight/50)*2 #50kg, walking speed 3km/h, 2 way

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
tg_group_depreciation=Powerhouse.powerhouse_helpstorage["turbine_cost"]/30
    #Regler,electrical:20
electrical_depreciation=Powerhouse.powerhouse_helpstorage["electric_equipment_cost"]

#calculate totall.......
#wirtschaftlichkeit rechnung, annuitäten...

