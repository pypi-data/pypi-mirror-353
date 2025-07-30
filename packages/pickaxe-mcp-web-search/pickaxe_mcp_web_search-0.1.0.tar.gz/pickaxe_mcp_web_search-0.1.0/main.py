import os
import json
from fastmcp import FastMCP
from openai import OpenAI

mcp = FastMCP(
    name="web-search",
    instructions="You are a web search engine. Call search() to find relevant information based on the user's query.",
)

client = OpenAI(
    api_key=os.environ["OPENAI_KEY_1"],
)

@mcp.tool()
def search(query: str) -> str:
    """
    Perform a web search for the given query.
    """
    response = client.responses.create(
        model="gpt-4.1",
        input=query,
        tools=[{ "type": "web_search_preview" }]
    )

    contents = ""
    for result in response.output:
        if result.type == "message":
            contents += "\n".join(item.text for item in result.content if item.type == "output_text")

    return f"""Search results for '{query}': {json.dumps(contents, default=str, ensure_ascii=False)}"""

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
