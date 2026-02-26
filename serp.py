# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "api.env"), override=True)

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json
import re

print(f"\n{'='*70}")
print("🚀 INFOFETCH AI - INITIALIZING ENHANCED BACKEND v2.0")
print(f"{'='*70}")

try:
    search = SerpAPIWrapper()
    print("✅ SerpAPI: CONNECTED")
except Exception as e:
    print(f"❌ SerpAPI: FAILED - {e}")
    search = None

def web_search(query: str) -> str:
    if search is None:
        return "Search service unavailable."
    try:
        result = search.run(query)
        print(f"   ✓ Search returned {len(result)} characters")
        return result
    except Exception as e:
        print(f"   ✗ Search error: {str(e)}")
        return f"Search failed: {str(e)}"

try:
    research_llm = ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        temperature=0.1,
        max_tokens=2500,
        timeout=60,
        max_retries=3,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    print("✅ Research LLM: CONNECTED (JSON mode, T=0.1)")

    chat_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=400,
        timeout=30,
        max_retries=2
    )
    print("✅ Chat LLM: CONNECTED (Conversational mode, T=0.7)")

    llm = research_llm

except Exception as e:
    print(f"❌ OpenAI: FAILED - {e}")
    research_llm = None
    chat_llm = None
    llm = None

print(f"{'='*70}\n")

# ============================================================================
# COMPANY DETECTION
# ============================================================================

COMPANY_KEYWORDS = [
    'company', 'career', 'job', 'hiring', 'work', 'salary', 'interview',
    'culture', 'benefits', 'openings', 'recruitment', 'intern', 'internship',
    'fresher', 'graduate', 'placement', 'apply', 'employer', 'organization',
    'corporation', 'firm', 'startup', 'tech company', 'mnc', 'contact',
    'address', 'email', 'phone', 'location', 'office', 'headquarters',
    'founded', 'ceo', 'employees', 'revenue', 'industry'
]

COMPANY_SUFFIXES = [
    'inc', 'llc', 'ltd', 'limited', 'corporation', 'corp', 'technologies',
    'tech', 'systems', 'solutions', 'services', 'group', 'labs', 'software'
]

KNOWN_COMPANIES = [
    'google', 'microsoft', 'amazon', 'apple', 'meta', 'facebook', 'netflix',
    'tesla', 'nvidia', 'intel', 'ibm', 'oracle', 'salesforce', 'adobe',
    'twitter', 'x corp', 'uber', 'airbnb', 'spotify', 'zoom', 'slack', 'linkedin',
    'infosys', 'tcs', 'wipro', 'cognizant', 'accenture', 'deloitte',
    'goldman sachs', 'jp morgan', 'morgan stanley', 'mckinsey', 'bain',
    'flipkart', 'zomato', 'swiggy', 'paytm', 'ola', 'byju', 'phonepe',
    'sony', 'samsung', 'dell', 'hp', 'cisco', 'vmware', 'servicenow',
    'shopify', 'stripe', 'square', 'paypal', 'visa', 'mastercard'
]

def is_company_query(query: str) -> bool:
    query_lower = query.lower()
    if any(company in query_lower for company in KNOWN_COMPANIES):
        return True
    for suffix in COMPANY_SUFFIXES:
        pattern = rf'\b[A-Z][a-zA-Z]*\s+{suffix}\b'
        if re.search(pattern, query):
            return True
    strict_company_patterns = [
        r'\bcompany\s+(?:named|called|about|info|information|details|contact)',
        r'\b(?:working|career|job|apply|join)\s+at\s+[A-Z]',
        r'\b[A-Z][a-zA-Z]+\s+(?:company|corporation|inc|llc|careers|jobs|hiring)',
        r'\b(?:contact|email|phone|address)\s+(?:for|of)\s+[A-Z]',
        r'\bcareer\s+(?:at|in|with)\s+[A-Z]',
        r'\b(?:ceo|founder|headquarters)\s+(?:of|at)\s+[A-Z]',
    ]
    for pattern in strict_company_patterns:
        if re.search(pattern, query):
            return True
    job_keywords = ['hiring', 'recruitment', 'intern', 'internship', 'placement', 'employer', 'salary', 'interview']
    for keyword in job_keywords:
        if keyword in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if keyword in word.lower():
                    for j in range(max(0, i-3), min(len(words), i+4)):
                        if len(words[j]) > 2 and words[j][0].isupper():
                            return True
    return False

def extract_company_name(query: str) -> str:
    query_lower = query.lower()
    for company in KNOWN_COMPANIES:
        if company in query_lower:
            return company.title()
    patterns = [
        r'(?:about|at|for|join|career at|working at)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+company|\s+career|\s+job|\s+salary|$|\.)',
        r'^([A-Z][a-zA-Z\s&]+?)(?:\s+company|\s+career|\s+job|\s+salary)',
        r'([A-Z][a-zA-Z\s&]+?)\s+(?:inc|llc|ltd|limited|corp|technologies|tech)'
    ]
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    words = query.split()
    for word in words:
        if len(word) > 2 and word[0].isupper():
            return word
    return "Company"

def is_chat_query(query: str) -> bool:
    query_lower = query.lower()
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'howdy', 'sup', "what's up"]
    if any(query_lower.startswith(g) for g in greetings):
        return True
    social = ['thank', 'thanks', 'bye', 'goodbye', 'see you', 'appreciate']
    if any(word in query_lower for word in social):
        return True
    meta = ['help', 'how to use', 'what can you do', 'features', 'about you']
    if any(phrase in query_lower for phrase in meta):
        return True
    simple_patterns = [
        r'^who is (the )?(ceo|founder|president|owner) of',
        r'^when (was|did) .{1,30} (founded|started|created|established)',
        r'^where is .{1,30} (located|based|headquartered)',
        r'^what (is|does) [A-Z]\w+ (do|make|sell)',
        r'^how (many|much) (employees|people work|revenue)',
    ]
    for pattern in simple_patterns:
        if re.search(pattern, query_lower):
            return True
    research_triggers = [
        'tell me about', 'research', 'detailed', 'comprehensive',
        'contact information', 'email', 'phone number', 'address',
        'career opportunities', 'job openings', 'hiring',
        'salary range', 'benefits', 'work culture',
        'compare', 'analyze', 'latest trends', 'overview'
    ]
    if any(trigger in query_lower for trigger in research_triggers):
        return False
    word_count = len(query.split())
    if word_count <= 8:
        return True
    return False

# ============================================================================
# 🔥 IMPROVED PROMPTS — MINIMISE "Unknown" FIELDS
# ============================================================================

COMPANY_RESEARCH_PROMPT = """You are an expert company data extractor. Your job is to extract ALL available information from the search results provided and return it as valid JSON.

CRITICAL RULES:
1. Output ONLY valid JSON — no text before/after, no markdown backticks
2. NEVER return "Unknown" if the information can be reasonably inferred or found anywhere in the search results
3. For well-known companies (Google, Microsoft, Apple, Amazon, Meta, Tesla, etc.) you already know their details — USE that knowledge to fill in fields even if the search results are sparse
4. For LinkedIn: always construct it as "https://www.linkedin.com/company/<company-name-slug>"
5. For careers page: always construct it as the official URL e.g. "https://careers.google.com" or "https://www.microsoft.com/en-us/careers"
6. For email: use official contact/support emails from the search results, or the standard format like "press@company.com" or "careers@company.com" if visible
7. For revenue and employee count — use your training knowledge for well-known companies
8. Only use "Not publicly available" (not "Unknown") as a last resort when information truly cannot be found or inferred

REQUIRED JSON FORMAT:
{
  "company_name": "Full Official Company Name",
  "company_type": "e.g. Multinational Technology Corporation",
  "contact_info": {
    "email": "official contact or press email address",
    "phone": "main headquarters phone number",
    "address": "full street address of headquarters",
    "website": "https://official-website.com",
    "careers_page": "https://careers.company.com or equivalent",
    "linkedin": "https://www.linkedin.com/company/company-name"
  },
  "basic_info": {
    "description": "3-4 sentence description covering what the company does, its products/services, market position, and why it matters",
    "founded": "year",
    "headquarters": "City, State, Country",
    "employees": "approximate headcount e.g. 150,000+",
    "ceo": "full name of current CEO",
    "revenue": "annual revenue e.g. $280 billion (2023)",
    "industry": "primary industry"
  },
  "careers": {
    "entry_roles": ["Specific role 1", "Specific role 2", "Specific role 3", "Specific role 4", "Specific role 5"],
    "key_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
    "salary_range": "87,800 - $96,600 USD per year (Entry Level) — plain text only, no asterisks or markdown",    
    "hiring_status": "Actively hiring",
    "application_process": "Apply via careers page → online assessment → interviews → offer"
  },
  "culture": {
    "work_environment": "description of work culture",
    "perks": ["perk 1", "perk 2", "perk 3", "perk 4"],
    "values": ["value 1", "value 2", "value 3"]
  },
  "sources": ["url1", "url2", "url3"],
  "confidence": "high"
}

Use your training knowledge generously for well-known companies. Fill every field."""

RESEARCH_SYSTEM_PROMPT = """You are an expert research assistant. Extract comprehensive information from the search results and return structured JSON.

CRITICAL RULES:
1. Output ONLY valid JSON — no markdown, no preamble
2. Make the overview SUBSTANTIAL (3-5 paragraphs, 200-300 words)
3. Each key_point must be 2-3 sentences with real depth
4. Provide 6-8 key points minimum
5. Fill ALL sections thoroughly — never leave arrays empty
6. Use concrete data, statistics, and examples wherever available

REQUIRED JSON FORMAT:
{
  "query": "original query",
  "topic": "Main Topic Title",
  "overview": "Comprehensive 3-5 paragraph overview...",
  "key_points": [
    "Detailed point 1 with full context (2-3 sentences)",
    "Detailed point 2 with full context (2-3 sentences)",
    "Detailed point 3 with full context (2-3 sentences)",
    "Detailed point 4 with full context (2-3 sentences)",
    "Detailed point 5 with full context (2-3 sentences)",
    "Detailed point 6 with full context (2-3 sentences)"
  ],
  "additional_info": {
    "benefits": ["Specific benefit 1", "Specific benefit 2", "Specific benefit 3"],
    "challenges": ["Specific challenge 1", "Specific challenge 2", "Specific challenge 3"],
    "examples": ["Concrete example 1", "Concrete example 2", "Concrete example 3"],
    "facts": ["Fact with numbers/data 1", "Fact 2", "Fact 3"]
  },
  "expert_insights": ["Insight 1", "Insight 2"],
  "practical_applications": ["Application 1", "Application 2"],
  "related_topics": ["Related topic 1", "Related topic 2", "Related topic 3"],
  "summary": "One compelling sentence summary",
  "sources": ["url1", "url2", "url3"],
  "confidence": "high or medium or low"
}"""

INTELLIGENT_CHATBOT_PROMPT = """You are InfoFetch AI, an intelligent research assistant and chatbot.

YOUR CAPABILITIES:
- Answer factual questions about companies, industries, and general topics
- Provide quick, accurate information from your knowledge
- Help users understand how to use InfoFetch features
- Be conversational, friendly, and professional

YOUR PERSONALITY:
- Professional but approachable
- Knowledgeable and confident
- Concise (under 150 words) but helpful
- Encouraging and supportive

RESPONSE STYLE:
- Start with direct answer
- Add 1-2 sentences of context if helpful
- End with follow-up question or suggestion when appropriate

BOUNDARIES:
- Don't make up contact information
- Don't claim to have real-time data
- Acknowledge gaps in knowledge honestly
- Redirect to Research feature for comprehensive analysis"""

# ============================================================================
# JSON PARSING
# ============================================================================

def extract_and_parse_json(text: str) -> dict:
    print(f"\n{'='*70}")
    print("📥 RAW LLM RESPONSE:")
    print(f"{'='*70}")
    print(text[:400] + "..." if len(text) > 400 else text)
    print(f"{'='*70}\n")

    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]

    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        print("❌ No JSON object found!")
        return None

    text = text[start:end+1].strip()

    try:
        parsed = json.loads(text)
        print("✅ JSON PARSED SUCCESSFULLY!")
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError as e:
        print(f"❌ JSON DECODE ERROR: {e}")
        try:
            fixed = text.replace("'", '"')
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            parsed = json.loads(fixed)
            print("✅ JSON FIXED AND PARSED!")
            return parsed
        except:
            print("❌ FIXES FAILED - returning None")
            return None

# ============================================================================
# 🔥 IMPROVED SEARCH QUERIES — TARGETED TO FILL EVERY FIELD
# ============================================================================

def research_company(user_query: str, company_name: str) -> dict:
    """
    Runs 5 highly targeted searches so every field in the result card
    has real data instead of 'Unknown'.
    """

    company_slug = company_name.lower().replace(' ', '')

    search_queries = [
        # 1. Official contact details — email, phone, address
        f"{company_name} official contact email phone number headquarters address site:linkedin.com OR site:{company_slug}.com",

        # 2. Careers page + job openings
        f"{company_name} careers jobs 2025 2026 entry level fresher internship hiring site:careers.{company_slug}.com OR site:linkedin.com/jobs",

        # 3. Company overview — CEO, founded, revenue, employees
        f"{company_name} company overview CEO founder founded year revenue employees industry 2025",

        # 4. LinkedIn company page
        f"{company_name} LinkedIn company page official profile employees",

        # 5. Salary, culture, benefits, work environment
        f"{company_name} salary range entry level work culture benefits perks glassdoor 2025",
    ]

    print(f"🔍 Running {len(search_queries)} targeted searches for {company_name}...\n")

    all_results = []
    for i, query in enumerate(search_queries, 1):
        print(f"  [{i}/{len(search_queries)}] {query}")
        try:
            result = web_search(query)
            all_results.append(result)
        except Exception as e:
            print(f"  ✗ Search failed: {e}")
            all_results.append("")

    combined = "\n\n--- SEARCH RESULT SET {} ---\n\n".join([""] * (len(all_results) + 1)).strip()
    combined = ""
    for idx, r in enumerate(all_results, 1):
        combined += f"\n\n=== SEARCH SET {idx} ===\n{r}"

    max_chars = 7000
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[Results truncated...]"

    print(f"\n📊 Total content: {len(combined)} characters")
    print(f"🤖 Sending to Research LLM for extraction...\n")

    messages = [
        SystemMessage(content=COMPANY_RESEARCH_PROMPT),
        HumanMessage(content=f"""COMPANY NAME: {company_name}
USER QUERY: {user_query}

IMPORTANT: This is {company_name}. Use BOTH the search results below AND your training knowledge to fill every single field. Do not return "Unknown" for any field you can reasonably know or infer about {company_name}.

For the LinkedIn field, construct it as: https://www.linkedin.com/company/{company_slug}
For the careers page, construct it as the known official URL for {company_name}.

SEARCH RESULTS:
{combined}

Return complete JSON with ALL fields populated.""")
    ]

    try:
        print("⏳ Waiting for Research LLM response...")
        response = research_llm.invoke(messages)
        response_text = response.content
        print(f"✅ Research LLM responded ({len(response_text)} chars)\n")

        parsed_data = extract_and_parse_json(response_text)

        if parsed_data is None:
            print("\n⚠️ JSON PARSING FAILED - USING INTELLIGENT FALLBACK\n")
            return create_smart_fallback_company(user_query, company_name, response_text, combined)

        # Post-process: fill in any remaining "Unknown" fields using known patterns
        parsed_data = fill_known_fields(parsed_data, company_name, company_slug)

        parsed_data['query_type'] = 'company'
        parsed_data['original_query'] = user_query

        print(f"✅ COMPANY RESEARCH COMPLETE - Confidence: {parsed_data.get('confidence', 'unknown')}\n")
        return parsed_data

    except Exception as e:
        print(f"\n❌ LLM ERROR: {e}\n")
        return create_smart_fallback_company(user_query, company_name, str(e), combined)


def fill_known_fields(data: dict, company_name: str, company_slug: str) -> dict:
    """
    Post-processing pass — fills any remaining Unknown/empty fields
    using pattern-based construction so the UI never shows blank cards.
    """
    contact = data.get('contact_info', {})

    # LinkedIn — always constructable
    if not contact.get('linkedin') or 'unknown' in str(contact.get('linkedin', '')).lower():
        contact['linkedin'] = f"https://www.linkedin.com/company/{company_slug}"

    # Website — always constructable
    if not contact.get('website') or 'unknown' in str(contact.get('website', '')).lower():
        contact['website'] = f"https://www.{company_slug}.com"

    # Careers page — always constructable
    if not contact.get('careers_page') or 'unknown' in str(contact.get('careers_page', '')).lower():
        # Try common patterns
        careers_patterns = {
            'google': 'https://careers.google.com',
            'microsoft': 'https://careers.microsoft.com',
            'amazon': 'https://www.amazon.jobs',
            'apple': 'https://jobs.apple.com',
            'meta': 'https://www.metacareers.com',
            'netflix': 'https://jobs.netflix.com',
            'tesla': 'https://www.tesla.com/careers',
            'nvidia': 'https://www.nvidia.com/en-us/about-nvidia/careers',
            'ibm': 'https://www.ibm.com/employment',
            'intel': 'https://jobs.intel.com',
            'infosys': 'https://www.infosys.com/careers',
            'tcs': 'https://www.tcs.com/careers',
            'wipro': 'https://careers.wipro.com',
            'accenture': 'https://www.accenture.com/in-en/careers',
            'cognizant': 'https://careers.cognizant.com',
        }
        slug_lower = company_slug.lower()
        matched = next((v for k, v in careers_patterns.items() if k in slug_lower), None)
        contact['careers_page'] = matched or f"https://www.{company_slug}.com/careers"

    # Email — use press/contact pattern if missing
    if not contact.get('email') or 'unknown' in str(contact.get('email', '')).lower():
        contact['email'] = f"press@{company_slug}.com (check official website)"

    data['contact_info'] = contact

    # Hiring status default
    careers = data.get('careers', {})
    if not careers.get('hiring_status') or 'unknown' in str(careers.get('hiring_status', '')).lower():
        careers['hiring_status'] = "Actively hiring — check careers page"
    data['careers'] = careers

    return data


def research_general(user_query: str) -> dict:
    print("🔍 Searching for comprehensive information...")
    try:
        search_results = web_search(user_query)
        print(f"✓ Search complete ({len(search_results)} chars)\n")
    except Exception as e:
        return create_error_response(user_query, f"Search failed: {str(e)}")

    max_chars = 6000
    if len(search_results) > max_chars:
        search_results = search_results[:max_chars] + "\n[Truncated...]"

    print("🤖 Analyzing with Research LLM...\n")

    messages = [
        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
        HumanMessage(content=f"""USER QUERY: {user_query}

SEARCH RESULTS:
{search_results}

Create a comprehensive, detailed research response. Output ONLY valid JSON.""")
    ]

    try:
        print("⏳ Waiting for Research LLM response...")
        response = research_llm.invoke(messages)
        response_text = response.content
        print(f"✅ Research LLM responded ({len(response_text)} chars)\n")

        parsed_data = extract_and_parse_json(response_text)

        if parsed_data is None:
            print("⚠️ JSON PARSING FAILED - Using smart fallback\n")
            return create_smart_fallback_general(user_query, response_text, search_results)

        parsed_data['query_type'] = 'general'
        parsed_data['original_query'] = user_query
        print(f"✅ GENERAL RESEARCH COMPLETE - Confidence: {parsed_data.get('confidence', 'unknown')}\n")
        return parsed_data

    except Exception as e:
        print(f"❌ LLM ERROR: {e}\n")
        return create_smart_fallback_general(user_query, str(e), search_results)


def run_research_agent(user_query: str) -> dict:
    print(f"\n{'='*70}")
    print(f"🔍 NEW RESEARCH QUERY: {user_query}")
    print(f"{'='*70}\n")

    if research_llm is None:
        return create_error_response(user_query, "OpenAI API not configured")
    if search is None:
        return create_error_response(user_query, "SerpAPI not configured")

    is_company = is_company_query(user_query)

    if is_company:
        print("✓ Detected: COMPANY RESEARCH")
        company_name = extract_company_name(user_query)
        print(f"✓ Company: {company_name}\n")
        return research_company(user_query, company_name)
    else:
        print("✓ Detected: GENERAL RESEARCH\n")
        return research_general(user_query)

# ============================================================================
# CHATBOT
# ============================================================================

def get_chat_response(user_message: str, chat_history: list) -> str:
    if chat_llm is None:
        return "⚠️ Chatbot unavailable. Please check OPENAI_API_KEY in api.env"

    print(f"\n{'='*50}")
    print(f"💬 CHATBOT QUERY: {user_message}")
    print(f"{'='*50}\n")

    user_lower = user_message.lower()

    if any(word in user_lower for word in ['hello', 'hi ', 'hey ', 'good morning', 'good afternoon']):
        return "👋 Hello! I'm InfoFetch AI, your intelligent research assistant. I can answer quick questions about companies, help you understand topics, or run deep research. What would you like to know?"

    if any(word in user_lower for word in ['thank you', 'thanks', 'appreciate']):
        import random
        return random.choice([
            "You're very welcome! Happy to help anytime! 😊",
            "My pleasure! Let me know if you need anything else!",
            "Glad I could help! Feel free to ask more questions."
        ])

    if any(phrase in user_lower for phrase in ['help', 'what can you do', 'how do i', 'how to use']):
        return """I can help you in two ways:

**💬 Quick Answers (Chat):** Ask me simple questions and I'll answer immediately.
• "Who is the CEO of Microsoft?"
• "When was Apple founded?"
• "What does Tesla do?"

**🔍 Deep Research:** For comprehensive info, use the **Research** button.
• Company contact details (email, phone, address)
• Career opportunities and salary ranges
• Detailed topic analysis with key points

What would you like to know?"""

    if is_company_query(user_message):
        company = extract_company_name(user_message)
        contact_keywords = ['email', 'phone', 'contact', 'address', 'reach', 'call']
        if any(keyword in user_lower for keyword in contact_keywords):
            return f"""For **{company}** contact information (email, phone, address), please use the **🔍 Research** feature on the Home page.

The Research feature will find:
✉️ Official email addresses
📞 Phone numbers
📍 Physical addresses
🌐 Website and careers page

I can answer quick questions about {company} if you have any!"""

        career_keywords = ['job', 'career', 'hiring', 'work at', 'salary', 'opening']
        if any(keyword in user_lower for keyword in career_keywords):
            return f"""For comprehensive career information at **{company}** including job openings, salary ranges, and benefits, use the **🔍 Research** feature.

If you have a quick question about {company}, feel free to ask and I'll help!"""

    messages = [SystemMessage(content=INTELLIGENT_CHATBOT_PROMPT)]
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
    for msg in recent_history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
    messages.append(HumanMessage(content=user_message))

    try:
        print("🤖 Calling Chat LLM...")
        response = chat_llm.invoke(messages)
        answer = response.content.strip()
        print(f"✅ Chat LLM responded ({len(answer)} chars)\n")
        if len(answer) > 600:
            answer = answer[:600] + "..."
        return answer
    except Exception as e:
        print(f"❌ Chat LLM error: {e}\n")
        return fallback_chat_response(user_message, chat_history)


def fallback_chat_response(user_message: str, chat_history: list) -> str:
    user_lower = user_message.lower()
    if is_company_query(user_message):
        company = extract_company_name(user_message)
        basic_info = get_basic_company_info(company)
        if basic_info:
            return f"""{basic_info}\n\nFor detailed information including contact details and career opportunities, use the **🔍 Research** feature."""
        return f"""I'd love to help with **{company}** information!\n\nFor comprehensive details including contact info, careers, and company overview, please use the **🔍 Research** button.\n\nDo you have a specific quick question about {company}?"""
    return """I'm here to help!\n\n• Ask me quick questions and I'll answer\n• Use **🔍 Research** for comprehensive analysis\n\nWhat would you like to know?"""


def get_basic_company_info(company_name: str) -> str:
    company_lower = company_name.lower()
    company_knowledge = {
        'google': "**Google** (Alphabet Inc.) is a multinational technology company specialising in internet services, search, advertising, cloud computing, and AI. Founded in 1998 by Larry Page and Sergey Brin, headquartered at 1600 Amphitheatre Parkway, Mountain View, California.",
        'microsoft': "**Microsoft** is a leading technology company known for Windows, Office, Azure cloud services, and Xbox. Founded in 1975 by Bill Gates and Paul Allen, headquartered in Redmond, Washington.",
        'apple': "**Apple Inc.** designs and manufactures consumer electronics including iPhone, iPad, Mac, and Apple Watch. Founded in 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne, based in Cupertino, California.",
        'amazon': "**Amazon** is a multinational technology company focusing on e-commerce, cloud computing (AWS), digital streaming, and AI. Founded by Jeff Bezos in 1994, headquartered in Seattle, Washington.",
        'meta': "**Meta** (formerly Facebook) specialises in social media, virtual reality, and metaverse technologies. Founded by Mark Zuckerberg in 2004, based in Menlo Park, California.",
        'tesla': "**Tesla** designs and manufactures electric vehicles, battery energy storage, and solar products. Founded in 2003 and led by Elon Musk, headquartered in Austin, Texas.",
        'netflix': "**Netflix** is a streaming entertainment service with 260+ million subscribers worldwide. Founded in 1997 by Reed Hastings and Marc Randolph, based in Los Gatos, California.",
        'nvidia': "**NVIDIA** is a leader in graphics processing units (GPUs) and AI computing. Founded in 1993 by Jensen Huang, Chris Malachowsky, and Curtis Priem, headquartered in Santa Clara, California.",
        'intel': "**Intel** is a major semiconductor manufacturer known for processors. Founded in 1968 by Gordon Moore and Robert Noyce, based in Santa Clara, California.",
        'ibm': "**IBM** (International Business Machines) offers hardware, software, cloud computing, and AI solutions. Founded in 1911, headquartered in Armonk, New York."
    }
    for key, info in company_knowledge.items():
        if key in company_lower:
            return info
    return None

# ============================================================================
# FALLBACK FUNCTIONS
# ============================================================================

def create_smart_fallback_company(query: str, company_name: str, error_info: str, search_results: str) -> dict:
    print(f"\n{'='*70}")
    print("🔧 CREATING SMART FALLBACK (COMPANY)")
    print(f"{'='*70}\n")

    company_slug = company_name.lower().replace(' ', '')
    email = extract_email(search_results)
    phone = extract_phone(search_results)
    website = extract_website(company_name, search_results)

    data = {
        "query": query,
        "query_type": "company",
        "company_name": company_name,
        "company_type": "Company",
        "contact_info": {
            "email": email,
            "phone": phone,
            "address": "See company website for address",
            "website": website,
            "careers_page": f"{website}/careers",
            "linkedin": f"https://www.linkedin.com/company/{company_slug}"
        },
        "basic_info": {
            "description": f"Information about {company_name}.",
            "founded": "See company website",
            "headquarters": "See company website",
            "employees": "See LinkedIn",
            "ceo": "See company website",
            "revenue": "See annual report",
            "industry": "See company website"
        },
        "careers": {
            "entry_roles": ["Software Engineer", "Data Analyst", "Product Manager", "Business Analyst", "Operations Associate"],
            "key_skills": ["Problem solving", "Communication", "Technical aptitude", "Teamwork"],
            "salary_range": f"See Glassdoor / Levels.fyi for {company_name}",
            "hiring_status": "Check careers page for current openings",
            "application_process": f"Visit {website}/careers to apply"
        },
        "culture": {
            "work_environment": "See Glassdoor reviews",
            "perks": ["Check company website", "Read Glassdoor reviews"],
            "values": ["See About Us page"]
        },
        "sources": [website, f"https://www.linkedin.com/company/{company_slug}", f"https://www.glassdoor.com/Overview/Working-at-{company_name.replace(' ', '-')}.htm"],
        "confidence": "low",
        "fallback_reason": "Partial data — showing extracted + constructed fields"
    }
    return fill_known_fields(data, company_name, company_slug)


def create_smart_fallback_general(query: str, error_info: str, search_results: str) -> dict:
    sentences = search_results.split('.')
    key_sentences = [s.strip() for s in sentences if len(s.strip()) > 50][:8]
    overview = '. '.join(key_sentences[:4]) + '.' if key_sentences else "Search results found but formatting failed."
    urls = re.findall(r'https?://[^\s<>"]+', search_results)
    unique_urls = list(dict.fromkeys(urls))[:5]
    return {
        "query": query,
        "query_type": "general",
        "original_query": query,
        "topic": query.title(),
        "overview": overview,
        "key_points": key_sentences if key_sentences else ["Search results found but AI formatting encountered issues"],
        "additional_info": {
            "benefits": ["See sources below"],
            "challenges": ["See sources below"],
            "examples": ["See sources below"],
            "facts": ["See sources below"]
        },
        "expert_insights": ["Check sources for expert opinions"],
        "practical_applications": ["Refer to sources"],
        "related_topics": ["Try a related search"],
        "summary": f"Research results for: {query}",
        "sources": unique_urls if unique_urls else ["No URLs extracted"],
        "confidence": "low",
        "fallback_reason": "AI formatting failed — showing extracted content"
    }


def extract_email(text: str) -> str:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    filtered = [m for m in matches if not any(skip in m.lower() for skip in ['example', 'test', 'noreply', 'no-reply'])]
    return filtered[0] if filtered else "See official website contact page"

def extract_phone(text: str) -> str:
    patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return "See official website contact page"

def extract_website(company_name: str, text: str) -> str:
    pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-z]{2,})'
    matches = re.findall(pattern, text.lower())
    company_lower = company_name.lower().replace(' ', '')
    for match in matches:
        if company_lower in match.replace('-', '').replace('.', ''):
            return f"https://{match}"
    return f"https://www.{company_lower}.com"

def create_error_response(query: str, error: str, is_company: bool = False) -> dict:
    base = {
        "query": query,
        "error": error,
        "suggestion": "Check api.env file and ensure API keys are configured",
        "confidence": "low",
        "query_type": "company" if is_company else "general"
    }
    if is_company:
        company = extract_company_name(query)
        company_slug = company.lower().replace(' ', '')
        base.update({
            "company_name": company,
            "company_type": "Company",
            "contact_info": {
                "email": "API not configured",
                "phone": "API not configured",
                "address": "API not configured",
                "website": f"https://www.{company_slug}.com",
                "careers_page": f"https://www.{company_slug}.com/careers",
                "linkedin": f"https://www.linkedin.com/company/{company_slug}"
            },
            "basic_info": {"description": "Unable to fetch — API error", "founded": "N/A", "headquarters": "N/A", "employees": "N/A", "ceo": "N/A", "revenue": "N/A", "industry": "N/A"},
            "careers": {"entry_roles": ["Configure API to see roles"], "key_skills": ["Configure API"], "salary_range": "N/A", "hiring_status": "N/A", "application_process": "N/A"},
            "culture": {"work_environment": "N/A", "perks": ["N/A"], "values": ["N/A"]},
            "sources": []
        })
    else:
        base.update({
            "topic": "Error",
            "overview": "Unable to search — API configuration error",
            "key_points": ["Check OPENAI_API_KEY", "Check SERPAPI_API_KEY"],
            "additional_info": {"benefits": ["N/A"], "challenges": ["API not configured"], "examples": ["N/A"], "facts": ["N/A"]},
            "expert_insights": ["Fix API configuration"],
            "practical_applications": ["Configure APIs first"],
            "related_topics": ["API configuration"],
            "summary": "API error",
            "sources": []
        })
    return base

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_company_results(result: dict, st_module):
    st = st_module
    if result.get('query_type') != 'company':
        return False

    company = result.get('company_name', 'Company')
    company_type = result.get('company_type', 'Company')

    st.markdown(f"""
    <div style="text-align:center;background:linear-gradient(135deg,rgba(0,245,255,0.2),rgba(255,0,255,0.2));padding:2rem;border-radius:20px;margin-bottom:2rem;">
        <h1 style="color:#00f5ff;font-family:Orbitron;font-size:2.5rem;">{company}</h1>
        <p style="color:#ff00ff;font-size:1.2rem;">{company_type}</p>
    </div>
    """, unsafe_allow_html=True)

    if result.get('error'):
        st.warning(f"⚠️ {result['error']}")
    if result.get('fallback_reason'):
        st.info(f"ℹ️ {result['fallback_reason']}")

    contact = result.get('contact_info', {})
    if contact:
        st.markdown("## 📞 CONTACT INFORMATION")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📧 Email:** {contact.get('email', 'See official website')}")
            st.markdown(f"**📞 Phone:** {contact.get('phone', 'See official website')}")
            st.markdown(f"**📍 Address:** {contact.get('address', 'See official website')}")
        with col2:
            website = contact.get('website', '')
            if website and website.startswith('http'):
                st.markdown(f"**🌐 Website:** [{website}]({website})")
            else:
                st.markdown(f"**🌐 Website:** {website}")

            careers = contact.get('careers_page', '')
            if careers and careers.startswith('http'):
                st.markdown(f"**💼 Careers:** [{careers}]({careers})")
            else:
                st.markdown(f"**💼 Careers:** {careers}")

            linkedin = contact.get('linkedin', '')
            if linkedin and linkedin.startswith('http'):
                st.markdown(f"**💡 LinkedIn:** [{linkedin}]({linkedin})")
            else:
                st.markdown(f"**💡 LinkedIn:** {linkedin}")
        st.markdown("---")

    basic = result.get('basic_info', {})
    if basic:
        st.markdown("## 🏢 COMPANY OVERVIEW")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Founded", basic.get('founded', 'N/A'))
            st.metric("Employees", basic.get('employees', 'N/A'))
        with col2:
            st.metric("Headquarters", str(basic.get('headquarters', 'N/A'))[:25])
            st.metric("Revenue", str(basic.get('revenue', 'N/A'))[:25])
        with col3:
            st.metric("CEO", str(basic.get('ceo', 'N/A'))[:25])
            st.metric("Industry", str(basic.get('industry', 'N/A'))[:25])
        if basic.get('description'):
            st.markdown(f"\n{basic['description']}")
        st.markdown("---")

    careers_data = result.get('careers', {})
    if careers_data:
        st.markdown("## 💼 CAREER OPPORTUNITIES")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🎯 Entry-Level Roles")
            for role in careers_data.get('entry_roles', [])[:5]:
                st.markdown(f"• {role}")
            if careers_data.get('salary_range'):
                salary_clean = str(careers_data['salary_range']).replace('**', '').replace('*', '').strip()
                st.markdown(f"\n**💰 Salary Range:** {salary_clean}")
        with col2:
            st.markdown("### 🛠️ Key Skills Required")
            for skill in careers_data.get('key_skills', [])[:5]:
                st.markdown(f"• {skill}")
            if careers_data.get('hiring_status'):
                st.markdown(f"\n**📊 Hiring Status:** {careers_data['hiring_status']}")
        if careers_data.get('application_process'):
            st.markdown(f"**📝 Application Process:** {careers_data['application_process']}")
        st.markdown("---")

    culture = result.get('culture', {})
    if culture and culture.get('work_environment') not in ['Unknown', 'N/A', None]:
        st.markdown("## 🌟 COMPANY CULTURE")
        if culture.get('work_environment'):
            st.markdown(f"**Work Environment:** {culture['work_environment']}")
        col1, col2 = st.columns(2)
        with col1:
            if culture.get('perks'):
                st.markdown("**Perks & Benefits:**")
                for perk in culture['perks'][:5]:
                    st.markdown(f"• {perk}")
        with col2:
            if culture.get('values'):
                st.markdown("**Company Values:**")
                for value in culture['values'][:5]:
                    st.markdown(f"• {value}")
        st.markdown("---")

    if result.get('sources'):
        st.markdown("## 🔗 SOURCES")
        for i, source in enumerate(result['sources'][:5], 1):
            if source and source.startswith('http'):
                st.markdown(f"{i}. [{source}]({source})")
            else:
                st.markdown(f"{i}. {source}")

    confidence = result.get('confidence', 'unknown')
    emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(confidence, '⚪')
    st.markdown(f"\n**Confidence:** {emoji} {confidence.upper()}")
    return True


def display_general_results(result: dict, st_module):
    st = st_module
    if result.get('query_type') != 'general':
        return False

    topic = result.get('topic', 'Research Results')
    st.markdown(f"""
    <div style="text-align:center;background:linear-gradient(135deg,rgba(0,245,255,0.2),rgba(255,0,255,0.2));padding:2rem;border-radius:20px;margin-bottom:2rem;">
        <h1 style="color:#00f5ff;font-family:Orbitron;font-size:2.5rem;">📚 {topic}</h1>
        <p style="color:#ff00ff;font-size:1.1rem;">Comprehensive Research</p>
    </div>
    """, unsafe_allow_html=True)

    if result.get('error'):
        st.warning(f"⚠️ {result['error']}")
    if result.get('fallback_reason'):
        st.info(f"ℹ️ {result['fallback_reason']}")

    if result.get('summary'):
        st.markdown(f"""
        <div style="background:rgba(0,245,255,0.1);padding:1rem;border-radius:10px;border-left:4px solid #00f5ff;margin-bottom:1.5rem;">
            <h3 style="color:#00f5ff;margin-top:0;">📝 Summary</h3>
            <p style="font-size:1.1rem;">{result['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

    if result.get('overview'):
        st.markdown("## 🔍 DETAILED OVERVIEW")
        st.markdown(result['overview'])
        st.markdown("---")

    key_points = result.get('key_points', [])
    if key_points:
        st.markdown("## 💡 KEY INSIGHTS")
        for i, point in enumerate(key_points, 1):
            st.markdown(f"""
            <div style="background:rgba(255,0,255,0.1);padding:1rem;border-radius:10px;margin-bottom:1rem;">
                <strong style="color:#ff00ff;">Point {i}:</strong> {point}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")

    if result.get('sources'):
        st.markdown("## 🔗 SOURCES")
        for i, source in enumerate(result['sources'][:5], 1):
            if source and "No URLs" not in source:
                st.markdown(f"{i}. {source}")

    confidence = result.get('confidence', 'unknown')
    emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(confidence, '⚪')
    st.markdown(f"\n**Confidence:** {emoji} {confidence.upper()}")
    return True


def display_results(result: dict, st_module):
    query_type = result.get('query_type')
    if query_type == 'company':
        return display_company_results(result, st_module)
    elif query_type == 'general':
        return display_general_results(result, st_module)
    else:
        st_module.error("Unknown query type")
        return False

# ============================================================================
# INIT CHECK
# ============================================================================

OPENAI_AVAILABLE = os.getenv("OPENAI_API_KEY") is not None and research_llm is not None
SERPAPI_AVAILABLE = os.getenv("SERPAPI_API_KEY") is not None and search is not None

print(f"\n{'='*70}")
print("✅ ENHANCED INITIALIZATION COMPLETE")
print(f"{'='*70}")
print(f"Research LLM: {'✅ Ready' if OPENAI_AVAILABLE else '❌ Not Configured'}")
print(f"Chat LLM:     {'✅ Ready' if chat_llm is not None else '❌ Not Configured'}")
print(f"SerpAPI:      {'✅ Ready' if SERPAPI_AVAILABLE else '❌ Not Configured'}")
print(f"{'='*70}\n")