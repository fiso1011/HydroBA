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

intake_data=input_data.input_dict["intake_data"] ["dict"]
intake_material=input_data.input_dict["intake_material"]["dict"]

Intake = c_in.Intake(intake_data,intake_material)
Intake.total_intake_cost()
print(Intake.total_intake_cost)  #total cost, detailed cost is stored in dict intake_cost

channel_data=input_data.input_dict["channel_data"] ["dict"]
channel_material=input_data.input_dict["channel_material"]["dict"]

Channel = c_ch.Channel(channel_data,channel_material)
Channel.total_channel_cost()
print(Channel.total_channel_cost)  #total cost, detailed cost is stored in dict intake_cost

sandtrap_data=input_data.input_dict["sandtrap_data"] ["dict"]
sandtrap_material=input_data.input_dict["sandtrap_material"]["dict"]

Sandtrap = c_st.Sandtrap(sandtrap_data,sandtrap_material)
Sandtrap.total_sandtrap_cost()
print(Sandtrap.total_sandtrap_cost)  #total cost, detailed cost is stored in dict intake_cost

penstock_data=input_data.input_dict["penstock_data"] ["dict"]
penstock_material=input_data.input_dict["penstock_material"]["dict"]

Penstock = c_ps.Penstock(penstock_data,penstock_material)
Penstock.total_penstock_cost()
print(Penstock.total_penstock_cost)  #total cost, detailed cost is stored in dict intake_cost

powerhouse_data=input_data.input_dict["powerhouse_data"] ["dict"]
powerhouse_material=input_data.input_dict["powerhouse_material"]["dict"]

Powerhouse = c_ph.Powerhouse(powerhouse_data,powerhouse_material)
Powerhouse.total_powerhouse_cost()
print(Powerhouse.total_powerhouse_cost)  #total cost, detailed cost is stored in dict intake_cost
