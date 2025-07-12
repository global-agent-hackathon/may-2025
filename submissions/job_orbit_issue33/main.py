# Enhanced main.py with batch resume customization

import os
import json
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import time

from dotenv import load_dotenv
from agno.agent import Agent, RunResponse
from agno.models.ollama import Ollama
from agno.models.aws import AwsBedrock
from agno.utils.pprint import pprint_run_response

from linkedin_api import Linkedin
from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document
from resume_customizer import ResumeCustomizer

import os

from agno.agent import Agent
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Set the endpoint and headers for LangSmith
endpoint = "https://api.smith.langchain.com"
headers = {
    "x-api-key": os.getenv("LANGSMITH_API_KEY"),
    "Langsmith-Project": os.getenv("LANGSMITH_PROJECT"),
}

# Configure the tracer provider
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint, headers=headers)))
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# Start instrumenting agno
AgnoInstrumentor().instrument()

# Load environment variables
load_dotenv()

# Initialize ResumeCustomizer
resume_customizer = ResumeCustomizer()

import boto3
from botocore.config import Config

config = Config(connect_timeout=5,
                read_timeout=5 * 60,
                retries={'max_attempts': 2})
bedrock_client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1',
    config=config)


def init_linkedin_api():
    """Initialize LinkedIn API client"""
    user_name = os.getenv('LINKEDIN_NAME')
    user_pass = os.getenv('LINKEDIN_PASSWORD')

    if not user_name or not user_pass:
        print("LinkedIn credentials not found in .env file")
        return None

    try:
        api = Linkedin(user_name, user_pass)
        return api
    except Exception as e:
        print(f"Error initializing LinkedIn API: {e}")
        return None


# Initialize LinkedIn API
linkedin_api = init_linkedin_api()

# us.anthropic.claude-3-5-sonnet-20241022-v2:0
# anthropic.claude-3-5-sonnet-20240620-v1:0
# us.anthropic.claude-3-7-sonnet-20250219-v1:0
# anthropic.claude-3-sonnet-20240229-v1:0


def get_model(provider: str):
    """Get LLM model based on provider"""
    if provider == 'ollama':
        return Ollama(id='llama3.1')
    elif provider == 'aws':
        return AwsBedrock(id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                          aws_region='us-east-1',
                          client=bedrock_client)
    else:
        raise ValueError("Unsupported provider")


def read_job_preferences() -> str:
    """Read job preferences from CSV file"""
    time.sleep(60)
    try:
        loader = CSVLoader(file_path='./data/job_pref.csv',
                           csv_args={
                               'delimiter':
                               ',',
                               'fieldnames': [
                                   'Company', 'Role', 'Location', 'Priority',
                                   'Referral', 'Job_Type', 'Keywords',
                                   'Exclude_Keywords', 'Experience',
                                   'Placeholder'
                               ]
                           })
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"Error reading job preferences: {e}"


def search_jobs(keywords: Optional[str] = None,
                companies: Optional[List[str]] = None,
                location_name: Optional[str] = None,
                listed_at: int = 86400,
                limit: int = 10) -> str:
    """
    Search for jobs on LinkedIn based on criteria
    Args:
        keywords (Optional[str]): Keywords to search for in job titles or descriptions.
        companies (Optional[List[str]]): List of company names to filter jobs by.
        location_name (Optional[str]): Name of the location to filter jobs by.
        listed_at (int, optional): Time in seconds since epoch when the job was listed. Defaults to 86400.
        limit (int, optional):Maximum number of jobs to fetch. Defaults to 10.

    Returns:
        list: List of job postings that match the criteria.
    """
    time.sleep(60)  # Simulate delay for testing
    if not linkedin_api:
        # Return mock data for testing
        return "Error: LinkedIn API not initialized. Please check your credentials."

    try:
        print("Using LinkedIn API to search for jobs...")
        print(
            f"Keywords: {keywords}, Companies: {companies}, Location: {location_name}"
        )

        jobs = linkedin_api.search_jobs(
            keywords=keywords,
            companies=companies,
            location_name=location_name,
            listed_at=86400 * 7,
            limit=15)  #need to be replaced by limit

        job_results = []
        for job in jobs:
            job_id = job["entityUrn"].split(":")[-1]
            print(f"Processing job ID: {job_id}")

            try:
                # Get detailed job information
                job_data = linkedin_api.get_job(job_id=job_id)
                job_skills = linkedin_api.get_job_skills(job_id=job_id)

                # Extract job details
                job_title = job_data.get("title", "Unknown Title")
                company_details = job_data.get("companyDetails", {}).get(
                    "com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany",
                    {})
                company_name = company_details.get("companyResolutionResult",
                                                   {}).get(
                                                       "name",
                                                       "Unknown Company")
                job_description = job_data.get("description", {}).get(
                    "text", "No description available")
                job_location = job_data.get("formattedLocation",
                                            "Unknown Location")

                # Try to get easyApplyUrl from multiple potential paths
                easy_apply_url = job_data.get("applyMethod",
                                              {}).get("easyApplyUrl")
                if not easy_apply_url:
                    easy_apply_url = job_data.get("applyMethod", {}).get(
                        "com.linkedin.voyager.jobs.ComplexOnsiteApply",
                        {}).get("easyApplyUrl")

                # easy_apply is True if an easy apply URL is found
                easy_apply = easy_apply_url is not None

                company_apply_url = None

                print(easy_apply_url)
                print("-" * 80)

                if not easy_apply:

                    company_apply_url = job_data.get("applyMethod", {}).get(
                        "com.linkedin.voyager.jobs.OffsiteApply",
                        {}).get("companyApplyUrl")

                job_result = {
                    "job_id": job_id,
                    "title": job_title,
                    "company": company_name,
                    "location": job_location,
                    "description": job_description,
                    "easy_apply": easy_apply,
                    "url": f"https://www.linkedin.com/jobs/view/{job_id}",
                    "posted_date": datetime.now().isoformat(),
                    "company_apply_url": company_apply_url
                }

                if easy_apply:
                    job_results.append(job_result)

                # Add delay to avoid rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
                continue

        # Save job results to memory for tracking

        save_job_search_results(job_results, keywords, companies,
                                location_name)
        print("job saved")

        return json.dumps(job_results, indent=2)

    except Exception as e:
        return f"Error searching jobs: {e}"


def save_job_search_results(jobs: List[Dict], keywords: str,
                            companies: List[str], location: str):
    """Save job search results to memory for tracking"""
    try:
        print("inside save job results")
        memory_path = "./data/memory.json"
        memory_data = {}

        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory_data = json.load(f)

        # Initialize if not exists
        if 'job_searches' not in memory_data:
            memory_data['job_searches'] = []
        if 'jobs_found' not in memory_data:
            memory_data['jobs_found'] = []

        # Add search record
        search_record = {
            'timestamp': datetime.now().isoformat(),
            'keywords': keywords,
            'companies': companies,
            'location': location,
            'jobs_count': len(jobs)
        }
        memory_data['job_searches'].append(search_record)

        # Add jobs to jobs_found (avoid duplicates)
        existing_job_ids = {
            job.get('job_id')
            for job in memory_data['jobs_found']
        }
        for job in jobs:
            if job.get('job_id') not in existing_job_ids:
                memory_data['jobs_found'].append(job)

        # Save updated memory
        with open(memory_path, 'w') as f:
            json.dump(memory_data, f, indent=2)

    except Exception as e:
        print(f"Error saving job search results: {e}")


def customize_resume_for_job(job_id: str,
                             job_description: str,
                             job_title: str = "",
                             company_name: str = "") -> str:
    """
    Customize resume for a specific job with enhanced naming and tracking.
    
    Args:
        job_id: Unique job identifier
        job_description: Full job description
        job_title: Job title for better file naming
        company_name: Company name for better file naming
    
    Returns:
        str: Success/error message with file path
    """
    time.sleep(60)
    try:
        base_resume_path = "./data/base_resume.pdf"

        # Check if base resume exists
        if not os.path.exists(base_resume_path):
            return "Error: Base resume not found. Please upload your base resume first."

        # Create safe filename from job details
        safe_company = "".join(c for c in company_name
                               if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = "".join(c for c in job_title
                             if c.isalnum() or c in (' ', '-', '_')).strip()

        # Create descriptive filename
        if safe_company and safe_title:
            filename = f"resume_{job_id}_{safe_company}_{safe_title}.pdf"
        else:
            filename = f"resume_{job_id}.pdf"

        # Ensure filename isn't too long
        if len(filename) > 100:
            filename = f"resume_{job_id}_{safe_company[:20]}.pdf"

        output_path = f"./data/customized_resumes/{filename}"

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"Customizing resume for Job ID: {job_id}")
        print(f"Company: {company_name}")
        print(f"Title: {job_title}")
        print(f"Output: {output_path}")

        # Customize resume using ResumeCustomizer
        success = resume_customizer.customize_resume(
            base_resume_path=base_resume_path,
            job_description=job_description,
            output_path=output_path)

        if success:
            # Track the customization
            track_resume_customization(job_id, job_title, company_name,
                                       output_path)
            return f"✅ Resume customized successfully for {company_name} - {job_title}\nSaved as: {filename}"
        else:
            return f"❌ Failed to customize resume for Job ID: {job_id}"

    except Exception as e:
        return f"❌ Error customizing resume for Job ID {job_id}: {str(e)}"


def track_resume_customization(job_id: str, job_title: str, company_name: str,
                               file_path: str):
    """Track resume customization in memory system"""
    try:
        memory_path = "./data/memory.json"
        memory_data = {}

        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory_data = json.load(f)

        if 'resume_customizations' not in memory_data:
            memory_data['resume_customizations'] = []

        customization_record = {
            'job_id': job_id,
            'job_title': job_title,
            'company': company_name,
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'filename': os.path.basename(file_path)
        }

        memory_data['resume_customizations'].append(customization_record)

        with open(memory_path, 'w') as f:
            json.dump(memory_data, f, indent=2)

    except Exception as e:
        print(f"Error tracking resume customization: {e}")


def customize_resumes_for_all_jobs(job_search_results: str) -> str:
    """
    Customize resumes for all jobs found in search results.
    
    Args:
        job_search_results: JSON string containing job search results
    
    Returns:
        str: Summary of customization results
    """
    time.sleep(60)
    try:
        # Parse job results
        jobs = json.loads(job_search_results)

        if not jobs:
            return "No jobs found to customize resumes for."

        customization_results = []
        successful_customizations = 0
        failed_customizations = 0

        print(f"Starting batch resume customization for {len(jobs)} jobs...")

        for i, job in enumerate(jobs, 1):
            job_id = job.get('job_id', f'unknown_{i}')
            job_title = job.get('title', 'Unknown Position')
            company_name = job.get('company', 'Unknown Company')
            job_description = job.get('description', '')

            print(f"\n[{i}/{len(jobs)}] Customizing resume for:")
            print(f"  Job ID: {job_id}")
            print(f"  Company: {company_name}")
            print(f"  Title: {job_title}")

            # Customize resume for this specific job
            result = customize_resume_for_job(job_id=job_id,
                                              job_description=job_description,
                                              job_title=job_title,
                                              company_name=company_name)

            customization_results.append({
                'job_id': job_id,
                'company': company_name,
                'title': job_title,
                'result': result,
                'success': '✅' in result
            })

            if '✅' in result:
                successful_customizations += 1
            else:
                failed_customizations += 1

            # Add delay to prevent overloading
            time.sleep(0.5)

        # Generate summary
        summary = f"""
📊 **Batch Resume Customization Complete**

✅ **Successful**: {successful_customizations}/{len(jobs)} resumes customized
❌ **Failed**: {failed_customizations}/{len(jobs)} customizations failed

📁 **Customized resumes saved in**: `./data/customized_resumes/`

**Individual Results:**
"""

        for result in customization_results:
            status = "✅" if result['success'] else "❌"
            summary += f"\n{status} **{result['company']}** - {result['title']}"
            if not result['success']:
                summary += f"\n   Error: {result['result']}"

        return summary

    except json.JSONDecodeError:
        return "❌ Error: Invalid job search results format"
    except Exception as e:
        return f"❌ Error in batch resume customization: {str(e)}"


def get_job_by_id(job_id: str) -> Dict:
    """Retrieve specific job details by job_id from memory"""
    time.sleep(60)
    try:
        memory_path = "./data/memory.json"
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory_data = json.load(f)

            jobs_found = memory_data.get('jobs_found', [])
            for job in jobs_found:
                if job.get('job_id') == job_id:
                    return job

        return {}
    except Exception as e:
        print(f"Error retrieving job {job_id}: {e}")
        return {}


def list_customized_resumes() -> str:
    """List all customized resumes with their details"""
    time.sleep(60)
    try:
        resumes_dir = "./data/customized_resumes"
        if not os.path.exists(resumes_dir):
            return "No customized resumes directory found."

        resume_files = [
            f for f in os.listdir(resumes_dir) if f.endswith('.pdf')
        ]

        if not resume_files:
            return "No customized resumes found."

        resume_list = f"📑 **Found {len(resume_files)} customized resumes:**\n\n"

        # Load tracking data
        memory_path = "./data/memory.json"
        tracking_data = {}
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory_data = json.load(f)
                tracking_data = {
                    item['filename']: item
                    for item in memory_data.get('resume_customizations', [])
                }

        for filename in sorted(resume_files):
            file_path = os.path.join(resumes_dir, filename)
            file_size = os.path.getsize(file_path) / 1024  # KB
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            # Get tracking info if available
            if filename in tracking_data:
                track_info = tracking_data[filename]
                resume_list += f"📄 **{filename}**\n"
                resume_list += f"   🏢 Company: {track_info.get('company', 'Unknown')}\n"
                resume_list += f"   💼 Position: {track_info.get('job_title', 'Unknown')}\n"
                resume_list += f"   🆔 Job ID: {track_info.get('job_id', 'Unknown')}\n"
            else:
                resume_list += f"📄 **{filename}**\n"

            resume_list += f"   📊 Size: {file_size:.1f} KB\n"
            resume_list += f"   📅 Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}\n\n"

        return resume_list

    except Exception as e:
        return f"Error listing resumes: {str(e)}"


# Create Agno agent with enhanced tools


def create_agent(provider: str = 'ollama'):
    """Create Agno agent with enhanced batch resume customization tools"""
    tools = [
        read_job_preferences,
        search_jobs,
        customize_resume_for_job,
        customize_resumes_for_all_jobs,  # New batch function
        list_customized_resumes,
        get_job_by_id
    ]

    return Agent(tools=tools,
                 show_tool_calls=True,
                 model=get_model(provider),
                 markdown=True,
                 debug_mode=True)


def run_agent(query: str, provider: str = 'ollama'):
    """Run the agent with a query"""
    agent = create_agent(provider)
    response_stream = agent.run(query)
    pprint_run_response(response_stream, markdown=True)


# Example usage
if __name__ == "__main__":
    # Example of batch resume customization
    run_agent("""
    Find data engineer jobs at HCLTech in Bangalore. 
    Then customize my resume for each individual job found, 
    creating separate resume files for each position.
    """,
              provider='aws')
