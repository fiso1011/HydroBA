import pandas as pd
import numpy as np
from openpyxl import load_workbook
import data_input as c_di
import Intake.py as c_in


# Read input files
input_data_path = 'C:/Users/soere/Google Drive/Wirtschaftsingenieurwesen/8.Semester/Bachelorarbeit/Meine Dateien/HydroBA_Input.xlsx'
input_data = c_di.data_input(input_data_path)

site_data=input_data.input_dict["hydro_data"]["dict"]
intake_data=input_data.input_dict["intake_data"] ["dict"]
intake_material=input_data.input_dict["intake_material"]["dict"]


Intake = c_in.Intake(site_data,intake_data,intake_material)
Intake.total_intake_cost()