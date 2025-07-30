import smtplib
from email.mime.text import MIMEText
import requests

class Action:
    name = "base_action"
    description = "Base action class."
    def run(self, **kwargs):
        raise NotImplementedError
    def set_agent_config(self, agent):
        self.agent = agent
    def get_openai_schema(self):
        return None

class SendEmailAction(Action):
    name = "send_email"
    description = "Send an email via SMTP. Params: recipient, subject, body. Uses agent's SMTP config."

    def set_agent_config(self, agent):
        self.agent = agent

    def run(self, recipient, subject, body, **kwargs):
        smtp_config = getattr(self, 'agent', None) and getattr(self.agent, 'smtp_config', {}) or {}
        smtp_server = smtp_config.get("smtp_server")
        smtp_port = smtp_config.get("smtp_port")
        sender_email = smtp_config.get("sender_email")
        sender_password = smtp_config.get("sender_password")
        if not all([smtp_server, smtp_port, sender_email, sender_password]):
            return "SMTP config is missing in the agent."
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient
        try:
            with smtplib.SMTP_SSL(smtp_server, int(smtp_port)) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [recipient], msg.as_string())
            return f"Email sent to {recipient}."
        except Exception as e:
            return f"Failed to send email: {e}"

    def get_openai_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject."},
                    "body": {"type": "string", "description": "Email body."}
                },
                "required": ["recipient", "subject", "body"]
            }
        }

class FetchAPIAction(Action):
    name = "fetch_api"
    description = "Fetch data from a configured API. Params: api_name, params (as key1:value1,key2:value2). Uses agent's API config."

    def set_agent_config(self, agent):
        self.agent = agent

    def run(self, api_name, params=None, **kwargs):
        apis = getattr(self, 'agent', None) and getattr(self.agent, 'apis', {}) or {}
        api = apis.get(api_name)
        if not api:
            return f"API '{api_name}' not found in agent config."
        url = api.get("url")
        headers = api.get("headers", {})
        # Parse params string to dict
        params_dict = {}
        if params:
            for pair in params.split(","):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    params_dict[k] = v
        try:
            response = requests.get(url, headers=headers, params=params_dict)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Failed to fetch data: {e}"

    def get_openai_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "api_name": {"type": "string", "description": "Name of the API as configured in the agent."},
                    "params": {"type": "string", "description": "Parameters as key:value pairs, comma separated (e.g., city:London)."}
                },
                "required": ["api_name"]
            }
        } 