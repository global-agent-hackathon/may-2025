# Prototype code for a court case pipeline using AGNO agents.
# Run app.py to start the Streamlit app. It was build referencing to this pipeline code.

import os
import streamlit as st
from dotenv import load_dotenv
from Agents import judge_agent, prosecutor_agent, plaintiff_agent, defense_agent, accused_agent, witness_agent, expert_agent, media_and_public_agent, narrative_agent
from textwrap import dedent
from agno.agent import RunResponse
from typing import Iterator

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")        

def court_case_pipeline(case_title: str, case_description: str, evidence_list: list, witnesses: list, plaintiff: str, accused: str, player_role: int):
    """
    Main pipeline for court case processing.
    """
    total_prompt = ""
    no_of_days = 1
    while no_of_days < 4:
        if no_of_days == 1:

            print("Trial of the case starts \n Court Case Hearing Day 1")

            judge_response_stream: Iterator[RunResponse] = judge_agent.print_response(
                dedent(f"""
                    "As the presiding Judge, commence the courtroom proceedings for Day 1 of the case {case_title}. 
                    Present the yourself, jury, and all others to the audience.
                    Remind all parties of courtroom decorum, outline today's agenda, 
                    and invite the Prosecutor to begin with their opening statement."
                    Present an objective and concise overview of the case,
                    Include the background of the incident, the parties involved, the nature of the charges, 
                    and what the court is expected to determine over the coming 3 days of trial.
                    Your goal is to help observers and participants understand the context before legal proceedings begin.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            prosecutor_response_stream: Iterator[RunResponse] = prosecutor_agent.print_response(
                dedent(f"""
                    "As the Prosecutor, present yourself first then deliver statement for the case {case_title}.
                    Present the key facts of the case, outline the evidence you will present,
                    and explain why the accused {accused} should be found guilty.
                    Use the following evidence list to support your arguments: {evidence_list[0]}
                    Your goal is to establish a compelling case against the defendant while maintaining professional courtroom conduct.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            plaintiff_response_stream: Iterator[RunResponse] = plaintiff_agent.print_response(
                dedent(f"""
                    "As the Plaintiff {plaintiff}, present yourself first then deliver statement for the case {case_title}.
                    Share your personal experience and the impact this case has had on you.
                    Explain why you are seeking justice and what you hope to achieve through these proceedings.
                    Your goal is to help the court understand your perspective while maintaining professional courtroom conduct.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            first_witness_response_stream: Iterator[RunResponse] = witness_agent.print_response(
                dedent(f"""
                    "As the first witness {witnesses[0]}, present yourself first then deliver statement for the case {case_title} and {case_description}.
                    Share what you know about the case {evidence_list[0]}, your relationship to the parties involved,
                    and any relevant information that may help the court understand the context.
                    Your goal is to help the court understand the witness's perspective while maintaining professional courtroom conduct.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            first_witness_question_direct_response_stream: Iterator[RunResponse] = prosecutor_agent.print_response(
                dedent(f"""
                    "As the Prosecutor, ask the first witness {witnesses[0]} a direct question about their testimony {first_witness_response_stream}.
                    Ensure your question is clear and relevant to the case {case_title}.
                    Your goal is to help the court understand the witness's perspective to your benefit.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            first_witness_question_response_stream: Iterator[RunResponse] = witness_agent.print_response(
                dedent(f"""
                    "As the first witness {witnesses[0]}, respond to the Prosecutor's question {first_witness_question_direct_response_stream}.
                    Ensure your response is clear and relevant to the case {case_title}.
                    Your goal is to help the court understand the witness's perspective to your benefit.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            defense_response_stream: Iterator[RunResponse] = defense_agent.print_response(
                dedent(f"""
                    "As the Defense Agent {accused}, present yourself first then deliver statement for the case {case_title}.
                    Present your case, challenge the prosecution's evidence, and explain why the accused should be found not guilty or receive a lenient sentence.
                    Use the following evidence list to support your arguments: {evidence_list[0]}
                    Your goal is to help the court understand your perspective while maintaining professional courtroom conduct.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            accused_response_stream: Iterator[RunResponse] = accused_agent.print_response(
                dedent(f"""
                    "As the Accused {accused}, present yourself first then deliver statement for the case {case_title}.
                    Share your perspective on the case, explain why you believe you are not guilty, and what you hope to achieve through these proceedings.
                    Your goal is to help the court understand your perspective while maintaining professional courtroom conduct.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            first_witness_question_cross_response_stream: Iterator[RunResponse] = defense_agent.print_response(
                dedent(f"""
                    "As the Defense Agent {accused}, ask the first witness {witnesses[0]} a cross-question about their testimony {first_witness_response_stream}.
                    Ensure your question is clear and relevant to the case {case_title}.
                    Your goal is to help the court understand the witness's perspective to your benefit.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            first_witness_question_cross_response_stream: Iterator[RunResponse] = witness_agent.print_response(
                dedent(f"""
                    "As the first witness {witnesses[0]}, respond to the Defense Agent's cross-question {first_witness_question_cross_response_stream}.
                    Ensure your response is clear and relevant to the case {case_title}.
                    Your goal is to help the court understand the witness's perspective to your benefit.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            expert_response_stream: Iterator[RunResponse] = expert_agent.print_response(
                dedent(f"""
                    "As the Expert in all fields, give your regards to judge and jury, and present your expert opinion on the case {case_title}.
                    Share any technical/forensic explanation to the evidence presented so far {evidence_list[0]}, and how it relates to the case.
                    Ensure validity of evidence or interpretation.
                    It should be in conversational tone and not too long."
                """),
                stream=True
            )

            media_and_public_response_stream: Iterator[RunResponse] = media_and_public_agent.print_response(
                dedent(f"""
                    "As the Media Agent, report facts accurately and provide balanced coverage and public opinion.
                    Avoid sensationalism."
                    It should be in report style and not too long.
                """),
                stream=True
            )

            narrative_response_stream: Iterator[RunResponse] = narrative_agent.print_response(
                dedent(f"""
                    "As the Narrative Agent, create a narrative for the case {case_title}.
                    Create a timeline for the case, and a list of witnesses for the case.
                    Ensure that the narrative is clear, concise, and relevant to the case."
                """),
                stream=True
            )

            judge_end_day_response_stream: Iterator[RunResponse] = judge_agent.print_response(
                dedent(f"""
                    "As the presiding Judge, conclude Day 1 of the case {case_title}.
                    Summarize the key points presented by each party, including the Prosecutor, Plaintiff, Defense, Accused, Witnesses, Expert, and Media Agent.
                    Ensure that the Judge's summary is clear, concise, and relevant to the case."
                    It should be in conversational tone and not too long.
                """),
                stream=True
            )

            total_prompt += f"""
            Day {no_of_days} Summary:
            Judge: {judge_response_stream}  
            Prosecutor: {prosecutor_response_stream}
            Plaintiff: {plaintiff_response_stream}
            First Witness: {first_witness_response_stream}
            First Witness Question Direct: {first_witness_question_direct_response_stream}
            First Witness Question Response: {first_witness_question_response_stream}
            Defense: {defense_response_stream}
            Accused: {accused_response_stream}  
            First Witness Question Cross: {first_witness_question_cross_response_stream}
            First Witness Question Response: {first_witness_question_cross_response_stream}
            Expert: {expert_response_stream}    
            Media and Public: {media_and_public_response_stream}
            Narrative: {narrative_response_stream}
            """

            no_of_days += 1
        
        return total_prompt




if __name__ == "__main__":
    prompt = court_case_pipeline(
        case_title="State vs. John Doe",
        case_description="A criminal case involving theft and assault. The accused, John Doe, is charged with stealing a car and assaulting the owner. The case involves multiple witnesses, including the victim and bystanders, as well as forensic evidence from the crime scene. The prosecution aims to prove the guilt of the accused, while the defense seeks to establish reasonable doubt.",
        evidence_list=["Witness testimonies from the victim, bystanders at the scene, CCTV footage of the crime scene, forensic reports from the crime scene, and a police report detailing the incident."],
        witnesses=["Alice Smith", "Bob Johnson"],
        plaintiff="Alice Smith",
        accused="John Doe",
        player_role=1
    )
    #print(prompt)



            




                    



            
            
            


    
    
