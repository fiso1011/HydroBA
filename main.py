import DataInput as c_di
import Intake as c_in
import Channel as c_ch
import Sandtrap as c_st
import Penstock as c_ps
import Powerhouse as c_ph

# Read input files from DataInput Class
input_data_path = 'C:/Users/soere/PycharmProjects/HydroBA/HydroBA_Input.xlsm'
input_data = c_di.data_input(input_data_path)  # class with all dicts from Excel

# Calculate cost for each division
Intake = c_in.Intake(input_data)
Intake.total_intake_cost()
print("total intake cost")
print(Intake.total_intake_cost)  # total cost of Intake, detailed cost is stored in dict intake_cost

Channel = c_ch.Channel(input_data)
Channel.total_channel_cost()
print("total channel cost")
print(Channel.total_channel_cost)  # total cost of Channel, detailed cost is stored in dict

Sandtrap = c_st.Sandtrap(input_data)
Sandtrap.total_sandtrap_cost()
print("total sandtrap cost")
print(Sandtrap.total_sandtrap_cost)  # total cost of Sandtrap, detailed cost is stored in dict

Penstock = c_ps.Penstock(input_data)
Penstock.total_penstock_cost()
print("total penstock cost")
print(Penstock.total_penstock_cost)  # total cost of Penstock, detailed cost is stored in dict

Powerhouse = c_ph.Powerhouse(input_data)
Powerhouse.total_powerhouse_cost()
print("powerhouse cost")
print(Powerhouse.total_powerhouse_cost-Powerhouse.powerhouse_storage["turbine_cost"])  # total cost of Powerhouse, detailed cost is stored in dict
print("turbine cost")
print(Powerhouse.powerhouse_storage["turbine_cost"])

# Import dicts for country specific cost calculation
country_data = input_data.input_dict["country_data"]["dict"]
site_data = input_data.input_dict["site_data"]["dict"]
labour_cost = input_data.input_dict["labour_cost"]["dict"]

# Calculate Miscellaneous cost for building structure (tools etc)
structure_misc_cost = (Intake.intake_cost["raw material"] + Channel.channel_cost["raw material"] +
                       Sandtrap.sandtrap_cost["raw material"] + Penstock.penstock_cost["raw material"] +\
                       Powerhouse.powerhouse_cost["raw material"]) * 0.05  # 5% material for total masonry or concrete

# Calculate Miscellaneous cost of tools&material for installations of electrics
installation_misc_cost = Powerhouse.powerhouse_cost["material"] * 0.05  # 5% material and tools
print("misc material cost")
print(structure_misc_cost + installation_misc_cost)

# calculate import cost
import_cost = (Powerhouse.powerhouse_storage["turbine_cost"] + Powerhouse.powerhouse_storage[
    "electric_equipment_cost"]) * country_data["import tax"]

# calculate delivery to site (international port: turbine, pipes)
flight_cost = 5500  # 1000kg turbine (gibt es hier Unterschiede zwischen Typen? Gewicht als Input?

# calculate delivery cost of 1 truckload to building site of goods that arrive in international port/airport:1 way from international port
turbine_transport_cost0 = country_data["truck_cost"] * country_data["int_port_distance"] * 1  # imported turbine 1 ton

# calculate total pipe volume to be transported
pipes_transport_volume = (Penstock.penstock_storage["pipe volume"] + Powerhouse.powerhouse_storage["pipe volume"])  # 0,66
if (pipes_transport_volume / 0.8) < 35:
    pipe_transport_cost0 = country_data["truck_cost"] * country_data["int_port_distance"] * 1
else:
    pipe_transport_cost0 = country_data["truck_cost"] * country_data["int_port_distance"] * (pipes_transport_volume / (35 * 0.8))  # 80% of Volume used

# calculate total volume building material, estimate total weight
material_transport_vol = Intake.intake_dimensions["structure_vol"] + Channel.channel_dimensions["structure_vol"] + \
                         Sandtrap.sandtrap_dimensions["structure_vol"] + Penstock.penstock_dimensions["structure_vol"] + \
                         Powerhouse.powerhouse_dimensions["structure_vol"]
gravel_transport_vol = (Channel.channel_dimensions["gravel_sqm"] + Sandtrap.sandtrap_dimensions["gravel_sqm"] +
                        Penstock.penstock_dimensions["gravel_sqm"] + Powerhouse.powerhouse_dimensions[
                            "gravel_sqm"]) * 0.1
structure_transport_weight = (material_transport_vol * 2300 + gravel_transport_vol * 1500) / 1000  # estimated density

# calculate the total transport cost for building material from next city
nat_transport_cost0 = country_data["ton_km_cost"] * structure_transport_weight * country_data["nat_port_distance"]

if country_data["road_condition"]=="paved":
    transport_cost_1=(turbine_transport_cost0+pipe_transport_cost0+nat_transport_cost0)*1
elif country_data["road_condition"]=="gravel":
    transport_cost_1 = (turbine_transport_cost0 + pipe_transport_cost0 + nat_transport_cost0) * 1.5
elif country_data["road_condition"] == "paved":
    transport_cost_1 = (turbine_transport_cost0 + pipe_transport_cost0 + nat_transport_cost0) * 2.5
total_import_transport = import_cost + flight_cost + transport_cost_1
print("import and transport cost")
print(total_import_transport)
#total powerplant cost
powerplant_cumulated_cost=Intake.total_intake_cost+Channel.total_channel_cost+Sandtrap.total_sandtrap_cost+Penstock.total_penstock_cost+ \
                      Powerhouse.total_powerhouse_cost+structure_misc_cost+installation_misc_cost+total_import_transport
planning_cost=powerplant_cumulated_cost*0.08
total_powerplant_cost=powerplant_cumulated_cost+planning_cost
print("Total Powerplant Cost")
print(total_powerplant_cost)

# calculate risk on top for each division
intake_mat_risk=Intake.intake_storage["material"]*0.1
channel_mat_risk=Channel.channel_storage["material"]*0.1
sandtrap_mat_risk=Sandtrap.sandtrap_storage["material"]*0.1
penstock_mat_risk=Penstock.penstock_storage["material"]*0.1
powerhouse_mat_risk=(Powerhouse.powerhouse_storage["material"]-Powerhouse.powerhouse_storage["turbine total"]-\
                     Powerhouse.powerhouse_storage["electric_equipment_cost"])*0.1
turbine_mat_risk=Powerhouse.powerhouse_storage["turbine total"]*0.1
electric_mat_risk=Powerhouse.powerhouse_storage["electric_equipment_cost"]*0.1
powerhouse_total_mat_risk=turbine_mat_risk+electric_mat_risk+powerhouse_mat_risk
total_rawmaterial_risk=intake_mat_risk+channel_mat_risk+sandtrap_mat_risk+penstock_mat_risk+powerhouse_total_mat_risk


intake_labour_risk=Intake.intake_storage["labour"]*0.1
channel_labour_risk=Channel.channel_storage["labour"]*0.1
sandtrap_labour_risk=Sandtrap.sandtrap_storage["labour"]*0.1
penstock_labour_risk=Penstock.penstock_storage["labour"]*0.1
powerhouse_labour_risk=Powerhouse.powerhouse_storage["labour"]*0.1
total_labour_risk=intake_labour_risk+channel_labour_risk+sandtrap_labour_risk+penstock_labour_risk+powerhouse_labour_risk

misc_risk=(installation_misc_cost+structure_misc_cost)*0.3
transport_risk=(transport_cost_1+flight_cost)*0.25
currency_risk=(Powerhouse.powerhouse_cost["material"]+Penstock.penstock_cost["material"])*0.05

#total risk
total_risk=total_rawmaterial_risk+total_labour_risk+misc_risk+transport_risk+currency_risk

# total investing cost
total_investing_cost=total_powerplant_cost+total_risk # single risk factors
print("Total Investment")
print(total_investing_cost)

# calculate running cost abbreviation
# Intake+Channel+Sandtrap:50 years
waterway_risk=intake_mat_risk+intake_labour_risk+channel_mat_risk+channel_labour_risk+sandtrap_mat_risk+sandtrap_labour_risk
waterway_depreciation = (Intake.total_intake_cost + Channel.total_channel_cost + Sandtrap.total_sandtrap_cost+waterway_risk) / 50
# Penstock:30
penstock_depreciation = (Penstock.total_penstock_cost+penstock_mat_risk+penstock_labour_risk) / 40
# Powerhouse,TG-Gruppe:30
turbine_depreciation = (Powerhouse.powerhouse_storage["turbine_cost"]+turbine_mat_risk) / 30
# Regler,electrical:20
electrical_depreciation = (Powerhouse.powerhouse_storage["electric_equipment_cost"]+electric_mat_risk)/20
#Powerhouse: 40 (roof, tailrace average)
powerhouse_depreciation=(Powerhouse.powerhouse_storage["material"]-Powerhouse.powerhouse_storage["turbine total"]-\
                         Powerhouse.powerhouse_storage["electric_equipment_cost"]+powerhouse_mat_risk+powerhouse_labour_risk)/40
powerhouse_total_depreciation=turbine_depreciation+electrical_depreciation+powerhouse_depreciation
#remaining depreciation
remaining_depreciation=(misc_risk+transport_risk+currency_risk)/30
# calculate running cost labour & material
om_annual_cost=total_investing_cost*0.03
# calculate total annual cost
total_annual_cost=waterway_depreciation+penstock_depreciation+turbine_depreciation+electrical_depreciation+powerhouse_depreciation+remaining_depreciation+om_annual_cost
print("total annual cost")
print(total_annual_cost)

#plant hours uptime
plant_hours=365*(5/7)*24*(12/24)*0.9 #5 work days, 12h working hours, 90% uptime
total_kwh=site_data["power"]*0.5*plant_hours #50% average of used flow
print("total kwh")
print(total_kwh)

print(total_annual_cost/total_kwh)
# wirtschaftlichkeit rechnung, annuitäten...

# plant hours uptime

#Unsicherheiten, Höhe Volumen Variation
#Sensitivitäten