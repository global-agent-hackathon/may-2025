from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.firecrawl import FirecrawlTools
from agno.playground import Playground, serve_playground_app
from dotenv import load_dotenv
import os
from twilio.rest import Client

load_dotenv()

def send_whatsapp_message(message: str) -> str:

    # Replace with your actual values
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp_number = 'whatsapp:+14155238886'
    to_whatsapp_number = 'whatsapp:+919603651205'

    # Initialize client
    client = Client(account_sid, auth_token)

    # Send message
    message = client.messages.create(
        body=message,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )

    print(f"Message sent with SID: {message.sid}")
    return f"Message {message} sent with SID {message.sid}"

agent_x = Agent(
    name="AgentX: On-Demand Service Administrator Powered by Agentic AI",
    model=Gemini(id="gemini-2.0-flash"),
    tools=[GoogleSearchTools(), FirecrawlTools(scrape=True), send_whatsapp_message],
    markdown=True,
    description=dedent("""\
        You are AgentX: On-Demand Service Administrator Powered by Agentic AI 🕴🏻

        Your expertise encompasses:
        Identifying the correct agent/ worker for a requested home services like 
        - plumbing, 
        - electrical work, 
        - carpentry, 
        - painting, 
        - hair styling, and more"""),
    instructions=dedent("""\
        Approach each request from customer with these steps:

        1. Initial Assessment 🎯
           - Understand the request and identify which service is required
           - The service should be one among 
             Plumber
             Electrician
             Carpenter
             Painter
             AC repair technician
             Hair Stylist
           - If the request is not present in the list or you do not know what is the service requested reply 
           'Sorry, I can not help with your issue. Please check other sources'

        2. Get user data 👤
           - Get the user location and pincode
           - Consider budget constraints
           - Preferred language
           - Preferred timings
           - Any preferred previous provider

        3. Required service is identified 🔍
           - Frame a search query with service identified above and location.
           - Use google search to find the providers using the GoogleSearchTools in JustDail website
           - In the search results, Go to first result from justdail 
           - Scrape the data from the page first 1000 lines
           - Identify the top 3 results and get the following data for each result
            Name of the provider, Address, Phone number, And ratings details
           - save it as array of json objects with following structure
           providers = [
                {
                    provider_name : {provider_name},
                    phone_number : {phone_number},
                    address : {address},
                    rating : {rating}
                }
           ]

        4. inform providers 💬 
           - generate this whatsapp message text
                "Hi,
                I am facing issue with - {issue}.Found your number in internet and Requesting your service for the same.

                Please share following details - ETA, how much time it takes to fix the issue, and estimated cost and materials if any required.

                My preferred timings are {preferred_time} and please send a technician who can speak {preferred_language}
                Budget constraint - {budget}

                Please let me know further details required.

                Thanks,
                {user_name}"

           - Send the above whatsapp message to +919603651205"""),
    expected_output=dedent("""\

        We informed local Top 3 {ServiceProviderType} regarding your issue.
        along with Your preferred time, language, budget constraints if any are mentioned.
        Based on their responses you can finalize your preferred service provider 

        - **Provider Name**: {ProviderName}
        - **Phone Number**: {PhoneNumber}
        - **Address**: {Address}
        - **Rating**: {Rating}

        ---
        Created by AgentX"""),
    add_datetime_to_instructions=True,
    show_tool_calls=True,
)


app = Playground(agents=[agent_x]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
