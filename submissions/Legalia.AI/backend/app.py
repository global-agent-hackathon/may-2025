import os
import streamlit as st
from dotenv import load_dotenv
from Agents import judge_agent, prosecutor_agent, plaintiff_agent, defense_agent, accused_agent, witness_agent, expert_agent, media_and_public_agent, narrative_agent
from textwrap import dedent
from agno.agent import RunResponse
from typing import Iterator


load_dotenv()

def display_chat_message(name, role, message, avatar_color="#4CAF50"):
    """Display message in chat format with avatar and styling"""
    # Create columns for avatar and message
    col1, col2 = st.columns([1, 10])
    
    with col1:
        st.markdown(f"""
        <div style="
            width: 45px;
            height: 45px;
            background: {avatar_color};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
            margin-top: 10px;
        ">
            {name.split()[0][:2].upper()}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**⚖️ {name}** • *{role}*")
        st.markdown(f"> {message}")
        st.markdown("---")

def display_sidebar_chat_message(name, role, message, avatar_color="#4CAF50"):
    """Display sidebar message in compact format"""
    st.markdown(f"**{name.split()[0][:2].upper()}** • *{role}*")
    st.markdown(f"> {message}")
    st.markdown("---")

def court_case_pipeline(case_title: str, case_description: str, evidence1: str, evidence2: str, evidence3: str, witness1: str , witness2: str, witness3: str, plaintiff: str, accused: str):
    """
    Main pipeline for court case processing.
    """
    total_prompt = ""
    judge_prompt = ""
    prosecutor_prompt = ""
    defense_prompt = ""
    expert_prompt = ""
    media_and_public_prompt = ""
    no_of_days = 1

    name_prompt = dedent(f"""
                    Name of the judge and advocates and other participants in the case.
                    Judge: Raghav Bansal
                    Prosecutor: Advocate Rohan Deshmukh
                    Defense: Advocate Priya Sharma
                    Plaintiff: {plaintiff}
                    Accused: {accused}
                    Expert: Dr. Anjali Verma
                """)
    
    # Create containers for sidebar reports
    sidebar_media_container = st.sidebar.container()
    sidebar_narrative_container = st.sidebar.container()
    
    while no_of_days < 4:
        ######################################################################
        if no_of_days == 1:

            day_prompt = ""
            total_prompt += dedent(f"""Day {no_of_days} Summary:\n""")
            day_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            judge_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            prosecutor_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            defense_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            expert_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            media_and_public_prompt += dedent(f"""Day {no_of_days} Coverage:\n""")
            
            # Enhanced header with chat styling
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e3c72, #2a5298);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h1 style="margin: 0; font-size: 28px;">⚖️ {case_title}</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Live Courtroom Proceedings - Day 1</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Chat container styling
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8f9fa, #ffffff);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                border: 1px solid #e9ecef;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            ">
                <h3 style="
                    color: #495057;
                    margin-bottom: 25px;
                    text-align: center;
                    border-bottom: 2px solid #dee2e6;
                    padding-bottom: 15px;
                    font-size: 20px;
                ">💬 Live Court Session</h3>
            """, unsafe_allow_html=True)

        #---------------------------------------------------------------------
            # Judge's opening with chat styling
            judge_response_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal presiding over the case "{case_title}". 
                    
                    TASK: Open Day 1 of court proceedings professionally.
                    
                    CONTEXT:
                    - Case: {case_description}
                    - Participants: {name_prompt}
                    - This is the formal opening of a 3-day trial
                    
                    STRUCTURE YOUR OPENING:
                    1. Call court to order and introduce yourself
                    2. Introduce all counsel and parties present
                    3. Provide objective case overview (background, charges, what court will determine)
                    4. Remind all parties of courtroom decorum
                    5. Outline today's agenda 
                    6. Invite Prosecutor to begin opening statement
                    
                    TONE: Authoritative but fair, professional, conversational
                    LENGTH: Under 200 words but comprehensive
                """),
                stream=True
            )

            response = ""
            # Create placeholder for streaming response
            message_placeholder = st.empty()
            
            for _resp_chunk in judge_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    # Update the chat message in real-time
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge", 
                            response, 
                            "#8B4513"
                        )

            total_prompt += f"Judge's Opening: {response}\n\n"
            day_prompt += f"Judge's Opening: {response}\n\n"
            judge_prompt += f"Judge's Opening: {response}\n\n"

        #---------------------------------------------------------------------
            # Prosecutor's statement with chat styling
            prosecutor_response_stream: Iterator[RunResponse] = prosecutor_agent.run(
                dedent(f"""
                    You are Advocate Rohan Deshmukh, the Prosecutor.

                    TASK: Deliver your opening statement for "{case_title}".

                    CONTEXT:
                    - Case Details: {case_description}
                    - Your key evidence: {evidence1}
                    - Accused: {accused}
                    - Court proceedings so far: {day_prompt}

                    STRUCTURE YOUR STATEMENT:
                    1. Introduce yourself professionally
                    2. Present the key facts you will prove
                    3. Outline evidence you will present
                    4. Explain why {accused} should be found guilty
                    5. Preview your case strategy

                    APPROACH: Confident, factual, methodical
                    GOAL: Establish compelling case for guilt
                    LENGTH: Under 100 words but impactful
                """),
                stream=True
            )

            response = ""
            # Create placeholder for streaming response
            message_placeholder = st.empty()
            
            for _resp_chunk in prosecutor_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    # Update the chat message in real-time
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Rohan Deshmukh", 
                            "Prosecutor", 
                            response, 
                            "#DC143C"
                        )

            day_prompt += f"Prosecutor's Statement: {response}\n\n"
            prosecutor_prompt += f"Prosecutor's Statement: {response}\n\n"

        #---------------------------------------------------------------------
            # Plaintiff's statement with chat styling
            plaintiff_response_stream: Iterator[RunResponse] = plaintiff_agent.run(
                dedent(f"""
                    You are {plaintiff}, the Plaintiff in this case.
                    
                    TASK: Share your personal statement about this case.
                    
                    CONTEXT:
                    - Case: {case_title} - {case_description}
                    - Supporting evidence: {evidence1}
                    - Court proceedings so far: {day_prompt}
                    
                    STRUCTURE YOUR STATEMENT:
                    1. Introduce yourself and your connection to this case
                    2. Describe your personal experience and what happened to you
                    3. Explain the impact this has had on your life
                    4. Express what justice means to you in this situation
                    5. Support the prosecution's case with your testimony
                    
                    TONE: Genuine, emotional but controlled, seeking justice
                    GOAL: Help court understand your perspective and suffering
                    LENGTH: Under 100 words but heartfelt
                """),
                stream=True
            )
                
            # Display response with chat styling
            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in plaintiff_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            plaintiff, 
                            "Plaintiff", 
                            response, 
                            "#FF6B35"
                        )

            day_prompt += f"Plaintiff's Statement: {response}\n\n"

        #---------------------------------------------------------------------
            # witnesses' statements with chat styling
            first_witness_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the first witness testifying in "{case_title}".
                    
                    TASK: Provide your witness testimony.
                    
                    WITNESS DETAILS: {witness1}
                    
                    CONTEXT:
                    - Case: {case_description}
                    - Evidence related to your testimony: {evidence1}
                    - Accused: {accused}
                    - Court proceedings so far: {day_prompt}
                    
                    STRUCTURE YOUR TESTIMONY:
                    1. State your name and relationship to this case
                    2. Describe what you witnessed or know about the incident
                    3. Be specific about dates, times, and details
                    4. Explain why your testimony supports finding {accused} guilty
                    5. Answer clearly and honestly
                    
                    APPROACH: Truthful, direct, detailed
                    GOAL: Provide credible testimony supporting prosecution
                    LENGTH: Under 100 words but complete
                """),
                stream=True
            )
                
            # Display response with chat styling
            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in first_witness_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 1", 
                            "First Witness", 
                            response, 
                            "#20B2AA"
                        )

            day_prompt += f"First Witness Testimony: {response}\n\n"

        #---------------------------------------------------------------------
            # Direct question to first witness from prosecutor with chat styling
            first_witness_question_direct_response_stream: Iterator[RunResponse] = prosecutor_agent.run(
                dedent(f"""
                    You are Prosecutor Advocate Rohan Deshmukh.
                    
                    TASK: Ask a direct examination question to the first witness.
                    
                    CONTEXT:
                    - Witness just testified: {first_witness_response_stream}
                    - Case: {case_title}
                    - Key evidence to explore: {evidence1}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Ask ONE specific, clear question that:
                    1. Clarifies or strengthens the witness's testimony
                    2. Highlights evidence that supports your case
                    3. Helps prove {accused}'s guilt
                    4. Is legally appropriate for direct examination
                    
                    FORMAT: "Witness [Name], [your question]?"
                    APPROACH: Professional, strategic, focused
                    LENGTH: One clear question under 50 words
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in first_witness_question_direct_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Rohan Deshmukh", 
                            "Prosecutor (Direct Examination)", 
                            response, 
                            "#DC143C"
                        )

            day_prompt += f"Prosecutor's Direct Question: {response}\n\n"
            prosecutor_prompt += f"Prosecutor's Direct Question: {response}\n\n"

        #---------------------------------------------------------------------
            # First witness's response to prosecutor's question with chat styling
            first_witness_answer_direct_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the first witness responding to the Prosecutor's question.
                    
                    PROSECUTOR'S QUESTION: {first_witness_question_direct_response_stream}
                    
                    CONTEXT:
                    - Your identity: {witness1}
                    - Case details: {case_title}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Answer the prosecutor's question:
                    1. Directly and honestly
                    2. With specific details if you have them
                    3. Stay consistent with your earlier testimony
                    4. If you don't know something, say so
                    
                    APPROACH: Truthful, cooperative, clear
                    GOAL: Provide helpful testimony
                    LENGTH: Under 100 words, direct answer
                """),
                stream=True
            )
                
            # Display response with chat styling
            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in first_witness_answer_direct_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 1", 
                            "First Witness (Response)", 
                            response, 
                            "#20B2AA"
                        )
            
            day_prompt += f"First Witness Response: {response}\n\n"

        #---------------------------------------------------------------------
            # Defense's statement with chat styling
            defense_response_stream: Iterator[RunResponse] = defense_agent.run(
                dedent(f"""
                    You are Advocate Priya Sharma, Defense Attorney for {accused}.
                    
                    TASK: Deliver your opening statement.
                    
                    CONTEXT:
                    - Case: {case_title} - {case_description}
                    - Your client: {accused}
                    - Evidence to challenge/reinterpret: {evidence1}
                    - Court proceedings so far: {day_prompt}
                    
                    STRUCTURE YOUR STATEMENT:
                    1. Introduce yourself and your role
                    2. Present your client's position (innocent/alternative explanation)
                    3. Challenge weaknesses in prosecution's case
                    4. Preview your defense strategy
                    5. Explain why reasonable doubt exists
                    
                    APPROACH: Confident, strategic skepticism
                    GOAL: Create doubt about prosecution's case
                    LENGTH: Under 100 words but compelling
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in defense_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Priya Sharma", 
                            "Defense Attorney", 
                            response, 
                            "#9932CC"
                        )

            day_prompt += f"Defense Opening: {response}\n\n"
            defense_prompt += f"Defense Opening: {response}\n\n"

        #---------------------------------------------------------------------
            # Accused's statement with chat styling
            accused_response_stream: Iterator[RunResponse] = accused_agent.run(
                dedent(f"""
                    You are {accused}, the person accused in this case.
                    
                    TASK: Give your personal statement to the court.
                    
                    CONTEXT:
                    - Case against you: {case_title} - {case_description}
                    - Evidence being used: {evidence1}
                    - Court proceedings so far: {day_prompt}
                    
                    STRUCTURE YOUR STATEMENT:
                    1. Introduce yourself respectfully
                    2. State your position (innocent/your version of events)
                    3. Explain your side of what happened
                    4. Show respect for the court process
                    5. Express what you hope to achieve
                    
                    TONE: Respectful, honest, seeking justice
                    APPROACH: Maintain your innocence or explain circumstances
                    LENGTH: Under 100 words but sincere
                """),
                stream=True
            )

            # Display response with chat styling
            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in accused_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            accused, 
                            "Accused", 
                            response, 
                            "#B22222"
                        )

            day_prompt += f"Accused's Statement: {response}\n\n"

        #---------------------------------------------------------------------
            # first witness's cross-question from defense with chat styling
            first_witness_question_cross_response_stream: Iterator[RunResponse] = defense_agent.run(
                dedent(f"""
                    You are Defense Attorney Advocate Priya Sharma.

                    TASK: Cross-examine the first witness.

                    CONTEXT:
                    - Witness's testimony: {first_witness_response_stream}
                    - Case: {case_title}
                    - Court proceedings: {day_prompt}

                    INSTRUCTION:
                    Ask ONE cross-examination question that:
                    1. Challenges the witness's testimony
                    2. Creates doubt about their reliability/memory
                    3. Reveals inconsistencies or limitations
                    4. Benefits your client's defense

                    CROSS-EXAMINATION TECHNIQUES:
                    - Question their certainty
                    - Probe gaps in memory
                    - Challenge assumptions

                    FORMAT: "Witness [Name], isn't it true that [your challenge]?"
                    LENGTH: One focused question under 50 words
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in first_witness_question_cross_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Priya Sharma", 
                            "Defense (Cross-Examination)", 
                            response, 
                            "#9932CC"
                        )

            day_prompt += f"Defense Cross-Question: {response}\n\n"
            defense_prompt += f"Defense Cross-Question: {response}\n\n"

        #---------------------------------------------------------------------
            # First witness cross-examination response with chat styling
            first_witness_answer_cross_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the first witness responding to Defense cross-examination.
                    
                    DEFENSE QUESTION: {first_witness_question_cross_response_stream}
                    
                    CONTEXT:
                    - Your identity: {witness1}
                    - Case: {case_title}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Answer the defense attorney's question:
                    1. Honestly and directly
                    2. Admit if you're uncertain about something
                    3. Don't embellish or guess
                    4. Stay calm under pressure
                    5. Maintain consistency with earlier testimony
                    
                    APPROACH: Truthful, composed
                    GOAL: Answer honestly regardless of which side benefits
                    LENGTH: Under 100 words, direct response
                """),
                stream=True
            )

            # Display response with chat styling
            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in first_witness_answer_cross_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 1", 
                            "First Witness (Cross-Response)", 
                            response, 
                            "#20B2AA"
                        )
            
            day_prompt += f"First Witness Cross-Response: {response}\n\n"

        #---------------------------------------------------------------------
            # Expert's statement with chat styling
            expert_response_stream: Iterator[RunResponse] = expert_agent.run(
                dedent(f"""
                    You are Dr. Anjali Verma, Expert Witness in this case.
                    
                    TASK: Provide expert analysis of evidence.
                    
                    CONTEXT:
                    - Case: {case_title}
                    - Evidence to analyze: {evidence1}
                    - Court proceedings: {day_prompt}
                    - Participants: {name_prompt}
                    
                    STRUCTURE YOUR TESTIMONY:
                    1. Greet the court and introduce your credentials
                    2. Analyze the technical/forensic aspects of evidence
                    3. Explain your methodology and findings
                    4. State your professional conclusions
                    5. Address any limitations or uncertainties
                    
                    APPROACH: Scientific objectivity, clear explanations
                    GOAL: Help court understand technical evidence
                    LENGTH: Under 100 words but thorough
                """),
                stream=True
            )

            # Display response with chat styling
            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in expert_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Dr. Anjali Verma", 
                            "Expert Witness", 
                            response, 
                            "#4169E1"
                        )
            
            day_prompt += f"Expert Testimony: {response}\n\n"
            expert_prompt += f"Expert Testimony: {response}\n\n"

        #---------------------------------------------------------------------
            # Judge's end of day summary with chat styling
            judge_end_day_response_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal concluding Day 1.

                    TASK: Formally end Day 1 and preview Day 2.

                    CONTEXT:
                    - Case: {case_title}
                    - Today's proceedings: {day_prompt}
                    - Witness scheduled for tomorrow: {witness2}

                    STRUCTURE YOUR CONCLUSION:
                    1. Summarize key points from today's proceedings
                    2. Acknowledge all parties' presentations
                    3. Explain why Day 2 is necessary
                    4. Preview tomorrow's agenda (witness {witness2}, evidence)
                    5. Give final instructions to all parties
                    6. Formally adjourn court

                    TONE: Authoritative, fair, professional
                    GOAL: Proper case management and clear next steps
                    LENGTH: Under 200 words but comprehensive
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in judge_end_day_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge (Day 1 Conclusion)", 
                            response, 
                            "#8B4513"
                        )

            total_prompt += f"Judge's Day 1 Summary: {response}\n\n"
            day_prompt += f"Judge's Day 1 Summary: {response}\n\n"
            judge_prompt += f"Judge's Day 1 Summary: {response}\n\n"

            # Close the main chat container
            st.markdown("</div>", unsafe_allow_html=True)

            # Narrative Agent's response - moved to sidebar with chat styling
            with sidebar_narrative_container:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #e8f4f8, #ffffff);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #2196F3;
                ">
                    <h4 style="
                        color: #1976D2;
                        margin-bottom: 15px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        📝 Case Narrative - Day 1
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                narrative_response_stream: Iterator[RunResponse] = narrative_agent.run(
                    dedent(f"""
                        You are a professional legal narrative specialist covering "{case_title}".
                        
                        TASK: Create Day 1 case narrative and timeline.
                        
                        CONTEXT:
                        - Today's proceedings: {day_prompt}
                        - Case participants: {name_prompt}
                        - Case details: {case_description}
                        
                        STRUCTURE YOUR NARRATIVE:
                        1. **Case Timeline**: Key events from today's proceedings
                        2. **Evidence Summary**: What evidence was presented
                        3. **Witness Overview**: Who testified and key points
                        4. **Legal Strategy**: Prosecution vs Defense approaches
                        5. **Next Steps**: What to expect in Day 2
                        
                        STYLE: Professional legal analysis, organized format
                        APPROACH: Analytical, comprehensive case tracking
                        LENGTH: Under 150 words, structured format
                    """),
                    stream=True
                )

                narrative_response = ""
                narrative_message_placeholder = st.empty()
                for _resp_chunk in narrative_response_stream:
                    if _resp_chunk.content is not None:
                        narrative_response += _resp_chunk.content
                        with narrative_message_placeholder.container():
                            display_sidebar_chat_message(
                                "Legal Analyst", 
                                "Case Narrative Specialist", 
                                narrative_response, 
                                "#2196F3"
                            )

            total_prompt += f"Day 1 Complete Summary: {day_prompt}\n\n"

            # Media and Public's statement - moved to sidebar with chat styling
            with sidebar_media_container:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fff3e0, #ffffff);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #FF9800;
                ">
                    <h4 style="
                        color: #F57C00;
                        margin-bottom: 15px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        📺 Media Report - Day 1
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                media_and_public_response_stream: Iterator[RunResponse] = media_and_public_agent.run(
                    dedent(f"""
                        You are a professional court reporter covering "{case_title}".

                        TASK: Share a summary of public opinion under 100 words about Day 1 of the trial.

                        CONTEXT:
                        - Today's proceedings: {day_prompt}
                        - Case participants: {name_prompt}

                        STRUCTURE YOUR REPORT:
                        1. Summarize the overall public sentiment and reaction to Day 1
                        2. Mention any notable public debates, support, or criticism
                        3. Reflect the tone and themes seen in social media or public commentary

                        STYLE: Professional journalism, balanced tone
                        APPROACH: Factual reporting, no speculation
                        LENGTH: Under 100 words, focused on public opinion
                    """),
                    stream=True
                )

                media_response = ""
                media_message_placeholder = st.empty()
                for _resp_chunk in media_and_public_response_stream:
                    if _resp_chunk.content is not None:
                        media_response += _resp_chunk.content
                        with media_message_placeholder.container():
                            display_sidebar_chat_message(
                                "Court Reporter", 
                                "Media & Public Opinion", 
                                media_response, 
                                "#FF9800"
                            )
                
                media_and_public_prompt += f"Day 1 Media Report: {media_response}\n\n"

        ######################################################################
            # End of Day 1 - increment day counter
            no_of_days += 1

        ######################################################################
        elif no_of_days == 2:
            day_prompt = ""
            total_prompt += dedent(f"""Day {no_of_days} Summary:\n""")
            day_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            judge_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            prosecutor_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            defense_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            expert_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            media_and_public_prompt += dedent(f"""Day {no_of_days} Coverage:\n""")

            # Enhanced header for Day 2
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2c5aa0, #1e3c72);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h1 style="margin: 0; font-size: 28px;">⚖️ {case_title}</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Live Courtroom Proceedings - Day 2</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Chat container styling
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8f9fa, #ffffff);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                border: 1px solid #e9ecef;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            ">
                <h3 style="
                    color: #495057;
                    margin-bottom: 25px;
                    text-align: center;
                    border-bottom: 2px solid #dee2e6;
                    padding-bottom: 15px;
                    font-size: 20px;
                ">💬 Day 2 Court Session</h3>
            """, unsafe_allow_html=True)

        #---------------------------------------------------------------------
            # Judge's resuming hearing with chat styling
            judge_resume_response_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal resuming Day 2 of "{case_title}".
                    
                    TASK: Formally resume court proceedings for Day 2.
                    
                    CONTEXT:
                    - Case: {case_description}
                    - Day 1 summary: {judge_prompt}
                    - Today's agenda: Second witness {witness2}, expert analysis, defense witness
                    
                    STRUCTURE YOUR RESUMPTION:
                    1. Call court back to order
                    2. Briefly recap Day 1's key developments
                    3. Outline today's scheduled proceedings
                    4. Remind parties of courtroom procedures
                    5. Call for the second witness
                    
                    TONE: Authoritative, efficient, professional
                    GOAL: Smooth transition into Day 2 proceedings
                    LENGTH: Under 150 words but comprehensive
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in judge_resume_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge (Day 2 Resume)", 
                            response, 
                            "#8B4513"
                        )

            total_prompt += f"Judge's Day 2 Opening: {response}\n\n"
            day_prompt += f"Judge's Day 2 Opening: {response}\n\n"
            judge_prompt += f"Judge's Day 2 Opening: {response}\n\n"

        #---------------------------------------------------------------------
            # Second witness statement with chat styling
            witness_2_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the second witness testifying in "{case_title}".
                    
                    TASK: Provide your witness testimony.
                    
                    WITNESS DETAILS: {witness2}
                    
                    CONTEXT:
                    - Case: {case_description}
                    - Evidence related to your testimony: {evidence2}
                    - Court proceedings so far: {day_prompt}
                    - Previous witness testimony from Day 1
                    
                    STRUCTURE YOUR TESTIMONY:
                    1. State your name and relationship to this case
                    2. Describe what you witnessed or know about the incident
                    3. Be specific about dates, times, and details
                    4. Explain how your testimony relates to evidence {evidence2}
                    5. Answer clearly and honestly
                    
                    APPROACH: Truthful, detailed, credible
                    GOAL: Provide additional evidence supporting the case
                    LENGTH: Under 100 words but complete
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in witness_2_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 2", 
                            "Second Witness", 
                            response, 
                            "#20B2AA"
                        )

            day_prompt += f"Second Witness Testimony: {response}\n\n"

        #---------------------------------------------------------------------
            # Prosecutor's direct question to second witness with chat styling
            prosecutor_direct_2_response_stream: Iterator[RunResponse] = prosecutor_agent.run(
                dedent(f"""
                    You are Prosecutor Advocate Rohan Deshmukh.
                    
                    TASK: Ask a direct examination question to the second witness.
                    
                    CONTEXT:
                    - Witness just testified: Previous testimony about {witness2}
                    - Case: {case_title}
                    - Key evidence to explore: {evidence2}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Ask ONE specific question that:
                    1. Clarifies or strengthens the witness's testimony
                    2. Highlights evidence {evidence2} that supports your case
                    3. Builds on Day 1's evidence
                    4. Is legally appropriate for direct examination
                    
                    FORMAT: "Witness [Name], [your question]?"
                    APPROACH: Professional, strategic, building your case
                    LENGTH: One clear question under 50 words
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in prosecutor_direct_2_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Rohan Deshmukh", 
                            "Prosecutor (Direct Examination)", 
                            response, 
                            "#DC143C"
                        )

            day_prompt += f"Prosecutor's Direct Question: {response}\n\n"
            prosecutor_prompt += f"Prosecutor's Direct Question: {response}\n\n"

        #---------------------------------------------------------------------
            # Second witness response to prosecutor with chat styling
            witness_2_answer_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the second witness responding to the Prosecutor's question.
                    
                    PROSECUTOR'S QUESTION: {prosecutor_direct_2_response_stream}
                    
                    CONTEXT:
                    - Your identity: {witness2}
                    - Case details: {case_title}
                    - Evidence: {evidence2}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Answer the prosecutor's question:
                    1. Directly and honestly
                    2. With specific details about {evidence2}
                    3. Stay consistent with your earlier testimony
                    4. If uncertain, say so clearly
                    
                    APPROACH: Truthful, cooperative, detailed
                    GOAL: Provide helpful testimony
                    LENGTH: Under 100 words, direct answer
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in witness_2_answer_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 2", 
                            "Second Witness (Response)", 
                            response, 
                            "#20B2AA"
                        )

            day_prompt += f"Second Witness Response: {response}\n\n"

        #---------------------------------------------------------------------
            # Defense cross-examination of second witness with chat styling
            defense_cross_2_response_stream: Iterator[RunResponse] = defense_agent.run(
                dedent(f"""
                    You are Defense Attorney Advocate Priya Sharma.

                    TASK: Cross-examine the second witness.

                    CONTEXT:
                    - Witness's testimony: Previous testimony about {witness2}
                    - Case: {case_title}
                    - Evidence to challenge: {evidence2}
                    - Court proceedings: {day_prompt}

                    INSTRUCTION:
                    Ask ONE cross-examination question that:
                    1. Challenges the witness's reliability or memory
                    2. Questions their interpretation of {evidence2}
                    3. Creates doubt about their testimony
                    4. Benefits your client's defense

                    CROSS-EXAMINATION TECHNIQUES:
                    - Question their vantage point or timing
                    - Probe inconsistencies
                    - Challenge assumptions

                    FORMAT: "Witness [Name], isn't it true that [your challenge]?"
                    LENGTH: One focused question under 50 words
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in defense_cross_2_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Priya Sharma", 
                            "Defense (Cross-Examination)", 
                            response, 
                            "#9932CC"
                        )

            day_prompt += f"Defense Cross-Question: {response}\n\n"
            defense_prompt += f"Defense Cross-Question: {response}\n\n"

        #---------------------------------------------------------------------
            # Second witness response to defense with chat styling
            witness_2_cross_answer_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the second witness responding to Defense cross-examination.
                    
                    DEFENSE QUESTION: {defense_cross_2_response_stream}
                    
                    CONTEXT:
                    - Your identity: {witness2}
                    - Case: {case_title}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Answer the defense attorney's question:
                    1. Honestly and directly
                    2. Admit uncertainties if they exist
                    3. Don't embellish or speculate
                    4. Stay calm and composed
                    5. Maintain consistency with earlier testimony
                    
                    APPROACH: Truthful, measured response
                    GOAL: Answer honestly regardless of which side benefits
                    LENGTH: Under 100 words, direct response
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in witness_2_cross_answer_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 2", 
                            "Second Witness (Cross-Response)", 
                            response, 
                            "#20B2AA"
                        )

            day_prompt += f"Second Witness Cross-Response: {response}\n\n"

        #---------------------------------------------------------------------
            # Expert's statement on new evidence with chat styling
            expert_day2_response_stream: Iterator[RunResponse] = expert_agent.run(
                dedent(f"""
                    You are Dr. Anjali Verma, Expert Witness continuing your analysis.
                    
                    TASK: Analyze new evidence presented on Day 2.
                    
                    CONTEXT:
                    - Case: {case_title}
                    - New evidence to analyze: {evidence2}
                    - Previous analysis from Day 1: {expert_prompt}
                    - Court proceedings: {day_prompt}
                    
                    STRUCTURE YOUR ANALYSIS:
                    1. Reference your previous testimony briefly
                    2. Analyze the technical aspects of {evidence2}
                    3. Compare/contrast with Day 1 evidence
                    4. State your professional findings
                    5. Address any implications or correlations
                    
                    APPROACH: Scientific objectivity, clear explanations
                    GOAL: Help court understand new technical evidence
                    LENGTH: Under 100 words but thorough
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in expert_day2_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Dr. Anjali Verma", 
                            "Expert Witness (Day 2 Analysis)", 
                            response, 
                            "#4169E1"
                        )

            day_prompt += f"Expert Day 2 Analysis: {response}\n\n"
            expert_prompt += f"Expert Day 2 Analysis: {response}\n\n"

        #---------------------------------------------------------------------
            # Defense witness statement with chat styling
            defense_witness_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the defense witness testifying in "{case_title}".
                    
                    TASK: Provide testimony that supports the defense case.
                    
                    WITNESS DETAILS: {witness3}
                    
                    CONTEXT:
                    - Case: {case_description}
                    - Evidence supporting your testimony: {evidence3}
                    - Accused: {accused}
                    - Court proceedings so far: {day_prompt}
                    
                    STRUCTURE YOUR TESTIMONY:
                    1. State your name and relationship to this case
                    2. Describe what you witnessed that supports the defense
                    3. Present evidence or information that contradicts prosecution
                    4. Explain how your testimony relates to {evidence3}
                    5. Support the accused's innocence or provide alternative explanation
                    
                    APPROACH: Truthful, supportive of defense case
                    GOAL: Create reasonable doubt or support innocence
                    LENGTH: Under 100 words but compelling
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in defense_witness_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 3", 
                            "Defense Witness", 
                            response, 
                            "#32CD32"
                        )

            day_prompt += f"Defense Witness Testimony: {response}\n\n"

        #---------------------------------------------------------------------
            # Prosecutor cross-examination of defense witness with chat styling
            prosecutor_cross_defense_response_stream: Iterator[RunResponse] = prosecutor_agent.run(
                dedent(f"""
                    You are Prosecutor Advocate Rohan Deshmukh.
                    
                    TASK: Cross-examine the defense witness.
                    
                    CONTEXT:
                    - Defense witness testimony: Previous testimony about {witness3}
                    - Case: {case_title}
                    - Evidence to challenge: {evidence3}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Ask ONE cross-examination question that:
                    1. Challenges the defense witness's credibility
                    2. Questions their version of events
                    3. Highlights inconsistencies with prosecution evidence
                    4. Undermines their support for the accused
                    
                    CROSS-EXAMINATION STRATEGY:
                    - Question their bias toward the accused
                    - Challenge their interpretation of {evidence3}
                    - Probe gaps in their account
                    
                    FORMAT: "Witness [Name], isn't it true that [your challenge]?"
                    LENGTH: One strategic question under 50 words
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in prosecutor_cross_defense_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Rohan Deshmukh", 
                            "Prosecutor (Cross-Examination)", 
                            response, 
                            "#DC143C"
                        )

            day_prompt += f"Prosecutor's Cross of Defense Witness: {response}\n\n"
            prosecutor_prompt += f"Prosecutor's Cross of Defense Witness: {response}\n\n"

        #---------------------------------------------------------------------
            # Defense witness response to prosecutor with chat styling
            defense_witness_cross_answer_response_stream: Iterator[RunResponse] = witness_agent.run(
                dedent(f"""
                    You are the defense witness responding to Prosecutor's cross-examination.
                    
                    PROSECUTOR'S QUESTION: {prosecutor_cross_defense_response_stream}
                    
                    CONTEXT:
                    - Your identity: {witness3}
                    - Case: {case_title}
                    - Your supporting evidence: {evidence3}
                    - Court proceedings: {day_prompt}
                    
                    INSTRUCTION:
                    Answer the prosecutor's question:
                    1. Honestly and directly
                    2. Defend your testimony if appropriate
                    3. Admit uncertainties rather than speculate
                    4. Stay supportive of defense case when truthful
                    5. Maintain composure under pressure
                    
                    APPROACH: Truthful, composed, consistent
                    GOAL: Maintain credibility while supporting defense
                    LENGTH: Under 100 words, direct response
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in defense_witness_cross_answer_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Witness 3", 
                            "Defense Witness (Cross-Response)", 
                            response, 
                            "#32CD32"
                        )

            day_prompt += f"Defense Witness Cross-Response: {response}\n\n"

        #---------------------------------------------------------------------
            # Judge's end of day 2 summary with chat styling
            judge_end_day2_response_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal concluding Day 2.

                    TASK: Formally end Day 2 and preview Day 3.

                    CONTEXT:
                    - Case: {case_title}
                    - Today's proceedings: {day_prompt}
                    - Previous day: {judge_prompt}

                    STRUCTURE YOUR CONCLUSION:
                    1. Summarize key developments from Day 2
                    2. Note important evidence and testimony presented
                    3. Acknowledge both prosecution and defense presentations
                    4. Explain the need for Day 3 (closing arguments, deliberation)
                    5. Preview tomorrow's agenda (final statements, verdict)
                    6. Give instructions to all parties
                    7. Formally adjourn court

                    TONE: Authoritative, fair, building toward conclusion
                    GOAL: Proper case management and final day preparation
                    LENGTH: Under 200 words but comprehensive
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in judge_end_day2_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge (Day 2 Conclusion)", 
                            response, 
                            "#8B4513"
                        )

            total_prompt += f"Judge's Day 2 Summary: {response}\n\n"
            day_prompt += f"Judge's Day 2 Summary: {response}\n\n"
            judge_prompt += f"Judge's Day 2 Summary: {response}\n\n"

            # Close the main chat container
            st.markdown("</div>", unsafe_allow_html=True)

            # Narrative Agent's response - moved to sidebar with chat styling
            with sidebar_narrative_container:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #e8f4f8, #ffffff);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #2196F3;
                ">
                    <h4 style="
                        color: #1976D2;
                        margin-bottom: 15px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        📝 Case Narrative - Day 2
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                narrative_day2_response_stream: Iterator[RunResponse] = narrative_agent.run(
                    dedent(f"""
                        You are a professional legal narrative specialist covering Day 2 of "{case_title}".
                        
                        TASK: Create Day 2 case narrative and updated timeline.
                        
                        CONTEXT:
                        - Today's proceedings: {day_prompt}
                        - Complete case history: {total_prompt}
                        - Case participants: {name_prompt}
                        
                        STRUCTURE YOUR NARRATIVE:
                        1. **Day 2 Timeline**: Key events and testimony
                        2. **Evidence Update**: New evidence {evidence2} and {evidence3}
                        3. **Strategic Analysis**: How each side is building their case
                        4. **Key Moments**: Most impactful testimony or exchanges
                        5. **Trial Trajectory**: How the case is developing
                        
                        STYLE: Professional legal analysis, comprehensive tracking
                        APPROACH: Analytical, building toward final day
                        LENGTH: Under 150 words, structured format
                    """),
                    stream=True
                )

                narrative_response = ""
                narrative_message_placeholder = st.empty()
                for _resp_chunk in narrative_day2_response_stream:
                    if _resp_chunk.content is not None:
                        narrative_response += _resp_chunk.content
                        with narrative_message_placeholder.container():
                            display_sidebar_chat_message(
                                "Legal Analyst", 
                                "Case Narrative Specialist", 
                                narrative_response, 
                                "#2196F3"
                            )

            total_prompt += f"Day 2 Complete Summary: {day_prompt}\n\n"

            # Media and Public's statement - moved to sidebar with chat styling
            with sidebar_media_container:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fff3e0, #ffffff);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #FF9800;
                ">
                    <h4 style="
                        color: #F57C00;
                        margin-bottom: 15px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        📺 Media Report - Day 2
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                media_day2_response_stream: Iterator[RunResponse] = media_and_public_agent.run(
                    dedent(f"""
                        You are a professional court reporter covering Day 2 of "{case_title}".

                        TASK: Share a summary of public opinion under 100 words about Day 2 of the trial.

                        CONTEXT:
                        - Today's proceedings: {day_prompt}
                        - Previous coverage: {media_and_public_prompt}
                        - Case participants: {name_prompt}

                        STRUCTURE YOUR REPORT:
                        1. Capture how the public reacted to Day 2
                        2. Highlight any shifts in sentiment after today's testimony or evidence
                        3. Mention notable public commentary or media buzz

                        STYLE: Professional journalism, balanced tone
                        APPROACH: Factual reporting, no speculation
                        LENGTH: Under 100 words, focused on public opinion
                    """),
                    stream=True
                )

                media_response = ""
                media_message_placeholder = st.empty()
                for _resp_chunk in media_day2_response_stream:
                    if _resp_chunk.content is not None:
                        media_response += _resp_chunk.content
                        with media_message_placeholder.container():
                            display_sidebar_chat_message(
                                "Court Reporter", 
                                "Media & Public Opinion", 
                                media_response, 
                                "#FF9800"
                            )

                media_and_public_prompt += f"Day 2 Media Report: {media_response}\n\n"

        ######################################################################
            # End of Day 2 - increment day counter
            no_of_days += 1

        ######################################################################
        elif no_of_days == 3:

            day_prompt = ""
            total_prompt += dedent(f"""Day {no_of_days} Summary:\n""")
            day_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            judge_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            prosecutor_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            defense_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            expert_prompt += dedent(f"""Day {no_of_days} Proceedings:\n""")
            media_and_public_prompt += dedent(f"""Day {no_of_days} Coverage:\n""")

            # Enhanced header for Day 3 with chat styling
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #8B0000, #DC143C);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h1 style="margin: 0; font-size: 28px;">⚖️ {case_title}</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Final Day - Verdict & Judgment - Day 3</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Chat container styling
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8f9fa, #ffffff);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                border: 1px solid #e9ecef;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            ">
                <h3 style="
                    color: #495057;
                    margin-bottom: 25px;
                    text-align: center;
                    border-bottom: 2px solid #dee2e6;
                    padding-bottom: 15px;
                    font-size: 20px;
                ">⚖️ Final Court Session - Verdict Day</h3>
            """, unsafe_allow_html=True)

        #---------------------------------------------------------------------
            # Judge's opening for final day with chat styling
            judge_response_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal opening Day 3 (Final Day) of "{case_title}".

                    TASK: Formally open the final day of proceedings.

                    CONTEXT:
                    - Case: {case_description}
                    - Participants: {name_prompt}
                    - Previous proceedings: {total_prompt}
                    - This is the decisive final day

                    STRUCTURE YOUR OPENING:
                    1. Call court to order and acknowledge this is the final day
                    2. Briefly summarize the case journey so far
                    3. Outline today's agenda (closing arguments, verdict)
                    4. Remind all parties this is their final opportunity
                    5. Set expectations for closing arguments
                    6. Invite Prosecutor to begin closing statement

                    TONE: Authoritative, solemn, decisive
                    LENGTH: Under 150 words but comprehensive
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in judge_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge (Final Day Opening)", 
                            response, 
                            "#8B4513"
                        )

            total_prompt += f"Judge's Day 3 Opening: {response}\n\n"
            day_prompt += f"Judge's Day 3 Opening: {response}\n\n"
            judge_prompt += f"Judge's Day 3 Opening: {response}\n\n"

        #---------------------------------------------------------------------
            # Prosecutor's closing statement with chat styling
            prosecutor_response_stream: Iterator[RunResponse] = prosecutor_agent.run(
                dedent(f"""
                    You are Advocate Rohan Deshmukh delivering your closing argument.
                    
                    TASK: Deliver a compelling closing statement for "{case_title}".
                    
                    CONTEXT:
                    - Case details: {case_description}
                    - All evidence presented: {evidence1}, {evidence2}, {evidence3}
                    - Previous proceedings: {prosecutor_prompt}
                    - Court proceedings today: {day_prompt}
                    
                    STRUCTURE YOUR CLOSING:
                    1. Thank the court and recap your case
                    2. Summarize the strongest evidence against {accused}
                    3. Address witness testimonies that support your case
                    4. Counter any defense arguments preemptively
                    5. Make final appeal for justice and conviction
                    6. Request specific verdict from the court
                    
                    APPROACH: Passionate but professional, conclusive
                    GOAL: Convince court of {accused}'s guilt beyond reasonable doubt
                    LENGTH: Under 150 words but powerful
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in prosecutor_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Rohan Deshmukh", 
                            "Prosecutor (Closing Statement)", 
                            response, 
                            "#DC143C"
                        )

            day_prompt += f"Prosecutor's Closing Statement: {response}\n\n"
            prosecutor_prompt += f"Prosecutor's Closing Statement: {response}\n\n"

        #---------------------------------------------------------------------
            # Defense's closing statement with chat styling
            defense_response_stream: Iterator[RunResponse] = defense_agent.run(
                dedent(f"""
                    You are Advocate Priya Sharma delivering your closing argument for {accused}.
                    
                    TASK: Deliver a compelling defense closing statement.
                    
                    CONTEXT:
                    - Case against your client: {case_description}
                    - Evidence to challenge: {evidence1}, {evidence2}, {evidence3}
                    - Previous defense arguments: {defense_prompt}
                    - Court proceedings today: {day_prompt}
                    
                    STRUCTURE YOUR CLOSING:
                    1. Thank the court and state your client's innocence
                    2. Highlight weaknesses in prosecution's evidence
                    3. Emphasize reasonable doubt created during trial
                    4. Reference favorable witness testimony or expert opinions
                    5. Appeal to principles of justice and burden of proof
                    6. Request acquittal or alternative verdict
                    
                    APPROACH: Confident, systematic doubt creation
                    GOAL: Create reasonable doubt and secure client's freedom
                    LENGTH: Under 150 words but persuasive
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in defense_response_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Advocate Priya Sharma", 
                            "Defense Attorney (Closing Statement)", 
                            response, 
                            "#9932CC"
                        )

            day_prompt += f"Defense's Closing Statement: {response}\n\n"
            defense_prompt += f"Defense's Closing Statement: {response}\n\n"

        #---------------------------------------------------------------------
            # Judge's deliberation and final verdict with chat styling
            judge_deliberation_verdict_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal concluding the trial for "{case_title}".

                    TASK: First announce your deliberation process then deliver the final verdict.

                    CONTEXT:
                    - Case: {case_title} - {case_description}
                    - All evidence presented: {evidence1}, {evidence2}, {evidence3}
                    - Complete proceedings: {total_prompt}
                    - Today's closing arguments: {day_prompt}
                    - Accused: {accused}
                    - Plaintiff: {plaintiff}

                    STRUCTURE YOUR RESPONSE:
                    1. Deliberation:
                    a. Acknowledge both closing arguments
                    b. State you will now consider all evidence and key factors
                    c. Reference legal standards (burden of proof, reasonable doubt)
                    d. Explain the gravity of this decision
                    e. Prepare court for the verdict announcement
                    2. Final Verdict:
                    a. Call for order and announce verdict
                    b. Summarize key evidence and testimony considered
                    c. Explain your legal reasoning and application of law
                    d. State the verdict clearly (Guilty/Not Guilty)
                    e. If guilty, announce sentencing; if not guilty, explain acquittal
                    f. Address both plaintiff and accused directly
                    g. Provide any final judicial remarks

                    TONE: Solemn, thoughtful, authoritative, fair
                    GOAL: Show proper consideration and deliver justice based on evidence and law
                    LENGTH: Under 300 words total
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in judge_deliberation_verdict_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge (Deliberation & Verdict)", 
                            response, 
                            "#8B0000"
                        )

            day_prompt += f"Judge's Deliberation and Final Verdict: {response}\n\n"
            judge_prompt += f"Judge's Deliberation and Final Verdict: {response}\n\n"
            total_prompt += f"Judge's Deliberation and Final Verdict: {response}\n\n"

        #---------------------------------------------------------------------
            # Judge's formal case conclusion with chat styling
            judge_conclusion_stream: Iterator[RunResponse] = judge_agent.run(
                dedent(f"""
                    You are Judge Raghav Bansal formally concluding the case "{case_title}".
                    
                    TASK: Formally close the case and dismiss court.
                    
                    CONTEXT:
                    - Verdict has been delivered: {judge_prompt}
                    - Case participants: {name_prompt}
                    - Complete case: {total_prompt}
                    
                    STRUCTURE YOUR CONCLUSION:
                    1. Acknowledge completion of all proceedings
                    2. Thank all parties for their participation
                    3. Confirm verdict is final (unless appealed)
                    4. Address any immediate post-trial matters
                    5. Thank court staff and legal teams
                    6. Formally adjourn court and close case
                    
                    TONE: Formal, respectful, conclusive
                    GOAL: Proper case closure and court dismissal
                    LENGTH: Under 100 words but dignified
                """),
                stream=True
            )

            response = ""
            message_placeholder = st.empty()
            for _resp_chunk in judge_conclusion_stream:
                if _resp_chunk.content is not None:
                    response += _resp_chunk.content
                    with message_placeholder.container():
                        display_chat_message(
                            "Judge Raghav Bansal", 
                            "Presiding Judge (Case Conclusion)", 
                            response, 
                            "#8B4513"
                        )

            total_prompt += f"Judge's Case Conclusion: {response}\n\n"
            day_prompt += f"Judge's Case Conclusion: {response}\n\n"
            judge_prompt += f"Judge's Case Conclusion: {response}\n\n"

            # Close the main chat container
            st.markdown("</div>", unsafe_allow_html=True)

            # Narrative Agent's final response - moved to sidebar with chat styling
            with sidebar_narrative_container:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #e8f4f8, #ffffff);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #2196F3;
                ">
                    <h4 style="
                        color: #1976D2;
                        margin-bottom: 15px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        📝 Case Narrative - Final Summary
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                narrative_response_stream: Iterator[RunResponse] = narrative_agent.run(
                    dedent(f"""
                        You are a professional legal narrative specialist providing final case analysis for "{case_title}".
                        
                        TASK: Create comprehensive case summary and legal analysis.
                        
                        CONTEXT:
                        - Complete case: {total_prompt}
                        - Final day proceedings: {day_prompt}
                        - All evidence: {evidence1}, {evidence2}, {evidence3}
                        - All witnesses: {witness1}, {witness2}, {witness3}
                        
                        STRUCTURE YOUR ANALYSIS:
                        1. **Case Overview**: Complete case summary from start to finish
                        2. **Evidence Analysis**: How evidence influenced the verdict
                        3. **Legal Strategy Review**: Prosecution vs Defense effectiveness
                        4. **Witness Impact**: How testimony shaped the case
                        5. **Verdict Analysis**: Why the judge reached this decision
                        6. **Case Significance**: Legal precedent or public impact
                        
                        STYLE: Professional legal analysis, comprehensive review
                        APPROACH: Analytical, educational, complete case study
                        LENGTH: Under 150 words, structured final analysis
                    """),
                    stream=True
                )

                narrative_response = ""
                narrative_message_placeholder = st.empty()
                for _resp_chunk in narrative_response_stream:
                    if _resp_chunk.content is not None:
                        narrative_response += _resp_chunk.content
                        with narrative_message_placeholder.container():
                            display_sidebar_chat_message(
                                "Legal Analyst", 
                                "Case Narrative Specialist (Final)", 
                                narrative_response, 
                                "#2196F3"
                            )

            total_prompt += f"Final Case Analysis: {narrative_response}\n\n"

            # Media and Public's final report - moved to sidebar with chat styling
            with sidebar_media_container:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fff3e0, #ffffff);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #FF9800;
                ">
                    <h4 style="
                        color: #F57C00;
                        margin-bottom: 15px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        📺 Media Final Report - Day 3
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                media_and_public_response_stream: Iterator[RunResponse] = media_and_public_agent.run(
                    dedent(f"""
                        You are a professional court reporter providing final coverage of "{case_title}".

                        TASK: Share a final summary of public opinion in under 150 words following the conclusion of the trial.

                        CONTEXT:
                        - Complete case proceedings: {total_prompt}
                        - Today's final day: {day_prompt}
                        - Case participants: {name_prompt}
                        - Final verdict delivered

                        STRUCTURE YOUR REPORT:
                        1. Reflect public sentiment on the verdict
                        2. Mention how opinion evolved over the 3 days
                        3. Highlight any strong reactions from media or community voices
                        4. Note conversations around justice, fairness, or controversy

                        STYLE: Professional journalism, balanced tone
                        APPROACH: Factual reporting of public sentiment only
                        LENGTH: Under 150 words, focused on public reaction
                    """),
                    stream=True
                )

                media_response = ""
                media_message_placeholder = st.empty()
                for _resp_chunk in media_and_public_response_stream:
                    if _resp_chunk.content is not None:
                        media_response += _resp_chunk.content
                        with media_message_placeholder.container():
                            display_sidebar_chat_message(
                                "Court Reporter", 
                                "Media & Public Opinion (Final)", 
                                media_response, 
                                "#FF9800"
                            )

                media_and_public_prompt += f"Final Media Report: {media_response}\n\n"

            # Success message with styling
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 30px 0;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h2 style="margin: 0; font-size: 24px;">🎯 Case Concluded Successfully!</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">The trial has reached its conclusion. All parties have been heard, evidence has been presented, and justice has been served.</p>
            </div>
            """, unsafe_allow_html=True)

            no_of_days += 1

        #---------------------------------------------------------------------
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f44336, #d32f2f);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 30px 0;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h2 style="margin: 0; font-size: 24px;">⚠️ Trial Already Concluded</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">The trial has already concluded. Please start a new case to continue.</p>
            </div>
            """, unsafe_allow_html=True)
            break

###############################################################################

#Validate API keys function
def validate_api_keys(openai_key: str) -> tuple[bool, str]:
    """Validate that API key is provided and has basic format"""
    if not openai_key or not openai_key.strip():
        return False, "OpenAI API Key is required"
    
    # Basic format validation
    if not openai_key.startswith('sk-'):
        return False, "OpenAI API Key should start with 'sk-'"
    
    if len(openai_key) < 20:
        return False, "OpenAI API Key appears to be too short"
    
    return True, "API Key validated successfully"

# Streamlit app creation function
def create_streamlit_app():
    st.set_page_config(
        page_title="Legal AI Court Case Simulator",
        page_icon="⚖️",
        layout="wide"
    )

    st.title("⚖️ Legalia.AI")
    st.markdown("Experience an AI-powered court case simulation with multiple roles and perspectives.")

    # API Keys Section - Show first
    st.header("🔑 API Configuration")
    st.markdown("Please provide your OpenAI API key to proceed with the simulation.")
    
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        type="password",
        help="Enter your OpenAI API key (starts with sk-)",
        placeholder="sk-..."
    )
    
    # Validate API key
    api_key_valid, validation_message = validate_api_keys(openai_api_key)
    
    if not api_key_valid:
        st.error(validation_message)
        st.info("👆 Please provide valid API key to continue.")
        st.stop()
    else:
        st.success("✅ API Key validated successfully!")
        # Set environment variables for the session
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    st.divider()

    # Sidebar for case details - Only show after API key is validated
    with st.sidebar:
        st.header("Case Details")
        case_title = st.text_input("Case Title", help="Enter a descriptive title for the case")
        case_description = st.text_area("Case Description", help="Provide a detailed description of the case")
        
        st.subheader("Parties Involved")
        plaintiff = st.text_input("Plaintiff Name", help="Name of the person bringing the case")
        accused = st.text_input("Accused Name", help="Name of the person being accused")
        
        st.subheader("Evidence")
        evidence1 = st.text_input("Evidence 1", help="First piece of evidence")
        evidence2 = st.text_input("Evidence 2", help="Second piece of evidence")
        evidence3 = st.text_input("Evidence 3", help="Third piece of evidence")
        
        st.subheader("Witnesses")
        witness1 = st.text_input("Witness 1 Name and Statement", help="First witness and their statement")
        witness2 = st.text_input("Witness 2 Name and Statement", help="Second witness and their statement")
        witness3 = st.text_input("Witness 3 Name and Statement", help="Third witness and their statement")
        
        start_trial = st.button("Start Trial", type="primary")

    # Main content area
    if start_trial:
        # Validation with better error messages
        required_fields = {
            "Case Title": case_title,
            "Case Description": case_description,
            "Plaintiff Name": plaintiff,
            "Accused Name": accused,
            "Evidence 1": evidence1,
            "Evidence 2": evidence2,
            "Evidence 3": evidence3,
            "Witness 1": witness1,
            "Witness 2": witness2,
            "Witness 3": witness3
        }
        
        empty_fields = [field for field, value in required_fields.items() if not value or not value.strip()]
        
        if empty_fields:
            st.error(f"Please fill in the following required fields: {', '.join(empty_fields)}")
        else:
            # Display case summary before starting
            st.subheader("Case Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Case:** {case_title}")
                st.write(f"**Description:** {case_description}")
                st.write(f"**Plaintiff:** {plaintiff}")
                st.write(f"**Accused:** {accused}")
                st.write(f"**Your Role:** Observer")
            
            with col2:
                st.write("**Evidence:**")
                st.write(f"1. {evidence1}")
                st.write(f"2. {evidence2}")
                st.write(f"3. {evidence3}")
                
                st.write("**Witnesses:**")
                st.write(f"1. {witness1}")
                st.write(f"2. {witness2}")
                st.write(f"3. {witness3}")
            
            st.divider()
            
            # Start the simulation
            with st.spinner("Initializing court case simulation..."):
                try:
                    court_case_pipeline(
                        case_title=case_title,
                        case_description=case_description,
                        evidence1=evidence1,
                        evidence2=evidence2,
                        evidence3=evidence3,
                        witness1=witness1,
                        witness2=witness2,
                        witness3=witness3,
                        plaintiff=plaintiff,
                        accused=accused
                    )
                except ImportError as e:
                    st.error(f"Import error: {str(e)}. Please ensure all required modules are installed and accessible.")
                except NameError as e:
                    st.error(f"Function not found: {str(e)}. Please ensure court_case_pipeline is properly imported.")
                except TypeError as e:
                    st.error(f"Function call error: {str(e)}. Please check the function parameters.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
                    st.write("Please check the console for more detailed error information.")
    
    else:
        # Show instructions when not started
        st.info("👈 Please fill in all the case details in the sidebar and click 'Start Trial' to begin the simulation.")
        
        # Add some example information
        with st.expander("Example Case Setup"):
            st.write("""
            **Case Title:** TechNova Inc. vs. Quantum Solutions: Trade Secret Theft
            
            **Case Description:** TechNova Inc. alleges that a former employee leaked proprietary AI model architectures to a competitor, Quantum Solutions. The plaintiff claims that this leak resulted in financial losses and compromised competitive advantage.
                     
            **Plaintiff:** TechNova Inc.
            
            **Accused:** Alex Morgan (Quantum Solutions)
            
            **Evidence Examples:**
            - Internal emails retrieved from Alex Morgan's company account showing communication with Quantum Solutions while still employed at TechNova.
            - A USB drive containing confidential architecture files found in Alex's personal belongings during a security audit.
            - Download logs from TechNova's internal server indicating large data transfers from Alex's account shortly before resignation.
            
            **Witness Examples:**
            - Sarah Kim (CTO, TechNova Inc.): "Alex was part of the restricted-access team and had full visibility into our next-gen AI project. He had no reason to download those files unless he intended to misuse them."
            - Dr. Raj Patel (Cybersecurity Analyst): "Our investigation shows that the files accessed match the confidential model specifications now seen in Quantum's new product line."
            - Alex Morgan (Accused): "The files in question were part of my assigned work. I did not share or misuse them, and Quantum's models were developed independently."
            """)

def main():
    """Main function to run the Streamlit app"""
    create_streamlit_app()

if __name__ == "__main__":
    main()