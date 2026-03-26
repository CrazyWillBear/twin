from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.markdown import Markdown

from agent.Agent import Agent
from agent.tools.search import duckduckgo_search

AGENT_NAME = "Twin"


console = Console()


def main():
    tools = [duckduckgo_search]
    agent = Agent(AGENT_NAME, tools=tools)

    print(f"{AGENT_NAME} is ready. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        reply = agent.invoke(user_input)
        content = reply.content if reply else "(no response)"
        console.print(f"\n{AGENT_NAME}:", style="bold")
        console.print(Markdown(content))
        print()


if __name__ == "__main__":
    main()
