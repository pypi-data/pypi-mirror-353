from typing import List, Optional
from termcolor import colored
from .agent import Agent

class Orchestrator:
    def __init__(self, agents: Optional[List] = None, analyser_agent=None, manager_agent=None, combine_mode: str = "concat", orchestra=False, api_key=None, model=None, provider="openai", workflow_mode="parallel"):
        """
        agents: list of Agent instances (specialists)
        analyser_agent: Agent instance that synthesizes all responses
        manager_agent: Agent instance that decomposes and aggregates tasks (for manager/worker mode)
        combine_mode: 'concat' (default) or 'vote' (future)
        orchestra: if True, auto-create default agents
        api_key, model, provider: used for auto-created agents
        workflow_mode: 'parallel', 'sequential', 'voting', or 'manager'
        """
        if orchestra:
            agents, analyser_agent, manager_agent = self._create_default_agents(api_key, model, provider)
        self.agents = agents or []
        self.analyser_agent = analyser_agent
        self.manager_agent = manager_agent
        self.combine_mode = combine_mode
        self.workflow_mode = workflow_mode
        # Auto-enable chain-of-thought for all agents
        for agent in self.agents:
            agent.cot = True
        if self.analyser_agent:
            self.analyser_agent.cot = True
        if self.manager_agent:
            self.manager_agent.cot = True

    def _create_default_agents(self, api_key, model, provider):
        research_agent = Agent(
            name="Researcher",
            version="1.0",
            description="Expert at finding and explaining information.",
            context="You are a research expert. Answer questions with detailed, well-sourced information.",
            provider=provider,
            api_key=api_key,
            model=model
        )
        summarizer_agent = Agent(
            name="Summarizer",
            version="1.0",
            description="Expert at summarizing information clearly.",
            context="You are a world-class summarizer. Summarize information in a concise, clear way.",
            provider=provider,
            api_key=api_key,
            model=model
        )
        fact_checker_agent = Agent(
            name="FactChecker",
            version="1.0",
            description="Expert at checking facts and verifying claims.",
            context="You are a fact checker. Verify the accuracy of claims and provide supporting evidence.",
            provider=provider,
            api_key=api_key,
            model=model
        )
        analyser_agent = Agent(
            name="Analyser",
            version="1.0",
            description="Expert at synthesizing and concluding from multiple expert responses.",
            context="You are an expert at analyzing multiple expert responses and providing a clear, reasoned final conclusion.",
            provider=provider,
            api_key=api_key,
            model=model
        )
        manager_agent = Agent(
            name="Manager",
            version="1.0",
            description="Expert at decomposing tasks and aggregating results from worker agents.",
            context="You are a manager agent. Decompose the user's query into subtasks, assign them to workers, and aggregate the results into a final answer.",
            provider=provider,
            api_key=api_key,
            model=model
        )
        return [research_agent, summarizer_agent, fact_checker_agent], analyser_agent, manager_agent

    def ask_all(self, user_input, history=None):
        responses = []
        for agent in self.agents:
            messages = (history or []) + [{"role": "user", "content": user_input}]
            try:
                response = agent.chat(messages)
                responses.append((agent.name, response))
            except Exception as e:
                responses.append((agent.name, f"Error: {e}"))
        return responses

    def sequential_workflow(self, user_input, history=None):
        responses = []
        prev_output = user_input
        messages = (history or [])
        for agent in self.agents:
            agent_input = messages + [{"role": "user", "content": prev_output}]
            try:
                response = agent.chat(agent_input)
                responses.append((agent.name, response))
                prev_output = response  # Pass output to next agent
                messages = messages + [{"role": "assistant", "content": response}]
            except Exception as e:
                responses.append((agent.name, f"Error: {e}"))
                prev_output = f"Error: {e}"
        return responses

    def voting_workflow(self, user_input, history=None):
        responses = self.ask_all(user_input, history)
        # The analyser agent acts as the voter/consensus builder
        summary = "\n\n".join([f"[{name}]\n{resp}" for name, resp in responses])
        prompt = (
            f"The following are responses from multiple expert agents to the user's question: '{user_input}'.\n"
            f"Please select the best answer or summarize the consensus.\n"
            f"\n{summary}\n"
        )
        messages = (history or []) + [{"role": "user", "content": prompt}]
        try:
            final = self.analyser_agent.chat(messages)
        except Exception as e:
            final = f"Error from analyser agent: {e}"
        return responses, final

    def manager_workflow(self, user_input, history=None):
        # The manager agent decomposes the task and assigns to workers
        prompt = (
            f"Decompose the following user query into subtasks, assign each to a worker agent (Researcher, Summarizer, FactChecker), and aggregate their results into a final answer.\n"
            f"User query: {user_input}"
        )
        messages = (history or []) + [{"role": "user", "content": prompt}]
        try:
            final = self.manager_agent.chat(messages)
        except Exception as e:
            final = f"Error from manager agent: {e}"
        return final

    def analyse(self, user_input, agent_responses, history=None):
        if not self.analyser_agent:
            return None
        summary = "\n\n".join([f"[{name}]\n{resp}" for name, resp in agent_responses])
        prompt = (
            f"The following are responses from multiple expert agents to the user's question: '{user_input}'.\n"
            f"Please analyze their answers, synthesize the information, and provide a clear, reasoned final conclusion.\n"
            f"\n{summary}\n"
        )
        messages = (history or []) + [{"role": "user", "content": prompt}]
        try:
            conclusion = self.analyser_agent.chat(messages)
        except Exception as e:
            conclusion = f"Error from analyser agent: {e}"
        return conclusion

    def chat_loop(self):
        print(colored(f"\nWelcome to Multi-Agent Orchestrator! Workflow mode: {self.workflow_mode}. Type /exit to quit.\n", "cyan"))
        history = []
        while True:
            user_input = input(colored("You: ", "green"))
            if user_input.strip().lower() == "/exit":
                print(colored("Exiting orchestrator chat. Goodbye!", "yellow"))
                break
            if self.workflow_mode == "parallel":
                responses = self.ask_all(user_input, history)
                print(colored(f"\n[Agent Responses]", "magenta"))
                for name, resp in responses:
                    print(colored(f"[{name}]\n{resp}\n", "magenta"))
                final_conclusion = self.analyse(user_input, responses, history)
                if final_conclusion:
                    print(colored(f"\n[Analyser Agent Conclusion]\n{final_conclusion}\n", "blue"))
                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "assistant", "content": final_conclusion})
                else:
                    combined = "\n\n".join([f"[{name}]\n{resp}" for name, resp in responses])
                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "assistant", "content": combined})
            elif self.workflow_mode == "sequential":
                responses = self.sequential_workflow(user_input, history)
                print(colored(f"\n[Sequential Agent Responses]", "magenta"))
                for name, resp in responses:
                    print(colored(f"[{name}]\n{resp}\n", "magenta"))
                final_conclusion = self.analyse(user_input, responses, history)
                if final_conclusion:
                    print(colored(f"\n[Analyser Agent Conclusion]\n{final_conclusion}\n", "blue"))
                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "assistant", "content": final_conclusion})
                else:
                    combined = "\n\n".join([f"[{name}]\n{resp}" for name, resp in responses])
                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "assistant", "content": combined})
            elif self.workflow_mode == "voting":
                responses, final = self.voting_workflow(user_input, history)
                print(colored(f"\n[Agent Responses]", "magenta"))
                for name, resp in responses:
                    print(colored(f"[{name}]\n{resp}\n", "magenta"))
                print(colored(f"\n[Voter/Analyser Agent Decision]\n{final}\n", "blue"))
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": final})
            elif self.workflow_mode == "manager":
                final = self.manager_workflow(user_input, history)
                print(colored(f"\n[Manager/Worker Orchestration]\n{final}\n", "blue"))
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": final})
            else:
                print(colored(f"Workflow mode '{self.workflow_mode}' not implemented.", "red")) 