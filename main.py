import logging
import json
from datetime import datetime
import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voicemail_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_voicemail(transcript: str) -> None:
    logger.info(f"Processing voicemail: {transcript[:50]}...")
    result = classify_voicemail(transcript)

    if result is None:
        logger.error("Failed to classify voicemail - escalating to human review")
        print("ESCALATE: Failed to classify — human review required")
        return None

    logger.info(f"Classification complete - intent={result['intent']}, urgency={result['urgency']}")

    print(f"Intent: {result['intent']}")
    print(f"Urgency: {result['urgency']}/5")
    print(f"Summary: {result['summary']}")
    print(f"Action: {result['action']}")

    if result['urgency'] >= 4:
        logger.warning(f"HIGH PRIORITY voicemail - urgency {result['urgency']}/5")
        print(f"HIGH PRIORITY: Urgency {result['urgency']}/5 - immediate human review required")
    else:
        logger.info(f"Routine voicemail - urgency {result['urgency']}/5")
        print(f"ROUTINE: Urgency {result['urgency']}/5 — standard queue")

def classify_voicemail(transcript: str) -> str:
    system = """You are a medical clinic receptionist assistant. 
    Classify the voicemail and respond ONLY in JSON with these fields:
    - intent: what the caller wants (appointment, prescription, test_results, urgent, other)
    - urgency: 1 (low) to 5 (high)
    - summary: one sentence summary
    - action: what the receptionist should do"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system}\n\nVoicemail transcript: {transcript}"
    )
    text = response.text.strip().strip("```json").strip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e.msg} at line {e.lineno}, column {e.colno}")
        return None

test_voicemails = [
    "Hi, this is Sarah, I'd like to book an appointment with Dr. Smith for next Tuesday if possible.",
    "Hello, this is Mike calling about my blood pressure medication. I've run out and need a refill prescription urgently.",
    "Hi, this is John, I've been having chest pains since this morning and wanted to speak to a doctor urgently"
]

for i, transcript in enumerate(test_voicemails, 1):
    print(f"\n--- Voicemail {i} ---")
    print(f"Transcript: {transcript}")
    process_voicemail(transcript)