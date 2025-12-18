from .config.config import get_database_url, get_Auth_Token
from .infra.gitHubInteraction import GitHubGraphQLClient
from .infra.repository import RepositoryDatabase
from .services.crawler import CrawlerService


def main():
    # Configuration
    github_token = get_Auth_Token()
    database_url = get_database_url()
    
    # Dependencies
    github_client = GitHubGraphQLClient(github_token)
    database = RepositoryDatabase(database_url)
    crawler = CrawlerService(github_client, database)
    
    # Execute
    total = crawler.crawl_and_store(total_repos=1000)
    print(f"Successfully crawled {total} repositories")

if __name__ == "__main__":
    main()