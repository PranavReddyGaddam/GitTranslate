/**
 * Validates if a string is a valid GitHub repository URL
 * @param url - The URL to validate
 * @returns true if valid GitHub repo URL, false otherwise
 */
export const isValidGitHubRepoUrl = (url: string): boolean => {
  const githubRepoUrlRegex = /^https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+$/;
  return githubRepoUrlRegex.test(url);
};

/**
 * Extracts repository information from a GitHub URL
 * @param url - The GitHub repository URL
 * @returns Object with username and repo name, or null if invalid
 */
export function extractRepoInfo(url: string): { username: string; repo: string } | null {
  if (!isValidGitHubRepoUrl(url)) {
    return null;
  }
  
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/').filter(Boolean);
    const [username, repo] = pathParts;
    
    return { username, repo };
  } catch {
    return null;
  }
}