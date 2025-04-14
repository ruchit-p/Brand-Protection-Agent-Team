import os
import sys
from termcolor import colored
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.storage.agent.sqlite import SqliteAgentStorage
from domain_intelligence_tool import domain_intelligence
from firecrawl_tool import FirecrawlTools
from image_analyzer import ImageAnalyzerTools
from file_toolkit import FileTools

# Load environment variables
load_dotenv()

# Define the brand protection agent
class BrandProtectionAgent(Agent):
    def __init__(self):
        # Ensure storage directory exists
        storage_dir = "/Users/ruchitpatel/Projects/agnoagent/storage"
        os.makedirs(storage_dir, exist_ok=True)
        
        super().__init__(
            name="Brand Intelligence Agent",
            model=Gemini(id="gemini-2.0-flash"),  # Using Gemini 2.0 Flash model
            tools=[
                # Removed YFinanceTools
                DuckDuckGoTools(),
                # Add domain intelligence tool
                domain_intelligence,
                # Add Firecrawl tools for web scraping and brand analysis
                FirecrawlTools(
                    formats=["markdown", "html", "screenshot"],
                    limit=10,
                    scrape=True,
                    crawl=True
                ),
                # Add image analysis tools using Gemini 2.0 Flash
                ImageAnalyzerTools(),
                # Add file tools for reading/writing files
                FileTools()  # This will use the hardcoded storage directory
            ],
            # Add memory using SQLite storage
            storage=SqliteAgentStorage(
                table_name="brand_agent_sessions",
                db_file="tmp/agent_storage.db"
            ),
            # Add conversation history to each message
            add_history_to_messages=True,
            # Include last 5 interactions in the context
            num_history_responses=5,
            # Add current date/time to instructions
            add_datetime_to_instructions=True,
            instructions=[
                "You are a professional brand intelligence agent who provides insights on brand protection.",
                "Use tables to display data when appropriate.",
                "Always include sources for your information.",
                "When referencing past conversations, be specific about previous topics discussed.",
                "You can perform domain intelligence to detect typosquatting and analyze domain registrations.",
                "You can scrape websites to analyze content for brand mentions and visual brand elements.",
                "You can analyze images to detect logos, product similarities, and potential brand infringements.",
                "When a user asks you to analyze a URL for a brand, use the Firecrawl tools to scrape the website and look for both textual mentions and visual brand elements.",
                "After scraping a website, use the image analysis tools to analyze any screenshots or logos found for potential brand infringement.",
                "Provide thorough analysis of both text content and visual elements for comprehensive brand protection.",
                "When comparing two different websites, analyze both the textual and visual similarities that might indicate brand infringement.",
                "You can read and write files (.txt, .md, .csv, .json) in the storage directory for reports and evidence.",
                "When you find evidence of brand infringement, save it to files for documentation purposes.",
                "For reports, prefer using markdown (.md) format for better readability and structure."
            ],
            show_tool_calls=True,  # Shows tool calls in the response
            markdown=True  # Format responses in markdown
        )

# Create the tmp directory if it doesn't exist
def ensure_tmp_directory():
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
        print("Created 'tmp' directory for agent storage.")

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
    # Ensure the tmp directory exists
    ensure_tmp_directory()
    
    # Initialize the agent
    agent = BrandProtectionAgent()
    
    # Print welcome message
    print(colored("🔍 Brand Protection Agent", "blue", attrs=["bold"]))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "blue"))
    print(colored("💾 Memory enabled ", "yellow") + "- Your conversation history is saved")
    print(colored("🔍 Domain intelligence ", "yellow") + "- Analyze domains for typosquatting")
    print(colored("🌐 Web scraping ", "yellow") + "- Analyze websites for brand mentions and imagery")
    print(colored("🖼️ Image analysis ", "yellow") + "- Detect logos and compare visual brand elements")
    print(colored("📁 File operations ", "yellow") + "- Save and retrieve reports and evidence")
    print(colored("💬 Type ", "yellow") + colored("'exit'", "red") + colored(" to quit", "yellow"))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "blue"))
    print(colored(f"Session ID: {agent.session_id}", "magenta"))
    print(colored(f"Storage directory: /Users/ruchitpatel/Projects/agnoagent/storage", "magenta"))
    print()
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input(colored("You: ", "cyan", attrs=["bold"]))
        print()
        
        # Check for exit command
        if user_input.strip().lower() == "exit":
            print(colored("👋 Goodbye!", "blue"))
            break
        
        # Check for debug commands
        if user_input.strip().lower() == "memory status":
            if hasattr(agent, 'memory') and agent.memory:
                print(colored(f"Memory: {len(agent.memory.messages)} messages in current session", "magenta"))
                print(colored(f"Session ID: {agent.session_id}", "magenta"))
            else:
                print(colored("Memory not initialized or no messages yet.", "magenta"))
            continue
        
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
