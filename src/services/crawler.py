from typing import List
from ..models.repository import Repository
from ..infra.gitHubInteraction import GitHubGraphQLClient
from ..infra.repository import RepositoryDatabase

class CrawlerService:
    """Application service - orchestrates the crawling process"""
    
    def __init__(self, github_client: GitHubGraphQLClient, database: RepositoryDatabase):
        self.github_client = github_client
        self.database = database
    
    def crawl_and_store(self, total_repos: int = 100000, batch_size: int = 1000) -> int:
        """Main crawling workflow"""
        print(f"Starting crawl for {total_repos} repositories...")
        
        # Fetch repositories in batches
        all_repos: List[Repository] = []
        remaining = total_repos
        
        while remaining > 0:
            current_batch = min(batch_size, remaining)
            repos = self.github_client.fetch_repositories(
                batch_size=100,
                total_repos=current_batch
            )
            
            if not repos:
                break
            
            # Store batch
            saved = self.database.save_repositories(repos)
            all_repos.extend(repos)
            remaining -= len(repos)
            
            print(f"Saved {saved} repositories. Total: {len(all_repos)}/{total_repos}")
        
        print(f"Crawl complete! Total repositories: {len(all_repos)}")
        return len(all_repos)