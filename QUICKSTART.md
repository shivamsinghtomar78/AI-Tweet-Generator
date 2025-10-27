# Quick Start Guide

## Prerequisites
- Python 3.11+
- Node.js 16+
- OpenRouter API Key

## Local Development Setup

### 1. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists with your API key
# OPENROUTER_API_KEY="your_key_here"

# Run backend server
python app.py
```

Backend will run on: http://localhost:5000

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on: http://localhost:3000

## Testing the Application

1. Open http://localhost:3000 in your browser
2. Enter a tweet topic (e.g., "artificial intelligence")
3. Select tone (Humorous, Serious, Professional)
4. Select length (Short, Medium, Long)
5. Adjust max iterations (1-5)
6. Click "🚀 Generate Tweet"
7. View the generated tweet with evaluation
8. Check tweet history and feedback

## Production Build

### Build Frontend
```bash
cd frontend
npm run build
```

### Test Production Build Locally
```bash
# From root directory
python app.py
```

Visit http://localhost:5000 to see the production build

## Deployment to Render

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up or log in

3. **Deploy**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Add environment variable: `OPENROUTER_API_KEY`
   - Click "Create Web Service"

4. **Access Your App**
   - Your app will be live at: `https://your-app-name.onrender.com`

## Environment Variables

Required:
- `OPENROUTER_API_KEY`: Your OpenRouter API key

Optional:
- `PORT`: Server port (default: 5000)

## Troubleshooting

### Backend Issues
- **API Key Error**: Verify OPENROUTER_API_KEY in .env file
- **Module Not Found**: Run `pip install -r requirements.txt`
- **Port Already in Use**: Change PORT in .env or kill process

### Frontend Issues
- **Dependencies Error**: Delete node_modules and run `npm install`
- **Build Fails**: Check Node.js version (16+)
- **API Connection**: Verify backend is running on port 5000

### Deployment Issues
- **Build Fails**: Check build.sh has execute permissions
- **API Key Missing**: Add OPENROUTER_API_KEY in Render dashboard
- **Timeout**: Increase max iterations or check API limits

## Features Overview

✨ **AI-Powered Generation**: Uses LangGraph workflow with LLM
🎨 **Multiple Tones**: Humorous, Serious, Professional
📏 **Length Control**: Short, Medium, Long tweets
🔄 **Iterative Improvement**: AI evaluates and optimizes
📊 **Real-time Feedback**: Shows generation process
🎭 **Modern UI**: Dark theme with smooth animations
📱 **Responsive**: Works on all devices

## API Endpoints

- `GET /api/health`: Health check
- `POST /api/generate-tweet`: Generate tweet
  ```json
  {
    "topic": "string",
    "tone": "humorous|serious|professional",
    "length": "short|medium|long",
    "max_iterations": 1-5
  }
  ```

## Tech Stack

- **Backend**: Flask, LangGraph, LangChain
- **Frontend**: React, Tailwind CSS, ShadCN UI
- **AI**: OpenRouter (Meta Llama 3.3 70B)
- **Deployment**: Render

## Support

For issues or questions:
1. Check this guide
2. Review README.md
3. Check ENHANCEMENTS.md for UI details
4. Review error messages in console

Happy tweeting! 🚀
