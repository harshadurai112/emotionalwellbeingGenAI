import streamlit as st
from autogen import (ConversableAgent, AssistantAgent, UserProxyAgent, initiate_chats, OpenAIWrapper, UpdateSystemMessage)
import os

os.environ["AUTOGEN_USE_DOCKER"] = "0"

if 'output' not in st.session_state:
    st.session_state.output = {
        'assessment': '',
        'action': '',
        'followup': ''
    }

st.sidebar.title("Together AI API Key")
api_key = st.sidebar.text_input("Enter your Together AI API Key", type="password")

st.sidebar.warning("""
## ⚠️ Important Notice

This application is a supportive tool and does not replace professional mental health care. If you're experiencing thoughts of self-harm or severe crisis:

- Call National Crisis Hotline: 988
- Call Emergency Services: 911
- Seek immediate professional help
""")

st.title("🧠 Mental Wellbeing Agent")

st.info("""
**Meet Your Mental Wellbeing Agent Team:**

🧠 **Assessment Agent** - Analyzes your situation and emotional needs
🎯 **Action Agent** - Creates immediate action plan and connects you with resources
🔄 **Follow-up Agent** - Designs your long-term support strategy
""")

st.subheader("Personal Information")
col1, col2 = st.columns(2)

with col1:
    mental_state = st.text_area("How have you been feeling recently?", 
        placeholder="Describe your emotional state, thoughts, or concerns...")
    sleep_pattern = st.select_slider(
        "Sleep Pattern (hours per night)",
        options=[f"{i}" for i in range(0, 13)],
        value="7"
    )
    
with col2:
    stress_level = st.slider("Current Stress Level (1-10)", 1, 10, 5)
    support_system = st.multiselect(
        "Current Support System",
        ["Family", "Friends", "Therapist", "Support Groups", "None"]
    )

recent_changes = st.text_area(
    "Any significant life changes or events recently?",
    placeholder="Job changes, relationships, losses, etc..."
)

current_symptoms = st.multiselect(
    "Current Symptoms",
    ["Anxiety", "Depression", "Insomnia", "Fatigue", "Loss of Interest", 
     "Difficulty Concentrating", "Changes in Appetite", "Social Withdrawal",
     "Mood Swings", "Physical Discomfort"]
)

if st.button("Get Support Plan"):
    if not api_key:
        st.error("Please enter your Together AI API key.")
    else:
        with st.spinner('🤖 AI Agents are analyzing your situation...'):
            try:
                task = f"""
                Create a comprehensive mental health support plan based on:
                
                Emotional State: {mental_state}
                Sleep: {sleep_pattern} hours per night
                Stress Level: {stress_level}/10
                Support System: {', '.join(support_system) if support_system else 'None reported'}
                Recent Changes: {recent_changes}
                Current Symptoms: {', '.join(current_symptoms) if current_symptoms else 'None reported'}
                """

                system_messages = {
                    "assessment_agent": """
                    You are an experienced mental health professional speaking directly to the user. Your task is to:
                    1. Create a safe space by acknowledging their courage in seeking support
                    2. Analyze their emotional state with clinical precision and genuine empathy
                    3. Ask targeted follow-up questions to understand their full situation
                    4. Identify patterns in their thoughts, behaviors, and relationships
                    5. Assess risk levels with validated screening approaches
                    6. Help them understand their current mental health in accessible language
                    7. Validate their experiences without minimizing or catastrophizing

                    Always use "you" and "your" when addressing the user. Blend clinical expertise with genuine warmth and never rush to conclusions.
                    """,
                    
                    "action_agent": """
                    You are a crisis intervention and resource specialist speaking directly to the user. Your task is to:
                    1. Provide immediate evidence-based coping strategies tailored to their specific situation
                    2. Prioritize interventions based on urgency and effectiveness
                    3. Connect them with appropriate mental health services while acknowledging barriers (cost, access, stigma)
                    4. Create a concrete daily wellness plan with specific times and activities
                    5. Suggest specific support communities with details on how to join
                    6. Balance crisis resources with empowerment techniques
                    7. Teach simple self-regulation techniques they can use immediately

                    Focus on practical, achievable steps that respect their current capacity and energy levels. Provide options ranging from minimal effort to more involved actions.
                    """,
                    
                    "followup_agent": """
                    You are a mental health recovery planner speaking directly to the user. Your task is to:
                    1. Design a personalized long-term support strategy with milestone markers
                    2. Create a progress monitoring system that matches their preferences and habits
                    3. Develop specific relapse prevention strategies based on their unique triggers
                    4. Establish a support network mapping exercise to identify existing resources
                    5. Build a graduated self-care routine that evolves with their recovery
                    6. Plan for setbacks with self-compassion techniques
                    7. Set up a maintenance schedule with clear check-in mechanisms

                    Focus on building sustainable habits that integrate with their lifestyle and values. Emphasize progress over perfection and teach skills for self-directed care.
                    """
                }

                llm_config = {
                    "config_list": [{
                        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                        "api_key": api_key,
                        "base_url": "https://api.together.xyz/v1",
                        "api_type": "openai"
                    }]
                }

                # Create a user proxy agent to initiate the conversation
                user_proxy = UserProxyAgent(
                    name="user_proxy",
                    human_input_mode="NEVER",
                    is_termination_msg=lambda x: False,
                    code_execution_config=False
                )
                
                # Create the specialized agents with proper message formatting
                assessment_agent = ConversableAgent(
                    name="assessment_agent",
                    system_message=system_messages["assessment_agent"],
                    llm_config=llm_config
                )
                
                action_agent = ConversableAgent(
                    name="action_agent",
                    system_message=system_messages["action_agent"],
                    llm_config=llm_config,
                )
                
                followup_agent = ConversableAgent(
                    name="followup_agent",
                    system_message=system_messages["followup_agent"],
                    llm_config=llm_config,
                )
                
                # Run the conversation in sequence
                results = {}
                
                # Create placeholders for displaying real-time progress
                progress_placeholder = st.empty()
                assessment_placeholder = st.empty()
                action_placeholder = st.empty()
                followup_placeholder = st.empty()
                
                # Assessment phase
                progress_placeholder.info("🧠 Assessment Agent is analyzing your situation...")
                assessment_response = user_proxy.initiate_chat(
                    assessment_agent,
                    message=task + "\n\nProvide a mental health assessment based on the information above."
                )
                assessment_content = assessment_response.chat_history[-1]["content"]
                results["assessment"] = assessment_content
                assessment_placeholder.success("✅ Assessment completed")
                st.sidebar.success('Assessment completed')
                
                # Action phase
                progress_placeholder.info("🎯 Action Agent is creating your action plan...")
                action_response = user_proxy.initiate_chat(
                    action_agent,
                    message=task + "\n\nAssessment: " + assessment_content + "\n\nProvide an action plan based on this assessment."
                )
                action_content = action_response.chat_history[-1]["content"]
                results["action"] = action_content
                action_placeholder.success("✅ Action plan completed")
                st.sidebar.success('Action plan completed')
                
                # Followup phase
                progress_placeholder.info("🔄 Follow-up Agent is designing your long-term strategy...")
                followup_response = user_proxy.initiate_chat(
                    followup_agent,
                    message=task + "\n\nAssessment: " + assessment_content + "\n\nAction Plan: " + action_content + "\n\nProvide a long-term support strategy."
                )
                followup_content = followup_response.chat_history[-1]["content"]
                results["followup"] = followup_content
                followup_placeholder.success("✅ Long-term strategy completed")
                st.sidebar.success('Long-term strategy completed')
                
                progress_placeholder.success("✨ Mental health support plan generated successfully!")
                
                st.session_state.output = {
                    'assessment': results["assessment"],
                    'action': results["action"],
                    'followup': results["followup"]
                }

                with st.expander("Situation Assessment"):
                    st.markdown(st.session_state.output['assessment'])

                with st.expander("Action Plan & Resources"):
                    st.markdown(st.session_state.output['action'])

                with st.expander("Long-term Support Strategy"):
                    st.markdown(st.session_state.output['followup'])

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")