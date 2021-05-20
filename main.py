import pandas as pd
import numpy as np
from openpyxl import load_workbook
import data_input as c_di
import Intake as c_in

# Read input files
c_di.data_storage.readingFunc()
input_data=c_di.data_storage.readingFunc.inputdata

intake_data=input_data.input_dict["intake_data"] ["dict"]
intake_material=input_data.input_dict["intake_material"]["dict"]

Intake = c_in.Intake(intake_data,intake_material)
Intake.total_intake_cost()
