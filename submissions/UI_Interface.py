import streamlit as st
import pandas as pd
from Emissions import *
from agno.tools.sql import SQLTools
from agno.agent import Agent
from sqlalchemy import create_engine,text
from read_env import *
from Instruction import instructions
import json
import matplotlib.pyplot as plt
from Forecasting_Agent import EmissionForecastAgent
from qna_agent import EmissionsQnAAgent

# Initialize QnA agent
qna_agent = EmissionsQnAAgent(
    deployment_id=Azure_Deployment,
    api_key=AZURE_OPENAI_API_KEY,
    endpoint=AZURE_OPENAI_ENDPOINT
)

st.title("🔍 Sustainability Tools")
tab1,tab2=st.tabs(['Fuel Emissions Calculator','Forecasting Tool'])
with tab1:
    st.header("Fuel Emissions")
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file:
        input_df = pd.read_excel(uploaded_file)
        st.write("Uploaded Data", input_df)
        if st.button("Run Agent for Unit Conversion"):
            # Send dataframe to your tool or agent
            result = agent.tools[0].emission1(input_df)
            # Save in session_state
            st.session_state["converted_df"] = result
            st.success("✅ Conversion done! You can now ask questions below.")
        if "converted_df" in st.session_state:
            result_df = st.session_state["converted_df"]
            st.subheader("📊 Emission Results")
            st.dataframe(result_df)

            # Save result_df to in-memory SQLite DB
            engine = create_engine("sqlite:///:memory:", echo=False)
            result_df.to_sql("emissions", con=engine, index=False, if_exists="replace")


            # SQL agent setup
            sql_agent = Agent(
                model=AzureOpenAI(
                    id=Azure_Deployment,
                    api_key=AZURE_OPENAI_API_KEY,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT
                ),
                tools=[SQLTools(db_engine=engine)],
                markdown=True,
                show_tool_calls=True,
                add_history_to_messages=True,
                retries=3,
                instructions = instructions

            )

            # Natural language query
            with st.form("query_form"):
                user_query = st.text_input("💬 Ask a question (e.g., 'Total emissions for scope1 in May'):")
                submit_button = st.form_submit_button("Run SQL Agent")

                if submit_button and user_query:
                    with st.spinner("🤖 Thinking..."):
                        try:
                            response = sql_agent.run(user_query)  # returns a string (or JSON string)
                            st.success("✅ Query successful!")
                            st.markdown("### 🧠 Agent Response")
                            st.markdown(response.content)

                        except Exception as e:
                            st.error(f"❌ Agent failed: {e}")
with tab2:
    st.header("Forecasting Tool")

    st.markdown("Upload your emissions Excel file and ask forecasting or data questions.")

    uploaded_file = st.file_uploader("Upload Emissions Excel File", type=["xlsx"])

    if uploaded_file:
        try:
            agent = EmissionForecastAgent(uploaded_file)

            with st.spinner("Analyzing data..."):
                summary_df = agent.generate_summary()
                st.subheader("📊 Emissions Data Summary")
                st.dataframe(summary_df)

            query = st.text_input("Ask a forecast question (e.g., 'Forecast CO2 and Scope 2 for 3 years'):")

            if query:
                matched_emissions, years = agent.parse_query(query)
                st.success(f"Detected: {', '.join(matched_emissions).upper()} | Years: {years}")

                full_insight = ""
                for emission_type in matched_emissions:
                    ts, forecast = agent.forecast(emission_type, years)
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ts.plot(ax=ax, label="Historical")
                    forecast.plot(ax=ax, label="Forecast", color="red")
                    ax.set_title(f"{emission_type.upper()} Forecast ({years} Years)")
                    ax.legend()
                    st.pyplot(fig)

                    with st.spinner(f"Generating insights for {emission_type.upper()}..."):
                        prompt = agent.generate_prompt(emission_type, years, forecast, summary_df)
                        insight = qna_agent.answer_question("", prompt)  # Save for future Q&A
                        full_insight += f"\n\n## {emission_type.upper()}\n" + insight
                        st.subheader(f"🧠 AI Insights: {emission_type.upper()}")
                        st.markdown(insight, unsafe_allow_html=True)

                # Multiturn QnA
                st.subheader("🤔 Ask Questions about the Insights or Uploaded Data")
                followup = st.text_input("Type your follow-up Q&A:")
                if followup:
                    with st.spinner("Thinking..."):
                        context = full_insight + "\n\nSnapshot:\n" + agent.get_data_snapshot()
                        followup_response = qna_agent.answer_question(context, followup)
                        st.markdown(followup_response)

        except Exception as e:
            st.error(f"Error: {e}")