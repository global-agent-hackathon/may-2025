# improved_app.py
import streamlit as st
import json
import os
from datetime import datetime
# Enhanced main.py with batch resume customization

import os
import json

from datetime import datetime
import time

from dotenv import load_dotenv

from linkedin_api import Linkedin

load_dotenv()


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


def print_easy():
    try:
        # Get detailed job information
        linkedin_api = init_linkedin_api()
        job_data = linkedin_api.get_job(job_id=4240174915)

        # Extract job details
        job_title = job_data.get("title", "Unknown Title")
        company_details = job_data.get("companyDetails", {}).get(
            "com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany",
            {})
        company_name = company_details.get("companyResolutionResult",
                                           {}).get("name", "Unknown Company")
        job_description = job_data.get("description",
                                       {}).get("text",
                                               "No description available")
        job_location = job_data.get("formattedLocation", "Unknown Location")
        easy_apply = job_data.get("applyMethod", {}).get("easyApplyUrl")
        easy_apply_url = job_data.get("applyMethod", {}).get(
            "com.linkedin.voyager.jobs.ComplexOnsiteApply",
            {}).get("easyApplyUrl")

        company_apply_url = None

        print(easy_apply, easy_apply_url)
        print("-" * 80)

        if not easy_apply and not easy_apply_url:
            print("skip")

            company_apply_url = job_data.get("applyMethod", {}).get(
                "com.linkedin.voyager.jobs.OffsiteApply",
                {}).get("companyApplyUrl")
            print("Company Apply URL:", company_apply_url)
    except Exception as e:
        print(f"Error processing job : {e}")


def search_jobs() -> str:
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
    linkedin_api = init_linkedin_api()
    # Simulate delay for testing
    if not linkedin_api:
        # Return mock data for testing
        return "Error: LinkedIn API not initialized. Please check your credentials."

    try:
        print("Using LinkedIn API to search for jobs...")

        jobs = linkedin_api.search_jobs(
            keywords="Software Engineer",
            companies=["PhonePe"],
            location_name="India",
            limit=100,
            listed_at=86400,  # 1 day ago
            easy_apply=True)  #need to be replaced by limit

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

                print(job_data)
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
                    "url": easy_apply_url
                    or f"https://www.linkedin.com/jobs/view/{job_id}",
                    "posted_date": datetime.now().isoformat(),
                    "company_apply_url": company_apply_url
                }

                job_results.append(job_result)

                # Add delay to avoid rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
                continue

        print("returning results")

        return json.dumps(job_results, indent=2)

    except Exception as e:
        return f"Error searching jobs: {e}"


# Example usage:
# resume_text = """Your resume text here"""
# create_latex_resume(resume_text, "resume.pdf")

if __name__ == "__main__":
    result = print_easy()