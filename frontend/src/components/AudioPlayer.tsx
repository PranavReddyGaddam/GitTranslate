import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Play, Pause, Download } from 'lucide-react';
import { Card, CardContent } from './ui/card';

interface AudioPlayerProps {
  src: string;
  onClose?: () => void;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ src }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      // Autoplay when component mounts
      audio.play().catch(error => console.error("Autoplay was prevented:", error));
      setIsPlaying(true);
    }
  }, [src]);

  const togglePlayPause = () => {
    if (isPlaying) {
      audioRef.current?.pause();
    } else {
      audioRef.current?.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    setCurrentTime(audioRef.current?.currentTime || 0);
  };

  const handleLoadedMetadata = () => {
    setDuration(audioRef.current?.duration || 0);
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const progressRect = progressRef.current?.getBoundingClientRect();
    if (progressRect && audioRef.current) {
      const clickPosition = e.clientX - progressRect.left;
      const progressWidth = progressRect.width;
      const newTime = (clickPosition / progressWidth) * duration;
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };
  
  const formatTime = (timeInSeconds: number) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg animate-fade-in-up">
      <CardContent className="p-4 flex items-center gap-4">
        <audio
          ref={audioRef}
          src={src}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
        />
        <Button onClick={togglePlayPause} size="icon" className="rounded-full flex-shrink-0">
          {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
        </Button>
        <div className="flex-grow flex items-center gap-3">
            <span className="text-xs text-muted-foreground w-10 text-right">{formatTime(currentTime)}</span>
            <div 
              ref={progressRef}
              className="w-full bg-slate-200 rounded-full h-1.5 cursor-pointer group"
              onClick={handleProgressClick}
            >
                <div 
                    className="bg-slate-800 h-1.5 rounded-full relative group-hover:bg-blue-600" 
                    style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
                >
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 h-3 w-3 bg-white rounded-full border border-slate-300 shadow opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
            </div>
            <span className="text-xs text-muted-foreground w-10">{formatTime(duration)}</span>
        </div>
        <a href={src} download="podcast.mp3">
          <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
            <Download className="h-5 w-5" />
          </Button>
        </a>
      </CardContent>
    </Card>
  );
}; 