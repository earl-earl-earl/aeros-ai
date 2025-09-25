from google import genai
from google.genai import types
from dotenv import load_dotenv
from termcolor import colored, cprint
from colorama import init as colorama_init
import re
import textwrap
import time

load_dotenv('.env.local')

# Initialize colorama so ANSI colors work correctly on Windows consoles
colorama_init()

MODEL = "gemini-2.5-flash"
NAME = "Aeros AI"
BEHAVIOR = f"You are {NAME}, a helpful, warm, and friendly AI assistant that helps users with their queries."

client = genai.Client()

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool],
    system_instruction=BEHAVIOR,
)

chat = client.chats.create(
    model=MODEL,
    config=config
)

def show_thinking():
    """Show thinking animation"""
    print(colored("Thinking", "dark_grey", attrs=["dark"]), end="", flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(colored(".", "dark_grey", attrs=["dark"]), end="", flush=True)
    
def clear_thinking():
    """Clear the thinking line"""
    # Move cursor to beginning of line and clear it
    print("\r" + " " * 15 + "\r", end="", flush=True)

def format_response(text):
    """
    Format AI response with enhanced styling:
    - **text** becomes bold
    - *text* becomes underlined
    - Headers with # become larger/bold
    - Code blocks get special formatting
    """
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Handle headers (# ## ###)
        if line.strip().startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()
            if level == 1:
                # Large header
                formatted_lines.append(colored(f"\n{'=' * len(header_text)}", "cyan", attrs=["bold"]))
                formatted_lines.append(colored(header_text.upper(), "cyan", attrs=["bold"]))
                formatted_lines.append(colored(f"{'=' * len(header_text)}", "cyan", attrs=["bold"]))
            elif level == 2:
                formatted_lines.append(colored(f"\n{header_text}", "yellow", attrs=["bold"]))
                formatted_lines.append(colored("-" * len(header_text), "yellow"))
            else:
                formatted_lines.append(colored(f"\n{header_text}", "magenta", attrs=["bold"]))
        
        # Handle code blocks (```code```)
        elif line.strip().startswith('```') and line.strip().endswith('```'):
            code = line.strip()[3:-3]
            formatted_lines.append(colored(f"  📝 {code}", "green", attrs=["reverse"]))
        
        # Handle inline code (`code`)
        elif '`' in line:
            # Replace `code` with highlighted version
            def replace_code(match):
                return colored(match.group(1), "green", attrs=["reverse"])
            line = re.sub(r'`([^`]+)`', replace_code, line)
            formatted_lines.append(line)
        
        else:
            # Handle bold **text** (remove ** and make bold)
            if '**' in line:
                def replace_bold(match):
                    return colored(match.group(1), attrs=["bold"])
                line = re.sub(r'\*\*([^*]+?)\*\*', replace_bold, line)
            
            # Handle italic/underline *text* (but not if it's part of **)
            if '*' in line and '**' not in line:
                def replace_italic(match):
                    return colored(match.group(1), attrs=["underline"])
                line = re.sub(r'\*([^*]+?)\*', replace_italic, line)
            
            # Handle bullet points
            if line.strip().startswith(('-', '•', '*')) and not line.strip().startswith('**'):
                bullet_text = line.strip()[1:].strip()
                formatted_lines.append(colored("  • ", "blue", attrs=["bold"]) + bullet_text)
            
            # Handle numbered lists
            elif re.match(r'^\s*\d+\.', line):
                formatted_lines.append(colored(line[:line.find('.')+1], "blue", attrs=["bold"]) + line[line.find('.')+1:])
            
            # Regular text with word wrapping for long lines
            else:
                if len(line) > 80:
                    wrapped = textwrap.fill(line, width=80, initial_indent="", subsequent_indent="  ")
                    formatted_lines.append(wrapped)
                else:
                    formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def print_ai_response(text):
    """Print AI response without additional formatting; colors for labels remain."""
    # Print with AI name styling (colors left untouched)
    cprint("\nAeros AI:", "green", attrs=["bold"], end=" ")

    # Print the raw response text (no markdown/code styling applied)
    print(text)
    print()

def send_message(prompt):
    response = chat.send_message(prompt)
    return response.text

def main():
  # Enhanced welcome message
  cprint("Welcome to Aeros AI!", "green", attrs=["bold"])
  cprint("Start typing below to start chatting! Ctrl+C to quit.", "yellow")
  print()
  
  while True:
    # Enhanced user prompt
    try:
        user_input = input(colored("> ", "blue", attrs=["bold"]))
    except (KeyboardInterrupt, EOFError):
        print()
        print_ai_response(send_message("Goodbye!"))
        break
    
    if not user_input.strip():
      cprint("Please enter a message!", "red")
      continue
      
    try:
      # Show thinking indicator
      show_thinking()
      
      # Generate response
      response = send_message(user_input)

      # Clear thinking indicator
      clear_thinking()
      
      # Print AI response
      print_ai_response(response)
    except Exception as e:
      clear_thinking()
      cprint(f"Error: {str(e)}", "red", attrs=["bold"])
      print()
    
if __name__ == "__main__":
  main()