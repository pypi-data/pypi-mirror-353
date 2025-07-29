# PDF.co MCP

#### Sample `.cursor/mcp.json` for test in cursor
```json
{
  "mcpServers": {
    "pdfco": {
      "command": "uvx",
      "args": [
        "pdfco-mcp"
      ],
      "env": {
        "X_API_KEY": "YOUR_API_KEY" // To get the API key please sign up at https://pdf.co and you can get the API key from the dashboard
      }
    }
  }
}
```