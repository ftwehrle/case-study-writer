# Disclaimer: Code written by Gemini 2.5 Pro

import streamlit as st
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

# --- Page Configuration ---
st.set_page_config(
    page_title="Personalized Case Study Writer",
    page_icon="✍️",
    layout="wide"
)

# --- Gemini API Configuration ---
def load_api_key():
    """
    Loads the Gemini API key securely. It first tries to load from a local .env
    file (for local development) and falls back to Streamlit's secrets management
    (for cloud deployment).
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        if api_key:
            return api_key
    except (KeyError, FileNotFoundError):
        pass
    st.error("GEMINI_API_KEY not found. Please set it in a local .env file or your Streamlit secrets.", icon="🚨")
    st.stop()

api_key = load_api_key()
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- Session State Initialization ---
if 'instructor_data' not in st.session_state:
    st.session_state.instructor_data = None
if 'generation_results' not in st.session_state:
    st.session_state.generation_results = {}
if 'final_case_study' not in st.session_state:
    st.session_state.final_case_study = ""


# --- Helper function to call Gemini ---
def call_gemini(prompt, chat_history=None):
    """
    Sends a prompt to the Gemini API. Can handle chat history for context.
    """
    try:
        if chat_history is not None:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
            return response.text, chat.history
        else:
            response = model.generate_content(prompt)
            return response.text, [
                {'role': 'user', 'parts': [prompt]},
                {'role': 'model', 'parts': [response.text]}
            ]
    except Exception as e:
        st.error(f"An error occurred with the API call: {e}")
        return None, chat_history

# --- Page Title ---
st.title("✍️ Personalized Case Study Writer")
st.caption("A tool to generate bespoke case studies for business school students.")

# --- Interface Tabs ---
instructor_tab, student_tab = st.tabs(["👨‍🏫 Step 1: Instructor Setup", "👩‍🎓 Step 2: Student Input & Generation"])

# --- Instructor Interface ---
with instructor_tab:
    st.header("Instructor Setup")
    st.markdown("First, please provide the general details for the case study you want to create.")
    with st.form(key="instructor_form"):
        institution = st.text_input("Name of the institution", "Harvard Business School")
        course_title = st.text_input("Course Title", "Strategic Management")
        discipline = st.text_input("Discipline", "Business Strategy")
        target_audience = st.text_input("Target Audience", "MBA Students")
        case_topic = st.text_area("Topic of the case study", "Analyzing market entry strategies in the renewable energy sector.")
        learning_objectives = st.text_area("Learning Objectives", "1. Apply Porter's Five Forces to the renewable energy industry.\n2. Evaluate the pros and cons of different market entry modes (e.g., acquisition, greenfield investment).\n3. Conduct a SWOT analysis of a key player.")
        student_questions = st.text_area("Questions for students", "1. What are the primary barriers to entry in this market?\n2. Which entry strategy would you recommend and why?\n3. What are the biggest risks associated with your recommended strategy?")
        submitted_instructor_form = st.form_submit_button("Save Instructor Setup", type="primary")
        if submitted_instructor_form:
            st.session_state.instructor_data = {
                "institution": institution, "course_title": course_title, "discipline": discipline,
                "target_audience": target_audience, "case_topic": case_topic,
                "learning_objectives": learning_objectives, "student_questions": student_questions,
            }
            st.success("Instructor information saved! Please proceed to the next tab.")

# --- Student Interface ---
with student_tab:
    st.header("Student Input & Generation")
    st.markdown("Next, provide the specific company and role for this version of the case study.")
    if not st.session_state.instructor_data:
        st.warning("Please complete and save the 'Instructor Setup' in the first tab before proceeding.")
    else:
        with st.form(key="student_form"):
            company_name = st.text_input("Company Name", "Tesla, Inc.")
            job_title = st.text_input("Job Title", "Head of Global Strategy")
            submitted_student_form = st.form_submit_button("Generate Full Case Study", type="primary")

            if submitted_student_form:
                st.session_state.generation_results = {}
                st.session_state.final_case_study = ""
                instructor = st.session_state.instructor_data
                chat_history = []

                # --- STEP 1: DEEP RESEARCH ---
                with st.spinner("Step 1/11: Conducting deep research..."):
                    prompt_step1 = f"""In the role of an expert corporate analyst with over 10 years of experience in creating meaningful and effective reports for leadership boards of Fortune 500 companies, please create an industry report for the leadership board of {company_name}. The topic of the report is: {instructor['case_topic']}. The leadership board wants to learn the following: {instructor['learning_objectives']}. The leadership board wants to be able to answer the following questions: {instructor['student_questions']}."""
                    report, _ = call_gemini(prompt_step1)
                    st.session_state.generation_results['1_report'] = report

                # --- STEP 2: PERSONA ---
                with st.spinner("Step 2/11: Defining writer persona..."):
                    persona_prompt = f"""Your role: You are a deep expert in {instructor['discipline']} with over 10 years of experience as {job_title} at {company_name}.

Your personality: You are extroverted, joyful and kind. You are a deeply analytical thinking, above average creative and you always think outside of the box to find unconventional, yet effective solutions to problems..

Your expertise: You have over 10 years of experience as {job_title} at {company_name}. You have taught case studies at ivy league business schools for over 5 years. You also have over 5 years of experience in writing highly engaging and meaningful case studies for MBA programs in ivy league business schools.

Your writing style: When writing case studies for MBA students at ivy league business schools, you adhere to the best practices of such quality case studies, but you add your own talent as an experienced storyteller to it. Your defining quality as a case study writer, which makes you stand out from others, is that you are able to write in such a way that the cases become particularly realistic and captivating for the students. You are also building in many engaging elements, which are not typical for case studies, but which make them much more engaging for students and therefore increase the completion rate significantly. Finally, you write based on high quality sources, which you rigorously cite throughout the document."""
                    st.session_state.generation_results['2_persona_prompt'] = persona_prompt
                    chat_history.append({'role': 'user', 'parts': [persona_prompt]})
                    chat_history.append({'role': 'model', 'parts': ["Understood. I will now act as this persona for all subsequent tasks."]})

                # --- STEP 3: OUTLINE ---
                with st.spinner("Step 3/11: Writing the case study outline..."):
                    case_structure = """- Title Page\n- Introduction\n- Case Study Narrative\n- Analysis of Strategic Decisions\n- Critical Discussion\n- Reflection and Application\n- Supplementary Materials\n- Conclusion"""
                    prompt_step3 = f"""In this role, you are writing a case study focused on the job of {job_title} at {company_name}. In this role, please create a brief overview of the case study on {instructor['case_topic']} which achieves the following learning objectives: {instructor['learning_objectives']}. The overview must follow this structure:\n{case_structure}"""
                    outline, chat_history = call_gemini(prompt_step3, chat_history=chat_history)
                    st.session_state.generation_results['3_outline'] = outline

                # --- STEPS 4-10: WRITING THE CASE STUDY ---
                sections_to_write = [
                    {"step": 4, "title": "Introduction", "description": "Background Information: Provide a brief introduction to the company or brand featured in the case study.\nIndustry Context: Describe the industry landscape and the market conditions at the time of the case study.\nPurpose of the Case Study: Clarify the educational objectives and what students should aim to learn from this case study."},
                    {"step": 5, "title": "Case Study Narrative", "description": "Company Overview: Detail the company’s history, mission, and market position prior to the implementation of the strategy being studied.\nStrategic Assessment: Outline specific challenges or opportunities for the company."},
                    {"step": 6, "title": "Analysis of Strategic Decisions", "description": "Strategic Decision-Making Process: Delve into how decisions were made, including the data and market research used.\nImplementation Challenges: Describe any obstacles encountered during the implementation of the strategy and how they were overcome.\nOutcomes and Performance: Short-Term Results (analyze immediate effects) and Long-Term Impact (assess long-term effects)."},
                    {"step": 7, "title": "Critical Discussion", "description": "Discussion Points: Provide key points for students to consider, fostering critical thinking about strategic choices made by the company.\nAlternative Strategies: Propose alternative strategies that could have been considered, encouraging students to think about different approaches.\nLessons Learned: Highlight key takeaways and lessons learned from the case study."},
                    {"step": 8, "title": "Reflection and Application", "description": "Reflective Questions: Pose thought-provoking questions to help students apply the insights from the case study to their own or other business contexts.\nHow could these strategies be applied in different industries?\nWhat would you have done differently if you were in charge?"},
                    {"step": 9, "title": "Supplementary Materials", "description": "Graphs and Charts: Include visual aids to represent data and results clearly, as found online.\nFurther Readings: Suggest additional resources for students who wish to explore related topics in more depth."},
                    {"step": 10, "title": "Conclusion", "description": "Recap: Summarize the main insights and the educational value of the case study.\nNext Steps: Encourage further exploration of the concepts learned and how they tie into the upcoming course material."},
                ]
                
                written_sections = []
                for section in sections_to_write:
                    with st.spinner(f"Step {section['step']}/11: Writing the {section['title']}..."):
                        preceding_parts = ", ".join(written_sections) if written_sections else "None"
                        # NEW: Added a negative constraint to prevent meta-commentary.
                        prompt = f"""In your defined role, please write out all details of the section '{section['title']}' for the case study.
                        
                        The specific requirements for this section are:
                        ---
                        {section['description']}
                        ---

                        Please make sure to take into consideration the content of the preceding parts of the case study: {preceding_parts}.
                        The overall case study outline is: '{st.session_state.generation_results['3_outline']}'.
                        Add relevant details, examples, research insights, data and testimonials of relevant personalities.
                        Ensure your writing is aligned with these learning objectives: {instructor['learning_objectives']}.

                        IMPORTANT INSTRUCTION: Your response for this section must contain ONLY the content for the section itself. Do not add any concluding summaries, meta-commentary, or statements about what the student will learn from this section. Write as if this section is part of a larger, continuous document."""

                        if section['title'] == "Supplementary Materials":
                            prompt += f"\nPlease make sure to create proper citations with corresponding URLs to the source, referencing the initial research report where applicable."
                        if section['title'] == "Conclusion":
                            prompt += f"\nPlease make sure to write elegantly and in a way that is thought provoking and engaging, and strongly aligned with these questions for the students: {instructor['student_questions']}."

                        section_content, chat_history = call_gemini(prompt, chat_history=chat_history)
                        st.session_state.generation_results[f"{section['step']}_{section['title']}"] = section_content
                        written_sections.append(section['title'])
                
                st.success("Full case study generation complete!")
                st.balloons()
                
                # --- STEP 11: Collate the final case study ---
                final_text = f"# Case Study: {instructor['case_topic']} for {company_name}\n\n"
                for section in sections_to_write:
                    key = f"{section['step']}_{section['title']}"
                    if key in st.session_state.generation_results:
                        final_text += f"## {section['title']}\n\n"
                        final_text += st.session_state.generation_results[key] + "\n\n---\n\n"
                st.session_state.final_case_study = final_text


# --- Display Generation Results ---
if st.session_state.generation_results:
    st.header("Final Case Study")
    if st.session_state.final_case_study:
        st.markdown(st.session_state.final_case_study)
        st.download_button(
            label="Download Case Study as Markdown File", 
            data=st.session_state.final_case_study, 
            file_name="case_study.md",
            mime="text/markdown"
        )
    
    st.header("Generation Process Details")
    display_order = [
        "1_report", "2_persona_prompt", "3_outline", "4_Introduction", 
        "5_Case Study Narrative", "6_Analysis of Strategic Decisions", 
        "7_Critical Discussion", "8_Reflection and Application", 
        "9_Supplementary Materials", "10_Conclusion"
    ]
    for key in display_order:
        if key in st.session_state.generation_results:
            title = key.split('_', 1)[1].replace('_', ' ').title()
            with st.expander(f"Step {key.split('_')[0]}: {title}", expanded=False):
                st.markdown(st.session_state.generation_results[key])
