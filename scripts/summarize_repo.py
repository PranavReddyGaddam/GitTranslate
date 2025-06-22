import json
import argparse
import os
import logging
from typing import Dict, Any, Optional
import anthropic
from utils import create_success_response, create_error_response, validate_required_fields

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_codebase_complexity(repo_data: Dict[str, Any]) -> tuple[str, int]:
    """
    Analyzes the complexity of a codebase based on file tree and README.
    Simpler than the full metadata analysis but effective for the agentic decision.
    """
    score = 0
    file_tree = repo_data.get('file_tree', [])
    readme_content = repo_data.get('readme', '')

    # 1. Score based on file count
    num_files = len(file_tree)
    if num_files > 1000:
        score += 4
    elif num_files > 500:
        score += 3
    elif num_files > 100:
        score += 2
    elif num_files > 20:
        score += 1
    
    # 2. Score based on number of directories (indicates structure)
    directories = {os.path.dirname(f) for f in file_tree if os.path.dirname(f)}
    if len(directories) > 50:
        score += 2
    elif len(directories) > 10:
        score += 1
        
    # 3. Score based on README length
    readme_len = len(readme_content)
    if readme_len > 10000:
        score += 2
    elif readme_len > 2000:
        score += 1

    # 4. Score based on presence of key files
    key_files = ['dockerfile', 'package.json', 'requirements.txt', 'pom.xml', 'build.gradle', '.github/workflows']
    for key_file in key_files:
        if any(key_file in f.lower() for f in file_tree):
            score += 1
            
    # Cap the score at 10
    score = min(score, 10)
    
    # Determine classification
    classification = 'deep-dive' if score >= 5 else 'simple'
    
    logging.info(f"Codebase Analysis Complete. Files: {num_files}, README length: {readme_len}, Score: {score}/10. Classification: {classification}.")
    
    return classification, score


class RepoSummarizer:
    """Handles repository summarization and script generation using Anthropic's Claude."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initializes the summarizer with the Anthropic API key."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        # Use the latest recommended Sonnet model
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620')

    def _generate_prompt(self, repo_data: Dict[str, Any], summary_type: str) -> str:
        """Constructs the appropriate prompt for the given summary type."""
        repo_name = repo_data.get('repo_name', 'Unnamed Repository')
        readme = repo_data.get('readme', 'No README content was provided.')
        file_tree_str = "\n".join(repo_data.get('file_tree', []))

        context_info = f"""
Here is the context for the GitHub repository "{repo_name}":

**README Summary:**
{readme[:4000]} 

**File Structure Overview:**
<file_tree>
{file_tree_str[:3000]}
</file_tree>
        """.strip()

        if summary_type == 'simple':
            return f"""
You are a tech journalist writing a summary for a tech blog.
Based on the provided context below, write a clear, engaging, and concise summary of the GitHub repository.
The summary should be a single, well-written paragraph of about 300-400 words.

Focus on:
1.  **What is the primary purpose of this project?** What problem does it solve?
2.  **What are its key features?** What makes it stand out?
3.  **Who is the target audience?** (e.g., frontend developers, data scientists, hobbyists)
4.  **What is its potential impact?** Why is this project interesting or useful?

{context_info}

Please generate the summary now.
            """
        else:  # 'deep-dive'
            return f"""
You are a scriptwriter for a popular tech podcast.
Your task is to create an engaging, conversational, deep-dive podcast script about the GitHub repository detailed below.
The script should be a dialogue between a "Host" and an "Expert".

**Instructions:**
-   **Format:** Start each line with either "Host:" or "Expert:".
-   **Content:** The dialogue should flow naturally, explaining the project's technical details, use cases, and significance.
-   **Tone:** Make it informative but also accessible and engaging for a technical audience.
-   **Length:** The final script should be substantial enough for a 5-7 minute segment (approx. 800-1200 words).

**Topics to Cover:**
1.  **Introduction:** The Host introduces the project and its core idea.
2.  **Technical Deep-Dive:** The Expert explains the architecture, key technologies used, and interesting implementation details found in the file structure.
3.  **Use Cases:** Both discuss practical applications and who would benefit from this repo.
4.  **Conclusion:** Summarize the project's importance and where listeners can learn more.

{context_info}

Please generate the podcast script now.
            """

    def generate_script(self, repo_data: Dict[str, Any], summary_type: str) -> str:
        """Generates a script using the constructed prompt."""
        prompt = self._generate_prompt(repo_data, summary_type)

        print('************************************************')
        print(prompt)
        print('************************************************')
        try:
            logging.info(f"Generating '{summary_type}' script for {repo_data.get('repo_name')} using {self.model}...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )
            logging.info("Successfully received response from Anthropic API.")
            return response.content[0].text
        except Exception as e:
            logging.error(f"Error communicating with Anthropic API: {e}", exc_info=True)
            raise Exception("Failed to generate script due to an API error.")

    def process_repo_data(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes repository data, decides summary type, and generates the script.
        This is the main entry point for using this class as a module.
        """
        try:
            # The new data structure is simpler, so we check for the core fields.
            validate_required_fields(repo_data, ['repo_name', 'readme', 'file_tree'])

            # === Agentic Decision Step ===
            summary_type, complexity_score = analyze_codebase_complexity(repo_data)
            
            script = self.generate_script(repo_data, summary_type)
            
            word_count = len(script.split())
            
            return {
                'script': script,
                'summary_type': summary_type,
                'complexity_score': complexity_score,
                'repo_name': repo_data['repo_name'],
                'repo_url': repo_data['repo_url'],
                'word_count': word_count,
            }
            
        except Exception as e:
            logging.error(f"Failed to process repository data: {e}", exc_info=True)
            # Re-raise to be caught by the Flask app's error handler
            raise

def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description="Summarize a GitHub repository into a podcast script.")
    parser.add_argument("--input", type=str, required=True, help="Input file path containing repository data from fetch_repo_data.py.")
    parser.add_argument("--output", type=str, required=True, help="Output file path to save the generated script.")
    
    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        
        # The actual data is under the 'data' key in the success response
        repo_data = input_data.get("data")
        if not repo_data:
            raise ValueError("Input JSON must contain a 'data' field.")

        summarizer = RepoSummarizer()
        result = summarizer.process_repo_data(repo_data)
        
        with open(args.output, 'w') as f:
            json.dump(create_success_response(result), f, indent=4)
        logging.info(f"Successfully generated and saved script to {args.output}")

    except Exception as e:
        logging.error(f"A critical error occurred: {e}", exc_info=True)
        with open(args.gargs.output, 'w') as f:
            json.dump(create_error_response(str(e)), f, indent=4)

if __name__ == "__main__":
    main()