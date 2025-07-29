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
        # --- Default ActionDemo Agent ---
        from state1.actions import SendEmailAction, FetchAPIAction
        action_agent = Agent(
            name="ActionDemo Agent",
            version="1.0",
            description="Demo agent with real-world actions (email, API fetch).",
            context="You are a helpful assistant that can also perform actions.",
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
            }
        )
        action_agent.register_action(SendEmailAction())
        action_agent.register_action(FetchAPIAction())
        save_agent_to_file(action_agent)
        agents[action_agent.agent_id] = action_agent

        # --- Default RAG Agent ---
        rag_agent = Agent(
            name="RAG Agent",
            version="1.0",
            description="Demo agent with document RAG and embeddings.",
            context="You are a helpful assistant that can answer questions using uploaded documents.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            rag=True
        )
        # Optionally add a default document (uncomment if example.pdf exists)
        # rag_agent.add_document("example.pdf")
        save_agent_to_file(rag_agent)
        agents[rag_agent.agent_id] = rag_agent

        # --- Default Auth Agent ---
        auth_agent = Agent(
            name="AuthTest Agent",
            version="1.0",
            description="Demo agent with authentication and persistent memory.",
            context="You are a helpful assistant that can answer questions. Your name is AuthBot.",
            provider="openai",
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-3.5-turbo",
            auth=True,
            memory=True
        )
        save_agent_to_file(auth_agent)
        agents[auth_agent.agent_id] = auth_agent

        # --- Default Orchestrator Demo (as a pseudo-agent) ---
        # Save orchestrator config as a pseudo-agent for listing/switching
        orchestrator_config = {
            "agent_id": "orchestrator-demo",
            "name": "Orchestrator Demo",
            "version": "1.0",
            "description": "Multi-agent orchestrator demo (manager workflow)",
            "context": "Multi-agent orchestrator. Try parallel, sequential, voting, or manager workflows.",
            "provider": "openai",
            "api_key": "YOUR_OPENAI_API_KEY",
            "model": "gpt-3.5-turbo",
            "orchestrator": True,
            "workflow_mode": "manager"
        }
        with open(os.path.join(AGENTS_DIR, f"{orchestrator_config['agent_id']}.json"), "w") as f:
            json.dump(orchestrator_config, f, indent=2)
        agents[orchestrator_config["agent_id"]] = orchestrator_config

        print("\nCreated default agents:")
        for aid, agent in agents.items():
            print(f"  {aid[:8]}: {agent['name'] if isinstance(agent, dict) else agent.name}")
        current_agent_id = next(iter(agents))
    else:
        current_agent_id = next(iter(agents))
        print(f"\nLoaded {len(agents)} agent(s) from {AGENTS_DIR}/. Default: {current_agent_id}")
    print("Type /help for commands.")
    history = [
        {"role": "system", "content": agents[current_agent_id].context if not isinstance(agents[current_agent_id], dict) else agents[current_agent_id]["context"]}
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
                print(f"  {aid[:8]}: {agent['name'] if isinstance(agent, dict) else agent.name}")
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
                print(f"Switched to agent {found[:8]}: {agents[found]['name'] if isinstance(agents[found], dict) else agents[found].name}")
                history = [
                    {"role": "system", "content": agents[current_agent_id].context if not isinstance(agents[current_agent_id], dict) else agents[current_agent_id]["context"]}
                ]
            else:
                print(f"Agent ID {switch_id} not found.")
            continue
        elif user_input.strip().lower() == "/new":
            new_agent = create_agent_interactive()
            agents[new_agent.agent_id] = new_agent
            print(f"Created new agent with ID: {new_agent.agent_id[:8]}")
            continue
        # Normal chat or orchestrator
        agent = agents[current_agent_id]
        if isinstance(agent, dict) and agent.get("orchestrator"):
            from state1.orchestrator import Orchestrator
            orchestrator = Orchestrator(
                orchestra=True,
                api_key=agent["api_key"],
                model=agent["model"],
                workflow_mode=agent.get("workflow_mode", "manager")
            )
            orchestrator.chat_loop()
            continue
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