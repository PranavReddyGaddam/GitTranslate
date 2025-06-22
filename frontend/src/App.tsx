import { useState, useRef, useEffect } from "react";
import "./index.css";
import { RepoInputCard } from "./components/RepoInputCard";
import { AudioPlayer } from "./components/AudioPlayer";
import ConstellationCanvas from "./components/ConstellationCanvas";
import { Navbar } from "./components/Navbar";

function App() {
  const [showAudioPlayer, setShowAudioPlayer] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const playerContainerRef = useRef<HTMLDivElement>(null);
  const [workflowId, setWorkflowId] = useState("");

  const handlePodcastGeneration = async (repoUrl: string, language: string) => {
    setIsGenerating(true);
    setShowAudioPlayer(false);
    setWorkflowId("");

    // Scroll the loading message into view
    setTimeout(() => {
        playerContainerRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }, 100);

    try {
      const response = await fetch("http://3.95.215.8:8000/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          language: language
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setWorkflowId(data.workflow_id);

    } catch (error) {
      console.error("Failed to start podcast generation:", error);
      alert("Sorry, something went wrong. Please try again later.");
      setIsGenerating(false);
    }
  };
  
  const checkWorkflowStatus = async (id: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/status/${id}`);

      if (!response.ok) {
        if (response.status !== 404) {
          throw new Error(`API error: ${response.statusText}`);
        }
        return;
      }

      const data = await response.json();

      if (data && data.result) {
        setAudioUrl(data.result);
        setShowAudioPlayer(true);
        setIsGenerating(false);
        setWorkflowId("");
      } else {
        console.log("Workflow status:", data.status || "In progress");
      }

    } catch (error) {
      console.error("Error checking workflow status:", error);
      alert("There was an error retrieving the podcast. Please try again.");
      setIsGenerating(false);
      setWorkflowId("");
    }
  };

  useEffect(() => {
    if (workflowId) {
      const intervalId = setInterval(() => {
        checkWorkflowStatus(workflowId);
      }, 3000);

      return () => clearInterval(intervalId);
    }
  }, [workflowId]);

  return (
    <main
      className="relative min-h-screen w-full bg-sky-100 flex flex-col items-center antialiased overflow-x-hidden"
    >
      <Navbar />
      <ConstellationCanvas />
      <div className="z-10 flex flex-col items-center justify-center text-center w-full flex-grow px-4 pt-32 pb-12">
        <div className="text-center mb-12">
            <h1 className="text-6xl font-bold text-slate-800 flex overflow-hidden justify-center pb-4">
              <span className="animate-text-slide-in block" style={{ animationDelay: '0s', animationFillMode: 'backwards' }}>
                Repository&nbsp;
              </span>
              <span className="animate-text-slide-in block" style={{ animationDelay: '0.15s', animationFillMode: 'backwards' }}>
                to&nbsp;
              </span>
              <span className="animate-text-slide-in block text-orange-500" style={{ animationDelay: '0.3s', animationFillMode: 'backwards' }}>
                Podcast
              </span>
            </h1>
          <p className="text-2xl font-medium text-gray-700 max-w-2xl mx-auto mt-4 text-balance">
            Now in Your Native Language — Learn Code the Way You Think.
          </p>
        </div>

        <div className="w-full mb-8 max-w-2xl">
          <RepoInputCard 
            onPodcast={handlePodcastGeneration}
            isGenerating={isGenerating}
          />
        </div>

        <div ref={playerContainerRef} className="w-full h-32 flex items-center justify-center px-4">
          {isGenerating ? (
             <div className="flex flex-col items-center gap-4 text-slate-700 animate-fade-in-up">
                <svg className="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-lg font-medium text-center text-balance">
                  Please wait while your tailored podcast is being generated...
                </p>
              </div>
          ) : (
            showAudioPlayer && <AudioPlayer src={audioUrl} />
          )}
        </div>
      </div>
    </main>
  );
}

export default App;
