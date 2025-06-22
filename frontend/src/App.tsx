import React, { useState } from 'react';
import { RepoInputCard } from './components/RepoInputCard';
import { Sparkles } from 'lucide-react';

function App() {
  const [isLoading, setIsLoading] = useState(false);

  const generatePodcast = async (repoUrl: string, language: string) => {
    setIsLoading(true);
    
    try {
      // Placeholder function - replace with actual API call
      console.log('Generating podcast for:', repoUrl, 'Language:', language);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // TODO: Replace with actual API call to your backend
      // const response = await fetch('/api/generate-podcast', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ repoUrl, language })
      // });
      
      // Show success message (you can replace this with a toast notification)
      alert(`Podcast generation started for ${repoUrl} in ${language}!`);
      
    } catch (error) {
      console.error('Error generating podcast:', error);
      alert('Error generating podcast. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col items-center justify-center p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* Hero Section */}
      <div className="relative z-10 text-center mb-12">
        <div className="flex items-center justify-center gap-4 mb-6">
          <Sparkles className="h-12 w-12 text-purple-600" />
          <h1 className="text-6xl font-bold text-slate-800">
            Repository to Podcast
          </h1>
          <Sparkles className="h-12 w-12 text-blue-600" />
        </div>
        <p className="text-2xl font-medium text-gray-700 max-w-2xl mx-auto">
           Now in your language.
        </p>
      </div>

      {/* Main content */}
      <div className="relative z-10 w-full">
        <RepoInputCard 
          onGeneratePodcast={generatePodcast}
          isLoading={isLoading}
        />
      </div>

      {/* Footer */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-center">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4" />
          <span>Powered by AI</span>
          <Sparkles className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
}

export default App;
