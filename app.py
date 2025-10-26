import streamlit as st
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Literal, Annotated
from dotenv import load_dotenv
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
import time
import json
from datetime import datetime
import re

# Page config
st.set_page_config(
    page_title="🐦 AI Tweet Generator",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Dark theme CSS with smoother transitions and professional touches
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --primary: #1DA1F2;
        --secondary: #14171A;
        --accent: #657786;
        --success: #17BF63;
        --warning: #FFAD1F;
        --danger: #E0245E;
        --bg-dark: #0D1117;
        --bg-card: #161B22;
        --bg-input: #21262D;
        --text-primary: #F0F6FC;
        --text-secondary: #8B949E;
        --border: #30363D;
    }
    
    /* Hide default streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Main app styling */
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Smooth transitions */
    * {
        transition: all 0.2s ease-in-out;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-card) !important;
        border-right: 1px solid var(--border);
        padding: 1rem !important;
    }
    
    .stSidebar .stButton button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        margin: 0.5rem 0 !important;
        width: 100% !important;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stSidebar .stButton button:hover {
        background: #0B87DA !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stSlider div {
        background-color: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(29, 161, 242, 0.2);
    }
    
    /* Cards */
    .card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .card-header {
        color: var(--primary);
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem;
    }
    
    /* Tweet display */
    .tweet {
        background: var(--bg-input);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: var(--text-primary);
        line-height: 1.5;
        font-size: 1.1rem;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.2rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .badge-approved { background: var(--success); color: white; }
    .badge-pending { background: var(--primary); color: white; }
    .badge-warning { background: var(--warning); color: black; }
    
    /* History items */
    .history-item {
        background: var(--bg-input);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .history-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Remove extra spacing */
    .block-container { padding: 2rem 1rem; }
    .stButton { margin: 0.5rem 0; }
    .stTextInput, .stSelectbox, .stSlider { margin: 1rem 0; }
    
    /* Compact layout */
    .main-content { padding: 0; }
    .sidebar-content { padding: 0; }
    
    /* Improved typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    p, small {
        color: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Initialize session state variables
def init_session_state():
    if 'tweet_history' not in st.session_state:
        st.session_state.tweet_history = []
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    if 'generation_complete' not in st.session_state:
        st.session_state.generation_complete = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'prompt_history' not in st.session_state:
        st.session_state.prompt_history = []
    if 'content_rejected' not in st.session_state:
        st.session_state.content_rejected = False

# Initialize LLMs
@st.cache_resource
def initialize_llms():
    generator_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
    evaluator_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
    optimizer_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
    return generator_llm, evaluator_llm, optimizer_llm

# Pydantic models
class TweetEvaluation(BaseModel):
    evaluation: Literal["approved", "needs_improvement", "rejected"] = Field(..., description="Final evaluation result.")
    feedback: str = Field(..., description="feedback for the tweet.")

# State class
class TweetState(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal["approved", "needs_improvement", "rejected"]
    feedback: str
    iteration: int
    max_iteration: int
    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]
    tone: str
    length: str

# Node functions
def generate_tweet(state: TweetState):
    generator_llm, _, _ = initialize_llms()
    
    # Tone-based system messages
    tone_prompts = {
        "humorous": "You are a funny and clever Twitter/X influencer who creates hilarious, witty, family-friendly content.",
        "serious": "You are a thoughtful Twitter/X content creator who writes insightful, serious, appropriate commentary.",
        "professional": "You are a professional Twitter/X business account that creates engaging, professional, appropriate content."
    }
    
    # Length guidelines
    length_guides = {
        "short": "Keep it very concise (under 100 characters). Be punchy and direct.",
        "medium": "Write a medium-length tweet (100-200 characters). Balance detail with brevity.",
        "long": "Use the full space available (up to 280 characters). Be descriptive and comprehensive."
    }
    
    tone = state.get('tone', 'humorous')
    length = state.get('length', 'medium')
    
    messages = [
        SystemMessage(content=tone_prompts[tone] + " Always create family-friendly, appropriate content that follows platform guidelines."),
        HumanMessage(content=f"""
Write a {tone} and {length} tweet on the topic: "{state['topic']}".

{length_guides[length]}

Rules for {tone} tone:
""" + ("""
- Use observational humor, irony, sarcasm, or cultural references
- Think in meme logic, punchlines, or relatable takes
- Do NOT use question-answer format
- Make it genuinely funny and original
- Keep it family-friendly and appropriate
""" if tone == "humorous" else """
- Be thoughtful and insightful
- Provide valuable commentary or perspective
- Use a serious, respectful tone
- Avoid jokes or humor
- Keep it appropriate and professional
""" if tone == "serious" else """
- Maintain professional language and tone
- Focus on value, insights, or business relevance
- Be informative and authoritative
- Keep it polished and credible
- Ensure content is workplace appropriate
""") + f"""

- Max 280 characters
- Use simple, clear English
- Make it engaging and shareable
- Always create family-friendly, appropriate content
- Avoid any inappropriate, offensive, or explicit content
""")
    ]
    
    response = generator_llm.invoke(messages).content
    
    return {'tweet': response, 'tweet_history': [response]}

def evaluate_tweet(state: TweetState):
    if state.get('evaluation') == 'rejected':
        return {'evaluation': 'rejected', 'feedback': 'Content rejected due to inappropriate nature.'}
    
    _, evaluator_llm, _ = initialize_llms()
    structured_evaluator_llm = evaluator_llm.with_structured_output(TweetEvaluation)
    
    tone = state.get('tone', 'humorous')
    
    evaluation_criteria = {
        "humorous": """
1. Humor – Did it genuinely make you smile, laugh, or chuckle?
2. Originality – Is this fresh, or have you seen it a hundred times before?
3. Punchiness – Is it short, sharp, and scroll-stopping?
4. Virality Potential – Would people retweet or share it?
5. Format – Is it a well-formed tweet (not a setup-punchline joke, not a Q&A joke)?
6. Appropriateness – Is it family-friendly and platform-appropriate?
""",
        "serious": """
1. Insight – Does it provide valuable perspective or commentary?
2. Clarity – Is the message clear and well-articulated?
3. Relevance – Is it timely and relevant to the topic?
4. Engagement – Would it spark meaningful discussion?
5. Professionalism – Does it maintain appropriate serious tone?
6. Appropriateness – Is it respectful and platform-appropriate?
""",
        "professional": """
1. Value – Does it provide useful information or insights?
2. Credibility – Does it sound authoritative and trustworthy?
3. Clarity – Is it well-structured and easy to understand?
4. Engagement – Would professionals find it worth sharing?
5. Brand-appropriate – Does it maintain professional standards?
6. Appropriateness – Is it workplace-safe and platform-appropriate?
"""
    }
    
    messages = [
        SystemMessage(content=f"You are a Twitter expert evaluating {tone} tweets for quality, effectiveness, and appropriateness."),
        HumanMessage(content=f"""
Evaluate this {tone} tweet:

Tweet: "{state['tweet']}"

Use these criteria:
{evaluation_criteria[tone]}

Auto-reject if:
- Exceeds 280 characters
- Poor quality or inappropriate for {tone} tone
- Generic or weak content
- Contains inappropriate, offensive, or explicit content
- Violates platform guidelines

Respond with:
- evaluation: "approved", "needs_improvement", or "rejected"
- feedback: Specific, actionable feedback
""")
    ]
    
    response = structured_evaluator_llm.invoke(messages)
    return {
        'evaluation': response.evaluation, 
        'feedback': response.feedback, 
        'feedback_history': [response.feedback]
    }

def optimize_tweet(state: TweetState):
    if state.get('evaluation') == 'rejected':
        return state
    
    _, _, optimizer_llm = initialize_llms()
    
    tone = state.get('tone', 'humorous')
    length = state.get('length', 'medium')
    
    messages = [
        SystemMessage(content=f"You improve {tone} tweets based on feedback to make them more effective and appropriate."),
        HumanMessage(content=f"""
Improve this {tone}, {length} tweet based on feedback:

Feedback: "{state['feedback']}"
Topic: "{state['topic']}"
Original Tweet: {state['tweet']}

Create an improved version that:
- Addresses the feedback points
- Maintains {tone} tone
- Stays under 280 characters
- Is more engaging and shareable
- Remains family-friendly and appropriate
- Avoids any inappropriate content
""")
    ]
    
    response = optimizer_llm.invoke(messages).content
    
    iteration = state['iteration'] + 1
    return {'tweet': response, 'iteration': iteration, 'tweet_history': [response]}

def route_evaluation(state: TweetState):
    if state['evaluation'] == 'approved' or state['iteration'] >= state['max_iteration']:
        return 'approved'
    elif state['evaluation'] == 'rejected':
        return 'rejected'
    else:
        return 'needs_improvement'

# Create workflow
@st.cache_resource
def create_workflow():
    graph = StateGraph(TweetState)
    
    graph.add_node('generate', generate_tweet)
    graph.add_node('evaluate', evaluate_tweet)
    graph.add_node('optimize', optimize_tweet)
    
    graph.add_edge(START, 'generate')
    graph.add_edge('generate', 'evaluate')
    graph.add_conditional_edges('evaluate', route_evaluation, {
        'approved': END, 
        'needs_improvement': 'optimize',
        'rejected': END
    })
    graph.add_edge('optimize', 'evaluate')
    
    return graph.compile()

# Main app
def main():
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(to bottom, var(--bg-card), var(--bg-dark)); border-radius: 12px; margin-bottom: 2rem;">
        <h1 style="color: var(--primary); margin-bottom: 0.5rem;">🐦 AI Tweet Generator</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem;">Craft viral-worthy tweets with AI-powered optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with improved visibility
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: var(--primary); margin: 0;">⚙️ Configuration</h3>
            <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0;">Customize your tweet generation</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # Topic input
        topic = st.text_input(
            "📝 Tweet Topic *",
            placeholder="Enter a fun topic...",
            help="What would you like to tweet about?",
            key="topic_input"
        )
        
        # Tone selection
        tone = st.selectbox(
            "🎭 Tone Style",
            options=["humorous", "serious", "professional"],
            help="Choose the style and tone for your tweet",
            key="tone_select"
        )
        
        # Length selection
        length = st.selectbox(
            "📏 Tweet Length",
            options=["short", "medium", "long"],
            help="Short: <100 chars, Medium: 100-200 chars, Long: up to 280 chars",
            key="length_select"
        )
        
        # Max iterations
        max_iterations = st.slider(
            "🔄 Max Improvement Cycles",
            min_value=1,
            max_value=5,
            value=2,
            help="Maximum number of improvement iterations",
            key="iterations_slider"
        )
        
        st.markdown("""
        <div style="background: #1E2A3A; padding: 1rem; border-radius: 10px; margin-top: 1rem; border-left: 4px solid var(--primary);">
            <small style="color: var(--text-secondary);">
                <strong>💡 Tip:</strong> Keep topics engaging and positive for best results.
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate button
        generate_clicked = st.button(
            "🚀 Generate Tweet", 
            disabled=not topic,
            use_container_width=True,
            type="primary"
        )
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.tweet_history = []
            st.session_state.feedback_history = []
            st.session_state.generation_complete = False
            st.session_state.chat_history = []
            st.session_state.prompt_history = []
            st.session_state.content_rejected = False
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Generate Tweet")
        
        if generate_clicked:
            if not topic:
                st.error("Please enter a topic!")
                st.stop()
            
            # Clear previous results
            st.session_state.tweet_history = []
            st.session_state.feedback_history = []
            st.session_state.generation_complete = False
            st.session_state.content_rejected = False
            
            # Progress tracking with spinner
            with st.spinner("Generating tweet..."):
                try:
                    workflow = create_workflow()
                    
                    initial_state = {
                        "topic": topic,
                        "iteration": 0,
                        "max_iteration": max_iterations,
                        "tone": tone,
                        "length": length,
                        "tweet": "",
                        "evaluation": "",
                        "feedback": "",
                        "tweet_history": [],
                        "feedback_history": []
                    }
                    
                    # Run workflow
                    result = workflow.invoke(initial_state)
                    
                    # Store results in session state
                    st.session_state.tweet_history = result.get('tweet_history', [])
                    st.session_state.feedback_history = result.get('feedback_history', [])
                    st.session_state.final_result = result
                    st.session_state.generation_complete = True
                    
                    # Add to chat history
                    chat_entry = {
                        'session_id': len(st.session_state.chat_history) + 1,
                        'timestamp': datetime.now().isoformat(),
                        'topic': topic,
                        'tone': tone,
                        'length': length,
                        'final_tweet': result.get('tweet', ''),
                        'iterations': result.get('iteration', 0),
                        'status': result.get('evaluation', 'completed')
                    }
                    st.session_state.chat_history.append(chat_entry)
                    
                    # Add to prompt history
                    prompt_entry = {
                        'session_id': len(st.session_state.prompt_history) + 1,
                        'timestamp': datetime.now().isoformat(),
                        'topic': topic,
                        'tone': tone,
                        'length': length,
                        'max_iterations': max_iterations
                    }
                    st.session_state.prompt_history.append(prompt_entry)
                    
                    # Show final status
                    status = result.get('evaluation', 'completed')
                    if status == 'approved':
                        st.success("✅ Tweet Approved!")
                    elif status == 'rejected':
                        st.error("🚫 Content Rejected")
                    else:
                        st.warning("⚠️ Max iterations reached")
                    
                    # Show final tweet if not rejected
                    if status != 'rejected':
                        final_tweet = result.get('tweet', '')
                        st.markdown(f"""
                        <div class="tweet">
                            {final_tweet}
                            <br><br>
                            <small style="color: #657786;">
                                Characters: {len(final_tweet)}/280 | 
                                Iterations: {result.get('iteration', 0)} | 
                                Status: {status.title()}
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show current result if available
        if st.session_state.generation_complete and 'final_result' in st.session_state:
            result = st.session_state.final_result
            final_tweet = result.get('tweet', '')
            status = result.get('evaluation', 'completed')
            
            if status != 'rejected':
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### 🎯 Current Tweet")
                
                # Status badge
                if status == 'approved':
                    st.markdown(
                        '<span class="badge badge-approved">✅ Approved</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<span class="badge badge-warning">⚠️ Needs Improvement</span>',
                        unsafe_allow_html=True
                    )
                
                # Tweet display
                st.markdown(f"""
                <div class="tweet">
                    {final_tweet}
                    <br><br>
                    <small style="color: #657786;">
                        Characters: {len(final_tweet)}/280 | 
                        Iterations: {result.get('iteration', 0)}/{max_iterations} | 
                        Tone: {tone.title()} | 
                        Length: {length.title()}
                    </small>
                </div>
                """, unsafe_allow_html=True)
                
                # Copy button
                if st.button("📋 Copy Tweet", key="copy_button"):
                    st.code(final_tweet, language="text")
                    st.success("Tweet copied to clipboard!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Tweet History
        if st.session_state.tweet_history and not st.session_state.content_rejected:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📝 Tweet Evolution")
            
            for i, tweet in enumerate(st.session_state.tweet_history):
                st.markdown(f"""
                <div class="history-item">
                    <strong style="color: var(--primary);">Iteration {i + 1}</strong>
                    <p style="margin: 0.5rem 0; color: var(--text-primary);">{tweet}</p>
                    <small style="color: #657786;">
                        {len(tweet)} characters
                    </small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Feedback History
        if st.session_state.feedback_history and not st.session_state.content_rejected:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 💭 Feedback History")
            
            for i, feedback in enumerate(st.session_state.feedback_history):
                st.markdown(f"""
                <div class="history-item">
                    <strong style="color: var(--primary);">Feedback {i + 1}</strong>
                    <div style="margin: 0.5rem 0; font-size: 0.9rem; color: var(--text-primary); line-height: 1.4;">
                        {feedback}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-secondary); padding: 1rem;">
        <p>Built with ❤️ using Streamlit and LangGraph | Create engaging content! 🌟</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()