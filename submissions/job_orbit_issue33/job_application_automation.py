import os
import json
import asyncio
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_ollama import ChatOllama
from langchain_aws import ChatBedrockConverse
import boto3
import PyPDF2
import re
from browser_use import Agent, BrowserSession
# Load environment variables
load_dotenv()

access_key = os.getenv('ACCESS_KEY')
secret_key = os.getenv('SECRET_KEY')
linkedin_name = os.getenv('LINKEDIN_NAME')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')


def get_model(model: str = 'deepseek-r1:7b', provider: str = 'local'):
    if provider == 'local':
        llm = ChatOllama(model=model, temperature=0.8)
        return llm
    elif provider == 'llama':
        llm = ChatOllama(model='llama3.1', temperature=0.8)
        return llm
    elif provider == 'aws':
        access_key = os.getenv('ACCESS_KEY')
        secret_key = os.getenv('SECRET_KEY')
        bedrock_client = boto3.client('bedrock-runtime',
                                      region_name='us-east-1',
                                      aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key)
        llm = ChatBedrockConverse(client=bedrock_client,
                                  model=model,
                                  temperature=0.8)
        return llm


# Initialize AWS Bedrock client
bedrock_client = boto3.client('bedrock-runtime',
                              region_name='us-east-1',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)

# Get LLM model
llm = get_model(model='anthropic.claude-3-sonnet-20240229-v1:0',
                provider='aws')


def load_job_data():
    """Load job data from memory.json"""
    with open('./data/memory.json', 'r') as f:
        data = json.load(f)
    return data


def extract_resume_info(resume_path):
    """Extract information from a PDF resume"""
    resume_info = {}

    try:
        with open(resume_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            # Extract basic information using regex patterns
            # Name (assuming it's at the top of the resume)
            name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', text,
                                   re.MULTILINE)
            if name_match:
                resume_info['name'] = name_match.group(1)

            # Email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
            if email_match:
                resume_info['email'] = email_match.group(0)

            # Phone
            phone_match = re.search(
                r'(\+\d{1,3}[-\.\s]??)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}',
                text)
            if phone_match:
                resume_info['phone'] = phone_match.group(0)

            # Education
            education_section = re.search(
                r'EDUCATION(.*?)(?:EXPERIENCE|SKILLS|PROJECTS)', text,
                re.DOTALL | re.IGNORECASE)
            if education_section:
                resume_info['education'] = education_section.group(1).strip()

            # Skills
            skills_section = re.search(
                r'SKILLS(.*?)(?:EXPERIENCE|EDUCATION|PROJECTS|$)', text,
                re.DOTALL | re.IGNORECASE)
            if skills_section:
                resume_info['skills'] = skills_section.group(1).strip()

            # Experience
            experience_section = re.search(
                r'EXPERIENCE(.*?)(?:EDUCATION|SKILLS|PROJECTS|$)', text,
                re.DOTALL | re.IGNORECASE)
            if experience_section:
                resume_info['experience'] = experience_section.group(1).strip()

            resume_info['full_text'] = text

    except Exception as e:
        print(f"Error extracting resume info: {e}")

    return resume_info


async def apply_for_job(job, resume_path):
    """Apply for a job using browser automation"""

    # Ensure resume path is absolute
    resume_abs_path = os.path.abspath(resume_path)

    # Extract resume information
    resume_info = extract_resume_info(resume_path)

    # Create application URL - use company_apply_url if available, otherwise use LinkedIn URL
    application_url = job.get('company_apply_url', job.get('url'))

    # Define initial actions to open the job application page
    if application_url is None:
        application_url = job.get("url")
    initial_actions = [{'open_tab': {'url': application_url}}]

    # Create dynamic tasks based on the job and resume information
    tasks = f"""
    1. You are on the job application page for {job['title']} at {job['company']}.
    2. Look for application form fields and fill them out using the following information:
       - Full Name: {resume_info.get('name', 'Not found')}
       - Email: {resume_info.get('email', 'Not found')}
       - Phone: {resume_info.get('phone', 'Not found')}
    3. If there's a resume upload option:
       - IMPORTANT: Look for a "Browse" or "Upload" button and click it
       - When the file dialog opens, the resume file is located at: {resume_abs_path}
       - Enter this exact path in the file dialog: {resume_abs_path}
       - If you need to select file type, choose PDF
    4. If there are questions about skills or experience, use this information:
       Skills: {resume_info.get('skills', 'Not found')}
       Experience: {resume_info.get('experience', 'Not found')}
    5. If there are questions about education, use this information:
       Education: {resume_info.get('education', 'Not found')}
    6. Look for any checkboxes related to terms and conditions or privacy policy and check them if required.
    7. Look for a submit/apply button and click it to complete the application.
    8. If there are multiple steps in the application process, navigate through them by clicking "Next" or similar buttons.
    9. If you encounter a login page, stop and report that login is required.
    10. Take a screenshot of the final confirmation page or any error messages.

    Below is my credentials for loging in:
    LinkedIn Name: {linkedin_name}
    LinkedIn Password: {linkedin_password}
    """

    # Create a unique log file name for this job application
    log_file = f"logs/job_application_{job['job_id']}_{job['company']}"

    print(tasks)
    print("-" * 80)

    # If no executable_path provided, uses Playwright/Patchright's built-in Chromium
    browser_session = BrowserSession(
        # Path to a specific Chromium-based executable (optional)
        executable_path=
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
        # For Windows: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        # For Linux: '/usr/bin/google-chrome'

        # Use a specific data directory on disk (optional, set to None for incognito)
        user_data_dir=
        '~/.config/browseruse/profiles/default',  # this is the default
        # ... any other BrowserProfile or playwright launch_persistnet_context config...
        # headless=False,
    )

    # Initialize agent and run the automation
    agent = Agent(
        task=tasks,
        initial_actions=initial_actions,
        llm=llm,
        save_conversation_path="logs/conversation",
        browser_session=browser_session,
    )

    try:
        result = await agent.run()
        print(
            f"Application result for {job['title']} at {job['company']}: {result}"
        )
        return result
    except Exception as e:
        print(f"Error applying for job {job['job_id']}: {e}")
        return {"status": "error", "message": str(e)}


async def initiate_job_application():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Load job data
    data = load_job_data()
    jobs = data.get('jobs_found', [])
    resume_customizations = data.get('resume_customizations', [])

    # Create a mapping of job_id to resume file path
    resume_map = {}
    for customization in resume_customizations:
        if 'job_id' in customization and 'file_path' in customization:
            resume_map[customization['job_id']] = customization['file_path']
        # Also check for filename if file_path is not available
        elif 'job_id' in customization and 'filename' in customization:
            resume_map[customization[
                'job_id']] = f"./data/customized_resumes/{customization['filename']}"

    print(f"Found {len(jobs)} jobs and {len(resume_map)} customized resumes")

    # Apply for each job
    for job in jobs:
        job_id = job.get('job_id')

        # Skip jobs without an application URL
        if not job.get('company_apply_url') and not job.get('url'):
            print(f"Skipping job {job_id}: No application URL found")
            continue

        # Find the corresponding resume
        resume_path = resume_map.get(job_id)
        if not resume_path:
            print(f"Skipping job {job_id}: No customized resume found")
            continue

        print(
            f"Applying for {job['title']} at {job['company']} using resume: {resume_path}"
        )
        await apply_for_job(job, resume_path)

        # Add a delay between job applications to avoid overwhelming the browser
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(initiate_job_application())
