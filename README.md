# ScoutTeam MCP
> ScoutTeam + power for AI Model

### More about MCP Setup
- [MCP Doc](https://modelcontextprotocol.io/quickstart/server)

### Installation
1. Clone the project
2. Create a virtual environment and activate it
   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. Run `uv pip install -r requirements.txt` 
4. Run `uv pip install "mcp[cli]" fastmcp`

## Getting Started - For Claude Desktop - Free

### Claude Setup
1. Install Claude Desktop
2. Run `mcp install ScoutTeam.py` in your terminal
3. Check for the tool config at `Claude > Settings > Developer > Edit Config`
4. If not automatically added, manually add this configuration:
   
   ```json
   "ScoutTeam": {
      "command": "/Users/username/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/PATH_TO_PROJECT_DIR/ScoutTeamMCP/",
      ]
    }
   ```
   
   Notes:
   - Find path to uv - for MacOS: run `which uv`, for Windows run `where uv`
   - Replace `/PATH_TO_PROJECT_DIR/ScoutTeamMCP/` with the actual path to your project
   - Replace `username` with your actual username

6. Restart Claude after making these changes

If everything is correct, you should be able to see the ScoutTeamMCP tool here in Claude Desktop.

<img width="515" alt="Screenshot 2025-05-09 at 12 25 54 PM" src="https://github.com/user-attachments/assets/c990149f-d1a8-4ea9-8f6b-b00b0b5dba85" />

## Running
Enter the following prompt in Claude Desktop:
> Give me a list of athletes from the Eastern Kentucky basketball team.

## Getting Started - For API - Paid based on no. of API calls, req res tokens, model

1. Create an API key from the [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Add minimum credit to your Anthropic account
3. Set up your environment variables - Add your Anthropic API key: ```ANTHROPIC_API_KEY=your_key_here```
4. Start the server: ```python3 ScoutTeamAPI.py```
5. Make a POST request to the API:
   ```bash
   curl -X POST http://localhost:8000/api/athletes \
     -H "Content-Type: application/json" \
     -d '{"university": ["Eastern Kentucky"], "sport": ["basketball"]}'
   ```

## Conclusion

The ScoutTeamMCP project provides two methods to access structured athlete roster data from university sports websites: Claude Desktop integration (via MCP) and the FastAPI-based API. Each method offers distinct advantages based on your needs:

- **Claude Desktop (MCP)**: Ideal for users who value an interactive, prompt-based interface. It’s free to use (assuming Claude Desktop access) and supports quick, ad-hoc queries without additional API costs. However, it requires manual prompt entry and familiarity with Claude’s interface, making it best for individual or exploratory use.
- **FastAPI Server (API)**: Designed for automation and scalability, the API enables programmatic access to roster data. It’s perfect for integration into larger applications or processing multiple requests. However, it incurs costs based on Anthropic API usage (e.g., number of calls, tokens processed, and model selected) and may be slower than Claude Desktop due to HTTP request overhead and external API calls.

Choose **Claude Desktop** for simple, cost-free exploration or the **API** for automated, large-scale data processing. Both methods harness Anthropic’s Claude model to deliver accurate, structured athlete data from university sports rosters.
