# Continue (VS Code Extension)

[Continue](https://www.continue.dev/) is an open-source AI code assistant available as a Visual Studio Code extension. It supports the Model Context Protocol (MCP), allowing seamless integration with MCP-compatible servers like MCP Gateway.

---

## 🧰 Key Features

- **AI-Powered Coding**: Provides code completions, edits, and chat-based assistance.
- **MCP Integration**: Connects to MCP servers to discover and utilize tools dynamically.
- **Customizable Models**: Supports various AI models, including local and remote options.
- **Contextual Awareness**: Understands your codebase to provide relevant suggestions.

---

## 🛠 Installation

1. **Install Continue Extension**:
   - Open VS Code.
   - Navigate to the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`).
   - Search for "Continue" and click "Install".

2. **Configure Continue**:
   - Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
   - Select "Continue: Open Config".
   - This opens the `~/.continue/config.json` file.

---

## 🔗 Connecting to MCP Gateway

To integrate Continue with your MCP Gateway:

1. **Add MCP Server Configuration**:
   In your `~/.continue/config.json`, add the following under the `experimental` section:

   ```json
   {
     "experimental": {
       "modelContextProtocolServer": {
         "transport": {
           "type": "stdio",
           "command": "uvx",
           "args": ["mcpgateway-wrapper"]
         }
       }
     }
   }
```

Replace `"mcpgateway-wrapper"` with the appropriate command or path to your MCP Gateway server if different.

2. **Set Environment Variables**:
   Ensure the following environment variables are set:

   * `MCP_GATEWAY_BASE_URL`: Base URL of your MCP Gateway (e.g., `http://localhost:4444`).
   * `MCP_SERVER_CATALOG_URLS`: URL(s) to the server catalog(s) (e.g., `http://localhost:4444/servers/2`).
   * `MCP_AUTH_USER`: Username for authentication (e.g., `admin`).
   * `MCP_AUTH_PASS`: Password for authentication (e.g., `changeme`).

   You can set these in your system environment or within the Continue configuration if supported.

---

## 🧪 Using MCP Tools in Continue

Once configured:

* **Discover Tools**: Continue will automatically fetch and list available tools from the MCP Gateway.
* **Invoke Tools**: Use natural language prompts in Continue to invoke tools. For example:

  * "Run the `hello_world` tool with the argument `name: Alice`."
* **Monitor Responses**: Continue will display the tool's output directly within the chat interface.

---

## 📝 Tips for Effective Use

* **Custom Instructions**: Utilize Continue's Custom Instructions feature to tailor its behavior across all projects.
* **Model Selection**: Choose the AI model that best fits your project's needs within the Continue settings.
* **.continue/config.json**: Customize your Continue experience by editing this configuration file.

---

## 📚 Additional Resources

* [Continue Official Website](https://www.continue.dev/)
* [Continue Documentation](https://docs.continue.dev/)
* [Continue GitHub Repository](https://github.com/continuedev/continue)

---
