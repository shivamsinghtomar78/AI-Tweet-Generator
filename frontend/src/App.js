import React, { useState } from 'react';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Input } from './components/ui/input';
import { Select } from './components/ui/select';
import { Slider } from './components/ui/slider';
import { LoadingSkeleton } from './components/LoadingSkeleton';
import { Twitter, Settings, History, MessageSquare, Copy, Trash2, Sparkles } from 'lucide-react';
import './index.css';

function App() {
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('humorous');
  const [length, setLength] = useState('medium');
  const [maxIterations, setMaxIterations] = useState(2);
  const [uncensored, setUncensored] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const generateTweet = async () => {
    if (!topic.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/generate-tweet', {
        topic,
        tone,
        length,
        max_iterations: maxIterations,
        uncensored
      });
      
      if (response.data.success) {
        setResult(response.data);
      } else {
        setError(response.data.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Error generating tweet:', error);
      console.error('Error response:', error.response);
      setError(error.response?.data?.error || error.message || 'Failed to generate tweet. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const [copySuccess, setCopySuccess] = useState(false);
  const [error, setError] = useState(null);

  const copyTweet = (text) => {
    navigator.clipboard.writeText(text);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const clearHistory = () => {
    setResult(null);
  };

  const getStatusBadge = (evaluation) => {
    const badges = {
      approved: 'bg-green-600 text-white',
      needs_improvement: 'bg-yellow-600 text-white',
      rejected: 'bg-red-600 text-white'
    };
    return badges[evaluation] || 'bg-gray-600 text-white';
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <div className="bg-gradient-to-b from-card to-background border-b border-border relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-primary/10 animate-pulse-slow"></div>
        <div className="container mx-auto px-4 py-8 text-center relative z-10">
          <div className="flex items-center justify-center gap-3 mb-4 animate-fade-in">
            <Twitter className="h-8 w-8 text-primary animate-pulse" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">AI Tweet Generator</h1>
          </div>
          <p className="text-muted-foreground text-lg animate-slide-up">Craft viral-worthy tweets with AI-powered optimization</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Sidebar */}
          <div className="lg:col-span-1 animate-slide-up">
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-primary" />
                    Tweet Topic *
                  </label>
                  <Input
                    placeholder="Enter a fun topic..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !loading && topic.trim() && generateTweet()}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tone Style</label>
                  <Select value={tone} onChange={(e) => setTone(e.target.value)}>
                    <option value="humorous">Humorous</option>
                    <option value="serious">Serious</option>
                    <option value="professional">Professional</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tweet Length</label>
                  <Select value={length} onChange={(e) => setLength(e.target.value)}>
                    <option value="short">Short (&lt;100 chars)</option>
                    <option value="medium">Medium (100-200 chars)</option>
                    <option value="long">Long (up to 280 chars)</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Max Improvement Cycles: {maxIterations}
                  </label>
                  <Slider
                    min="1"
                    max="5"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(parseInt(e.target.value))}
                  />
                </div>

                <div className="bg-yellow-900/20 border border-yellow-600/50 p-3 rounded-lg">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={uncensored}
                      onChange={(e) => setUncensored(e.target.checked)}
                      className="rounded cursor-pointer"
                    />
                    <span className="text-sm font-medium">🔓 Uncensored Mode</span>
                  </label>
                  <p className="text-xs text-muted-foreground mt-1">Removes content safety filters</p>
                </div>

                <div className="bg-gradient-to-r from-primary/10 to-blue-500/10 p-4 rounded-lg border border-primary/20">
                  <p className="text-sm text-muted-foreground">
                    <strong className="text-primary">💡 Tip:</strong> Keep topics engaging and positive for best results.
                  </p>
                </div>

                <Button 
                  onClick={generateTweet} 
                  disabled={!topic.trim() || loading}
                  className="w-full relative overflow-hidden group"
                  size="lg"
                >
                  {loading && (
                    <span className="absolute inset-0 loading-shimmer"></span>
                  )}
                  <span className="relative z-10">
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        Generating...
                      </span>
                    ) : '🚀 Generate Tweet'}
                  </span>
                </Button>

                <Button 
                  onClick={clearHistory} 
                  variant="outline"
                  className="w-full"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear History
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Error Display */}
            {error && (
              <div className="bg-red-900/20 border border-red-600 text-red-400 p-4 rounded-lg animate-scale-in">
                <strong>Error:</strong> {error}
              </div>
            )}
            
            {/* Loading State */}
            {loading && <LoadingSkeleton />}
            
            {/* Current Result */}
            {!loading && result && (
              <Card className="animate-scale-in">
                <CardHeader>
                  <CardTitle>🎯 Generated Tweet</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium transition-all duration-300 ${getStatusBadge(result.evaluation)}`}>
                      {result.evaluation === 'approved' ? '✅ Approved' : 
                       result.evaluation === 'needs_improvement' ? '⚠️ Needs Improvement' : 
                       '🚫 Rejected'}
                    </span>
                  </div>

                  <div className="bg-muted p-4 rounded-lg mb-4 border border-primary/20 hover:border-primary/40 transition-all duration-300">
                    <p className="text-lg leading-relaxed">{result.tweet}</p>
                    <div className="mt-3 flex flex-wrap gap-2 text-sm text-muted-foreground">
                      <span className="px-2 py-1 bg-background rounded">📝 {result.tweet.length}/280</span>
                      <span className="px-2 py-1 bg-background rounded">🔄 {result.iterations} iterations</span>
                      <span className="px-2 py-1 bg-background rounded">🎭 {tone}</span>
                      <span className="px-2 py-1 bg-background rounded">📏 {length}</span>
                    </div>
                  </div>

                  <Button onClick={() => copyTweet(result.tweet)} variant="outline" className="group">
                    <Copy className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
                    {copySuccess ? '✓ Copied!' : 'Copy Tweet'}
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Tweet History */}
            {result && result.tweet_history && result.tweet_history.length > 0 && (
              <Card className="animate-slide-up" style={{animationDelay: '0.1s'}}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <History className="h-5 w-5" />
                    Tweet Evolution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {result.tweet_history.map((tweet, index) => (
                      <div key={index} className="bg-muted p-3 rounded-lg border border-transparent hover:border-primary/30 transition-all duration-300 transform hover:scale-[1.02]">
                        <div className="font-medium text-primary mb-2 flex items-center gap-2">
                          <span className="inline-block w-6 h-6 rounded-full bg-primary/20 text-center text-xs leading-6">{index + 1}</span>
                          Iteration {index + 1}
                        </div>
                        <p className="text-sm">{tweet}</p>
                        <div className="text-xs text-muted-foreground mt-1">
                          📝 {tweet.length} characters
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Feedback History */}
            {result && result.feedback_history && result.feedback_history.length > 0 && (
              <Card className="animate-slide-up" style={{animationDelay: '0.2s'}}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    Feedback History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {result.feedback_history.map((feedback, index) => (
                      <div key={index} className="bg-muted p-3 rounded-lg border border-transparent hover:border-primary/30 transition-all duration-300">
                        <div className="font-medium text-primary mb-2 flex items-center gap-2">
                          <MessageSquare className="h-4 w-4" />
                          Feedback {index + 1}
                        </div>
                        <p className="text-sm leading-relaxed">{feedback}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-12 bg-gradient-to-t from-card to-transparent">
        <div className="container mx-auto px-4 py-6 text-center text-muted-foreground">
          <p className="animate-fade-in">Built with ❤️ using Flask, React, and LangGraph | Create engaging content! 🌟</p>
        </div>
      </footer>
    </div>
  );
}

export default App;