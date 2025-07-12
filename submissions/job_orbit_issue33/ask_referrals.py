import os
import json
import asyncio
from dotenv import load_dotenv
from browser_use import Agent, BrowserSession
from langchain_aws import ChatBedrockConverse
import boto3
from datetime import datetime

# Load environment variables
load_dotenv()

access_key = os.getenv('ACCESS_KEY')
secret_key = os.getenv('SECRET_KEY')
linkedin_name = os.getenv('LINKEDIN_NAME')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')


def get_model(model: str = 'anthropic.claude-3-sonnet-20240229-v1:0',
              provider: str = 'aws'):
    """Initialize the LLM model"""
    if provider == 'aws':
        bedrock_client = boto3.client('bedrock-runtime',
                                      region_name='us-east-1',
                                      aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key)
        llm = ChatBedrockConverse(client=bedrock_client,
                                  model=model,
                                  temperature=0.8)
        return llm


def load_memory_data():
    """Load data from memory.json"""
    try:
        with open('./data/memory.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {
            "job_searches": [],
            "jobs_found": [],
            "resume_customizations": [],
            "referral_contacts": [],
            "referral_requests": []
        }


def save_memory_data(data):
    """Save data to memory.json"""
    with open('./data/memory.json', 'w') as f:
        json.dump(data, f, indent=2)


def extract_company_names(jobs_data):
    """Extract unique company names from jobs data"""
    companies = set()
    for job in jobs_data.get('jobs_found', []):
        company_name = job.get('company', '').strip()
        if company_name:
            companies.add(company_name)
    return list(companies)


async def search_and_request_referral(company_name, job_info, llm):
    """Use browser automation to search for people at a company and request referrals"""

    # Create personalized referral message template
    referral_message = f"""Hi there,

I hope this message finds you well. I noticed you work at {company_name}, and I'm very interested in opportunities there.

I'm actively looking for {job_info.get('title', 'software engineering')} roles and have experience in Python, data engineering, cloud technologies, and backend development.

I recently came across a {job_info.get('title', 'position')} opening at {company_name} and would love to learn more about the company culture and this role. Would you be open to providing a referral or sharing insights about opportunities there?

I'd be happy to share my resume and discuss how I might contribute to your team.

Thank you for your time and consideration!

Best regards"""

    # Define comprehensive browser automation tasks
    tasks = f"""
    You are going to help find and contact someone at {company_name} for a job referral. Follow these steps carefully:

    1. You will get a list of people working at {company_name} on LinkedIn.
    2. SEND CONNECTION REQUEST OR MESSAGE:
        - Click on the first profile that has a human name to go their profile page. 
       - On their profile page, look for "Connect" or "Message" button
       - If you see "Connect":
         * Click "Connect"
         * If prompted, click "Add a note" or "Send a personalized invitation"
         * In the message field, paste this message: {referral_message}
         * Click "Send invitation"
       - If you see "Message" with paper plane icon (for premium users):
         * Click "Message"
         * Give the message a subject.
         * Paste this message: {referral_message}
         * Click "Send" that looks like an arrow or paper plane icon present towards bottom right corner

    3. IMPORTANT NOTES:
       - Only contact ONE person per company for now
       - Be respectful and don't spam
       - If the company has very few employees on LinkedIn, that's okay - just find the best available person
       - If no one is found, report this so we can try alternative approaches

    Your goal is to successfully send one referral request to someone at {company_name} and report back with the person's name and whether the message was sent successfully.
    """

    # Start from LinkedIn homepage
    initial_actions = [{
        'open_tab': {
            'url':
            f'https://www.linkedin.com/search/results/people/?keywords={company_name}'
        }
    }]

    # Create browser session
    browser_session = BrowserSession(
        executable_path=
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        user_data_dir='~/.config/browseruse/profiles/default',
        headless=False,  # Keep visible so we can see what's happening
    )

    # Initialize agent
    agent = Agent(
        task=tasks,
        initial_actions=initial_actions,
        llm=llm,
        save_conversation_path=
        f"logs/referral_search_{company_name.replace(' ', '_')}",
        browser_session=browser_session,
    )

    try:
        result = await agent.run()
        print(f"Referral search result for {company_name}: {result}")
        return {"status": "success", "result": result, "company": company_name}
    except Exception as e:
        print(f"Error searching for referral at {company_name}: {e}")
        return {"status": "error", "message": str(e), "company": company_name}


async def automate_browser_referrals():
    """Main function to automate referral requests using browser automation only"""

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Load memory data
    memory_data = load_memory_data()

    # Initialize LLM
    llm = get_model()

    # Extract company names and job info from jobs
    companies = extract_company_names(memory_data)
    jobs_by_company = {}
    for job in memory_data.get('jobs_found', []):
        company = job.get('company', '').strip()
        if company:
            jobs_by_company[company] = job

    print(f"Found {len(companies)} companies to search: {companies}")

    # Initialize referral tracking if not exists
    if 'referral_contacts' not in memory_data:
        memory_data['referral_contacts'] = []
    if 'referral_requests' not in memory_data:
        memory_data['referral_requests'] = []

    # Check which companies we haven't contacted yet
    contacted_companies = set()
    for request in memory_data['referral_requests']:
        contacted_companies.add(request.get('company', ''))

    companies_to_contact = [
        company for company in companies if company not in contacted_companies
    ]

    if not companies_to_contact:
        print("All companies have already been contacted!")
        return

    print(
        f"Will search for referrals at {len(companies_to_contact)} companies")

    # Process each company (limit to 3 per run to avoid overwhelming)
    for i, company in enumerate(companies_to_contact[:3]):
        print(f"\n{'='*50}")
        print(
            f"Processing company {i+1}/{len(companies_to_contact[:3])}: {company}"
        )
        print(f"{'='*50}")

        job_info = jobs_by_company.get(company, {})

        # Search for people and request referral
        result = await search_and_request_referral(company, job_info, llm)

        # Log the referral request
        referral_request = {
            "company": company,
            "job_title": job_info.get('title', 'Unknown'),
            "request_date": datetime.now().isoformat(),
            "status": result['status'],
            "method": "browser_automation"
        }
        memory_data['referral_requests'].append(referral_request)

        # Save progress after each company
        save_memory_data(memory_data)
        print(
            f"Completed referral request for {company}. Status: {result['status']}"
        )

        # Add delay between companies to be respectful
        if i < len(
                companies_to_contact[:3]) - 1:  # Don't wait after the last one
            print("Waiting 30 seconds before next company...")
            await asyncio.sleep(30)

    print(f"\n{'='*50}")
    print("Referral automation completed!")
    print(
        f"Total referral requests made: {len(memory_data['referral_requests'])}"
    )
    print(f"{'='*50}")


def get_referral_status():
    """Get status of referral requests"""
    memory_data = load_memory_data()

    requests = memory_data.get('referral_requests', [])

    print("=== REFERRAL STATUS REPORT ===")
    print(f"Total referral requests made: {len(requests)}")

    # Group by status
    status_counts = {}
    company_status = {}

    for request in requests:
        status = request.get('status', 'unknown')
        company = request.get('company', 'Unknown')

        # Count by status
        status_counts[status] = status_counts.get(status, 0) + 1

        # Track by company
        company_status[company] = {
            'status': status,
            'date': request.get('request_date', 'Unknown'),
            'job_title': request.get('job_title', 'Unknown')
        }

    print(f"\n=== STATUS BREAKDOWN ===")
    for status, count in status_counts.items():
        print(f"{status.upper()}: {count}")

    print(f"\n=== BY COMPANY ===")
    for company, info in company_status.items():
        print(
            f"{company}: {info['status']} ({info['job_title']}) - {info['date'][:10]}"
        )

    return {
        'total_requests': len(requests),
        'status_counts': status_counts,
        'company_status': company_status
    }


async def test_single_company(company_name):
    """Test the referral process for a single company"""
    print(f"Testing referral process for: {company_name}")

    llm = get_model()
    job_info = {"title": "Software Engineer", "company": company_name}

    result = await search_and_request_referral(company_name, job_info, llm)
    print(f"Test result: {result}")


def show_help():
    """Show help information"""
    print("""
=== REFERRAL AUTOMATION SCRIPT ===

Usage:
  python referrals_automation.py              - Run full automation
  python referrals_automation.py status       - Show referral status
  python referrals_automation.py test <company> - Test with single company
  python referrals_automation.py help         - Show this help

Examples:
  python referrals_automation.py
  python referrals_automation.py status
  python referrals_automation.py test "Google"
  python referrals_automation.py help

The script will:
1. Read job data from ./data/memory.json
2. Extract company names from job applications
3. Use browser automation to search LinkedIn for employees
4. Send personalized referral requests
5. Track all requests in memory.json
    """)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            get_referral_status()
        elif command == "test" and len(sys.argv) > 2:
            company_name = sys.argv[2]
            asyncio.run(test_single_company(company_name))
        elif command == "help":
            show_help()
        else:
            print("Invalid command. Use 'help' for usage information.")
    else:
        asyncio.run(automate_browser_referrals())
