# **AI-Powered Case Study Writer**

This is a prototype of an advanced web application that uses a multi-step, agentic AI process to generate high-quality, personalized business case studies. The application is built with Python and Streamlit and is powered by the Google Gemini API and Google Search.

The key innovation of this tool is its ability to perform its own targeted web searches to gather real-time, factual information, which it then uses to ground the case study, significantly reducing the risk of AI "hallucinations" and ensuring the final output is credible and well-sourced.

The script and documentation are written with Gemini 2.5 Pro.

## **Key Features**

* **Instructor & Student Interfaces:** A simple two-tab interface for instructors to define the case study parameters and for students to specify the company and role.  
* **Intelligent Multi-Source Research:** The application initiates a multi-query web search to gather a diverse set of high-quality sources before writing begins.  
* **Agentic Search-and-Write Loop:** For each section of the case study, the AI agent first determines what information it needs, formulates its own targeted search queries, performs a live web search, and then synthesizes the results into its writing.  
* **Custom AI Persona:** The AI adopts a specific, expert persona to ensure a consistent tone and high-quality writing style throughout the document.  
* **Downloadable Output:** The final, complete case study can be downloaded as a Markdown (.md) file, preserving formatting for easy use in other applications.

## **How to Deploy Your Own Version**

This guide will walk you through the steps to deploy your own live, web-accessible instance of the AI Case Study Writer application using GitHub and Streamlit Community Cloud.

### **Prerequisites**

* A **GitHub** account.  
* A **Google Cloud** account (for API keys).
* * A **Streamlit** account.

### **Step 1: Get the Project Code on GitHub**

First, you need your own copy of the project's code in a GitHub repository.

1. **Fork the Repository:** To begin, you must "Fork" this project repository. Click the **"Fork"** button in the top-right corner of this page. This creates your own independent copy of the project under your GitHub account.  
2. **Verify Files:** Ensure your forked repository contains the following two files:  
   * Case\_writer\_v2\_beta.py (or the latest version of the script)  
   * requirements.txt

The requirements.txt file must contain the following lines:streamlit  
google-generativeai  
python-dotenv  
google-api-python-client

### **Step 2: Get Your API Keys and ID**

The application needs three secret "keys" to connect to Google's services.

**A. Get the Gemini API Key:**

1. Go to the [**Google AI Studio**](https://aistudio.google.com) and sign in.  
2. Click **"Get API key"** \> **"Create API key in new project"**.  
3. **Copy** the generated key.

**B. Get the Google Search API Key:**

1. Go to the [**Google Cloud Console**](https://console.cloud.google.com) and sign in.  
2. Select the same project you used for the Gemini key.  
3. In the top search bar, search for and **enable** the **"Custom Search API"**.  
4. Go to **Credentials** \> **\+ CREATE CREDENTIALS** \> **API key**.  
5. **Copy** the generated key.

**C. Get the Search Engine ID:**

1. Go to the [**Programmable Search Engine**](https://programmablesearchengine.google.com) page.  
2. Click **"Add"** to create a new search engine.  
3. Give it a name and select **"Search the entire web"**. Click **"Create"**.  
4. On the next page, click **"Customize"** and copy the **"Search engine ID"**.

### **Step 3: Deploy on Streamlit Cloud**

Now, let's connect your GitHub repository to Streamlit to make the app live.

1. Go to [**Streamlit Community Cloud**](https://share.streamlit.io) and sign up or log in with your GitHub account.  
2. From your dashboard, click **"New app"**.  
3. **Configure Deployment:**  
   * **Repository:** Choose the repository you just forked.  
   * **Branch:** Leave this as main.  
   * **Main file path:** Ensure this points to Case\_writer\_v2\_beta.py (or the latest version).  
4. Click **"Deploy\!"**. Your app will now be built and deployed, which may take a few minutes.

### **Step 4: Add Secrets to Your Live App**

The final step is to provide your live app with the secret keys.

1. From your Streamlit dashboard, find your newly deployed app. Click the three dots (...) next to its name and select **"Settings"**.  
2. Go to the **"Secrets"** tab.  
3. In the text box, paste all three of your keys in the following format, replacing the placeholders with your actual keys:  
   GEMINI\_API\_KEY="PASTE\_YOUR\_GEMINI\_KEY\_HERE"  
   GOOGLE\_SEARCH\_API\_KEY="PASTE\_YOUR\_SEARCH\_KEY\_HERE"  
   SEARCH\_ENGINE\_ID="PASTE\_YOUR\_ENGINE\_ID\_HERE"

4. Click **"Save"**. Streamlit will prompt you to reboot the app. Click **"Reboot"**.

Your application is now live on its own public URL, fully configured and ready to use.

## **License**

This project is licensed under the MIT License \- see the LICENSE file for details.
