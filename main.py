import DataInput as c_di
import Intake as c_in
import Channel as c_ch
import Sandtrap as c_st
import Penstock as c_ps
import Powerhouse as c_ph
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

runversion=input("Version eingeben")

# Read input files from DataInput Class
input_data_path = 'C:/Users/soere/PycharmProjects/HydroBA/HydroBA_Input_test.xlsm'
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
currency=input_data.input_dict["currency"]["dict"]

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
elif country_data["road_condition"] == "unsurfaced":
    turbine_transport = turbine_transport_0 * 2.5
    pipe_transport = pipe_transport_0 * 2.5
    mat_transport = mat_transport_0 * 2.5
total_import_transport=turbine_flight_cost+total_import_cost+pipe_transport+turbine_transport+mat_transport

#total powerplant cost
cumulated_divisions_cost=cumulated_divisions_0+structure_misc_cost+installation_misc_cost+total_import_transport
planning_cost=cumulated_divisions_cost*country_data["planning_cost"]
cumulated_powerplant_cost=cumulated_divisions_cost+planning_cost

# calculate risk on top for each division
intake_risk=(Intake.intake_storage["material"]+Intake.intake_storage["labour"])*0.1
channel_risk=(Channel.channel_storage["material"]+Channel.channel_storage["labour"])*0.15 #geo obstacles
sandtrap_risk=(Sandtrap.sandtrap_storage["material"]+Sandtrap.sandtrap_storage["labour"])*0.15 #complex geometry
penstock_risk=(Penstock.penstock_storage["material"]+Penstock.penstock_storage["labour"])*0.1
pipe_risk=Penstock.penstock_storage["penstock pipe total"]*0.1
powerhouse_risk=(Powerhouse.powerhouse_storage["powerhouse_cost"]+Powerhouse.powerhouse_storage["labour"])*0.1
turbine_risk=Powerhouse.powerhouse_storage["turbine_cost"]*0.1
electric_risk=Powerhouse.powerhouse_storage["electric_equipment_cost"]*0.1
powerhouse_total_risk=turbine_risk+electric_risk+powerhouse_risk

misc_risk=(installation_misc_cost+structure_misc_cost)*0.15
planning_risk=planning_cost*0.1

turbine_transport_risk=(turbine_flight_cost+turbine_transport)*0.2
pipe_transport_risk=pipe_transport*0.2
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
intake_invest=Intake.total_intake_cost+intake_transport+intake_risk
channel_invest=Channel.total_channel_cost+channel_transport+channel_risk
sandtrap_invest=Sandtrap.total_sandtrap_cost+sandtrap_transport+sandtrap_risk
penstock_invest=(Penstock.penstock_storage["material"])+Penstock.penstock_storage["labour"]+(pipe_import_cost+penstock_transport+pipe_transport_cost)+(pipe_transport_risk+penstock_risk+pipe_risk+pipe_currency_risk)
powerhouse_invest=Powerhouse.powerhouse_storage["powerhouse_cost"]+Powerhouse.powerhouse_storage["powerhouse install"]+Powerhouse.powerhouse_cost["structure labour"]+powerhouse_transport+powerhouse_risk
turbine_invest=Powerhouse.powerhouse_storage["turbine_cost"]+Powerhouse.powerhouse_storage["turbine install"]+turbine_flight_cost+turbine_import_cost+turbine_transport_cost+turbine_risk+turbine_transport_risk+turbine_currency_risk
electrics_invest=Powerhouse.powerhouse_storage["electric_equipment_cost"]+Powerhouse.powerhouse_storage["electrics install"]+(Powerhouse.powerhouse_storage["electrics install"]*0.1+electrics_import_cost)+(electric_risk+electrics_currency_risk+Powerhouse.powerhouse_storage["electrics install"]*0.1*0.1)
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
crf_60=(currency["capital_cost"]*np.power(1+currency["capital_cost"],60))/(np.power(1+currency["capital_cost"],60)-1)
crf_50=(currency["capital_cost"]*np.power(1+currency["capital_cost"],50))/(np.power(1+currency["capital_cost"],50)-1)
crf_45=(currency["capital_cost"]*np.power(1+currency["capital_cost"],45))/(np.power(1+currency["capital_cost"],45)-1)
crf_40=(currency["capital_cost"]*np.power(1+currency["capital_cost"],40))/(np.power(1+currency["capital_cost"],40)-1)
crf_30=(currency["capital_cost"]*np.power(1+currency["capital_cost"],30))/(np.power(1+currency["capital_cost"],30)-1)
crf_20=(currency["capital_cost"]*np.power(1+currency["capital_cost"],20))/(np.power(1+currency["capital_cost"],20)-1)

waterway_annuity = (intake_invest+channel_invest+sandtrap_invest) *crf_50
penstock_annuity = (penstock_invest) *crf_40
rest_annuity=(misc_risk+planning_invest)*crf_20

if site_data["turbine_abrasion"]=="high":
    turbine_annuity = (turbine_invest)*crf_30
elif site_data["turbine_abrasion"]=="normal":
    turbine_annuity = (turbine_invest)*crf_45
elif site_data["turbine_abrasion"] == "normal":
    turbine_annuity = (turbine_invest)*crf_60
electrical_annuity = (electrics_invest)*crf_20
powerhouse_annuity=(powerhouse_invest)*crf_40
powerhouse_total_annuity=turbine_annuity+powerhouse_annuity+electrical_annuity

# calculate running cost labour & material
om_annual_cost=total_investing_cost*0.03
# calculate total annual cost
total_annual_cost=(waterway_annuity+penstock_annuity+powerhouse_total_annuity+rest_annuity)+om_annual_cost
print("total annual cost")
print(total_annual_cost)

#plant hours uptime
plant_hours=365*24*(6/7)*site_data["usage_factor"]#50% used
total_kwh=site_data["power"]*plant_hours*0.8 #water flow average
print("total kwh")
print(total_kwh)
#print average cost per kWh
print("USD/kwh")
lcoe=total_annual_cost/total_kwh
print(lcoe)

print("Turbine percent")
t_percent=turbine_invest/total_investing_cost
print(t_percent)

#Export into Excel
dataframe = {'Kostenart': ['Zulauf','Kanal','Sandfang','Fallrohr','Maschinenhaus','Turbine','Elektrik','Planung','Sonstiges','Summe','Annuität','Leistung in kwH','USD/kWh','Turbine Anteil'],
        'Kosten': [intake_invest,channel_invest,sandtrap_invest,penstock_invest,powerhouse_invest,turbine_invest,electrics_invest,planning_invest,misc_invest,total_investing_cost,total_annual_cost,total_kwh,lcoe,t_percent]
        }

df = pd.DataFrame(dataframe, columns = ['Kostenart', 'Kosten'])
string1="C:/Users/soere/PycharmProjects/HydroBA/Output/Kosten_Output_"
string2=str(runversion)
string3=".xlsx"
string4=string1+string2+string3
# storing into the excel file
df.to_excel(string4)
print("Exported to Excel")

#Plot using different methods
def plot_bar_chart():
    #BAR CHART
    # Creating our own dataframe
    #https://www.geeksforgeeks.org/how-to-annotate-bars-in-barplot-with-matplotlib-in-python/
    data = {"Name": ["Wasserbau","Fallrohr","Maschinenhaus","Turbine","Elektrik","Planung&Sonstiges"],
            "Cost": [(intake_invest+channel_invest+sandtrap_invest),penstock_invest,powerhouse_invest,\
                turbine_invest,electrics_invest,(planning_invest+misc_invest)]}

    # Now convert this dictionary type data into a pandas dataframe
    # specifying what are the column names
    df = pd.DataFrame(data, columns=['Name', 'Cost'])

    # Defining the plot size
    plt.figure(figsize=(8, 8))

    # Defining the values for x-axis, y-axis
    # and from which datafarme the values are to be picked
    plots = sns.barplot(x="Name", y="Cost", data=df)

    # Iterrating over the bars one-by-one
    for bar in plots.patches:
        # Using Matplotlib's annotate function and
        # passing the coordinates where the annotation shall be done
        # x-coordinate: bar.get_x() + bar.get_width() / 2
        # y-coordinate: bar.get_height()
        # free space to be left to make graph pleasing: (0, 8)
        # ha and va stand for the horizontal and vertical alignment
        plots.annotate(format(bar.get_height(), '.2f'),
                       (bar.get_x() + bar.get_width() / 2,
                        bar.get_height()), ha='center', va='center',
                       size=15, xytext=(0, 8),
                       textcoords='offset points')

    # Setting the label for x-axis
    plt.xlabel("Abschnitte", size=14)

    # Setting the label for y-axis
    plt.ylabel("Dollar", size=14)

    # Setting the title for the graph
    plt.title("Kosten der Abschnitte")

    # Fianlly showing the plot
    # https://riptutorial.com/matplotlib/example/14063/plot-with-gridlines
    # Show the major grid lines with dark grey lines
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    # Show the minor grid lines with very faint and almost transparent grey lines
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()
    plt.show()

def plot_pie_chart():
        #PIE CHART
        labels=["Wasserbau","Fallrohr","Maschinenhaus","Turbine","Elektrik","Planung&Sonstiges"]
        sizes=[((intake_invest+channel_invest+sandtrap_invest)/total_investing_cost),\
                    (penstock_invest/total_investing_cost),(powerhouse_invest/total_investing_cost),\
                    (turbine_invest/total_investing_cost),(electrics_invest/total_investing_cost),\
                    ((planning_invest+misc_invest)/total_investing_cost)]
        plt.pie(sizes,labels=labels,autopct='%1.2f%%')
        plt.show()

def plot_bar2_chart():
    #https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html#sphx-glr-gallery-lines-bars-and-markers-bar-stacked-py
    #BAR CHART 2, Cost of the sections without risk added
    N = 5
    material = ((Intake.intake_storage["material"]+Channel.channel_storage["material"]+Sandtrap.sandtrap_storage["material"]),\
    Penstock.penstock_storage["material"],Powerhouse.powerhouse_storage["powerhouse_cost"], Powerhouse.powerhouse_storage["turbine_cost"],\
                Powerhouse.powerhouse_storage["electric_equipment_cost"])
    labour = ((Intake.intake_storage["labour"]+Channel.channel_storage["labour"]+Sandtrap.sandtrap_storage["labour"]),\
              Penstock.penstock_storage["labour"], (Powerhouse.powerhouse_storage["powerhouse install"]+Powerhouse.powerhouse_cost["structure labour"]),\
              Powerhouse.powerhouse_storage["turbine install"],Powerhouse.powerhouse_storage["electrics install"])
    addedvalues=tuple(map(sum, zip(material, labour)))
    transport = ((intake_transport+channel_transport+sandtrap_transport),(pipe_import_cost+penstock_transport+pipe_transport_cost),\
                 powerhouse_transport,(turbine_flight_cost+turbine_import_cost+turbine_transport_cost),\
                 (Powerhouse.powerhouse_storage["electrics install"]*0.1+electrics_import_cost))
    totalStd = ((intake_risk+channel_risk+sandtrap_risk), (pipe_transport_risk+penstock_risk+pipe_risk+pipe_currency_risk), \
                powerhouse_risk, (turbine_risk+turbine_transport_risk+turbine_currency_risk), \
                (electric_risk+electrics_currency_risk+Powerhouse.powerhouse_storage["electrics install"]*0.1*0.1))
    ind = np.arange(N)    # the x locations for the groups
    width = 0.4       # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()

    p1 = ax.bar(ind, material, width, label='Material')
    p2 = ax.bar(ind, labour, width,bottom=material, label='Arbeit')
    p3 = ax.bar(ind, transport, width,bottom=addedvalues, yerr=totalStd, label='Transport')

    ax.axhline(0, color='grey', linewidth=0.8)
    ax.set_ylabel('Kosten in USD')
    ax.set_title('Kosten nach Abschnitt und Typ')
    ax.set_xticks(ind)
    ax.set_xticklabels(('Wasserbau', 'Fallrohr', 'Maschinenhaus', 'Turbine', 'Elektrik'))
    ax.legend()

    # Label with label_type 'center' instead of the default 'edge'
    #ax.bar_label(p1, label_type='center')
    #ax.bar_label(p2, label_type='center')
    #ax.bar_label(p3, label_type='center')
    ax.bar_label(p3)

    #https://riptutorial.com/matplotlib/example/14063/plot-with-gridlines
    # Show the major grid lines with dark grey lines
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    # Show the minor grid lines with very faint and almost transparent grey lines
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()

plottype=input("Enter Type: 1.Bar 2.Pie 3.Bar2:")
if plottype=="Bar":
    plot_bar_chart()
elif plottype=="Pie":
    plot_pie_chart()
elif plottype=="Bar2":
    plot_bar2_chart()