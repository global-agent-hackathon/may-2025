from agno.tools import Toolkit
from read_env import *
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI
from agno.tools.sql import SQLTools # used to query
#from sqlalchemy import create_engine #used to establsih connectiomn to sqlite database
import sqlite3
import pandas as pd
import streamlit as st 
#db_url = "sqlite:///scope_1_3.db"

class Emissiontoolkit(Toolkit):
    def __init__(self):
        super().__init__(name="emission_toolkit")
        #self.register(self.emisison_finder)
        self.register(self.emission1)

    def emission1(self,df):
        df=pd.DataFrame(df)
        '''Match the unit and give the quantity in default unit from the scope tables'''
        if 'Quantity' not in df.columns:
            return "Missing required columns."
        converted_quantity=[]
        emission=[]
        conn=sqlite3.connect('scope_1_3.db')
        cursor = conn.cursor()
        for i in range(len(df)):
            val=df["Unit"].iloc[i]
            cursor.execute("SELECT UnitofMeasureId FROM unitofMeasure WHERE UnitOfMeasureName = ?", (val,))# to find the id of the unit in the dataframe
            result = cursor.fetchone()# fetchone stores the data as tuple
            unit= result[0] if result else 1
            scope=df['Scope'][i]
            fuel=df['Fuel'][i]
            cursor.execute(f"Select Unit_Id from {scope} where Fuel_Combusted='{fuel}'")
            result=cursor.fetchone()
            conversion_unitid= result[0] if result else 1
            cursor.execute(f"Select ConversionFactor from UnitofMeasureConversion where ConvertFromUnitOfMeasureId={unit} and  ConvertToUnitOfMeasureId ={conversion_unitid}")
            row= cursor.fetchone()
            conversion_factor= row[0] if row else 1
            quant= df['Quantity'][i] * conversion_factor
            # print(type(df['Quantity'][i]))
            # print(type(conversion_factor))
            # print(type(quant))
            # print(quant)
            cursor.execute(f'''Select "Emission_factor(kgCO2-e)" from {scope} where Fuel_Combusted ='{fuel}' ''')
            ef= cursor.fetchone()
            #print(ef)
            ef=ef[0] if ef else 1
            #print(type(ef))
            em=quant*ef
            em=float(em) # to remove float64 from the value
            #print(em)
            emission.append(em)
            converted_quantity.append(quant)
            
        df['emissions(kgCO2e)']=emission
        return df
    
agent=Agent(model=AzureOpenAI(id=Azure_Deployment,
                               api_key=AZURE_OPENAI_API_KEY,
                               azure_endpoint=AZURE_OPENAI_ENDPOINT),
            tools=[Emissiontoolkit()],
            show_tool_calls=True,
            instructions=["Use emission1 tool to get emission factors and not the web"])
'''agent.print_response(
    f"Conversion for{df}"
)'''
