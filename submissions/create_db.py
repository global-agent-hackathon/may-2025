import pandas as pd
import sqlite3
 
# Step 1: File path (replace with your file name)
excel_file = r"Emission_factor.xlsx" # <- Put your Excel file name here
 
# Step 2: Read all sheets by name
sheets = pd.read_excel(excel_file, sheet_name=None)
 
# Step 3: Extract each sheet's data
scope1 = sheets.get("Energy-Scope1",)
scope3 = sheets.get("Energy-Scope3")
uom=sheets.get("UnitofMeasure")
uom_conversion=sheets.get("UnitofMeasureConversion")
'''print(scope3)
print(scope1.columns)'''
scope1.columns=['Fuel_Type','Fuel_Combusted',"Emission_factor_CO2(kgCO2-e/GJ)","Emission_factor_CH4(kgCO2-e/GJ)" ,"Emission_factor_N2O(kgCO2-e/GJ)","Emission_factor_Combined(kgCO2-e/GJ)","Energy_content_factor(GJ)","Energy_content_factor(GJ/Unit)" ,"Emission_factor(kgCO2-e)" ,"Emission_factor(kgCO2e/Unit)" ,'Unit',"Unit_ID","Scope","Source"]
scope3.columns=['Fuel_Type','Fuel_Combusted',"Emission_factor(kgCO2-e/GJ)","Energy_content_factor(GJ)","Energy_content_factor(GJ/Unit)" ,"Emission_factor(kgCO2-e)" ,"Emission_factor(kgCO2e/Unit)" ,
               'Unit',"Unit_ID","Scope","Source"]
#print(scope1.columns)
 
 #Step 4: Create SQLite database
conn = sqlite3.connect('scope_1_3.db')
cursor = conn.cursor()
 
# Step 5: Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Scope1(
    Fuel_Type TEXT NOT NULL ,
    Fuel_Combusted TEXT NOT NULL,
    "Emission_factor_CO2(kgCO2-e/GJ)" FLOAT NOT NULL,
    "Emission_factor_CH4(kgCO2-e/GJ)" FLOAT NOT NULL ,
    "Emission_factor_N2O(kgCO2-e/GJ)" FLOAT NOT NULL,
    "Emission_factor_Combined(kgCO2-e/GJ)" FLOAT NOT NULL,
    "Energy_content_factor(GJ)" FLOAT NOT NULL,
    "Energy_content_factor(GJ/Unit)" TEXT NOT NULL ,
    "Emission_factor(kgCO2-e)" FLOAT NOT NULL,
    "Emission_factor(kgCO2e/Unit)" TEXT NOT NULL,
    Unit Text NOT NULL,
    "Unit_Id" INTEGER NOT NULL,
    Scope INTEGER NOT NULL,
    Source TEXT NOT NUll
)
''')
 
cursor.execute('''
CREATE TABLE IF NOT EXISTS Scope3 (
    Fuel_Type TEXT NOT NULL,
    Fuel_Combusted TEXT NOT NULL,
    "Emission_factor(kgCO2-e/GJ)" FLOAT NOT NULL,
    "Energy_content_factor(GJ)" FLOAT NOT NULL,
    "Energy_content_factor(GJ/Unit)" TEXT NOT NULL ,
    "Emission_factor(kgCO2-e)" FLOAT NOT NULL,
    "Emission_factor(kgCO2e/Unit)" TEXT NOT NULL,
     Unit Text NOT NULL,
    "Unit_Id" INTEGER NOT NULL,
    Scope INTEGER NOT NULL,
    Source TEXT NOT NUll
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS UnitofMeasure (
    UnitofMeasureId Integer NOT NULL,
    UnitofMeasureName TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS UnitofMeasureConversion (
    UnitOfMeasureConversionId Integer NOT NULL,
    ConvertFromUnitOfMeasureId Integer NOT NULL,
    ConvertToUnitOfMeasureId   Integer NOT NULL,
    ConversionFactor   FLOAT NOT NULL,
    UnitOfMeasureConversionNote TEXT NOT NULL
    )         
''')

#cursor.execute("PRAGMA table_info(Scope1)")
#print(cursor.fetchall())

 
# Step 6: Insert data using pandas
scope1.to_sql('Scope1', conn, if_exists='append', index=False)
scope3.to_sql('Scope3', conn, if_exists='append', index=False)
uom.to_sql('UnitofMeasure', conn, if_exists='append', index=False)
uom_conversion.to_sql('UnitofMeasureConversion', conn, if_exists='append', index=False)


# Step 7: Finish
conn.commit()
conn.close()
 
print("✅ Excel data loaded into company.db successfully.")