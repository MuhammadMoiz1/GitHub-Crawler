import requests
from dotenv import load_dotenv
import os
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

GRAPHQL_URL = "https://api.github.com/graphql"

# Simple query: fetch 5 repositories with >1000 stars
query = """
query {
  search(query: "stars:>0", type: REPOSITORY, first: 5) {
    nodes {
      ... on Repository {
        id
        name
        owner {
          login
        }
        stargazerCount
      }
    }
  }
}
"""

response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)

if response.status_code == 200:
    data = response.json()["data"]["search"]["nodes"]
    for repo in data:
        print(f"{repo['id']}-{repo['owner']['login']}/{repo['name']} - ⭐ {repo['stargazerCount']}")
else:
    print("Error:", response.status_code, response.text)
