import uuid
import os
import json
from state1 import Agent

AGENTS_DIR = "agents"

def save_agent_to_file(agent):
    if not os.path.exists(AGENTS_DIR):
        os.makedirs(AGENTS_DIR)
    agent_data = {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "version": agent.version,
        "description": agent.description,
        "context": agent.context,
        "provider": agent.provider,
        "api_key": agent.api_key,
        "model": agent.model,
        "rag": agent.rag,
        "websearch": agent.websearch,
        "cot": agent.cot,
        "auth": agent.auth,
        "memory": agent.memory,
        "smtp_config": agent.smtp_config,
        "apis": agent.apis
    }
    with open(os.path.join(AGENTS_DIR, f"{agent.agent_id}.json"), "w") as f:
        json.dump(agent_data, f, indent=2)

def load_agents_from_files():
    agents = {}
    if not os.path.exists(AGENTS_DIR):
        return agents
    for fname in os.listdir(AGENTS_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(AGENTS_DIR, fname), "r") as f:
                data = json.load(f)
                agent = Agent(
                    name=data.get("name"),
                    version=data.get("version", "1.0"),
                    description=data.get("description"),
                    context=data.get("context"),
                    provider=data.get("provider", "openai"),
                    api_key=data.get("api_key"),
                    model=data.get("model"),
                    rag=data.get("rag", False),
                    websearch=data.get("websearch", False),
                    cot=data.get("cot", False),
                    auth=data.get("auth", False),
                    memory=data.get("memory", False),
                    smtp_config=data.get("smtp_config", {}),
                    apis=data.get("apis", {}),
                    agent_id=data.get("agent_id")
                )
                agents[agent.agent_id] = agent
    return agents

def create_agent_interactive():
    name = input("Agent name: ")
    provider = input("Provider (openai/openrouter) [openai]: ") or "openai"
    api_key = input("API key: ")
    model = input("Model [gpt-3.5-turbo]: ") or "gpt-3.5-turbo"
    context = input("Context [You are a helpful assistant.]: ") or "You are a helpful assistant."
    agent = Agent(
        name=name,
        provider=provider,
        api_key=api_key,
        model=model,
        context=context
    )
    save_agent_to_file(agent)
    return agent

def main():
    agents = load_agents_from_files()
    if not agents:
        # Create a default agent if none exist
        default_agent = Agent(
            name="Terminal Agent",
            version="1.0",
            description="Chat with your AI agent in the terminal!",
            context="You are a helpful assistant.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            websearch=False,
            cot=True
        )
        agents[default_agent.agent_id] = default_agent
        save_agent_to_file(default_agent)
        print(f"\nCreated default agent with ID: {default_agent.agent_id}")
        current_agent_id = default_agent.agent_id
    else:
        # Use the first agent as default
        current_agent_id = next(iter(agents))
        print(f"\nLoaded {len(agents)} agent(s) from {AGENTS_DIR}/. Default: {current_agent_id}")
    print("Type /help for commands.")
    history = [
        {"role": "system", "content": agents[current_agent_id].context}
    ]
    while True:
        prompt = f"[Agent {current_agent_id[:8]}] You: "
        user_input = input(prompt)
        if user_input.strip().lower() == "/exit":
            print("Exiting chat. Goodbye!")
            break
        elif user_input.strip().lower() == "/help":
            print("""
Commands:
  /list                List all agents and their IDs
  /switch <agent_id>   Switch to another agent by ID
  /new                 Create a new agent interactively
  /exit                Exit the chat
  /help                Show this help message
""")
            continue
        elif user_input.strip().lower() == "/list":
            print("Agents:")
            for aid, agent in agents.items():
                print(f"  {aid[:8]}: {agent.name}")
            continue
        elif user_input.strip().startswith("/switch"):
            parts = user_input.strip().split()
            if len(parts) != 2:
                print("Usage: /switch <agent_id>")
                continue
            switch_id = parts[1]
            found = None
            for aid in agents:
                if aid.startswith(switch_id):
                    found = aid
                    break
            if found:
                current_agent_id = found
                print(f"Switched to agent {found[:8]}: {agents[found].name}")
                history = [
                    {"role": "system", "content": agents[current_agent_id].context}
                ]
            else:
                print(f"Agent ID {switch_id} not found.")
            continue
        elif user_input.strip().lower() == "/new":
            new_agent = create_agent_interactive()
            agents[new_agent.agent_id] = new_agent
            print(f"Created new agent with ID: {new_agent.agent_id[:8]}")
            continue
        # Normal chat
        agent = agents[current_agent_id]
        messages = history.copy()
        messages.append({"role": "user", "content": user_input})
        try:
            response = agent.chat(messages)
            print(f"{agent.name}: {response}")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 