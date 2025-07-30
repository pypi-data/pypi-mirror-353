from typing import Dict, Any, List, Optional
from ..base import LocalTool

class AskForClarificationTool(LocalTool):
    """Tool for requesting clarification from the user on specific details"""
    name: str = "ask_for_clarification"
    description: str = """Request clarification from the user on specific details.

Use this tool when you need more information to complete a task properly.
Presents a clear question to the user with optional context and response options.
Supports interactive console input with formatted display."""
    
    async def execute(self, question: str, context: Optional[str] = None, options: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Requests clarification from the user by presenting a specific question.
        
        Args:
            question: The specific question to ask the user
            context: Optional background information about the question
            options: Optional list of possible options for the user to choose from
            
        Returns:
            Dict with success status, message about the operation, and the user's response
        """
        try:
            # Validate input parameters
            if not question or not isinstance(question, str):
                return {
                    "success": False, 
                    "message": f"Invalid question: {question}"
                }
            
            # Validate context if provided
            if context is not None and not isinstance(context, str):
                return {
                    "success": False,
                    "message": f"Context must be a string: {context}"
                }
            
            # Validate options if provided
            if options is not None:
                if not isinstance(options, list):
                    return {
                        "success": False,
                        "message": f"Options must be a list: {options}"
                    }
                
                for option in options:
                    if not isinstance(option, str):
                        return {
                            "success": False,
                            "message": f"Each option must be a string: {option}"
                        }
            
            # Use console formatting similar to tool_executor's confirm step
            console = None
            try:
                # Try to import Rich console if available
                from rich.console import Console
                console = Console()
            except ImportError:
                console = None
                
            # Display header with formatting similar to tool_executor's confirm step
            if console:
                console.print("\n" + "!" * 60)
                console.print("!!" + " " * 56 + "!!")
                console.print("!!" + " 🔍 Clarification Requested ".center(56) + "!!")
                console.print("!!" + " " * 56 + "!!")
                console.print("!" * 60)
                console.print(f"\n❓ Question: [bold cyan]{question}[/bold cyan]")
                
                # Display context if provided
                if context:
                    console.print(f"\n📋 Context: {context}")
                
                # Display options if provided
                if options and len(options) > 0:
                    console.print("\n🔢 Options:")
                    for i, option in enumerate(options, 1):
                        console.print(f"  {i}. [bold yellow]{option}[/bold yellow]")
                
                console.print("\n" + "-" * 60)
                
                # Get user response using console interaction
                if options and len(options) > 0:
                    # If options are provided, suggest choosing by number
                    console.print("\n[bold green]💬 Enter your response (or enter a number to select an option):[/bold green]")
                    user_response = input("> ").strip()
                    
                    # Check if user entered a number to select an option
                    try:
                        option_index = int(user_response) - 1
                        if 0 <= option_index < len(options):
                            user_response = options[option_index]
                            console.print(f"\n[bold green]✅ Selected: \"{user_response}\"[/bold green]")
                        else:
                            console.print(f"\n[bold yellow]⚠️ Note: You entered a number ({user_response}) but it doesn't match any option.[/bold yellow]")
                    except ValueError:
                        # Not a number or not a valid option index, use the input as is
                        console.print(f"\n[bold green]✅ Response received[/bold green]")
                else:
                    # Simple text response
                    console.print("\n[bold green]💬 Enter your response:[/bold green]")
                    user_response = input("> ").strip()
                    console.print(f"\n[bold green]✅ Response received[/bold green]")
            else:
                # Fallback to standard terminal formatting
                print("\n" + "!" * 60)
                print("!!" + " " * 56 + "!!")
                print("!!" + " 🔍 Clarification Requested ".center(56) + "!!")
                print("!!" + " " * 56 + "!!")
                print("!" * 60)
                
                # Display the question
                print(f"\n❓ Question: \033[1;36m{question}\033[0m")
                
                # Display context if provided
                if context:
                    print(f"\n📋 Context: {context}")
                
                # Display options if provided
                if options and len(options) > 0:
                    print("\n🔢 Options:")
                    for i, option in enumerate(options, 1):
                        print(f"  {i}. \033[1;33m{option}\033[0m")
                
                print("\n" + "-" * 60)
                
                # Get user response using console interaction
                if options and len(options) > 0:
                    # If options are provided, suggest choosing by number
                    print("\n\033[1;32m💬 Enter your response (or enter a number to select an option):\033[0m")
                    user_response = input("\033[1;37m> \033[0m").strip()
                    
                    # Check if user entered a number to select an option
                    try:
                        option_index = int(user_response) - 1
                        if 0 <= option_index < len(options):
                            user_response = options[option_index]
                            print(f"\n\033[1;32m✅ Selected: \"{user_response}\"\033[0m")
                        else:
                            print(f"\n\033[1;33m⚠️ Note: You entered a number ({user_response}) but it doesn't match any option.\033[0m")
                    except ValueError:
                        # Not a number or not a valid option index, use the input as is
                        print(f"\n\033[1;32m✅ Response received\033[0m")
                else:
                    # Simple text response
                    print("\n\033[1;32m💬 Enter your response:\033[0m")
                    user_response = input("\033[1;37m> \033[0m").strip()
                    print(f"\n\033[1;32m✅ Response received\033[0m")
            
            # Ask if the user wants to provide additional context with their response
            if console:
                console.print("\n[bold yellow]想要提供额外的上下文或解释吗? (y/n):[/bold yellow]")
                wants_context = input("> ").strip().lower() == 'y'
            else:
                print("\n\033[1;33m想要提供额外的上下文或解释吗? (y/n):\033[0m")
                wants_context = input("\033[1;37m> \033[0m").strip().lower() == 'y'
            
            additional_context = ""
            if wants_context:
                if console:
                    console.print("\n[bold green]请输入额外的上下文或解释:[/bold green]")
                    additional_context = input("> ").strip()
                    console.print("\n[bold green]✅ 额外上下文已接收[/bold green]")
                else:
                    print("\n\033[1;32m请输入额外的上下文或解释:\033[0m")
                    additional_context = input("\033[1;37m> \033[0m").strip()
                    print("\n\033[1;32m✅ 额外上下文已接收\033[0m")
            
            # Return the user's response with optional additional context
            result = {
                "success": True,
                "message": "Received clarification from user",
                "question": question,
                "response": user_response
            }
            
            if additional_context:
                result["additional_context"] = additional_context
                
            return result
                
        except Exception as e:
            # Catch any unexpected errors
            if console:
                console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
            else:
                print(f"\n\033[1;31m❌ Error: {str(e)}\033[0m")
            return {
                "success": False,
                "message": f"Unexpected error requesting clarification: {str(e)}",
                "question": question
            }