# AI Tweet Generator

A modern web application that generates high-quality tweets using AI with Flask backend and React frontend.

## Architecture

- **Backend**: Flask with LangChain/LangGraph for AI workflow orchestration
- **Frontend**: React with Tailwind CSS and ShadCN UI components
- **AI Models**: Google Gemini (1.5 Flash for generation, 2.0 Flash for evaluation/optimization)

## Local Development

### Backend

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your API key:
```
OPENROUTER_API_KEY="your_key_here"
```

4. Run Flask server:
```bash
python app.py
```

### Frontend

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## Features

### Core Functionality
- **Multi-tone Generation**: Humorous, Serious, Professional
- **Length Control**: Short, Medium, Long tweets
- **Iterative Improvement**: AI evaluates and optimizes tweets (1-5 iterations)
- **Real-time Feedback**: Shows generation process and history
- **Tweet History**: View all iterations of generated tweets
- **Feedback History**: See AI evaluation feedback for each iteration

### Modern UI/UX
- **Smooth Animations**: Fade-in, slide-up, scale-in effects throughout
- **Loading States**: Skeleton screens and shimmer effects
- **Interactive Elements**: Hover effects, active states, transitions
- **Gradient Design**: Modern gradients on header, buttons, and accents
- **Icon System**: Lucide React icons for visual clarity
- **Badge Displays**: Metadata shown in styled badges
- **Sticky Sidebar**: Easy access to controls while scrolling
- **Keyboard Support**: Enter key to generate tweets
- **Copy to Clipboard**: One-click tweet copying
- **Dark Theme**: Professional dark mode with ShadCN components
- **Responsive Design**: Works perfectly on all device sizes

## API Endpoints

- `POST /api/generate-tweet`: Generate and optimize tweets

## Environment Variables

Required in `.env` file:
- `OPENROUTER_API_KEY`: OpenRouter API key (required)

## Deployment

### Deploy to Render (Single Service)

This app is configured for one-click deployment on Render:

1. Push code to GitHub
2. Connect repository to Render
3. Render auto-detects `render.yaml`
4. Add `OPENROUTER_API_KEY` environment variable
5. Deploy!

See [QUICKSTART.md](QUICKSTART.md) and [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed instructions.

**Live URL:** `https://your-app-name.onrender.com`

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Complete setup and deployment guide
- **[ENHANCEMENTS.md](ENHANCEMENTS.md)**: Detailed UI/UX improvements
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**: Pre-deployment verification
- **[ANALYSIS_SUMMARY.md](ANALYSIS_SUMMARY.md)**: Complete application analysis

## Tech Stack Details

### Backend
- **Flask**: Web framework
- **LangGraph**: AI workflow orchestration
- **LangChain**: LLM integration
- **OpenRouter**: API gateway for LLMs
- **Pydantic**: Data validation
- **Gunicorn**: Production WSGI server

### Frontend
- **React 18**: UI framework
- **Tailwind CSS**: Utility-first styling
- **ShadCN UI**: Component library
- **Lucide React**: Icon system
- **Axios**: HTTP client
- **Custom Animations**: GPU-accelerated CSS animations

### AI Models
- **Meta Llama 3.3 70B Instruct**: Generation, evaluation, and optimization
- **Temperature Control**: Optimized for each task (0.2-0.7)

## Performance

- **Initial Load**: < 3 seconds
- **Tweet Generation**: 5-15 seconds (depends on iterations)
- **Animations**: 60 FPS (GPU-accelerated)
- **Mobile Responsive**: All screen sizes supported