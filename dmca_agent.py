"""
DMCA Report Writer Agent

A specialized agent for generating DMCA takedown notices based on brand infringement evidence.
"""

import os
import sys
from termcolor import colored
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.storage.agent.sqlite import SqliteAgentStorage
from file_toolkit import FileTools
from dmca_report_tool import DmcaReportTools

# Load environment variables
load_dotenv()

class DmcaReportAgent(Agent):
    """
    Agent specialized in creating DMCA takedown notices and related legal documentation
    for brand protection and copyright enforcement.
    """
    
    def __init__(self):
        # Ensure storage directory exists
        storage_dir = "/Users/ruchitpatel/Projects/agnoagent/storage"
        os.makedirs(storage_dir, exist_ok=True)
        
        super().__init__(
            name="DMCA Report Writer",
            model=Gemini(id="gemini-2.0-flash"),  # Using Gemini 2.0 Flash model
            tools=[
                DuckDuckGoTools(),
                # Add DMCA-specific tools
                DmcaReportTools(storage_directory=storage_dir),
                # Add file tools for reading/writing files
                FileTools()  # This will use the hardcoded storage directory
            ],
            # Add memory using SQLite storage
            storage=SqliteAgentStorage(
                table_name="dmca_agent_sessions",
                db_file="tmp/agent_storage.db"
            ),
            # Add conversation history to each message
            add_history_to_messages=True,
            # Include last 5 interactions in the context
            num_history_responses=5,
            # Add current date/time to instructions
            add_datetime_to_instructions=True,
            instructions=[
                "You are a professional DMCA report writer specialized in creating legally sound takedown notices.",
                "Your primary goal is to help copyright owners protect their content from unauthorized use.",
                "Always ask for all required information to create a valid DMCA notice.",
                "Required information includes: copyright owner details, contact information, description of original work, location of infringing material, and details of infringement.",
                "Ensure all DMCA notices include the required good faith statement and accuracy statement under penalty of perjury.",
                "Advise users to verify infringement before proceeding, ensuring they have a good-faith belief that the use is unauthorized.",
                "Generate comprehensive, clear, and professional DMCA notices that comply with all legal requirements.",
                "Save all DMCA notices as markdown files for easy reading and proper formatting.",
                "You can look up domain registration information to help find the appropriate recipient for DMCA notices.",
                "Remind users that they should be the copyright owner or authorized to act on behalf of the owner.",
                "When creating a DMCA notice, aim to be thorough but concise, including all legally required elements.",
                "Advise users to consider fair use before proceeding with a DMCA takedown notice.",
                "You can read previously saved brand infringement reports to incorporate evidence into DMCA notices."
            ],
            show_tool_calls=True,  # Shows tool calls in the response
            markdown=True  # Format responses in markdown
        )

# Format and print tool call information
def print_tool_call(tool_name, tool_args):
    """
    Format and print tool call information
    
    Args:
        tool_name: Name of the tool being called
        tool_args: Arguments passed to the tool
    """
    print(colored("\n🔧 TOOL CALL: ", "cyan", attrs=["bold"]), end="")
    print(colored(tool_name, "cyan"))
    
    if tool_args:
        args_str = ", ".join([f"{k}={v}" for k, v in tool_args.items()])
        print(colored("   Args: ", "cyan"), end="")
        print(colored(args_str, "cyan"))
    print()

# Print tool results
def print_tool_result(tool_result):
    """
    Print the results returned by a tool
    
    Args:
        tool_result: Result string from the tool
    """
    print(colored("\n📊 TOOL RESULT:", "green", attrs=["bold"]))
    print(colored("─" * 80, "green"))
    print(colored(tool_result, "green"))
    print(colored("─" * 80, "green"))
    print()

# Run the agent
def main():
    # Create tmp directory if it doesn't exist
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    
    # Initialize the agent
    agent = DmcaReportAgent()
    
    # Print welcome message
    print(colored("📝 DMCA Report Writer", "red", attrs=["bold"]))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "red"))
    print(colored("💼 Legal specialist ", "yellow") + "- Creating DMCA takedown notices")
    print(colored("🔍 Domain lookup ", "yellow") + "- Find registrar and contact information")
    print(colored("📋 Report generator ", "yellow") + "- Complete DMCA notice creation")
    print(colored("📁 File operations ", "yellow") + "- Save and retrieve DMCA notices")
    print(colored("💬 Type ", "yellow") + colored("'exit'", "red") + colored(" to quit", "yellow"))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "red"))
    print(colored(f"Session ID: {agent.session_id}", "magenta"))
    print(colored(f"Storage directory: /Users/ruchitpatel/Projects/agnoagent/storage", "magenta"))
    print()
    print(colored("How to use: Provide details about copyright infringement, and I'll help you create a proper DMCA takedown notice.", "white"))
    print()
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input(colored("You: ", "cyan", attrs=["bold"]))
        print()
        
        # Check for exit command
        if user_input.strip().lower() == "exit":
            print(colored("👋 Goodbye!", "red"))
            break
        
        # Process the user input with proper streaming
        try:
            print(colored("Agent: ", "green", attrs=["bold"]), end="")
            sys.stdout.flush()
            
            # Use the agent's print_response method with streaming
            agent.print_response(user_input, stream=True)
            print()  # Add an extra line after the response
            
        except Exception as e:
            print(colored(f"\nError: {str(e)}", "red"))
            print()

if __name__ == "__main__":
    main()
