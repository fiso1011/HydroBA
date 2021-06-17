import DataInput as c_di
import Intake as c_in
import Channel as c_ch
import Sandtrap as c_st
import Penstock as c_ps
import Powerhouse as c_ph
import matplotlib.pyplot as plt
import numpy as np

# Read input files from DataInput Class
input_data_path = 'C:/Users/soere/PycharmProjects/HydroBA/HydroBA_Input.xlsm'
input_data = c_di.data_input(input_data_path)  # class with all dicts from Excel

# Calculate cost for each division
Intake = c_in.Intake(input_data)
Intake.total_intake_cost()
Channel = c_ch.Channel(input_data)
Channel.total_channel_cost()
Sandtrap = c_st.Sandtrap(input_data)
Sandtrap.total_sandtrap_cost()
Penstock = c_ps.Penstock(input_data)
Penstock.total_penstock_cost()
Powerhouse = c_ph.Powerhouse(input_data)
Powerhouse.total_powerhouse_cost()
cumulated_divisions_0=Intake.total_intake_cost+Channel.total_channel_cost+Sandtrap.total_sandtrap_cost+\
                        Penstock.total_penstock_cost+Powerhouse.total_powerhouse_cost

# Import dicts for country specific cost calculation
country_data = input_data.input_dict["country_data"]["dict"]
site_data = input_data.input_dict["site_data"]["dict"]
labour_cost = input_data.input_dict["labour_cost"]["dict"]
constants=input_data.input_dict["constants"]["dict"]
raw_material=input_data.input_dict["raw_material"]["dict"]

# Calculate Miscellaneous cost
structure_misc_cost = (Intake.intake_cost["raw material"] + Channel.channel_cost["raw material"] +
                       Sandtrap.sandtrap_cost["raw material"] + Penstock.penstock_cost["raw material"] +\
                       Powerhouse.powerhouse_cost["raw material"]) * 0.015  # 1,5% for tools etc.
installation_misc_cost = (Penstock.penstock_cost["material"]+Powerhouse.powerhouse_cost["material"]) * 0.015

# calculate import cost
turbine_import_cost = Powerhouse.powerhouse_storage["turbine_cost"] * country_data["import tax"]
electrics_import_cost=Powerhouse.powerhouse_storage["electric_equipment_cost"]* country_data["import tax"]
pipe_import_cost=(Penstock.penstock_storage["penstock pipe total"]+Powerhouse.powerhouse_storage["tailrace total cost"])*\
                 country_data["import tax"]
total_import_cost=turbine_import_cost+electrics_import_cost+pipe_import_cost

# calculate turbine transport cost without road factor
turbine_flight_cost = 4000  # 750kg turbine (gibt es hier Unterschiede zwischen Typen? Gewicht als Input?
turbine_transport_0 = labour_cost["truck_cost"] * country_data["int_port_distance"] * 1  # imported turbine 1 ton

# calculate pipe transport cost without road factor
pipes_transport_volume = (Penstock.penstock_storage["pipe volume"] + Powerhouse.powerhouse_storage["pipe volume"])
if (pipes_transport_volume*2) < 35:
    pipe_transport_0 = labour_cost["truck_cost"] * country_data["int_port_distance"] * 1
else:
    pipe_transport_0 = labour_cost["truck_cost"] * country_data["int_port_distance"] * (pipes_transport_volume*2 / (35))

# calculate the transport cost for building material from next city without road factor
p_s=(constants["p_structure"]/1000)
p_g=(constants["p_gravel"]/1000)
g_t=raw_material["gravel_thickness"]
intake_transport_weight = Intake.intake_dimensions["structure_vol"]*p_s
channel_transport_weight=Channel.channel_dimensions["structure_vol"]*p_s+Channel.channel_dimensions["gravel_sqm"]*p_g*g_t
sandtrap_transport_weight=Sandtrap.sandtrap_dimensions["structure_vol"]*p_s+Sandtrap.sandtrap_dimensions["gravel_sqm"]*p_g*g_t
penstock_transport_weight=Penstock.penstock_dimensions["structure_vol"]*p_s+Penstock.penstock_dimensions["gravel_sqm"]*p_g*g_t
powerhouse_transport_weight=Powerhouse.powerhouse_dimensions["structure_vol"]*p_s+Powerhouse.powerhouse_dimensions["gravel_sqm"]*p_g*g_t
#total structure weight and material transport cost without road factor
structure_transport_weight = (intake_transport_weight+channel_transport_weight+sandtrap_transport_weight+\
                              penstock_transport_weight+powerhouse_transport_weight)  # estimated density
mat_transport_0 = labour_cost["ton_km_cost"] * structure_transport_weight * country_data["nat_port_distance"]

#calculate total transport cost with road factor
if country_data["road_condition"]=="paved":
    turbine_transport=turbine_transport_0*1
    pipe_transport=pipe_transport_0*1
    mat_transport=mat_transport_0*1
elif country_data["road_condition"]=="gravel":
    turbine_transport = turbine_transport_0 * 1.5
    pipe_transport = pipe_transport_0 * 1.5
    mat_transport = mat_transport_0 * 1.5
elif country_data["road_condition"] == "paved":
    turbine_transport = turbine_transport_0 * 2.5
    pipe_transport = pipe_transport_0 * 2.5
    mat_transport = mat_transport_0 * 2.5
total_import_transport=turbine_flight_cost+total_import_cost+pipe_transport+turbine_transport+mat_transport

#total powerplant cost
cumulated_divisions_cost=cumulated_divisions_0+structure_misc_cost+installation_misc_cost+total_import_transport
planning_cost=cumulated_divisions_cost*0.08
cumulated_powerplant_cost=cumulated_divisions_cost+planning_cost

# calculate risk on top for each division
intake_risk=(Intake.intake_storage["material"]+Intake.intake_storage["labour"])*0.1
channel_risk=(Channel.channel_storage["material"]+Channel.channel_storage["labour"])*0.2 #geo obstacles
sandtrap_risk=(Sandtrap.sandtrap_storage["material"]+Sandtrap.sandtrap_storage["labour"])*0.2 #complex geometry
penstock_risk=(Penstock.penstock_storage["material"]+Penstock.penstock_storage["labour"])*0.1
pipe_risk=Penstock.penstock_storage["penstock pipe total"]*0.1
powerhouse_risk=(Powerhouse.powerhouse_storage["powerhouse_cost"]+Powerhouse.powerhouse_storage["labour"])*0.1
turbine_risk=Powerhouse.powerhouse_storage["turbine_cost"]*0.1
electric_risk=Powerhouse.powerhouse_storage["electric_equipment_cost"]*0.1
powerhouse_total_risk=turbine_risk+electric_risk+powerhouse_risk

misc_risk=(installation_misc_cost+structure_misc_cost)*0.2
planning_risk=planning_cost*0.1

turbine_transport_risk=(turbine_flight_cost+turbine_transport)*0.25
pipe_transport_risk=pipe_transport*0.25
mat_transport_risk=mat_transport*0.1

pipe_currency_risk=(Penstock.penstock_storage["penstock pipe total"]+Powerhouse.powerhouse_storage["tailrace total cost"])*0.05
turbine_currency_risk=Powerhouse.powerhouse_storage["turbine_cost"]*0.05
electrics_currency_risk=Powerhouse.powerhouse_storage["electric_equipment_cost"]*0.05

#Split material transport cost on each division
intake_transport=(mat_transport+mat_transport_risk)*(intake_transport_weight/structure_transport_weight)
channel_transport=(mat_transport+mat_transport_risk)*(channel_transport_weight/structure_transport_weight)
sandtrap_transport=(mat_transport+mat_transport_risk)*(sandtrap_transport_weight/structure_transport_weight)
penstock_transport=(mat_transport+mat_transport_risk)*(penstock_transport_weight/structure_transport_weight)
powerhouse_transport=(mat_transport+mat_transport_risk)*(powerhouse_transport_weight/structure_transport_weight)

pipe_transport_cost=pipe_transport+pipe_transport_risk
turbine_transport_cost=turbine_transport+turbine_transport_risk+turbine_flight_cost

# total investing cost
intake_invest=Intake.total_intake_cost+intake_risk+intake_transport
channel_invest=Channel.total_channel_cost+channel_risk+channel_transport
sandtrap_invest=Sandtrap.total_sandtrap_cost+sandtrap_risk+sandtrap_transport
penstock_invest=Penstock.total_penstock_cost+pipe_import_cost+penstock_transport+pipe_transport_cost+\
                pipe_transport_risk+penstock_risk+pipe_risk+pipe_currency_risk
powerhouse_invest=Powerhouse.powerhouse_storage["powerhouse_cost"]+powerhouse_transport+powerhouse_risk
turbine_invest=Powerhouse.powerhouse_storage["turbine_cost"]+turbine_flight_cost+turbine_import_cost+\
               turbine_transport_cost+turbine_risk+turbine_transport_risk+turbine_currency_risk
electrics_invest=Powerhouse.powerhouse_storage["electric_equipment_cost"]+electric_risk+electrics_import_cost+\
                 electrics_currency_risk
misc_invest=structure_misc_cost+installation_misc_cost+misc_risk
planning_invest=planning_cost+planning_risk

total_investing_cost=intake_invest+channel_invest+sandtrap_invest+penstock_invest+powerhouse_invest+\
                     turbine_invest+electrics_invest+planning_invest+misc_invest
print("Intake")
print(intake_invest)
print("Channel")
print(channel_invest)
print("Sandtrap")
print(sandtrap_invest)
print("Penstock")
print(penstock_invest)
print("Powerhouse")
print(powerhouse_invest)
print("Turbine")
print(turbine_invest)
print("Electrics")
print(electrics_invest)
print("Planning")
print(planning_invest)
print("Miscellaneous")
print(misc_invest)
print("Total Investment")
print(total_investing_cost)

# calculate running cost abbreviation
waterway_depreciation = (intake_invest+channel_invest+sandtrap_invest) / 50
penstock_depreciation = (penstock_invest) / 40
rest_depreciation=(misc_risk+planning_invest)/20

if site_data["turbine_abrasion"]=="high":
    turbine_depreciation = (turbine_invest) / 30
elif site_data["turbine_abrasion"]=="normal":
    turbine_depreciation = (turbine_invest) / 45
elif site_data["turbine_abrasion"] == "normal":
    turbine_depreciation = (turbine_invest) / 60
electrical_depreciation = (electrics_invest)/20
powerhouse_depreciation=(powerhouse_invest)/40
powerhouse_total_depreciation=turbine_depreciation+electrical_depreciation+powerhouse_depreciation

# calculate running cost labour & material
om_annual_cost=total_investing_cost*0.03
# calculate total annual cost
total_annual_cost=waterway_depreciation+penstock_depreciation+powerhouse_total_depreciation+\
                  rest_depreciation+om_annual_cost
print("total annual cost")
print(total_annual_cost)

#plant hours uptime
plant_hours=365*(6/7)*24*(12/24)*0.9 #5 work days, 12h working hours, 90% uptime
total_kwh=site_data["power"]*0.6*plant_hours #60% average of used flow
print("total kwh")
print(total_kwh)
#print average cost per kWh
print("USD/kwh")
print(total_annual_cost/total_kwh)
print("Turbine percent")
print(turbine_invest/total_investing_cost)
print(Powerhouse.powerhouse_storage["turbine_cost"])

# wirtschaftlichkeit rechnung, annuitäten...
#Sensitivitäten

x=np.array(["Wasserbau","Fallrohr","Maschinenhaus","Turbine","Elektrik","Planung&Sonstiges"])
y=np.array([(intake_invest+channel_invest+sandtrap_invest),penstock_invest,powerhouse_invest,\
            turbine_invest,electrics_invest,(planning_invest+misc_invest)])

plt.bar(x,y)
plt.grid()
xpoints = np.array([2, 3])
ypoints = np.array([10000, 10000])

plt.plot(xpoints, ypoints, 'o')
plt.show()

