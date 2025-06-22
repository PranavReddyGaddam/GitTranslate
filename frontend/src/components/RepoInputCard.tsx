import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Mic } from 'lucide-react';
import { isValidGitHubRepoUrl } from '../lib/validation';

interface RepoInputCardProps {
  onGeneratePodcast: (repoUrl: string, language: string) => void;
  isLoading?: boolean;
}

const languages = [
  { name: 'Mandarin', flag: '🇨🇳' },
  { name: 'Spanish', flag: '🇪🇸' },
  { name: 'Hindi', flag: '🇮🇳' }
];

export const RepoInputCard: React.FC<RepoInputCardProps> = ({ 
  onGeneratePodcast, 
  isLoading = false 
}) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (repoUrl.trim() && isValidGitHubRepoUrl(repoUrl.trim()) && selectedLanguage) {
      onGeneratePodcast(repoUrl.trim(), selectedLanguage);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setRepoUrl(url);
    
    if (url.trim()) {
      setIsValidUrl(isValidGitHubRepoUrl(url.trim()));
    } else {
      setIsValidUrl(true);
    }
  };

  const isFormValid = repoUrl.trim() && isValidUrl && !!selectedLanguage;

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg">
      <CardContent className="p-8 space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                type="url"
                placeholder="https://github.com/username/repo"
                value={repoUrl}
                onChange={handleUrlChange}
                onKeyPress={handleKeyPress}
                className={`flex-1 ${!isValidUrl && repoUrl.trim() ? 'border-red-500 focus-visible:ring-red-500' : ''}`}
                disabled={isLoading}
              />
              <Button 
                type="submit" 
                disabled={!isFormValid || isLoading}
                className="px-6"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Processing...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Mic className="h-4 w-4" />
                    Podcast
                  </div>
                )}
              </Button>
            </div>
            {!isValidUrl && repoUrl.trim() && (
              <p className="text-sm text-red-500">
                Please enter a valid GitHub repository URL (e.g., https://github.com/username/repo)
              </p>
            )}
          </div>
        </form>

        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">Select a language:</p>
          <div className="flex flex-wrap gap-3">
            {languages.map((lang) => (
              <Button
                key={lang.name}
                type="button"
                variant={selectedLanguage === lang.name ? 'default' : 'outline'}
                size="default"
                onClick={() => setSelectedLanguage(lang.name)}
                disabled={isLoading}
                className="text-sm"
              >
                <span className="mr-2 text-lg">{lang.flag}</span>
                {lang.name}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 