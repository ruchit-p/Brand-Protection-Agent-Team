"""
Agent Team Module

This module coordinates the Brand Protection Agent and DMCA Report Agent,
allowing them to work together as a team with seamless handoffs.
"""

import os
import sys
import json
import uuid
from datetime import datetime
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
from dmca_report_tool import DmcaReportTools
from brand_analysis_report import BrandAnalysisReportGenerator
from agno.tools import Toolkit
from config import get_storage_dir, get_tmp_dir

# Load environment variables
load_dotenv()

# Create the tmp directory for database storage (configurable)
os.makedirs(get_tmp_dir(), exist_ok=True)

class HandoffTools(Toolkit):
    """
    Toolkit that enables agents to hand off tasks to other agents.
    """
    
    def __init__(self, storage_dir, dmca_agent_path=None):
        """
        Initialize the handoff toolkit.
        
        Args:
            storage_dir: Path to the storage directory
            dmca_agent_path: Path to the DMCA agent script
        """
        super().__init__(name="handoff_tools")
        self.storage_dir = storage_dir
        self.dmca_agent_path = dmca_agent_path or os.path.join(os.path.dirname(__file__), "dmca_agent.py")
        
        # Register handoff functions
        self.register(self.handoff_to_dmca_agent)
        self.register(self.save_infringement_context)
    
    def handoff_to_dmca_agent(self, reason: str, infringement_report_path: str) -> str:
        """
        Hand off a task to the DMCA Report Agent.
        
        Args:
            reason: Reason for the handoff
            infringement_report_path: Path to the infringement report
            
        Returns:
            Confirmation of the handoff
        """
        # Ensure the infringement_report_path is just a filename, not a full path
        if "/" in infringement_report_path:
            report_filename = os.path.basename(infringement_report_path)
        else:
            report_filename = infringement_report_path
        
        # Check if the report exists
        report_path = os.path.join(self.storage_dir, report_filename)
        if not os.path.exists(report_path):
            return f"Error: Cannot hand off to DMCA agent because infringement report '{report_filename}' was not found."
        
        # Create a context file to pass information to the DMCA agent
        context = {
            "reason": reason,
            "infringement_report": report_filename,
            "timestamp": datetime.now().isoformat()
        }
        
        context_filename = "handoff_context.json"
        context_path = os.path.join(self.storage_dir, context_filename)
        
        with open(context_path, "w") as f:
            json.dump(context, f, indent=2)
        
        # Provide instructions to the user to run the DMCA agent
        result = f"""
## Handoff to DMCA Report Agent

The brand protection analysis is complete and has identified potential infringement. 
The infringement report has been saved to: **{report_filename}**

### Reason for handoff
{reason}

### Next Steps

To proceed with creating a DMCA takedown notice, please run the DMCA Report Agent:

```
python dmca_agent.py
```

The DMCA Report Agent will have access to the infringement report and will guide you through
creating a proper DMCA takedown notice.

### Handoff Context
Context information has been saved to {context_filename} for the DMCA agent to reference.
"""
        return result
    
    def save_infringement_context(self, infringing_url: str, brand_name: str, evidence_summary: str, report_path: str) -> str:
        """
        Save infringement context for potential DMCA action.
        
        Args:
            infringing_url: URL of the infringing website
            brand_name: Name of the brand being infringed
            evidence_summary: Summary of infringement evidence
            report_path: Path to the full infringement report
            
        Returns:
            Confirmation of saved context
        """
        # Create a context file with infringement details
        context = {
            "infringing_url": infringing_url,
            "brand_name": brand_name,
            "evidence_summary": evidence_summary,
            "report_path": report_path,
            "timestamp": datetime.now().isoformat()
        }
        
        context_filename = f"infringement_context_{brand_name}.json"
        context_path = os.path.join(self.storage_dir, context_filename)
        
        with open(context_path, "w") as f:
            json.dump(context, f, indent=2)
        
        return f"Infringement context saved to {context_filename} for potential DMCA action."

class EnhancedBrandProtectionAgent(Agent):
    """
    Enhanced Brand Protection Agent with ability to hand off to DMCA agent.
    """
    
    def __init__(self, session_id=None):
        # Create a unique session ID if not provided
        self.session_id = session_id or str(uuid.uuid4())
        
        # Create session-specific storage directory
        self.storage_dir = get_storage_dir()
        self.session_dir = os.path.join(self.storage_dir, f"session_{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
        
        # First create the image analyzer so it can be passed to Firecrawl tools
        self.image_analyzer = ImageAnalyzerTools()
        
        # Create the firecrawl tools with reference to image analyzer
        self.firecrawl_tools = FirecrawlTools(
            formats=["markdown", "html", "screenshot"],
            limit=10,
            scrape=True,
            crawl=True,
            session_id=self.session_id,
            image_analyzer=self.image_analyzer
        )
        
        super().__init__(
            name="Brand Intelligence Agent",
            model=Gemini(id="gemini-2.0-flash"),
            tools=[
                DuckDuckGoTools(),
                domain_intelligence,
                self.firecrawl_tools,
                self.image_analyzer,
                FileTools(base_directory=self.session_dir),
                HandoffTools(storage_dir=self.session_dir),
                BrandAnalysisReportGenerator(storage_dir=self.session_dir)
            ],
            storage=SqliteAgentStorage(
                table_name="brand_agent_sessions",
                db_file=os.path.join(get_tmp_dir(), "agent_storage.db")
            ),
            add_history_to_messages=True,
            num_history_responses=5,
            add_datetime_to_instructions=True,
            instructions=[
                "You are a professional brand intelligence agent who provides insights on brand protection using a zero-trust approach.",
                "You MUST take a zero-trust approach when analyzing websites - assume NO infringement exists until conclusively proven with direct evidence.",
                "You conduct analysis like a forensic investigator, requiring concrete, verifiable evidence before making any claims of brand usage.",
                "You always follow a standardized format for brand analysis reports, using the BrandAnalysisReportGenerator tool.",
                "When analyzing potential brand usage, you always provide an evidence-based numerical score from 0-100.",
                "Use tables to display data when appropriate.",
                "Always include sources for your information and cite specific evidence for any claims made.",
                "When referencing past conversations, be specific about previous topics discussed.",
                "You can perform domain intelligence to detect typosquatting and analyze domain registrations.",
                "You can scrape websites to analyze content for brand mentions and visual brand elements.",
                "You can analyze images to detect logos, product similarities, and potential brand usage.",
                "IMPORTANT: When a user asks you to analyze a URL for a brand, work autonomously to complete the full analysis task without asking for intermediate confirmation:",
                "  1. First, use the Firecrawl tools to scrape the website completely",
                "  2. Analyze the textual content for exact brand mentions",
                "  3. Analyze any screenshots for exact visual matches",
                "  4. Use domain intelligence to check domain information",
                "  5. Generate a complete brand analysis report with all findings",
                "  6. Only after completing ALL steps, present the final analysis to the user",
                "When scraping websites, images are automatically analyzed for brand elements - you don't need to analyze them separately.",
                "When multiple websites are scraped, screenshots are automatically compared for visual similarities.",
                "Provide thorough analysis of both text content and visual elements for comprehensive brand protection.",
                "When comparing two different websites, analyze both the textual and visual matches that might indicate brand usage.",
                "For all brand analysis, use the BrandAnalysisReportGenerator to create a standardized report.",
                "The reports should include sections for Executive Summary, Subject Details, Evidence Collection, Analysis, Evidence Assessment, and Recommendations.",
                "The evidence-based score calculation is extremely conservative and considers ONLY concrete evidence: exact text matches, identical visual elements, verified logo usage, and identical product images.",
                "You MUST be extremely conservative in your assessment - clearly state when evidence is inconclusive or ambiguous.",
                "NEVER make assumptions about intent or association without clear evidence in the content or code of the website.",
                "You can read and write files (.txt, .md, .csv, .json) in the storage directory for reports and evidence.",
                "When you find evidence of brand usage, save it to files for documentation purposes.",
                "For reports, prefer using markdown (.md) format for better readability and structure.",
                "If you find evidence of significant brand usage (score above 80), offer to hand off to the DMCA Report Agent.",
                "A score above 80 should ONLY be assigned when there is unambiguous evidence of intentional brand impersonation with multiple verified instances.",
                "When handing off to the DMCA agent, save all relevant context and evidence first.",
                "The handoff should include the infringement report path and a clear reason why further action is recommended.",
                "In cases of uncertainty, always err on the side of caution and report lower evidence scores.",
                "A truly zero-trust approach means that similarities alone are NEVER sufficient - only exact matches count as evidence.",
                "Work autonomously through the full analysis process without asking for confirmation at intermediate steps."
            ],
            show_tool_calls=True,
            markdown=True
        )

class EnhancedDmcaReportAgent(Agent):
    """
    Enhanced DMCA Report Agent that can pick up from Brand Protection handoffs.
    """
    
    def __init__(self, session_id=None):
        # Create a unique session ID if not provided
        self.session_id = session_id or str(uuid.uuid4())
        
        # Create session-specific storage directory
        self.storage_dir = get_storage_dir()
        self.session_dir = os.path.join(self.storage_dir, f"session_{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
        
        super().__init__(
            name="DMCA Report Writer",
            model=Gemini(id="gemini-2.0-flash"),
            tools=[
                DuckDuckGoTools(),
                DmcaReportTools(storage_directory=self.session_dir),
                FileTools(base_directory=self.session_dir)
            ],
            storage=SqliteAgentStorage(
                table_name="dmca_agent_sessions",
                db_file=os.path.join(get_tmp_dir(), "agent_storage.db")
            ),
            add_history_to_messages=True,
            num_history_responses=5,
            add_datetime_to_instructions=True,
            instructions=[
                "You are a professional DMCA report writer specialized in creating legally sound takedown notices with a zero-trust approach.",
                "Your primary goal is to help copyright owners protect their content from unauthorized use, while ensuring that only clear evidence-based claims are made.",
                "Always ask for all required information to create a valid DMCA notice and VERIFY that the information is accurate and supported by evidence.",
                "Required information includes: copyright owner details, contact information, description of original work, location of material, and VERIFIED details of unauthorized use.",
                "Ensure all DMCA notices include the required good faith statement and accuracy statement under penalty of perjury.",
                "STRONGLY advise users to verify potential infringement before proceeding, ensuring they have a good-faith belief based on CONCRETE EVIDENCE that the use is unauthorized.",
                "Generate comprehensive, clear, and professional DMCA notices that comply with all legal requirements while maintaining strict fact-based claims.",
                "Save all DMCA notices as markdown files for easy reading and proper formatting.",
                "You can look up domain registration information to help find the appropriate recipient for DMCA notices.",
                "EMPHASIZE to users that they should be the copyright owner or authorized to act on behalf of the owner and verify their rights before proceeding.",
                "When creating a DMCA notice, aim to be thorough but concise, including all legally required elements.",
                "EXPLICITLY advise users to consider fair use before proceeding with a DMCA takedown notice, explaining specific fair use criteria.",
                "Check for handoff_context.json and evidence context files in the storage directory.",
                "If you find handoff context, verify the evidence in the brand analysis report to ensure it contains concrete verification of unauthorized use, not just similarities.",
                "Reference ONLY the concrete evidence in the brand analysis report when creating the DMCA notice - do not include speculation or assumptions.",
                "Recommend a human review of all evidence before submitting any DMCA notice.",
                "Apply a zero-trust approach where the burden of proof is on demonstrating unauthorized use with clear evidence, not assumptions.",
                "Advise users that DMCA notices should only be sent when there is unambiguous evidence of unauthorized use, not merely suspicious similarities.",
                "Work autonomously to create a complete DMCA notice without asking for confirmation at intermediate steps."
            ],
            show_tool_calls=True,
            markdown=True
        )
        
        # Check for handoff context on initialization
        self.check_for_handoff()
    
    def check_for_handoff(self):
        """Check if there's a handoff context file to process."""
        handoff_path = os.path.join(self.storage_dir, "handoff_context.json")
        if os.path.exists(handoff_path):
            try:
                with open(handoff_path, "r") as f:
                    self.handoff_context = json.load(f)
                self.has_handoff = True
            except:
                self.has_handoff = False
        else:
            self.has_handoff = False

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

def run_brand_protection_agent():
    """Run the Brand Protection Agent with handoff capability."""
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    agent = EnhancedBrandProtectionAgent(session_id=session_id)
    
    # Create session directory path
    session_dir = os.path.join(get_storage_dir(), f"session_{session_id}")
    
    # Print welcome message
    print(colored("🔍 Brand Protection Agent", "blue", attrs=["bold"]))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "blue"))
    print(colored("💾 Memory enabled ", "yellow") + "- Your conversation history is saved")
    print(colored("🔍 Domain intelligence ", "yellow") + "- Analyze domains for typosquatting")
    print(colored("🌐 Web scraping ", "yellow") + "- Analyze websites for brand mentions and imagery")
    print(colored("🖼️ Auto image analysis ", "yellow") + "- Images are automatically analyzed for brand elements")
    print(colored("📊 Infringement scoring ", "yellow") + "- 0-100 scale with detailed breakdown")
    print(colored("📝 Standardized reports ", "yellow") + "- Analytical format with forensic detail")
    print(colored("📁 File operations ", "yellow") + "- Save and retrieve reports and evidence")
    print(colored("🔄 DMCA handoff ", "yellow") + "- Can transfer to DMCA agent when infringement found")
    print(colored("💬 Type ", "yellow") + colored("'exit'", "red") + colored(" to quit", "yellow"))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "blue"))
    print(colored(f"Session ID: {session_id}", "magenta"))
    print(colored(f"Session directory: {session_dir}", "magenta"))
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
            
        # Check for agent switching command
        if user_input.strip().lower() == "switch to dmca":
            print(colored("Switching to DMCA Report Agent...", "yellow"))
            return "dmca", session_id
        
        # Check for debug commands
        if user_input.strip().lower() == "memory status":
            if hasattr(agent, 'memory') and agent.memory:
                print(colored(f"Memory: {len(agent.memory.messages)} messages in current session", "magenta"))
                print(colored(f"Session ID: {session_id}", "magenta"))
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
            
            # Check if response includes handoff recommendation
            if "handoff to dmca" in user_input.lower() or "switch to dmca" in user_input.lower():
                confirm = input(colored("Would you like to switch to the DMCA Report Agent now? (yes/no): ", "yellow"))
                if confirm.strip().lower() in ["yes", "y"]:
                    print(colored("Switching to DMCA Report Agent...", "yellow"))
                    return "dmca", session_id
            
        except Exception as e:
            print(colored(f"\nError: {str(e)}", "red"))
            print()
    
    return "exit", session_id

def run_dmca_report_agent(session_id=None):
    """Run the DMCA Report Agent with handoff awareness."""
    # Use provided session ID or generate a new one
    if not session_id:
        session_id = str(uuid.uuid4())
    
    agent = EnhancedDmcaReportAgent(session_id=session_id)
    
    # Get session directory path
    session_dir = os.path.join(get_storage_dir(), f"session_{session_id}")
    
    # Print welcome message
    print(colored("📝 DMCA Report Writer", "red", attrs=["bold"]))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "red"))
    print(colored("💼 Legal specialist ", "yellow") + "- Creating DMCA takedown notices")
    print(colored("🔍 Domain lookup ", "yellow") + "- Find registrar and contact information")
    print(colored("📋 Report generator ", "yellow") + "- Complete DMCA notice creation")
    print(colored("📁 File operations ", "yellow") + "- Save and retrieve DMCA notices")
    print(colored("🔄 Context aware ", "yellow") + "- Can continue from Brand Protection analysis")
    print(colored("💬 Type ", "yellow") + colored("'exit'", "red") + colored(" to quit or ", "yellow") + colored("'switch to brand'", "blue") + colored(" to switch agents", "yellow"))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "red"))
    print(colored(f"Session ID: {session_id}", "magenta"))
    print(colored(f"Session directory: {session_dir}", "magenta"))
    print()
    
    # Check for handoff context
    if hasattr(agent, 'has_handoff') and agent.has_handoff:
        print(colored("📩 Handoff detected from Brand Protection Agent", "yellow"))
        print(colored(f"Reason: {agent.handoff_context.get('reason', 'Potential brand infringement')}", "yellow"))
        print(colored(f"Report: {agent.handoff_context.get('infringement_report', 'No report specified')}", "yellow"))
        print()
        
        # Automatically prompt about the handoff
        first_message = f"I'd like to create a DMCA takedown notice based on the brand infringement report: {agent.handoff_context.get('infringement_report', 'latest report')}"
        print(colored(f"Auto-prompt: {first_message}", "cyan"))
        print()
        
        print(colored("Agent: ", "green", attrs=["bold"]), end="")
        sys.stdout.flush()
        agent.print_response(first_message, stream=True)
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
            
        # Check for agent switching command
        if user_input.strip().lower() == "switch to brand":
            print(colored("Switching to Brand Protection Agent...", "yellow"))
            return "brand", session_id
        
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
    
    return "exit", session_id

def main():
    """Main function that coordinates the agent team."""
    print(colored("\n💼 Brand Protection Suite", "magenta", attrs=["bold"]))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "magenta"))
    print(colored("This suite contains two specialized agents:", "white"))
    print(colored("🔍 Brand Protection Agent ", "blue") + "- Analyzes websites for brand infringement")
    print(colored("📝 DMCA Report Writer ", "red") + "- Creates legal DMCA takedown notices")
    print()
    print(colored("The agents work together as a team with seamless handoffs.", "white"))
    print(colored("Type ", "white") + colored("'switch to brand'", "blue") + colored(" or ", "white") + colored("'switch to dmca'", "red") + colored(" at any time to change agents.", "white"))
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "magenta"))
    print()
    
    # Start with Brand Protection Agent by default
    current_agent = "brand"
    session_id = None
    
    # Agent switching loop
    while current_agent != "exit":
        if current_agent == "brand":
            current_agent, session_id = run_brand_protection_agent()
        elif current_agent == "dmca":
            current_agent, session_id = run_dmca_report_agent(session_id)
        else:
            print(colored("Unknown agent type. Exiting...", "red"))
            break

if __name__ == "__main__":
    main()
