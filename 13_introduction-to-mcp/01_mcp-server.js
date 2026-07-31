import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { string, z } from "zod";

const server = new McpServer({
    "name": "chaicode-server",
    "version": "1.0.0"
});

server.registerTool(
    "addTwoNumbers",
    {
        title: "addTwoNumbers",
        description: "Add two numbers",
        inputSchema: { a: z.number(), b: z.number()}
    }, 
    async function({a,b}) {
        return { content: [{ type: "text", text: String(a+b) }] };
    }
);

const transport = new StdioServerTransport();
await server.connect(transport)