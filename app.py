from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal, Annotated
from dotenv import load_dotenv
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
import os

load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

class TweetEvaluation(BaseModel):
    evaluation: Literal["approved", "needs_improvement", "rejected"] = Field(..., description="Final evaluation result.")
    feedback: str = Field(..., description="feedback for the tweet.")

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

_llm_cache = None

def initialize_llms():
    global _llm_cache
    if _llm_cache:
        return _llm_cache
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment")
    
    base_config = {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": api_key
    }
    
    generator_llm = ChatOpenAI(model="meta-llama/llama-3.3-70b-instruct:free", temperature=0.7, **base_config)
    evaluator_llm = ChatOpenAI(model="meta-llama/llama-3.3-70b-instruct:free", temperature=0.2, **base_config)
    optimizer_llm = ChatOpenAI(model="meta-llama/llama-3.3-70b-instruct:free", temperature=0.6, **base_config)
    
    _llm_cache = (generator_llm, evaluator_llm, optimizer_llm)
    return _llm_cache

def generate_tweet(state: TweetState):
    generator_llm, _, _ = initialize_llms()
    
    tone_prompts = {
        "humorous": "You are a funny and clever Twitter/X influencer who creates hilarious, witty, family-friendly content.",
        "serious": "You are a thoughtful Twitter/X content creator who writes insightful, serious, appropriate commentary.",
        "professional": "You are a professional Twitter/X business account that creates engaging, professional, appropriate content."
    }
    
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

- Max 280 characters
- Use simple, clear English
- Make it engaging and shareable
- Always create family-friendly, appropriate content
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
    
    messages = [
        SystemMessage(content=f"You are a Twitter expert evaluating {tone} tweets for quality, effectiveness, and appropriateness."),
        HumanMessage(content=f"""
Evaluate this {tone} tweet:

Tweet: "{state['tweet']}"

Auto-reject if:
- Exceeds 280 characters
- Poor quality or inappropriate for {tone} tone
- Generic or weak content
- Contains inappropriate, offensive, or explicit content

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

@app.route('/api/health', methods=['GET'])
def health_check():
    api_key = os.getenv("OPENROUTER_API_KEY")
    return jsonify({
        'status': 'ok',
        'api_key_configured': bool(api_key)
    })

@app.route('/api/generate-tweet', methods=['POST'])
def generate_tweet_api():
    try:
        data = request.json
        if not data or 'topic' not in data:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        print(f"Received data: {data}")
        
        # Test API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return jsonify({'success': False, 'error': 'OPENROUTER_API_KEY not configured'}), 500
        
        workflow = create_workflow()
        
        initial_state = {
            "topic": data['topic'],
            "iteration": 0,
            "max_iteration": data.get('max_iterations', 2),
            "tone": data.get('tone', 'humorous'),
            "length": data.get('length', 'medium'),
            "tweet": "",
            "evaluation": "",
            "feedback": "",
            "tweet_history": [],
            "feedback_history": []
        }
        
        result = workflow.invoke(initial_state)
        
        return jsonify({
            'success': True,
            'tweet': result.get('tweet', ''),
            'evaluation': result.get('evaluation', ''),
            'feedback': result.get('feedback', ''),
            'iterations': result.get('iteration', 0),
            'tweet_history': result.get('tweet_history', []),
            'feedback_history': result.get('feedback_history', [])
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    if app.static_folder and os.path.exists(app.static_folder):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
    
    return jsonify({
        'message': 'AI Tweet Generator API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'generate': '/api/generate-tweet'
        },
        'note': 'Frontend build not found. Run: cd frontend && npm run build'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
