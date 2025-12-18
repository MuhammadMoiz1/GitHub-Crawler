import psycopg2
from psycopg2.extras import execute_batch
from typing import List
from ..models.repository import Repository

class RepositoryDatabase:
    """Database operations layer"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def save_repositories(self, repositories: List[Repository]) -> int:
        """Save repositories with metrics efficiently"""
        conn = psycopg2.connect(self.database_url)
        saved_count = 0
        
        try:
            with conn.cursor() as cursor:
                
                repo_data = [
                    (
                        r.id, r.full_name, r.owner_login
                    )
                    for r in repositories
                ]
                
                execute_batch(cursor, """
                    INSERT INTO repositories 
                    (id, full_name, owner_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO DO UPDATE SET
                        full_name = EXCLUDED.full_name,
                        owner_name = EXCLUDED.owner_name
                """, repo_data)
                
                # Insert metrics (time-series data)
                metrics_data = [
                    (
                        r.id, r.stars_count
                    )
                    for r in repositories
                ]
                
                execute_batch(cursor, """
                    INSERT INTO repository_metrics
                    (repository_id, stars_count)
                    VALUES (%s, %s)
                """, metrics_data)
                
                conn.commit()
                saved_count = len(repositories)
                
        except Exception as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()
        
        return saved_count