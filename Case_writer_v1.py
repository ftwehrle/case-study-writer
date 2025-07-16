import streamlit as st
import google.generativeai as genai
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Personalized Case Study Writer",
    page_icon="✍️",
    layout="wide" # Changed to wide layout to better display results
)

# --- Gemini API Configuration ---
# This function securely loads your API key from Streamlit's secrets management.
def load_api_key():
    """Loads the Gemini API key from Streamlit's secrets."""
    try:
        # The key must be set in the Streamlit Community Cloud dashboard's secrets.
        # It should be in the format: GEMINI_API_KEY = "YOUR_API_KEY_HERE"
        api_key = st.secrets["GEMINI_API_KEY"]
        return api_key
    except (KeyError, FileNotFoundError):
        st.error("GEMINI_API_KEY not found. Please add it to your Streamlit secrets.", icon="🚨")
        st.stop()

# Configure the generative AI model
api_key = load_api_key()
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- Session State Initialization ---
# This is crucial for passing data between user interactions.
if 'instructor_data' not in st.session_state:
    st.session_state.instructor_data = None
if 'generation_results' not in st.session_state:
    st.session_state.generation_results = {}

# --- Helper function to call Gemini ---
def call_gemini(prompt):
    """Sends a prompt to the Gemini API and returns the response."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred with the API call: {e}")
        return None

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
        learning_objectives = st.text_area("Learning Objectives", "1. Apply Porter's Five Forces...\n2. Evaluate market entry modes...\n3. Conduct a SWOT analysis...")
        student_questions = st.text_area("Questions for students", "1. What are the primary barriers to entry...?\n2. Which entry strategy would you recommend...?\n3. What are the biggest risks...?")

        submitted_instructor_form = st.form_submit_button("Save Instructor Setup", type="primary")

        if submitted_instructor_form:
            # Store all instructor inputs in the session state
            st.session_state.instructor_data = {
                "institution": institution,
                "course_title": course_title,
                "discipline": discipline,
                "target_audience": target_audience,
                "case_topic": case_topic,
                "learning_objectives": learning_objectives,
                "student_questions": student_questions,
            }
            st.success("Instructor information saved! Please proceed to the next tab to generate the case study.")

# --- Student Interface ---
with student_tab:
    st.header("Student Input & Generation")
    st.markdown("Next, provide the specific company and role for this version of the case study.")

    # Check if instructor data exists before showing the form
    if not st.session_state.instructor_data:
        st.warning("Please complete and save the 'Instructor Setup' in the first tab before proceeding.")
    else:
        with st.form(key="student_form"):
            company_name = st.text_input("Company Name", "Tesla, Inc.")
            job_title = st.text_input("Job Title", "Head of Global Strategy")

            submitted_student_form = st.form_submit_button("Generate Case Study", type="primary")

            if submitted_student_form:
                # --- This is where the AI Generation Process Begins ---
                with st.spinner("Step 1/11: Conducting deep research... This may take a moment."):
                    # Step 1: Deep research on the topic
                    prompt_step1 = f"""In the role of an expert corporate analyst with over 10 years of experience in creating meaningful and effective reports for leadership boards of Fortune 500 companies, please create an industry report for the leadership board of {company_name}.
                    The topic of the report is: {st.session_state.instructor_data['case_topic']}.
                    The leadership board wants to learn the following: {st.session_state.instructor_data['learning_objectives']}.
                    The leadership board wants to be able to answer the following questions: {st.session_state.instructor_data['student_questions']}."""
                    
                    report = call_gemini(prompt_step1)
                    st.session_state.generation_results['report'] = report

                with st.spinner("Step 2/11: Creating the case study writer persona..."):
                    # Step 2: Creating the case study writer persona
                    prompt_step2 = f"""Your role: You are a deep expert in {st.session_state.instructor_data['discipline']} with over 10 years of experience as {job_title} at {company_name}.
                    Your personality: You are extroverted, joyful and kind. You are a deeply analytical thinking, above average creative and you always think outside of the box to find unconventional, yet effective solutions to problems..
                    Your expertise: You have over 10 years of experience as {job_title} at {company_name}. You have taught case studies at ivy league business schools for over 5 years. You also have over 5 years of experience in writing highly engaging and meaningful case studies for MBA programs in ivy league business schools.
                    Your writing style: When writing case studies for MBA students at ivy league business schools, you adhere to the best practices of such quality case studies, but you add your own talent as an experienced storyteller to it. Your defining quality as a case study writer, which makes you stand out from others, is that you are able to write in such a way that the cases become particularly realistic and captivating for the students. You are also building in many engaging elements, which are not typical for case studies, but which make them much more engaging for students and therefore increase the completion rate significantly. Finally, you write based on high quality sources, which you rigorously cite throughout the document."""
                    
                    persona = call_gemini(prompt_step2)
                    st.session_state.generation_results['persona'] = persona
                
                st.success("Initial generation steps complete!")

# --- Display Generation Results ---
if st.session_state.generation_results:
    st.header("Generation Progress")
    
    if 'report' in st.session_state.generation_results and st.session_state.generation_results['report']:
        with st.expander("Step 1: Deep Research Report (Result)", expanded=True):
            st.markdown(st.session_state.generation_results['report'])
            
    if 'persona' in st.session_state.generation_results and st.session_state.generation_results['persona']:
        with st.expander("Step 2: Writer Persona (Result)", expanded=True):
            st.markdown(st.session_state.generation_results['persona'])
