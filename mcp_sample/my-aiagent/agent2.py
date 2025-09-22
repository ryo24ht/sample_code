import os
import logging

from prompt_toolkit import prompt
from strands import Agent
from strands.models.litellm import LiteLLMModel
from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient


# 環境変数からAPIキーを取得
api_key = os.environ["OPENAI_API_KEY"]

# モデルを指定してAIエージェントを作成
model = LiteLLMModel(
    client_args={
        "api_key": api_key,
    },
    model_id="gemini/gemini-2.5-flash",
    params={
        "max_token": 5000,
        "temperature": 0.0,
    }
)

# agent = Agent(
#     model=model
# )

# Fetch MCP Serverのクライアントを作成
fetch_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="docker",
            args=["run", "-i", "--rm", "mcp/fetch"]
        )
    )
)

with fetch_mcp_client:
    # MCPサーバからツールを取得
    tools = fetch_mcp_client.list_tools_sync()

    # モデルとツールを指定してAIエージェントを作成
    agent = Agent(
        model=model,
        tools=tools
    )

    print("URLをもとにサイトの情報を取得することができます。")

    while True:
        # ユーザーからの入力を受け取る
        user_input = prompt("> ")

        # "exit" または "quit" と入力されたら終了
        if user_input.lower() in ["exit", "quit"]:
            
            break

        # AIエージェントにユーザー入力を渡して応答を出力
        result = agent(user_input)

        # 応答時に使用したtoken数を表示
        print()
        print('-' * 50)
        print(result.metrics.get_summary()['accumulated_usage'])
        print('-' * 50)
        print()
