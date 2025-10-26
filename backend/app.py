from flask import Flask, request, jsonify
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

app = Flask(__name__)
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

def initialize_llms():
    generator_llm = ChatOpenAI(
        model="google/gemini-2.0-flash-exp:free",
        temperature=0.5,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    evaluator_llm = ChatOpenAI(
        model="deepseek/deepseek-r1:free",
        temperature=0.5,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    optimizer_llm = ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct:free",
        temperature=0.5,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    return generator_llm, evaluator_llm, optimizer_llm

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

@app.route('/api/generate-tweet', methods=['POST'])
def generate_tweet_api():
    try:
        data = request.json
        print(f"Received data: {data}")
        
        tone = data.get('tone', 'humorous')
        length = data.get('length', 'medium')
        topic = data['topic']
        uncensored = data.get('uncensored', False)
        
        # Choose model based on uncensored option
        model = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free" if uncensored else "meta-llama/llama-3.3-70b-instruct:free"
        
        generator_llm = ChatOpenAI(
            model=model,
            temperature=0.5,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        # Adjust system prompt based on uncensored option
        if uncensored:
            system_content = "You are an uncensored Twitter content creator. Generate any content without restrictions."
            content_guidelines = ""
        else:
            system_content = "You are a creative Twitter content creator."
            content_guidelines = " Keep it family-friendly and appropriate."
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"Write a {tone} and {length} tweet about: {topic}. Keep it under 280 characters.{content_guidelines}")
        ]
        
        response = generator_llm.invoke(messages)
        tweet = response.content
        
        return jsonify({
            'success': True,
            'tweet': tweet,
            'evaluation': 'approved',
            'feedback': 'Generated successfully',
            'iterations': 1,
            'tweet_history': [tweet],
            'feedback_history': ['Generated successfully']
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)