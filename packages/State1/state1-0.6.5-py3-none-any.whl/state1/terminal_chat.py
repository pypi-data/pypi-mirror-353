import uuid
import os
import json
from state1 import Agent
import shutil

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
    rag = input("Enable RAG (document retrieval)? (y/n) [n]: ").lower().startswith("y")
    websearch = input("Enable web search? (y/n) [n]: ").lower().startswith("y")
    cot = input("Enable Chain-of-Thought reasoning? (y/n) [n]: ").lower().startswith("y")
    auth = input("Require authentication? (y/n) [n]: ").lower().startswith("y")
    memory = input("Enable persistent memory? (y/n) [n]: ").lower().startswith("y")
    actions = input("Enable actions (email/API)? (y/n) [n]: ").lower().startswith("y")
    smtp_config = {}
    apis = {}
    if actions:
        if input("Add SendEmailAction? (y/n) [n]: ").lower().startswith("y"):
            smtp_config = {
                "smtp_server": input("SMTP server: "),
                "smtp_port": int(input("SMTP port: ") or 465),
                "sender_email": input("Sender email: "),
                "sender_password": input("Sender app password: ")
            }
        if input("Add FetchAPIAction? (y/n) [n]: ").lower().startswith("y"):
            while True:
                api_name = input("API name (or blank to finish): ")
                if not api_name:
                    break
                url = input(f"URL for {api_name}: ")
                apis[api_name] = {"url": url, "headers": {}}
    agent = Agent(
        name=name,
        provider=provider,
        api_key=api_key,
        model=model,
        context=context,
        rag=rag,
        websearch=websearch,
        cot=cot,
        auth=auth,
        memory=memory,
        smtp_config=smtp_config,
        apis=apis
    )
    if actions:
        from state1.actions import SendEmailAction, FetchAPIAction
        if smtp_config:
            agent.register_action(SendEmailAction())
        if apis:
            agent.register_action(FetchAPIAction())
    save_agent_to_file(agent)
    print(f"Created agent '{name}' with ID: {agent.agent_id[:8]}")
    if rag and input("Add a document now? (y/n) [n]: ").lower().startswith("y"):
        doc_path = input("Path to document (txt/pdf/docx): ")
        try:
            agent.add_document(doc_path)
        except Exception as e:
            print(f"Failed to add document: {e}")
    return agent

def print_agents_summary(agents):
    print("\nAvailable agents:")
    for idx, (aid, agent) in enumerate(agents.items(), 1):
        features = []
        if getattr(agent, 'websearch', False): features.append('websearch')
        if getattr(agent, 'rag', False): features.append('rag')
        if getattr(agent, 'cot', False): features.append('cot')
        if getattr(agent, 'auth', False): features.append('auth')
        if getattr(agent, 'memory', False): features.append('memory')
        if getattr(agent, 'smtp_config', {}):
            if agent.smtp_config: features.append('actions')
        print(f"  [{idx}] {agent.name} (ID: {aid[:8]}) | Features: {', '.join(features) if features else 'none'}")


def debug_print_agents(agents):
    print("\n[DEBUG] Agent configs:")
    for aid, agent in agents.items():
        print(f"--- {agent.name} (ID: {aid[:8]}) ---")
        print(json.dumps({
            'name': agent.name,
            'auth': getattr(agent, 'auth', False),
            'rag': getattr(agent, 'rag', False),
            'websearch': getattr(agent, 'websearch', False),
            'cot': getattr(agent, 'cot', False),
            'memory': getattr(agent, 'memory', False),
            'smtp_config': getattr(agent, 'smtp_config', {}),
            'apis': getattr(agent, 'apis', {})
        }, indent=2))


def find_default_agent_id(agents):
    for aid, agent in agents.items():
        if getattr(agent, 'name', None) == "Default Agent":
            return aid
    # fallback: return first agent
    return next(iter(agents))

def clean_agents_dir():
    if os.path.exists(AGENTS_DIR):
        for fname in os.listdir(AGENTS_DIR):
            if fname.endswith('.json'):
                os.remove(os.path.join(AGENTS_DIR, fname))

def main():
    agents = load_agents_from_files()
    # Startup clean prompt if agents exist
    if agents:
        print_agents_summary(agents)
        debug_print_agents(agents)
        # Failsafe: check for any non-Auth agent with auth=True
        non_auth_with_auth = [agent for agent in agents.values() if agent.name != "Auth Demo Agent" and getattr(agent, 'auth', False)]
        if non_auth_with_auth:
            print("[WARNING] One or more non-Auth agents have auth=True. This is likely a bug or stale agent file.")
        print("\nYou have existing agents. Would you like to delete all agents and start fresh with the latest showcase agents? (y/n)")
        resp = input("> ").strip().lower()
        if resp == "y":
            clean_agents_dir()
            agents = {}
            print("All agents deleted. Recreating showcase agents...")
    if not agents:
        # --- Minimal Default Agent ---
        default_agent = Agent(
            name="Default Agent",
            version="1.0",
            description="Minimal default agent (just LLM chat).",
            context="You are a helpful assistant.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            rag=False,
            websearch=False,
            cot=False,
            auth=False,
            memory=False
        )
        save_agent_to_file(default_agent)
        agents[default_agent.agent_id] = default_agent

        # --- Web Search Agent ---
        web_agent = Agent(
            name="Web Search Agent",
            version="1.0",
            description="Agent with web search enabled.",
            context="You are a helpful assistant with access to web search.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            websearch=True,
            rag=False,
            cot=False,
            auth=False,
            memory=False
        )
        save_agent_to_file(web_agent)
        agents[web_agent.agent_id] = web_agent

        # --- RAG Agent ---
        rag_agent = Agent(
            name="RAG Agent",
            version="1.0",
            description="Agent with Retrieval-Augmented Generation (RAG) enabled.",
            context="You are a helpful assistant that can answer questions using uploaded documents.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            rag=True,
            websearch=False,
            cot=False,
            auth=False,
            memory=False
        )
        save_agent_to_file(rag_agent)
        agents[rag_agent.agent_id] = rag_agent
        print(f"[RAG Agent] You can add a document with: agent.add_document('path/to/file') in Python, or extend the agent in code.")

        # --- CoT Agent ---
        cot_agent = Agent(
            name="CoT Agent",
            version="1.0",
            description="Agent with Chain-of-Thought reasoning enabled.",
            context="You are a helpful assistant. Please reason step by step before answering.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            cot=True,
            rag=False,
            websearch=False,
            auth=False,
            memory=False
        )
        save_agent_to_file(cot_agent)
        agents[cot_agent.agent_id] = cot_agent

        # --- Actions Agent ---
        from state1.actions import SendEmailAction, FetchAPIAction
        actions_agent = Agent(
            name="Actions Agent",
            version="1.0",
            description="Agent with real-world actions (email, API fetch) enabled.",
            context="You are a helpful assistant that can send emails and fetch API data.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-4o",
            smtp_config={
                "smtp_server": "smtp.example.com",
                "smtp_port": 465,
                "sender_email": "your@email.com",
                "sender_password": "your_app_password"
            },
            apis={
                "github": {"url": "https://api.github.com"},
                "weather": {"url": "https://wttr.in", "headers": {}}
            },
            rag=False,
            websearch=False,
            cot=False,
            auth=False,
            memory=False
        )
        actions_agent.register_action(SendEmailAction())
        actions_agent.register_action(FetchAPIAction())
        save_agent_to_file(actions_agent)
        agents[actions_agent.agent_id] = actions_agent

        # --- Auth Demo Agent ---
        auth_agent = Agent(
            name="Auth Demo Agent",
            version="1.0",
            description="Demo agent with authentication and persistent memory.",
            context="You are a helpful assistant that can answer questions. Your name is AuthBot.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            auth=True,
            memory=True,
            rag=False,
            websearch=False,
            cot=False
        )
        save_agent_to_file(auth_agent)
        agents[auth_agent.agent_id] = auth_agent

        print("\nCreated showcase agents:")
        for aid, agent in agents.items():
            print(f"  {aid[:8]}: {agent.name}")

    # Print all agents and prompt user to select one
    print_agents_summary(agents)
    debug_print_agents(agents)
    agent_ids = list(agents.keys())
    agent_names = [agent.name for agent in agents.values()]
    print("\nSelect an agent to start:")
    print("  Enter the number or agent ID (or press Enter for Default Agent). Type /new to create your own agent.")
    selection = input("> ").strip()
    if not selection:
        current_agent_id = find_default_agent_id(agents)
    elif selection.lower() == "/new":
        new_agent = create_agent_interactive()
        agents[new_agent.agent_id] = new_agent
        current_agent_id = new_agent.agent_id
    else:
        # Try to match by number or ID
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(agent_ids):
                current_agent_id = agent_ids[idx]
            else:
                print("Invalid selection. Using Default Agent.")
                current_agent_id = find_default_agent_id(agents)
        except ValueError:
            # Try to match by agent ID prefix
            found = None
            for aid in agent_ids:
                if aid.startswith(selection):
                    found = aid
                    break
            if found:
                current_agent_id = found
            else:
                print("Invalid selection. Using Default Agent.")
                current_agent_id = find_default_agent_id(agents)
    print(f"\nUsing agent: {agents[current_agent_id].name} (ID: {current_agent_id[:8]})")
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
  /orchestrator        Create and launch an orchestrator demo agent
  /debug               Print all agent configs
  /exit                Exit the chat
  /help                Show this help message
""")
            continue
        elif user_input.strip().lower() == "/list":
            print_agents_summary(agents)
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
            current_agent_id = new_agent.agent_id
            print(f"Switched to new agent: {new_agent.name} (ID: {new_agent.agent_id[:8]})")
            history = [
                {"role": "system", "content": agents[current_agent_id].context}
            ]
            continue
        elif user_input.strip().lower() == "/orchestrator":
            from state1.orchestrator import Orchestrator
            api_key = input("API key for orchestrator agents: ")
            model = input("Model [gpt-3.5-turbo]: ") or "gpt-3.5-turbo"
            workflow_mode = input("Workflow mode (parallel/sequential/voting/manager) [manager]: ") or "manager"
            orchestrator = Orchestrator(
                orchestra=True,
                api_key=api_key,
                model=model,
                workflow_mode=workflow_mode
            )
            orchestrator.chat_loop()
            continue
        elif user_input.strip().lower() == "/debug":
            debug_print_agents(agents)
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