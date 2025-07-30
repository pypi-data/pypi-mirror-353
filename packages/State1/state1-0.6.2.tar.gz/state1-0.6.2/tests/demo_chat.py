from state1 import Agent

# Create the agent
agent = Agent(
    name="Demo Agent",
    version="1.0",
    description="An example AI agent",
    context="Sample Context",
    provider="openai",  # or "openrouter"
    api_key="$YourOpenAIKey",
    model="gpt-3.5-turbo"  # or e.g. "google/gemini-2.5-pro-preview" for OpenRouter
)

# Prepare a chat message
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! What can you do?"}
]

# Chat with the agent
response = agent.chat(messages)
print("Agent:", response)
