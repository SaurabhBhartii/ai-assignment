from crewai import Agent, Crew, Task, LLM
from crewai_tools import FileReadTool
import sqlite3

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key="AIzaSyA2mwbvwqjnl54gfm88eWq-rHCrj0"
)

# read_csv_tool = FileReadTool(file_path=r"C:\Users\saura\OneDrive\Desktop\Synthetic_Financial_datasets_log.csv")

ingestion_agent = Agent(
    role="Lead Data Ingestion Specialist",
    goal="Read CSV and store leads into database",
    backstory="Expert in data cleaning and ingestion pipelines",
    verbose=True,
    llm=llm
)

channel_agent = Agent(
    role="Multi-Channel NLP Analyzer",
    goal="Extract structured data from messages",
    backstory="Expert in NLP and extracting insights from unstructured data",
    verbose=True,
    llm=llm
)

reconciliation_agent = Agent(
    role="Data Reconciliation Expert",
    goal="Merge new updates with existing database truth",
    backstory="Specialist in maintaining single source of truth",
    verbose=True,
    llm=llm
)

qualification_agent = Agent(
    role="Lead Qualification Analyst",
    goal="Determine onboarding stage and lead score",
    backstory="Expert in evaluating onboarding readiness",
    verbose=True,
    llm=llm
)

response_agent = Agent(
    role="Customer Communication Specialist",
    goal="Generate WhatsApp, Email, and Call responses",
    backstory="Expert in customer communication across channels",
    verbose=True,
    llm=llm
)

sync_agent = Agent(
    role="Database Sync Manager",
    goal="Update database and maintain consistency",
    backstory="Ensures all systems reflect latest data",
    verbose=True,
    llm=llm
)


ingestion_task = Task(
    description="Read CSV file and insert leads into database",
    agent=ingestion_agent,
    expected_output="Leads stored in database"
)

channel_task = Task(
    description="Analyze incoming message and extract structured data",
    agent=channel_agent,
    expected_output="Structured JSON with extracted fields"
)

reconciliation_task = Task(
    description="Merge extracted data with existing database records",
    agent=reconciliation_agent,
    expected_output="Updated lead data"
)

qualification_task = Task(
    description="Determine onboarding stage and calculate lead score",
    agent=qualification_agent,
    expected_output="Lead stage and score"
)


response_task = Task(
    description="Generate WhatsApp, Email, and Call responses",
    agent=response_agent,
    expected_output="Communication drafts"
)


sync_task = Task(
    description="Update database with latest state and history",
    agent=sync_agent,
    expected_output="Database updated successfully"
)


from crewai import Crew

crew = Crew(
    agents=[
        ingestion_agent,
        channel_agent,
        reconciliation_agent,
        qualification_agent,
        response_agent,
        sync_agent
    ],
    tasks=[
        ingestion_task,
        channel_task,
        reconciliation_task,
        qualification_task,
        response_task,
        sync_task
    ],
    verbose=True
)


if __name__ == "__main__":
    result = crew.kickoff()
    print(result)


conn = sqlite3.connect("leads.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    lead_id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    email TEXT,
    vehicle_count INTEGER,
    aadhaar_status TEXT,
    bank_status TEXT,
    rc_status TEXT,
    stage TEXT,
    score INTEGER
)
""")

conn.commit()


def calculate_score(lead):
    score = 0
    if lead["aadhaar_status"] == "completed":
        score += 30
    if lead["bank_status"] == "completed":
        score += 30
    if lead["rc_status"] == "completed":
        score += 40
    return score

EXTRACTION_PROMPT = """
Extract the following fields:
- vehicle_count
- aadhaar_status
- bank_status

Return JSON only.
"""