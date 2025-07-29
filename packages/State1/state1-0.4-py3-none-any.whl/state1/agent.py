import os
import json
import sqlite3
import bcrypt
from datetime import datetime
from openai import OpenAI
from typing import List, Dict
import uuid

try:
    from termcolor import colored
except ImportError:
    def colored(text, color):
        return text

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

import PyPDF2
import docx

from state1.actions import Action

DEFAULT_COT_INSTRUCTION = (
    "Let's think step by step. Please show your detailed reasoning process, and make sure your reasoning is at least 500 tokens before giving the final answer. "
    "At the end, provide your final answer clearly labeled as 'Final Answer:'."
)

DB_FILE = "state1_users.db"
MEMORY_DIR = "user_memory"

class Agent:
    def __init__(self, name, version="1.0", description=None, context=None, provider="openai", rag=False, websearch=False, cot=False, ui=None, actions=None, action_context=None, api_key=None, model=None, cot_instruction=None, auth=False, memory=False, smtp_config=None, apis=None, agent_id=None):
        self.name = name
        self.version = version
        self.description = description
        self.context = context
        self.provider = provider.lower()
        self.rag = rag
        self.websearch = websearch
        self.cot = cot
        self.cot_instruction = cot_instruction or DEFAULT_COT_INSTRUCTION
        self.ui = ui
        self.actions = actions
        self.action_context = action_context
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or ("gpt-3.5-turbo" if self.provider == "openai" else "google/gemini-2.5-pro-preview")
        self.auth = auth
        self.memory = memory
        self.user = None
        self.session_id = None
        self.user_memory = []
        self.registered_actions = {}
        self.smtp_config = smtp_config or {}
        self.apis = apis or {}
        self.agent_id = agent_id or str(uuid.uuid4())
        self._ensure_memory_dir()
        self.client = self._init_client()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.chroma_client.get_or_create_collection(
            name="state1_docs",
            embedding_function=self.embedding_function
        )
        if self.auth:
            self._init_db()
            self._auth_flow()
        if self.memory and self.user:
            self._load_user_memory()

    def _ensure_memory_dir(self):
        if not os.path.exists(MEMORY_DIR):
            os.makedirs(MEMORY_DIR)

    def _init_db(self):
        if not os.path.exists(DB_FILE):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )''')
            c.execute('''CREATE TABLE sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
            c.execute('''CREATE TABLE memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                memory_json TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
            conn.commit()
            conn.close()

    def _auth_flow(self):
        print(colored("Authentication required. Please log in or sign up with your email.", "yellow"))
        while True:
            email = input("Email: ").strip().lower()
            user = self._get_user_by_email(email)
            if user:
                password = input("Password: ").strip()
                if bcrypt.checkpw(password.encode(), user[2].encode()):
                    print(colored(f"Welcome back, {email}!", "cyan"))
                    self.user = email
                    self.user_id = user[0]
                    self.session_id = self._create_session(self.user_id)
                    break
                else:
                    print(colored("Incorrect password. Try again.", "red"))
            else:
                print(colored("Email not found. Would you like to sign up? (y/n)", "yellow"))
                if input().strip().lower() == "y":
                    password = input("Choose a password: ").strip()
                    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    self.user_id = self._create_user(email, password_hash)
                    print(colored(f"User {email} created. Please log in.", "green"))
                else:
                    continue

    def _get_user_by_email(self, email):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()
        return user

    def _create_user(self, email, password_hash):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                  (email, password_hash, datetime.utcnow().isoformat()))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id

    def _create_session(self, user_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO sessions (user_id, created_at, last_active) VALUES (?, ?, ?)",
                  (user_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
        conn.commit()
        session_id = c.lastrowid
        conn.close()
        return session_id

    def _memory_file(self):
        if not self.user:
            return None
        return os.path.join(MEMORY_DIR, f"{self.user}_memory.json")

    def _load_user_memory(self):
        if self.auth:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT memory_json FROM memory WHERE user_id=?", (self.user_id,))
            row = c.fetchone()
            if row and row[0]:
                self.user_memory = json.loads(row[0])
            else:
                self.user_memory = []
            conn.close()
        else:
            mem_file = self._memory_file()
            if mem_file and os.path.exists(mem_file):
                with open(mem_file, "r") as f:
                    self.user_memory = json.load(f)
            else:
                self.user_memory = []

    def _save_user_memory(self):
        if self.auth:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            mem_json = json.dumps(self.user_memory)
            c.execute("SELECT id FROM memory WHERE user_id=?", (self.user_id,))
            row = c.fetchone()
            if row:
                c.execute("UPDATE memory SET memory_json=? WHERE user_id=?", (mem_json, self.user_id))
            else:
                c.execute("INSERT INTO memory (user_id, memory_json) VALUES (?, ?)", (self.user_id, mem_json))
            conn.commit()
            conn.close()
        else:
            mem_file = self._memory_file()
            if mem_file:
                with open(mem_file, "w") as f:
                    json.dump(self.user_memory, f)

    def _init_client(self):
        if self.provider == "openrouter":
            return OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
        elif self.provider == "openai":
            return OpenAI(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(self, messages: List[Dict], extra_headers=None, extra_body=None):
        # OpenAI function calling support
        function_schemas = [a.get_openai_schema() for a in self.registered_actions.values() if a.get_openai_schema()]
        if self.provider in ["openai", "openrouter"] and function_schemas:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=function_schemas,
                function_call="auto"
            )
            message = completion.choices[0].message
            # If function_call, execute the action and continue
            if hasattr(message, "function_call") and message.function_call:
                func_name = message.function_call.name
                args = message.function_call.arguments
                import json as _json
                try:
                    func_args = _json.loads(args) if isinstance(args, str) else args
                except Exception:
                    func_args = {}
                result = self.run_action(func_name, **func_args)
                # Continue conversation with function result
                messages.append({"role": "assistant", "content": None, "function_call": {"name": func_name, "arguments": args}})
                messages.append({"role": "function", "name": func_name, "content": str(result)})
                completion2 = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    functions=function_schemas,
                    function_call="none"
                )
                return completion2.choices[0].message.content
            return message.content
        # Fallback: no function calling
        if self.provider == "openrouter":
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_headers=extra_headers or {},
                extra_body=extra_body or {}
            )
        else:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
        return completion.choices[0].message.content

    def web_search(self, query, max_results=3):
        if DDGS is None:
            raise ImportError("duckduckgo-search is not installed.")
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"{r['title']}: {r['href']}\n{r['body']}")
        return results

    def add_document(self, file_path, doc_type=None, chunk_size=500):
        """Add a document (txt, pdf, docx) to the agent's knowledge base."""
        ext = os.path.splitext(file_path)[1].lower()
        if doc_type:
            ext = doc_type.lower()
        if ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == ".pdf":
            text = self._extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        # Split text into chunks
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        # Add to ChromaDB
        for idx, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                ids=[f"{os.path.basename(file_path)}_{idx}"]
            )
        print(colored(f"Added {len(chunks)} chunks from {file_path}", "magenta"))

    def _extract_text_from_pdf(self, file_path):
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    def _extract_text_from_docx(self, file_path):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def retrieve_relevant_chunks(self, query, n_results=3):
        """Retrieve the most relevant document chunks for a query."""
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results["documents"][0] if results["documents"] else []

    def register_action(self, action: Action):
        if hasattr(action, 'set_agent_config'):
            action.set_agent_config(self)
        self.registered_actions[action.name] = action

    def run_action(self, action_name, **kwargs):
        action = self.registered_actions.get(action_name)
        if not action:
            return f"Action '{action_name}' not found."
        return action.run(**kwargs)

    def chat_loop(self):
        print(colored(f"\nWelcome to {self.name} (v{self.version})! Type /exit to quit.", "cyan"))
        if self.auth:
            print(colored(f"User: {self.user} | Session: {self.session_id}", "yellow"))
        if self.memory:
            print(colored("[Memory enabled: your chat history will be saved and used as context]", "yellow"))
        print(colored("You can add documents with agent.add_document('path/to/file').", "magenta"))
        print(colored("Type /action <action_name> <key1=value1> <key2=value2> ... to run an action.", "magenta"))
        history = [
            {"role": "system", "content": self.context or "You are a helpful assistant."}
        ]
        if self.memory and self.user_memory:
            history += self.user_memory
        while True:
            user_input = input(colored("You: ", "green"))
            if user_input.strip().lower() == "/exit":
                print(colored("Exiting chat. Goodbye!", "yellow"))
                if self.memory:
                    self._save_user_memory()
                break
            if user_input.strip().startswith("/action"):
                # Parse: /action action_name key1=val1 key2=val2 ...
                parts = user_input.strip().split()
                if len(parts) < 2:
                    print(colored("Usage: /action <action_name> <key1=value1> ...", "red"))
                    continue
                action_name = parts[1]
                kwargs = {}
                for kv in parts[2:]:
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        kwargs[k] = v
                result = self.run_action(action_name, **kwargs)
                print(colored(f"[Action Result] {result}", "yellow"))
                continue
            messages = history.copy()
            if self.rag:
                rag_chunks = self.retrieve_relevant_chunks(user_input)
                if rag_chunks:
                    rag_context = "[RAG Retrieved Chunks]\n" + "\n".join(rag_chunks)
                    messages.append({"role": "system", "content": rag_context})
            if self.websearch:
                try:
                    search_results = self.web_search(user_input)
                    web_context = "[Web Search Results]\n" + "\n".join([f"{i+1}. {res}" for i, res in enumerate(search_results)])
                except Exception as e:
                    web_context = f"[Web Search Error] {e}"
                messages.append({"role": "system", "content": web_context})
            if self.cot:
                messages.append({"role": "system", "content": self.cot_instruction})
            messages.append({"role": "user", "content": user_input})
            try:
                response = self.chat(messages)
                print(colored(f"{self.name}: {response}", "blue"))
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": response})
                if self.memory:
                    self.user_memory.append({"role": "user", "content": user_input})
                    self.user_memory.append({"role": "assistant", "content": response})
            except Exception as e:
                print(colored(f"Error: {e}", "red"))

    def run(self):
        print(f"Agent '{self.name}' (v{self.version}) initialized.")
        print(f"Description: {self.description}")
        print(f"Context: {self.context}")
        print(f"Provider: {self.provider}")
        print(f"RAG: {self.rag}, WebSearch: {self.websearch}, CoT: {self.cot}")
        print(f"UI: {self.ui}, Actions: {self.actions}, ActionContext: {self.action_context}")
        print("[This is a placeholder. Actual agent logic will go here.]") 