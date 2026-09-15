import json
import logging
import os
import re
from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class HTMLSanitizer(HTMLParser):
    ALLOWED_TAGS = {'p', 'ul', 'ol', 'li', 'h3', 'h4', 'strong', 'em', 'br'}

    def __init__(self):
        super().__init__()
        self.result = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        if tag in self.ALLOWED_TAGS:
            self.result.append(f'<{tag}>')
            self.current_tag = tag

    def handle_endtag(self, tag):
        if tag in self.ALLOWED_TAGS:
            self.result.append(f'</{tag}>')

    def handle_data(self, data):
        self.result.append(data)

    def get_result(self):
        return ''.join(self.result)


def sanitize_html(html_content: str) -> str:
    if not html_content:
        return ''
    sanitizer = HTMLSanitizer()
    sanitizer.feed(html_content)
    return sanitizer.get_result()


def load_prd_content() -> str:
    prd_path = getattr(settings, 'AI_REVIEW_PRD_PATH', None)
    if not prd_path:
        prd_path = Path(settings.BASE_DIR) / 'requirements_app' / 'prompts' / 'it_review_prd.md'
    try:
        with open(prd_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load PRD from {prd_path}: {e}")
        return ""


def build_system_prompt(prd_content: str) -> str:
    return f"""You are a senior product manager reviewing a requirement for the BreathCare WEB platform.

Your role:
- Ask follow-up questions ONE AT A TIME based on the user's previous answers
- Dig deep into important details (user roles, business rules, edge cases, data flows)
- You can ask UP TO 5 questions maximum
- If you have enough information before 5 questions, you can converge early

The platform context (PRD):
{prd_content}

Review rules:
1. Ask one question per turn
2. Each question should build on the user's previous answer
3. Focus on: user roles, permissions, business logic, data validation, edge cases
4. After ≤5 questions, generate the final result

Output format:
- For questions: {{"finished": false, "question": "your question here"}}
- For final result: {{"finished": true, "description_html": "<p>refined description</p>", "acceptance_criteria_html": "<ul><li>criteria 1</li></ul>"}}

The description_html and acceptance_criteria_html should use simple HTML tags: p, ul, ol, li, h3, h4, strong, em, br.
"""


class AiReviewClient:
    def __init__(self):
        api_key = getattr(settings, 'DASHSCOPE_API_KEY', None)
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY not configured")
        
        base_url = getattr(settings, 'AI_REVIEW_BASE_URL', 'https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1')
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0
        )
        self.model = getattr(settings, 'AI_REVIEW_MODEL', 'qwen-plus')
        self.prd_content = load_prd_content()

    def chat(self, messages: list, question_count: int) -> dict:
        system_prompt = build_system_prompt(self.prd_content)
        
        if question_count >= 5:
            system_prompt += "\n\nIMPORTANT: You have already asked 5 questions. You MUST generate the final result now."
        
        # Map 'ai' role to 'assistant' for OpenAI API compatibility
        mapped_messages = []
        for msg in messages:
            role = msg['role']
            if role == 'ai':
                role = 'assistant'
            mapped_messages.append({'role': role, 'content': msg['content']})
        
        full_messages = [{"role": "system", "content": system_prompt}] + mapped_messages
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            for attempt in range(2):
                try:
                    result = json.loads(content)
                    if 'finished' in result:
                        if result['finished']:
                            result['description_html'] = sanitize_html(result.get('description_html', ''))
                            result['acceptance_criteria_html'] = sanitize_html(result.get('acceptance_criteria_html', ''))
                        return result
                except json.JSONDecodeError:
                    if attempt == 0:
                        logger.warning(f"LLM returned invalid JSON, retrying: {content[:200]}")
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=full_messages + [{"role": "assistant", "content": content}, {"role": "user", "content": "Please output valid JSON only."}],
                            temperature=0.5,
                            max_tokens=2000
                        )
                        content = response.choices[0].message.content.strip()
                    else:
                        logger.error(f"LLM returned invalid JSON after retry: {content[:200]}")
                        return {"finished": False, "question": "I encountered an error processing your response. Please try again."}
            
            return {"finished": False, "question": "I encountered an error. Please try again."}
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
