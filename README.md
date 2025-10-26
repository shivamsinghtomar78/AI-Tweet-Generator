# AI Tweet Generator

A modern web application that generates high-quality tweets using AI with Flask backend and React frontend.

## Architecture

- **Backend**: Flask with LangChain/LangGraph for AI workflow orchestration
- **Frontend**: React with Tailwind CSS and ShadCN UI components
- **AI Models**: Google Gemini (1.5 Flash for generation, 2.0 Flash for evaluation/optimization)

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy .env file from root to backend directory

5. Run Flask server:
```bash
python app.py
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Install additional dependencies:
```bash
npm install tailwindcss-animate @radix-ui/react-slot
```

4. Start React development server:
```bash
npm start
```

## Features

- **Multi-tone Generation**: Humorous, Serious, Professional
- **Length Control**: Short, Medium, Long tweets
- **Iterative Improvement**: AI evaluates and optimizes tweets
- **Real-time Feedback**: Shows generation process and history
- **Modern UI**: Dark theme with ShadCN components
- **Responsive Design**: Works on all device sizes

## API Endpoints

- `POST /api/generate-tweet`: Generate and optimize tweets

## Environment Variables

Required in `.env` file:
- `GOOGLE_API_KEY`: Google Gemini API key
- `OPENROUTER_API_KEY`: OpenRouter API key (optional)
- `HUGGINGFACEHUB_API_TOKEN`: HuggingFace API token (optional)