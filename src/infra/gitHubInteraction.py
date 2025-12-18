import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
from ..models.repository import Repository

class GitHubGraphQLClient:
    """Anti-corruption layer for GitHub API"""
    
    def __init__(self, token: str):
        self.token = token
        self.endpoint = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def fetch_repositories(self, batch_size: int = 100, total_repos: int = 100000) -> List[Repository]:
        """Fetch repositories using GraphQL with pagination"""
        repositories = []
        cursor = None
        query = """
        query($cursor: String, $pageSize: Int!) {
          search(query: "stars:>1", type: REPOSITORY, first: $pageSize, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              ... on Repository {
                id
                databaseId
                name
                owner {
                  login
                }
                stargazerCount
              }
            }
          }
          rateLimit {
            remaining
            resetAt
          }
        }
        """
        
        while len(repositories) < total_repos:
            variables = {
                "cursor": cursor,
                "pageSize": min(batch_size, total_repos - len(repositories))
            }
            
            response = self._execute_query(query, variables)
            if not response:
                break
                
            search_result = response.get("data", {}).get("search", {})
            nodes = search_result.get("nodes", [])
            
            # Transform API response to domain models
            for node in nodes:
                if node and node.get("databaseId"):
                    repo = self._to_domain_model(node)
                    repositories.append(repo)
            
            # Handle pagination
            page_info = search_result.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
            
            # Handle rate limiting
            rate_limit = response.get("data", {}).get("rateLimit", {})
            self._handle_rate_limit(rate_limit)
            
            print(f"Fetched {len(repositories)} repositories...")
        
        return repositories[:total_repos]
    
    def _execute_query(self, query: str, variables: Dict) -> Optional[Dict]:
        """Execute GraphQL query with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.endpoint,
                    json={"query": query, "variables": variables},
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    # Rate limit exceeded
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        wait_time = int(reset_time) - int(time.time()) + 10
                        time.sleep(wait_time)
                        continue
                elif response.status_code >= 500:
                    # Server error - retry
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def _to_domain_model(self, node: Dict) -> Repository:
        """Convert API response to domain model (anti-corruption)"""
        return Repository(
            id=node["databaseId"],
            name=node["name"],
            owner_name=node["owner"]["login"],
            stars_count=node["stargazerCount"]
        )
    
    
    def _handle_rate_limit(self, rate_limit: Dict):
        """Handle rate limiting proactively"""
        remaining = rate_limit.get("remaining", 1)
        
        if remaining < 100:
            reset_at = rate_limit.get("resetAt")
            if reset_at:
                reset_time = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
                wait_time = (reset_time - datetime.now(reset_time.tzinfo)).total_seconds() + 10
                if wait_time > 0:
                    print(f"Rate limit low ({remaining}). Waiting {wait_time:.0f}s...")
                    time.sleep(wait_time)