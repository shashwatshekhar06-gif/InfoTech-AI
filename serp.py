import os
from dotenv import load_dotenv
load_dotenv("api.env", override=True)

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json

# Initialize search
search = SerpAPIWrapper()

def web_search(query: str) -> str:
    """Search the web for real-time information."""
    try:
        return search.run(query)
    except Exception as e:
        return f"Search failed: {str(e)}"

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=500
)

# System prompt for research agent
RESEARCH_SYSTEM_PROMPT = """You are a web research assistant that provides accurate, well-sourced information.

WORKFLOW:
1. I will search the web for you using the provided query
2. You will receive the search results
3. You must format the response as valid JSON with this structure:

{
  "query": "the search query used",
  "sources": ["list of source URLs or titles from results"],
  "summary": "comprehensive summary of findings",
  "key_points": ["bullet point 1", "bullet point 2", "..."],
  "confidence": "high/medium/low based on source quality"
}

RULES:
- Analyze the search results carefully
- Extract relevant URLs/sources from the results
- NEVER make up information not in the search results
- Base confidence on source credibility and consistency
- Output ONLY valid JSON, no extra text or markdown
"""

# System prompt for chatbot
CHATBOT_SYSTEM_PROMPT = """You are InfoFetch AI, an intelligent and helpful research assistant chatbot.

PERSONALITY:
- Friendly, professional, and knowledgeable
- Concise but informative responses
- Use emojis sparingly for engagement
- Reference previous conversation context when relevant

CAPABILITIES:
- Answer questions on any topic
- Provide explanations and insights
- Help with research and information gathering
- Remember conversation context

GUIDELINES:
- Keep responses under 200 words unless asked for detail
- Be conversational and natural
- If unsure, acknowledge limitations
- Suggest using the Research feature for deep web analysis
- Always be helpful and encouraging

Remember previous messages in the conversation to provide contextual responses.
"""

def run_research_agent(user_query: str) -> dict:
    """
    Main research agent function that:
    1. Uses SerpAPI to search the web
    2. Uses ChatGPT to format results into JSON
    """
    
    print(f"\n{'='*60}")
    print(f"QUERY: {user_query}")
    print(f"{'='*60}\n")
    
    # Search the web
    print("🔍 Searching the web...")
    try:
        search_results = web_search(user_query)
        print(f"✓ Search completed\n")
    except Exception as e:
        return {
            "query": user_query,
            "error": f"Search failed: {str(e)}",
            "suggestion": "Check your SERPAPI_API_KEY in api.env",
            "summary": "Unable to complete search",
            "sources": [],
            "key_points": [],
            "confidence": "low"
        }
    
    # Format with ChatGPT
    print("🤖 Formatting results with ChatGPT...\n")
    
    messages = [
        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
        HumanMessage(content=f"""Query: {user_query}

Search Results:
{search_results}

Please format this into the required JSON structure.""")
    ]
    
    try:
        response = llm.invoke(messages)
        result_text = response.content
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            parsed_result = json.loads(result_text)
            return parsed_result
            
        except json.JSONDecodeError:
            # Request fix if JSON is invalid
            print("⚠️  Initial response wasn't valid JSON, requesting fix...\n")
            
            fix_messages = messages + [
                AIMessage(content=result_text),
                HumanMessage(content="Please output ONLY the valid JSON object, no extra text or markdown.")
            ]
            
            fix_response = llm.invoke(fix_messages)
            fix_text = fix_response.content.strip()
            
            if "```json" in fix_text:
                fix_text = fix_text.split("```json")[1].split("```")[0].strip()
            elif "```" in fix_text:
                fix_text = fix_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(fix_text)
            
    except Exception as e:
        return {
            "query": user_query,
            "error": f"Formatting failed: {str(e)}",
            "summary": "Error processing results",
            "sources": [],
            "key_points": [],
            "confidence": "low"
        }

def get_chat_response(user_message: str, chat_history: list) -> str:
    """
    Advanced chatbot using GPT-3.5-turbo with conversation history
    
    Args:
        user_message: The user's current message
        chat_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        AI response string
    """
    
    # Build conversation messages for OpenAI
    messages = [SystemMessage(content=CHATBOT_SYSTEM_PROMPT)]
    
    # Add recent conversation history (last 10 messages for context)
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
    
    for msg in recent_history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
    
    # Add current user message
    messages.append(HumanMessage(content=user_message))
    
    try:
        # Get response from ChatGPT
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        # Fallback to rule-based responses if API fails
        print(f"⚠️  ChatGPT error: {e}. Using fallback...")
        return fallback_chat_response(user_message, chat_history)

def fallback_chat_response(user_message: str, chat_history: list) -> str:
    """Fallback chatbot when OpenAI API is unavailable"""
    
    user_lower = user_message.lower()
    
    # Greetings
    if any(word in user_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "👋 Hello! I'm InfoFetch AI, your research assistant. How can I help you today?"
    
    # Help requests
    if 'help' in user_lower or 'what can you' in user_lower or 'how do' in user_lower:
        return """🤖 **I can help you with:**

✨ **Answer questions** - Ask me anything!
🔍 **Deep research** - Use the Research button for web analysis
📊 **Data insights** - Analyze trends and information
📚 **Search history** - View all your past searches

What would you like to explore?"""
    
    # Research-related
    if any(word in user_lower for word in ['research', 'search', 'find', 'look up', 'google']):
        return "🔍 For comprehensive web research with sources and confidence scores, use the **🚀 DEEP RESEARCH** button on the Home page!"
    
    # Time/date
    if 'time' in user_lower or 'date' in user_lower:
        from datetime import datetime
        return f"🕐 Current time: **{datetime.now().strftime('%H:%M:%S')}**\n📅 Date: **{datetime.now().strftime('%B %d, %Y')}**"
    
    # History
    if 'history' in user_lower or 'past' in user_lower or 'previous' in user_lower:
        return "📚 Check the **History** tab in the sidebar to see all your past searches and chat conversations!"
    
    # Features
    if 'feature' in user_lower or 'capability' in user_lower or 'what you do' in user_lower:
        return """✨ **InfoFetch AI Features:**

🔍 **Smart Research** - AI-powered web analysis
💬 **Intelligent Chat** - Conversational Q&A
📊 **Confidence Scores** - Source quality ratings
📚 **History Tracking** - All searches saved
🎯 **Accurate Sources** - Referenced information

Try asking me a question!"""
    
    # Thanks
    if any(word in user_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! 😊 Feel free to ask anything else!"
    
    # Goodbye
    if any(word in user_lower for word in ['bye', 'goodbye', 'see you', 'later']):
        return "👋 Goodbye! Come back anytime for more research!"
    
    # Default intelligent response
    return f"""🎯 I understand you're asking about: **"{user_message}"**

I'm processing your query! Here's what I can tell you:

• This is an interesting topic worth exploring
• For detailed research with web sources, use the **Research** feature
• I can provide more specific information if you ask follow-up questions

Would you like me to:
1. **Research this topic** comprehensively (use Research button)
2. **Answer specific questions** about it
3. **Explain concepts** related to it

Feel free to ask!"""

# Initialize for demo mode
OPENAI_AVAILABLE = os.getenv("OPENAI_API_KEY") is not None
SERPAPI_AVAILABLE = os.getenv("SERPAPI_API_KEY") is not None

if __name__ == "__main__":
    # Test the research agent
    query = "What are the latest AI trends in 2026?"
    
    print("\n" + "="*60)
    print("TESTING RESEARCH AGENT")
    print("="*60)
    
    result = run_research_agent(query)
    print(f"\n{'='*60}")
    print("RESULT:")
    print(f"{'='*60}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Test the chatbot
    print("\n" + "="*60)
    print("TESTING CHATBOT")
    print("="*60 + "\n")
    
    test_history = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi! How can I help you?"}
    ]
    
    response = get_chat_response("What can you do?", test_history)
    print(f"User: What can you do?")
    print(f"AI: {response}\n")