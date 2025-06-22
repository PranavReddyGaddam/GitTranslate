import os
import argparse
import json
from github import Github, Auth
from dotenv import load_dotenv
import logging

# Local imports
from scripts.utils import create_success_response, create_error_response, get_file_content_from_repo

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubRepoFetcher:
    """
    Handles fetching and processing of GitHub repository data using either a
    GitHub App or a Personal Access Token (PAT) for authentication.
    """
    def __init__(self):
        load_dotenv()
        self.github_api = self._authenticate()

    def _authenticate(self):
        """
        Authenticates with the GitHub API using either a GitHub App's private
        key and installation ID or a Personal Access Token (PAT).
        """
        private_key = os.getenv("GITHUB_PRIVATE_KEY")
        installation_id = os.getenv("GITHUB_INSTALLATION_ID")
        pat = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")

        if private_key and installation_id:
            try:
                logging.info("Authenticating with GitHub App...")
                auth = Auth.AppAuth(app_id=os.getenv("GITHUB_APP_ID"), private_key=private_key)
                gi = Github(app_auth=auth)
                installation = gi.get_installation(int(installation_id))
                return installation.get_github_for_installation()
            except Exception as e:
                logging.error(f"GitHub App authentication failed: {e}")
                raise
        elif pat:
            logging.info("Authenticating with Personal Access Token...")
            auth = Auth.Token(pat)
            return Github(auth=auth)
        else:
            raise ValueError("No valid GitHub credentials found. Set GITHUB_PRIVATE_KEY/GITHUB_INSTALLATION_ID or GITHUB_TOKEN/GITHUB_PAT.")

    def _get_repo_object(self, repo_url):
        """
        Parses repo URL and returns a PyGithub Repository object.
        """
        try:
            # Flexible parsing for different GitHub URL formats
            repo_name = repo_url.replace("https://github.com/", "").strip('/')
            return self.github_api.get_repo(repo_name)
        except Exception as e:
            logging.error(f"Failed to get repo object for '{repo_url}': {e}")
            raise ValueError(f"Invalid repository URL or insufficient permissions: {repo_url}")


    def _get_file_tree(self, repo, branch='main'):
        """
        Fetches the file tree for a given repository branch, respecting .gitignore.
        Returns a list of file paths.
        """
        logging.info(f"Fetching file tree for branch '{branch}'...")
        try:
            # Attempt to get the specified branch first
            git_tree = repo.get_git_tree(sha=branch, recursive=True)
        except Exception:
            # If it fails, try getting the default branch
            logging.warning(f"Branch '{branch}' not found, falling back to default branch '{repo.default_branch}'.")
            branch = repo.default_branch
            git_tree = repo.get_git_tree(sha=branch, recursive=True)

        all_files = [element.path for element in git_tree.tree if element.type == 'blob']
        
        # Respect .gitignore if present
        try:
            gitignore_content = repo.get_contents(".gitignore", ref=branch).decoded_content.decode()
            import pathspec
            spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_content.splitlines())
            included_files = [f for f in all_files if not spec.match_file(f)]
            logging.info(f"Filtered {len(all_files) - len(included_files)} files based on .gitignore.")
            return included_files
        except Exception:
            logging.warning(".gitignore not found or failed to parse. Returning all files.")
            return all_files


    def fetch_repo_data(self, repo_url):
        """
        Main method to fetch all relevant data for a repository.
        This is the primary entry point for use as a module.
        """
        try:
            repo = self._get_repo_object(repo_url)
            readme_content = get_file_content_from_repo(repo, "README.md")
            file_tree = self._get_file_tree(repo)
            
            return {
                "repo_name": repo.full_name,
                "repo_url": repo.html_url,
                "readme": readme_content,
                "file_tree": file_tree,
                "clone_url": repo.clone_url,
            }
        except Exception as e:
            logging.error(f"Error fetching data for {repo_url}: {e}", exc_info=True)
            # Re-raise the exception to be handled by the caller (e.g., the Flask app)
            raise 

def main():
    """
    Main function for command-line execution. Parses arguments, fetches data,
    and saves it to a file.
    """
    parser = argparse.ArgumentParser(description="Fetch GitHub repository data including README and file tree.")
    parser.add_argument("--input", type=str, required=True, help="Input source. Use '-' for stdin or provide a file path.")
    parser.add_argument("--output", type=str, required=True, help="Output file path to save the repository data.")
    
    args = parser.parse_args()

    try:
        # Read input from stdin or file
        if args.input == '-':
            logging.info("Reading repo URL from stdin...")
            input_data = json.load(sys.stdin)
        else:
            logging.info(f"Reading repo URL from file: {args.input}")
            with open(args.input, 'r') as f:
                input_data = json.load(f)
        
        repo_url = input_data.get("repo_url")
        if not repo_url:
            raise ValueError("repo_url not found in input data.")

        # Fetch data using the class
        fetcher = GitHubRepoFetcher()
        repo_data = fetcher.fetch_repo_data(repo_url)

        # Write success response to output file
        with open(args.output, 'w') as f:
            json.dump(create_success_response(repo_data), f, indent=4)
        logging.info(f"Successfully fetched and saved data to {args.output}")

    except Exception as e:
        # Write error response to output file
        logging.error(f"A critical error occurred: {e}", exc_info=True)
        with open(args.output, 'w') as f:
            json.dump(create_error_response(str(e)), f, indent=4)

if __name__ == "__main__":
    import sys # Import sys only when running as a script
    main()