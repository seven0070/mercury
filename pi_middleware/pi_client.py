import os
from openai import OpenAI

class PiClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("PI_API_KEY")
        self.model = os.getenv("PI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def extract_goal(self, user_message: str) -> str:
        if not self.client:
            if "news" in user_message.lower() or "tech" in user_message.lower():
                return "latest tech news"
            return user_message.strip()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the main objective from the user's message. Return a short query suitable for a web search."},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Pi extract_goal error: {e}")
            return user_message.strip()

    def generate_response(self, pipeline_result: str, user_message: str) -> str:
        if not self.client:
            return f"Here's what my team found:\n\n{pipeline_result}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Mercury's chief of staff. Summarize the following pipeline result in a friendly, helpful way."},
                    {"role": "user", "content": f"User asked: {user_message}\n\nPipeline result:\n{pipeline_result}"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Pi generate_response error: {e}")
            return f"Here's what my team found:\n\n{pipeline_result}"
