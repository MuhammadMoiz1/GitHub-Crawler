from typing import List
from datetime import datetime, timedelta
from ..models.repository import Repository
from ..infra.gitHubInteraction import GitHubGraphQLClient
from ..infra.repository import RepositoryDatabase

class CrawlerService:
    """Application service - orchestrates the crawling process"""
    
    def __init__(self, github_client: GitHubGraphQLClient, database: RepositoryDatabase):
        self.github_client = github_client
        self.database = database
    
    def github_date(self,days_ago: int = 0) -> str:
        """
        Returns a GitHub-formatted date
        """
        date = datetime.utcnow() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")

    def crawl_and_store(self, total_repos: int = 100000, batch_size: int = 1000) -> int:
        """Main crawling workflow"""
        print(f"Starting crawl for {total_repos} repositories...")
        
        # Fetch repositories in batches
        all_repos: List[Repository] = []
        remaining = total_repos
        daysCount=0
        
        
        while remaining > 0:
            current_batch = min(batch_size, remaining)
            date= self.github_date(days_ago=daysCount)
            repos = self.github_client.fetch_repositories(
                batch_size=100,
                total_repos=current_batch,
                filterDate= date
            )
            
            if not repos :
                break
            
            # Store batch
            saved = self.database.save_repositories(repos)
            all_repos.extend(repos)
            remaining -= len(repos)
            daysCount+=1
            
            print(f"Saved {saved} repositories. Total: {len(all_repos)}/{total_repos}")
        
        print(f"Crawl complete! Total repositories: {len(all_repos)}")
        return len(all_repos)