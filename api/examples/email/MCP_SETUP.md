# MCP Setup Guide for Dynamic Agents

This guide shows you how to enable the Global MCP Server for the dynamic agents demo.

## 🚀 Quick Start

### Option 1: Run Local MCP Server (Recommended for Testing)

1. **Start the Global MCP Server locally:**

```bash
# Navigate to the MCP server directory
cd ../../../../../synq-mcp-server

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional - tools will work in demo mode without real credentials)
cp .env.example .env

# Start server
python server.py
```

The server will start at `http://localhost:8080`

2. **Run the dynamic agents demo:**

```bash
# Navigate back to the demo directory
cd ../synqed-samples/api/examples/email

# Run the demo (it will auto-detect the local MCP server)
python dynamic_agents_email.py
```

The demo will automatically connect to `http://localhost:8080` and all agents will have MCP access!

### Option 2: Use Environment Variable for Different Endpoint

If you want to point to a different MCP server:

```bash
# Set custom endpoint
export SYNQ_GLOBAL_MCP_ENDPOINT=http://localhost:8080

# Or point to a deployed server
export SYNQ_GLOBAL_MCP_ENDPOINT=https://your-mcp-server.fly.dev

# Run demo
python dynamic_agents_email.py
```

### Option 3: Deploy to Fly.io (Production)

1. **Deploy the Global MCP Server:**

```bash
cd synq-mcp-server

# Install Fly CLI if needed
brew install flyctl  # macOS
# or curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Set secrets
fly secrets set ZOOM_API_KEY=your_key
fly secrets set ZOOM_API_SECRET=your_secret
fly secrets set ZOOM_ACCOUNT_ID=your_account
fly secrets set SALESFORCE_CLIENT_ID=your_id
fly secrets set SALESFORCE_CLIENT_SECRET=your_secret
fly secrets set SALESFORCE_REFRESH_TOKEN=your_token
fly secrets set BEAUTIFUL_API_KEY=your_key

# Deploy
fly deploy
```

2. **Use the deployed server:**

```bash
export SYNQ_GLOBAL_MCP_ENDPOINT=https://synq-mcp.fly.dev
python dynamic_agents_email.py
```

## 🛠 What the MCP Server Provides

When running, the Global MCP Server exposes these tools to ALL agents:

### Zoom Tools
- `zoom.create_meeting` - Create a new Zoom meeting
- `zoom.list_meetings` - List upcoming meetings
- `zoom.get_meeting` - Get meeting details
- `zoom.delete_meeting` - Delete a meeting

### Salesforce Tools
- `salesforce.query` - Execute SOQL queries
- `salesforce.update_lead` - Update lead records
- `salesforce.create_lead` - Create new leads
- `salesforce.get_opportunity` - Get opportunity details
- `salesforce.get_lead` - Get lead details

### Beautiful Tools
- `beautiful.scrape` - Scrape website content
- `beautiful.extract` - Extract specific elements
- `beautiful.summarize` - Summarize HTML content

## 🧪 Testing

Once the MCP server is running, you can test it:

```bash
# Check health
curl http://localhost:8080/health

# List available tools
curl http://localhost:8080/mcp/tools | jq

# Test a tool call
curl -X POST http://localhost:8080/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "zoom.list_meetings",
    "arguments": {"type": "upcoming"}
  }' | jq
```

## 📝 Demo Mode

The MCP server works in "demo mode" even without real API credentials:

- Tools will be listed and callable
- Responses will indicate missing credentials
- Agents can still make calls and receive structured error responses
- Perfect for testing the integration!

To use real services, configure the `.env` file in `synq-mcp-server/`:

```bash
# In synq-mcp-server/.env
ZOOM_API_KEY=your_real_key
ZOOM_API_SECRET=your_real_secret
# ... etc
```

## 🔧 Troubleshooting

### Error: "nodename nor servname provided, or not known"

**Solution**: The MCP server is not running. Start it with:
```bash
cd synq-mcp-server && python server.py
```

### Error: "Connection refused"

**Solution**: Check that the server is running on the expected port:
```bash
ps aux | grep server.py
curl http://localhost:8080/health
```

### Tools Return Errors

**Solution**: This is expected if you haven't configured real API credentials. The integration still works - agents can make calls and get responses. To use real services, configure the `.env` file.

## 📚 More Information

- **Server Documentation**: See `synq-mcp-server/README.md`
- **Integration Guide**: See `synq-mcp-server/INTEGRATION.md`
- **Deployment Guide**: See `synq-mcp-server/DEPLOYMENT.md`
- **Quick Start**: See `synq-mcp-server/QUICKSTART.md`

## 💡 Example Workflow

```bash
# Terminal 1: Start MCP Server
cd synq-mcp-server
python server.py

# Terminal 2: Run Dynamic Agents Demo
cd synqed-samples/api/examples/email
python dynamic_agents_email.py
```

Now all dynamically created agents can use Zoom, Salesforce, and Beautiful tools! 🎉

