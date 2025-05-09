from typing import Any, List, Optional
import httpx
from pydantic import BaseModel
from fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import uvicorn

mcp = FastMCP("ScoutTeam")

# resources
async def list_resources(university: list[str] = None, sport: list[str] = None) -> list[str]:
    universityRoster = {
        "Ottawa University Arizona": {
            "basketball": "https://ouazspirit.com/sports/mens-basketball/roster",
            "baseball": "https://ouazspirit.com/sports/mens-baseball/roster",
        },
        "eastern kentucky": {
            "basketball": "https://ekusports.com/sports/mens-basketball/roster",
            "baseball": "https://ekusports.com/sports/mens-baseball/roster",
        }
    }
    
    if not university and not sport:
        return ["Specify University or Sport"]

    roster_list = []

    if not university:
        for uni, sports in universityRoster.items():
            for s, url in sports.items():
                if sport and s.lower() in [sp.lower() for sp in sport]:
                    roster_list.append(url)
                elif not sport:
                    roster_list.append(url)
    else:
        for uni, sports in universityRoster.items():
            if any(u.lower() in uni.lower() for u in university):
                if sport:
                    for s, url in sports.items():
                        if any(s.lower() in sp.lower() for sp in sport):
                            roster_list.append(url)
                else:
                    for url in sports.values():
                        roster_list.append(url)

    return roster_list

# Explicitly register the resources function
mcp.list_resources_func = list_resources

@mcp.tool()
async def get_Athlete(list: list[str]) -> str:
    """Get player list content from university and/or sport

    Args:
        list: List of roster URLs to fetch
    """
    if not list or list[0] == "Specify University or Sport":
        return f"Unable to fetch roster: Please specify a university or sport"

    playerListResponse = []

    for roster_url in list:
        try:
            page = requests.get(roster_url)

            soup = BeautifulSoup(page.content, "html.parser")

            if not soup:
                return f"unable to parse page content"

            players_container = soup.find("ul", class_="sidearm-roster-players")

            if not players_container:
                return f"No players found"

            player_list = players_container.find_all("li", class_="sidearm-roster-player")

            if not player_list:
                return f"No player list found for {university}"

            playerListResponse.append("\n".join([str(player) for player in player_list]))
        except Exception as e:
            playerListResponse.append(f"Error fetching {roster_url}: {str(e)}")
    
    return "\n---\n".join(playerListResponse)

if __name__ == "__main__":
    mcp.run(transport='stdio')
