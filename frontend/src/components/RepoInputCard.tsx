import { Button } from "./ui/button";
import {
  Card,
  CardContent,
} from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Mic } from "lucide-react";
import { useState } from "react";

const GITHUB_REPO_URL_REGEX = new RegExp('^https://github\\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$');

interface LanguageButtonProps {
  language: string;
  code: string;
  flag: string;
  selected: boolean;
  onClick: (code: string) => void;
}

const LanguageButton = ({ language, code, flag, selected, onClick }: LanguageButtonProps) => (
  <Button
    variant="outline"
    onClick={() => onClick(code)}
    className={`flex items-center justify-center space-x-2 rounded-md border-2 border-black py-6 text-lg transition-all duration-200 text-black ${selected ? 'bg-retro-blue hover:bg-blue-300' : 'bg-white hover:bg-gray-100'}`}
    style={{
      boxShadow: '4px 4px 0 0 #000',
      transform: selected ? 'translate(2px, 2px)' : 'none',
    }}
  >
    <img
      src={`https://flagcdn.com/w20/${flag}.png`}
      alt={language}
      className="h-5 w-5 rounded-full"
    />
    <span>{language}</span>
  </Button>
);

interface RepoInputCardProps {
  onPodcast: (repoUrl: string, language: string) => void;
  isGenerating: boolean;
}

export function RepoInputCard({ onPodcast, isGenerating }: RepoInputCardProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("english");
  const [error, setError] = useState("");

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRepoUrl(e.target.value);
    if (error) {
      setError("");
    }
  };

  const validateUrl = () => {
    return GITHUB_REPO_URL_REGEX.test(repoUrl);
  };

  const handleSubmit = () => {
    if (validateUrl()) {
      onPodcast(repoUrl, selectedLanguage);
    } else {
      setError("Please enter a valid GitHub repository URL.");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto font-sans">
      <Card className="bg-transparent border-none shadow-none">
        <CardContent className="space-y-6 p-8 bg-white rounded-lg" style={{ boxShadow: '0 0 0 2px black, 8px 8px 0 0 black' }}>
          <div className="flex w-full items-center space-x-4">
            <div className="flex-grow">
              <Input
                type="url"
                placeholder="https://github.com/username/repo"
                value={repoUrl}
                onChange={handleUrlChange}
                className="py-6 px-4 border-2 border-black rounded-md bg-retro-blue focus:ring-2 focus:ring-blue-400 placeholder:text-slate-600"
                style={{ boxShadow: 'inset 2px 2px 0 0 #00000040' }}
              />
            </div>
            <Button
              onClick={handleSubmit}
              disabled={isGenerating || !repoUrl || !selectedLanguage}
              className="py-6 px-6 bg-retro-blue text-slate-800 border-2 border-black rounded-md hover:bg-blue-300 active:translate-y-px active:translate-x-px shadow-[4px_4px_0_0_black] disabled:bg-slate-200 disabled:text-slate-500 disabled:border-slate-300 disabled:shadow-none"
            >
              <Mic className="mr-2 h-5 w-5" />
              {isGenerating ? "Generating..." : "Podcast"}
            </Button>
          </div>
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          <div className="space-y-4 pt-4">
            <Label htmlFor="language" className="text-lg font-medium text-gray-800">
              Select a language:
            </Label>
            <div className="grid grid-cols-3 gap-4">
                <LanguageButton
                  language="English"
                  code="english"
                  flag="us"
                  selected={selectedLanguage === "english"}
                  onClick={setSelectedLanguage}
                />
              <LanguageButton
                language="Mandarin"
                code="mandarin"
                flag="cn"
                selected={selectedLanguage === "mandarin"}
                onClick={setSelectedLanguage}
              />
              <LanguageButton
                language="Spanish"
                code="spanish"
                flag="es"
                selected={selectedLanguage === "spanish"}
                onClick={setSelectedLanguage}
              />
              <LanguageButton
                language="Hindi"
                code="hindi"
                flag="in"
                selected={selectedLanguage === "hindi"}
                onClick={setSelectedLanguage}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 