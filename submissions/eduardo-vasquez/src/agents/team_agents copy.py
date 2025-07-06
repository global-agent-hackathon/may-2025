from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agents.gmail_agent import gmail_agent
from agents.trello_agent import trello_agent
from agents.slack_agent import slack_agent
from agents.summarizer_agent import summarizer_agent
from config import settings
from textwrap import dedent
from agno.tools.reasoning import ReasoningTools


instructions = dedent(
    """\
You are a team of AI meeting assistants responsible for executing a structured workflow to summarize meetings, notify attendees, and create follow-up tasks.

Your responsibilities must be completed **step-by-step in the exact order** below.

Step 1 – Summarize the meeting using the summarizer_agent.

Step 2 – Use gmail_agent to send an email to all attendees.

Step 3 – Use slack_agent to post a message in the #meetings-repository channel.

Step 4 – Use trello_agent to create a Trello card for each action item.


"""
)


team_agents = Team(
    name="Workflow Executor",
    mode="coordinate",
    model=OpenAIChat("gpt-4.1", api_key=settings.OPENAI_API_KEY),
    members=[summarizer_agent, gmail_agent, trello_agent, slack_agent],
    tools=[ReasoningTools(add_instructions=True)],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
    share_member_interactions=True,
    instructions=instructions,
    success_criteria="The team has successfully completed **all** the tasks. Do not stop until completing all tasks.",
)


# inquiry = """
# This is the following meeting transcript:
# Onboarding Process Bottleneck Review
# Date: 06/05/2025
# Time: 11:00 AM – 12:00 PM

# Attendees and Email Addresses

# Emily Chen (Head of Operations): emily.chen@example.com

# David Kumar (Engineering Lead): david.kumar@example.com

# Laura Smith (Product Designer): laura.smith@example.com

# eduardo vasquez (CTO): ev.webtest@gmail.com

# [00:00:00] Emily Chen (Head of Operations):
# Good morning, team. The main agenda today is to address bottlenecks in our onboarding process. User retention for new sign-ups has dropped by 12% in the last two weeks, and we’ve seen a spike in support tickets during onboarding.

# [00:01:20] Laura Smith (Product Designer):
# I’ve reviewed session recordings and analytics. Most users seem confused by the third step in the tutorial, especially the API integration walkthrough. It's too technical for our target audience. I’d recommend simplifying the interface and breaking down the explanation.

# [00:03:05] David Kumar (Engineering Lead):
# That makes sense. We also noticed that latency spikes during API verification—our backend logs show a 2–3 second delay, which might be adding to the confusion. I’ll work with the infrastructure team to optimize that.

# [00:04:45] eduardo vasquez (CTO):
# Let’s set an aggressive but realistic timeline. David, aim to implement backend fixes and streamline the flow by Friday. Laura, once David’s changes hit staging, can your team conduct A/B testing on two simplified UI variants?

# [00:06:00] Laura Smith (Product Designer):
# Absolutely. I’ll prepare wireframes today and have prototypes ready by tomorrow. Usability testing can begin early next week. We’ll track completion rates and friction points across both variants.

# [00:07:50] Emily Chen (Head of Operations):
# Great. Also, let’s not forget internal documentation. Once the new flow is finalized, we’ll need updated onboarding guides for the support team. I’ll assign that to Ops, but I’ll need inputs from you, Laura, on the user flow changes."""

# team_agents.print_response(
#     inquiry,
# )
