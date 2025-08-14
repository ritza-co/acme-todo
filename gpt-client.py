from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "todo",
            "server_url": "https://app.getgram.ai/mcp/ritza-rzx-u6zis",
            "require_approval": "never",
        },
    ],
    input="What are my TODOs",
)

print(resp.output_text)
