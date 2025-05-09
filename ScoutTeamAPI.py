from typing import Any, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import uvicorn
from anthropic import Anthropic
import logging
import os
import json
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler("api_debug.log")  # Also save to file
    ]
)

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
                return f"unable to parse page content {university}"

            players_container = soup.find("ul", class_="sidearm-roster-players")

            if not players_container:
                return f"No players found for {university}"

            player_list = players_container.find_all("li", class_="sidearm-roster-player")

            if not player_list:
                return f"No player list found for {university}"

            playerListResponse.append("\n".join([str(player) for player in player_list]))
        except Exception as e:
            playerListResponse.append(f"Error fetching {roster_url}: {str(e)}")
    
    return "\n---\n".join(playerListResponse)

# Define the Pydantic model for the request
class UniversityRequest(BaseModel):
    university: Optional[List[str]] = None
    sport: Optional[List[str]] = None

app = FastAPI(title="Athlete Scrapper API", description="API for scrapping university athlete rosters")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_with_claude(html_data, university=None, sport=None):
    """
        Process HTML data with claude API and retun structured athlete information.
    """
    try:
        anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = f"""
            You are helping parse athlete roster HTML data from university sports websites.
        
            Below is HTML content from a roster page.
            
            Extract all athlete information into a structured JSON format with these fields:
            - name: Athlete's full name
            - number: Jersey number
            - position: Playing position
            - year: Academic year or class
            - hometown: Hometown (if available)
            - high_school: High school (if available)
            - previous_school: Previous school or transfer info (if available)
            - image_url: URL to player's image (if available in the HTML)
            
            Return ONLY valid JSON without any explanations or additional text.
            
            Here's the HTML to parse:  

            {html_data}
        """

        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=0,
            system="you are an expert at parsing HTML and extracting structured data. Return only valid JSON.",
            messages=[{"role":"user", "content": prompt}]
        )

        claude_response = response.content[0].text

        try:
            import re
            json_match = re.search(r'```json\n([\s\S]*?)\n```', claude_response)

            if json_match:
                athlete_data = json.loads(json_match.group(1))
            else:
                athlete_data = json.loads(claude_response)

            return {
                "success": True,
                "data": athlete_data,
                "source": "Claude AI"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse Calude's response as JSON: {str(e)}",
                "raw_response": claude_response
            }
    except Exception as e:
        logger.error(f"Error processing with Claude: {str(e)}", exc_info=True)
        return {
            "success": False, 
            "error": f"Error calling Calude API: {str(e)}"
        }


@app.post("/api/athletes")
async def process_univeristy(request: UniversityRequest):
    """
        Process a university roster URL and return athlete data 
    """
    try:
        roster_urls = await list_resources(university=request.university, sport=request.sport)
        logger.debug(f"Roster URLs: {roster_urls}")


        if not roster_urls:
            return {
                "success": False,
                "error": "Please specify a valid university or sport name"
            }

        athlete_data = await get_Athlete(list=roster_urls)

        structured_data = await process_with_claude(athlete_data)

        return {
            "success": structured_data.get("success", False),
            "data": structured_data.get("data", []),
            "university": request.university,
            "sport": request.sport,
            "urls_processed": roster_urls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        # Run MCP server
        mcp.run(transport='stdio')
    else:
        # Run FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000)
