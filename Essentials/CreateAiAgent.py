from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import logging
import traceback

log = logging.getLogger(__name__)
tools = []

def create_agent(config):
  try:
    log.info("Creating ai agent.")
    llm = ChatGoogleGenerativeAI(
      model="gemini-2.5-flash",
      google_api_key=config.GOOGLE_API_KEY
    )
    agent = create_react_agent(
      model=llm,
      tools=tools
    )
    log.info("Ai agent created successfully.")
  except:
    if config.GOOGLE_API_KEY: log.error(traceback.format_exc())
    llm, agent = None, None
  finally:
    return llm, agent
