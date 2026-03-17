import os
from turtle import update
from fastmcp import FastMCP
import httpx
from config import settings
import json
from typing import Optional, Dict, Any
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

gitHubMcpServer = FastMCP("GitHub")

def getHeader():
    # sending partial header 
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.GITHUB_ACCESS_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

@gitHubMcpServer.tool()
async def getUserRepo(repoName: str):
    """
    Fetches detailed information for a specific GitHub repository.

    Args: 
        repoName(str): he name of the repository to be fetched
    
    Return:
        str: A JSON string containing:
            - id (int): The unique GitHub database ID for the repository.
            - repoName (str): The full name of the repository.
            - url (str): The browser URL to view the repository on GitHub.
            - private (bool): Whether the repository is private (true) or public (false).
            - description (str): The short summary text for the repository.
            - created_at (str): ISO 8601 timestamp of when the repo was created.
            - updated_at (str): ISO 8601 timestamp of the last push or modification.
            - languages (str): The primary programming language detected by GitHub.
            - open_issues_count (int): Total number of open issues and pull requests.
            - topics (list): List of project tags.
    """
    headers = getHeader()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/repos/{settings.OWNER_NAME}/{repoName}", headers=headers)

            if response.status_code == 200:
                data = response.json()
                repoBody = {
                    "id": data.get("id"),
                    "repoName": data.get("name"),
                    "url": data.get("html_url"),
                    "private": data.get("private"),
                    "description": data.get("description"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "languages": data.get("language"),
                    "open_issues_count": data.get("open_issues_count"),
                    "topics": data.get("topics")
                }
                return json.dumps(repoBody)
            elif response.status_code == 301:
                return "status_code: 301 -> Moved Permanently"
            elif response.status_code == 403:
                return "status_code: 403 -> forbidden"
            elif response.status_code == 404:
                return "status_code: 404 -> Resource not found"
    except Exception as e:
        return f"Error: some internal server issue {e}"
        
@gitHubMcpServer.tool()
async def updateRepo(
    repoName: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    homepage: Optional[str] = None,
    private: Optional[bool] = None,
    visibility: Optional[str] = None,
    has_issues: Optional[bool] = None,
    has_projects: Optional[bool] = None,
    has_wiki: Optional[bool] = None,
    is_template: Optional[bool] = None,
    default_branch: Optional[str] = None,
    allow_squash_merge: Optional[bool] = None,
    allow_merge_commit: Optional[bool] = None,
    allow_rebase_merge: Optional[bool] = None,
    allow_auto_merge: Optional[bool] = None,
    delete_branch_on_merge: Optional[bool] = None,
    archived: Optional[bool] = None,
    allow_forking: Optional[bool] = None
):
    """
    Updates an existing GitHub repository for 'moksh555'. 
    Only provide the arguments that need to be changed.

    Args:
        repoName (str): The current name of the repository to update.
        name (str): The new name for the repository.
        description (str): A short description of the repository.
        homepage (str): A URL with more information about the repository.
        private (bool): True to make the repository private, false for public.
        visibility (str): Can be 'public' or 'private'.
        has_issues (bool): Whether to enable issues.
        has_projects (bool): Whether to enable projects.
        has_wiki (bool): Whether to enable the wiki.
        is_template (bool): True to make this a template repository.
        default_branch (str): Updates the default branch name.
        allow_squash_merge (bool): Allow/prevent squash-merging.
        archived (bool): Set to true to archive the repository.
    
    Return: 
        str: A JSON string containing:
            - id (int): The unique GitHub database ID for the repository.
            - repoName (str): The full name of the repository.
            - url (str): The browser URL to view the repository on GitHub.
            - private (bool): Whether the repository is private (true) or public (false).
            - created_at (str): ISO 8601 timestamp of when the repo was created.
    """
    headers = getHeader()

    updateData = {k:v for k,v in locals().items() if v is not None and k not in ['repoName', 'headers']}

    if not updateData:
        return "No data provided to patch"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.github.com/repos/{settings.OWNER_NAME}/{repoName}",
                headers=headers,
                json=updateData
                )

            if response.status_code == 200:
                data = response.json()
                updatedRepoBody = {
                    "id": data.get("id"),
                    "repoName": data.get("name"),
                    "private": data.get("private"),
                    "url": data.get("html_url"),
                    "updated_at": data.get("updated_at"),

                }
                return json.dumps(updatedRepoBody)
            error_codes = {
                307: "Temporary Redirect",
                403: "Forbidden (Check your Token permissions)",
                404: "Resource not found",
                422: "Validation failed (Invalid field values)"
            }
            return error_codes.get(response.status_code, f"GitHub Error: {response.status_code}")
    except Exception as e:
        return f"Error: some internal server issue {e}"


@gitHubMcpServer.tool()
async def getRepoActivity(
    repoName: str,
    direction: Optional[str] = None,
    ref: Optional[str] = None,
    actor: Optional[str] = None,
    time_period: Optional[str] = None,
    activity_type: Optional[str] = None
    ):
    """
    Fetches a list of recent activities (pushes, merges, branch changes) for a repository.
    Use this to find SHA hashes, then use the Commit tool to see specific changes.

    Args:
        repoName (str): The name of the repository.
        direction (str): The direction of the activity (asc or desc).
        ref (str): The git reference (e.g., 'refs/heads/main').
        actor (str): Filter by the username of the person who performed the activity.
        timePeriod (str): Filter by time (e.g., 'day', 'week', 'month').
        activityType (str): Type of activity (e.g., 'push', 'force_push', 'branch_creation').
    
    Returns:
        str: A JSON string containing a list of activities, each with:
            - id (int): Unique activity ID.
            - user (str): The username of the person who pushed.
            - type (str): The type of activity (e.g., 'normal' push).
            - branch (str): The branch name.
            - before (str): The SHA of the repo before the activity.
            - after (str): The SHA of the repo after the activity.
            - timestamp (str): ISO 8601 timestamp of the activity.
    """

    headers = getHeader()
    queryParams = {k:v for k,v in locals().items() if v is not None and k not in ["headers", "repoName"] }

    try:
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{settings.OWNER_NAME}/{repoName}/activity",
                headers=headers,
                params=queryParams
            )

            if response.status_code == 200:
                data = response.json()
                allActivities = []
                for activity in response.json():
                    allActivities.append({
                        "id": activity.get("id"),
                        "before": activity.get("before"),
                        "after": activity.get("after"),
                        "type": activity.get("activity_type"),
                        "user": activity.get("actor").get("login"),
                        "branch": activity.get("ref").replace("refs/heads"),
                        "timestamp": activity.get("timestamp")
                    })
                return json.dumps(allActivities)
            
            error = {
                422: "Validation failed, or the endpoint has been spammed"
            }
            return f" GitHub Error: {error[response.status_code]}"
    except Exception as e:
        return f"Internal Server error {e}"

@gitHubMcpServer.tool()
async def geAllUserRepo(
    type: Optional[str] = None,
    sort: Optional[str] = None,
    per_page: Optional[str] = 30,
    page: Optional[str] = 1,
    direction: Optional[str] = None,
):
    """
    Retrieves a list of repositories for the authenticated user. By deafult it only returns 30 repositories
    
    Args:
        type (str): Can be one of 'all', 'owner', 'member'. Default is 'owner'.
        sort (str): Can be one of 'created', 'updated', 'pushed', 'full_name'.
        direction (str): 'asc' or 'desc'.
        per_page (int): Results per page (max 100).
        page (int): Page number to retrieve.

    Returns:
        str: A JSON string containing a list of repositories with their id, name, and description.
    """
    queryParams = {k:v for k,v in locals().items() if v is not None and k not in ["headers"]}
    headers = getHeader()
    

    try: 
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/users/{settings.OWNER_NAME}/repos",
                headers=headers,
                params=queryParams
            )
            repositories = response.json()
            repoInfo = []

            for repo in repositories:
                repoInfo.append({
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "description": repo.get("description")
                })
            
            return json.dumps(repoInfo)
    except Exception as e:
        return f"Internal Server error {e}"

@gitHubMcpServer.tool()
async def createRepository(
    name: str,
    description: Optional[str] = None,
    visibility: Optional[str] = None,
    auto_init: Optional[bool] = True,
    ):
    """
    Creates a new repository for the user 

    Args:
        name (str): The name of the repository.
        description (str): A short description of the repository.
        visibility (str): The visibility of the repository.
        auto_init (bool): Pass False to not create an initial commit with empty README.

    Returns:
        str: A JSON string with the new repository's details (status, id, name, html_url, description).
    """
    headers = getHeader()
    bodyParams = {k:v for k,v in locals().items() if v  is not None and k not in ["headers"]}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=bodyParams
            )

            if response.status_code == 201:
                data = response.json()
                createdRepoInfo = {
                    "id" : data.get("id"),
                    "name" : data.get("name"),
                    "description" : data.get("description"),
                    "url" : data.get("html_url"),
                    "status" : "success",
                }
                return json.dumps(createdRepoInfo)
            
            errorCode = {
                403: "Forbidden",
                422: "Validation failed, or the endpoint has been spammed",
                451: "Validation failed, or the endpoint has been spammed"
            }
            return f"GitHub Error {response.status_code} - {errorCode[response.status_code]}"
    except Exception as e:
        return f"Internal Server error {e}"
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    gitHubMcpServer.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["mcp-session-id"],
            )
        ]
    )

