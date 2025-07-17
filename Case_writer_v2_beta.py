# Disclaimer: Code written by Gemini 2.5 Pro

import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import time
import os
from dotenv import load_dotenv
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Personalized Case Study Writer",
    page_icon="✍️",
    layout="wide"
)

# --- API Configuration ---
def load_credentials():
    """Loads all necessary API keys and IDs securely."""
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not all([gemini_api_key, search_api_key, search_engine_id]):
        try:
            gemini_api_key = st.secrets["GEMINI_API_KEY"]
            search_api_key = st.secrets["GOOGLE_SEARCH_API_KEY"]
            search_engine_id = st.secrets["SEARCH_ENGINE_ID"]
        except (KeyError, FileNotFoundError):
            pass

    if not all([gemini_api_key, search_api_key, search_engine_id]):
        st.error("One or more API keys/IDs are missing. Please check your .env file or Streamlit secrets.", icon="🚨")
        st.stop()
        
    return gemini_api_key, search_api_key, search_engine_id

GEMINI_API_KEY, SEARCH_API_KEY, SEARCH_ENGINE_ID = load_credentials()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
# This variable holds the model name for use in the disclaimer
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- Session State Initialization ---
if 'instructor_data' not in st.session_state:
    st.session_state.instructor_data = None
if 'generation_results' not in st.session_state:
    st.session_state.generation_results = {}
if 'final_case_study' not in st.session_state:
    st.session_state.final_case_study = ""

# --- Helper Functions ---
def perform_google_search(queries, num_per_query=3):
    """Performs multiple Google searches and returns a formatted string of results."""
    all_results_text = ""
    seen_links = set()
    try:
        service = build("customsearch", "v1", developerKey=SEARCH_API_KEY)
        for query in queries:
            st.info(f"🤖 Searching for: \"{query}\"")
            res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, num=num_per_query).execute()
            for item in res.get('items', []):
                link = item.get('link')
                if link and link not in seen_links:
                    all_results_text += f"- Title: {item.get('title', '')}\n  URL: {link}\n  Snippet: {item.get('snippet', '')}\n"
                    seen_links.add(link)
        return all_results_text if all_results_text else "No new search results found."
    except Exception as e:
        st.error(f"An error occurred during Google Search: {e}")
        return "Search failed."

def call_gemini(prompt, chat_history=None):
    """A standard call to the Gemini API for text generation."""
    try:
        if chat_history is not None:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
            return response.text, chat.history
        else:
            response = model.generate_content(prompt)
            return response.text, [{'role': 'user', 'parts': [prompt]}, {'role': 'model', 'parts': [response.text]}]
    except Exception as e:
        st.error(f"An error occurred with the Gemini API call: {e}")
        return None, chat_history

# --- UI and Main Logic ---
st.title("✍️ Personalized Case Study Writer")
st.caption("An intelligent agent that researches and writes personalized case studies.")

instructor_tab, student_tab = st.tabs(["👨‍🏫 Step 1: Instructor Setup", "👩‍🎓 Step 2: Student Input & Generation"])

with instructor_tab:
    st.header("Instructor Setup")
    st.markdown("Provide the core details for the case study.")
    with st.form(key="instructor_form"):
        # Simplified form based on user feedback
        discipline = st.text_input("Discipline", "Business Strategy")
        target_audience = st.text_input("Target Audience", "MBA Students")
        case_topic = st.text_area("Topic of the case study", "How to break into a new market")
        learning_objectives = st.text_area("Learning Objectives", "1. Apply Porter's Five Forces to the new market.\n2. Evaluate the pros and cons of different market entry modes.\n3. Conduct a SWOT analysis of a key player.")
        student_questions = st.text_area("Questions for students", "1. What are the primary barriers to entry in this market?\n2. Which entry strategy would you recommend and why?\n3. What are the biggest risks associated with your recommended strategy?")
        submitted_instructor_form = st.form_submit_button("Save Instructor Setup", type="primary")
        if submitted_instructor_form:
            st.session_state.instructor_data = {
                "discipline": discipline, "target_audience": target_audience, "case_topic": case_topic,
                "learning_objectives": learning_objectives, "student_questions": student_questions,
            }
            st.success("Instructor information saved! Please proceed to the next tab.")

with student_tab:
    st.header("Student Input & Generation")
    st.markdown("Provide the specific company and role for this version of the case study.")
    if not st.session_state.instructor_data:
        st.warning("Please complete and save the 'Instructor Setup' in the first tab before proceeding.")
    else:
        with st.form(key="student_form"):
            company_name = st.text_input("Company Name", "Apple")
            job_title = st.text_input("Job Title", "Head of Global Strategy")
            submitted_student_form = st.form_submit_button("Generate Full Case Study", type="primary")

            if submitted_student_form:
                st.session_state.generation_results = {}
                st.session_state.final_case_study = ""
                instructor = st.session_state.instructor_data
                chat_history = []

                # --- STEP 0 - INTELLIGENT MULTI-SEARCH ---
                with st.spinner("Step 0/11: Performing intelligent web search for sources..."):
                    search_queries = [
                        f"{company_name} {instructor['case_topic']}",
                        f"financial reports of {company_name} in the context of {instructor['case_topic']}",
                        f"performance analysis of {company_name} in the context of {instructor['case_topic']}",
                        f"strategic challenges and opportunities of {company_name} in the context of {instructor['case_topic']}"
                    ]
                    initial_sources = perform_google_search(search_queries)
                    st.session_state.generation_results['0_initial_search'] = initial_sources

                # --- STEP 1: RESEARCH REPORT ---
                with st.spinner("Step 1/11: Synthesizing research report..."):
                    prompt_step1 = f"""In the role of an expert corporate analyst with over 10 years of experience in creating meaningful and effective reports for leadership boards of Fortune 500 companies, please create an industry report for the leadership board of {company_name}. The topic of the report is: {instructor['case_topic']}.
                    Use the following live web search results as the additional sources for your report:
                    ---
                    {initial_sources}
                    ---
                    The leadership board wants to learn the following: {instructor['learning_objectives']}. The leadership board wants to be able to answer the following questions: {instructor['student_questions']}."""
                    report, _ = call_gemini(prompt_step1)
                    st.session_state.generation_results['1_report'] = report

                # --- STEP 2: PERSONA ---
                with st.spinner("Step 2/11: Defining writer persona..."):
                    persona_prompt = f"""Your role: You are a deep expert in {instructor['discipline']} with over 10 years of experience as {job_title} at {company_name}.

Your personality: You are extroverted, joyful and kind. You are a deeply analytical thinking, above average creative and you always think outside of the box to find unconventional, yet effective solutions to problems..

Your expertise: You have over 10 years of experience as {job_title} at {company_name}. You have taught case studies at ivy league business schools for over 5 years. You also have over 5 years of experience in writing highly engaging and meaningful case studies for {instructor['target_audience']} in top tier business schools.

Your writing style: When writing case studies for {instructor['target_audience']} at top tier business schools, you adhere to the best practices of such quality case studies, but you add your own talent as an experienced storyteller to it. Your defining quality as a case study writer, which makes you stand out from others, is that you are able to write in such a way that the cases become particularly realistic and captivating for the students. You are also building in many engaging elements, which are not typical for case studies, but which make them much more engaging for students and therefore increase the completion rate significantly. Finally, you write based on high quality sources, which you rigorously cite throughout the document."""
                    st.session_state.generation_results['2_persona_prompt'] = persona_prompt
                    chat_history.append({'role': 'user', 'parts': [persona_prompt]})
                    chat_history.append({'role': 'model', 'parts': ["Understood. I will now act as this persona for all subsequent tasks."]})

                # --- STEP 3: OUTLINE ---
                with st.spinner("Step 3/11: Writing the case study outline..."):
                    case_structure = """- Title Page\n- Introduction\n- Case Study Narrative\n- Analysis of Strategic Decisions\n- Critical Discussion\n- Reflection and Application\n- Supplementary Materials\n- Conclusion"""
                    prompt_step3 = f"""In this role, you are writing a case study focused on the job of {job_title} at {company_name}. In this role, please create a brief overview of the case study on {instructor['case_topic']} which achieves the following learning objectives: {instructor['learning_objectives']}. The overview must follow this structure:\n{case_structure}"""
                    outline, chat_history = call_gemini(prompt_step3, chat_history=chat_history)
                    st.session_state.generation_results['3_outline'] = outline

                # --- STEPS 4-10: AGENTIC WRITING LOOP ---
                sections_to_write = [
                    {"step": 4, "title": "Introduction", "description": "Background Information: Provide a brief introduction to the company or brand featured in the case study.\nIndustry Context: Describe the industry landscape and the market conditions at the time of the case study.\nPurpose of the Case Study: Clarify the educational objectives and what students should aim to learn from this case study."},
                    {"step": 5, "title": "Case Study Narrative", "description": "Company Overview: Detail the company’s history, mission, and market position prior to the implementation of the strategy being studied.\nStrategic Assessment: Outline specific challenges or opportunities for the company."},
                    {"step": 6, "title": "Analysis of Strategic Decisions", "description": "Strategic Decision-Making Process: Delve into how decisions were made, including the data and market research used.\nImplementation Challenges: Describe any obstacles encountered during the implementation of the strategy and how they were overcome.\nOutcomes and Performance: Short-Term Results (analyze immediate effects) and Long-Term Impact (assess long-term effects)."},
                    {"step": 7, "title": "Critical Discussion", "description": "Discussion Points: Provide key points for students to consider, fostering critical thinking about strategic choices made by the company.\nAlternative Strategies: Propose alternative strategies that could have been considered, encouraging students to think about different approaches.\nLessons Learned: Highlight key takeaways and lessons learned from the case study."},
                    {"step": 8, "title": "Reflection and Application", "description": "Reflective Questions: Pose thought-provoking questions to help students apply the insights from the case study to their own or other business contexts.\nHow could these strategies be applied in different industries?\nWhat would you have done differently if you were in charge?"},
                    {"step": 9, "title": "Supplementary Materials", "description": "Data Sources: Include data sources, as found online.\nFurther Readings: Suggest additional resources for students who wish to explore related topics in more depth."},
                    {"step": 10, "title": "Conclusion", "description": "Recap: Summarize the main insights and the educational value of the case study.\nNext Steps: Encourage further exploration of the concepts learned and how they tie into the upcoming course material."},
                ]
                
                written_sections = []
                for section in sections_to_write:
                    with st.spinner(f"Step {section['step']}/11: Writing the {section['title']}..."):
                        preceding_parts = "\n\n".join(written_sections) if written_sections else "None"
                        
                        # --- AGENT STEP A: THINK & FORMULATE QUERIES ---
                        st.info(f"🤖 Thinking: What information do I need for the '{section['title']}' section?")
                        think_prompt = f"""I am about to write the '{section['title']}' section of a case study.
                        My instructions for this section are: {section['description']}.
                        The context from previous sections is: {preceding_parts}.
                        
                        Do I need more specific, real-time information to write this section comprehensively? 
                        If yes, formulate up to 2 specific Google search queries that would give me the data, examples, or details I need.
                        Respond ONLY with a JSON object with two keys: "search_needed" (true/false) and "queries" (a list of strings).
                        If no search is needed, the "queries" list should be empty."""
                        
                        query_response_text, _ = call_gemini(think_prompt, chat_history)
                        
                        try:
                            clean_json_text = query_response_text.strip().replace("```json", "").replace("```", "")
                            query_decision = json.loads(clean_json_text)
                        except json.JSONDecodeError:
                            query_decision = {"search_needed": False, "queries": []}

                        # --- AGENT STEP B: ACT (SEARCH) ---
                        new_sources = ""
                        if query_decision.get("search_needed") and query_decision.get("queries"):
                            new_sources = perform_google_search(query_decision["queries"])
                            st.session_state.generation_results[f"{section['step']}_{section['title']}_search"] = new_sources
                        
                        # --- AGENT STEP C: SYNTHESIZE & WRITE ---
                        write_prompt = f"""In your defined role, please write out all details of the section '{section['title']}'.
                        The specific requirements for this section are: {section['description']}
                        I have performed a targeted search for you. Use these new sources to inform your writing:
                        ---
                        {new_sources if new_sources else "No new search was performed for this section."}
                        ---
                        Please make sure to take into consideration the content of the preceding parts of the case study: {preceding_parts}.
                        IMPORTANT: Write ONLY the content for the section itself. Do not add meta-commentary."""
                        
                        section_content, chat_history = call_gemini(write_prompt, chat_history=chat_history)
                        st.session_state.generation_results[f"{section['step']}_{section['title']}"] = section_content
                        written_sections.append(f"## {section['title']}\n{section_content}")
                
                st.success("Full case study generation complete!")
                st.balloons()
                
                # --- STEP 11: Collate the final case study with Title and Disclaimer ---
                # Create the title and disclaimer
                title_and_disclaimer = f"# Case Study: {instructor['case_topic']} for {company_name}\n\n"
                title_and_disclaimer += f"**_Disclaimer: This case study was written by {MODEL_NAME} and may contain hallucinations._**\n\n---\n\n"

                # Join the main body of the case study
                case_body = "\n\n---\n\n".join(written_sections)

                # Combine everything into the final text
                st.session_state.final_case_study = title_and_disclaimer + case_body

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
        "0_initial_search", "1_report", "2_persona_prompt", "3_outline", "4_Introduction", 
        "5_Case Study Narrative", "6_Analysis of Strategic Decisions", 
        "7_Critical Discussion", "8_Reflection and Application", 
        "9_Supplementary Materials", "10_Conclusion"
    ]
    for key in display_order:
        if key in st.session_state.generation_results:
            if "_search" in key:
                 with st.expander(f"Agent Search Results for {key.split('_')[1]}", expanded=False):
                    st.markdown(st.session_state.generation_results[key])
            else:
                title = key.split('_', 1)[1].replace('_', ' ').title()
                with st.expander(f"Step {key.split('_')[0]}: {title}", expanded=False):
                    st.markdown(st.session_state.generation_results[key])
