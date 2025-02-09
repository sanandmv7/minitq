import json
import os
import sys
import time
import pandas as pd
from typing import List

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI 
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from cdp_sdk import Wallet, Transaction

wallet_data_file = "wallet_data.txt"

class TransferInput(BaseModel):
    recipient_address: str = Field(..., description="The recipient wallet address")
    amount: str = Field(..., description="The amount to transfer")

class SignMessageInput(BaseModel):
    message: str = Field(..., description="The message to sign")

class RewardInput(BaseModel):
    total_reward: str = Field(..., description="The total reward amount to distribute")

def transfer_usdc(wallet: Wallet, recipient_address: str, amount: str) -> str:
    """Transfer USDC to specified address."""
    try:
        # Request USDC from faucet before transfer
        faucet_tx = wallet.faucet(asset_id="usdc")
        faucet_tx.wait()
        print("Received USDC from faucet")

        # Perform the transfer
        transfer = wallet.transfer(float(amount), "usdc", recipient_address)
        result = transfer.wait()
        return f"Successfully transferred {amount} USDC to {recipient_address}"
    except Exception as e:
        return f"Failed to transfer USDC: {str(e)}"

def sign_message(wallet: Wallet, message: str) -> str:
    """Sign message using EIP-191 hash."""
    payload_signature = wallet.sign_payload(hash_message(message)).wait()
    return f"The payload signature {payload_signature}"

def read_leaderboard() -> pd.DataFrame:
    """Read and return the leaderboard data."""
    try:
        df = pd.read_csv('leaderboard.csv')
        return df.head(3)  # Get top 3 entries
    except FileNotFoundError:
        print("Leaderboard file not found!")
        return None

def sign_and_distribute_rewards(wallet: Wallet, total_reward: str) -> List[str]:
    """Sign leaderboard and distribute rewards to top 3 wallets."""
    # Read leaderboard
    df = read_leaderboard()
    if df is None:
        return ["Error: Leaderboard file not found"]

    try:
        # Sign the leaderboard data
        leaderboard_data = df.to_json()
        signature = wallet.sign_payload(hash_message(leaderboard_data)).wait()

        # Convert signature to string format
        signature_str = str(signature)

        # Store signature onchain using a smart contract invocation
        storage_contract_abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "data", "type": "string"}
                ],
                "name": "store",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        # Replace with your deployed storage contract address
        storage_contract_address = "0x252558FBB8eaF442604833974e414FEF41F5784c"

        # Store the signature on-chain
        store_tx = wallet.invoke_contract(
            contract_address=storage_contract_address,
            method="store",
            args={"data": signature_str},
            abi=storage_contract_abi
        ).wait()

        # Calculate reward per wallet (equal distribution)
        reward_amount = float(total_reward) / 3
        reward_per_wallet = f"{reward_amount:.6f}"

        # Transfer rewards to top 3 wallets
        results = []
        for _, row in df.iterrows():
            command = transfer_usdc(wallet, row['wallet_address'], reward_per_wallet)
            results.append(command)

        return [
            f"Leaderboard signature: {signature_str}",
            f"Signature stored onchain with transaction hash: {store_tx.transaction_hash}",
            f"Agent wallet address: {wallet.default_address.address_id}",
            "Reward distribution:",
            *results
        ]
    except Exception as e:
        return [f"Error during reward distribution: {str(e)}"]

def add_reward_tool(tools, agentkit):
    reward_tool = CdpTool(
        name="distribute_daily_rewards",
        description="Sign the leaderboard and distribute rewards to top 3 wallets",
        cdp_agentkit_wrapper=agentkit,
        args_schema=RewardInput,
        func=sign_and_distribute_rewards
    )
    return tools + [reward_tool]

def initialize_agent():
    llm = ChatOpenAI(model="gpt-4o-mini")
    wallet_data = None

    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    values = {}
    if wallet_data is not None:
        values = {"cdp_wallet_data": wallet_data}

    agentkit = CdpAgentkitWrapper(**values)
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()

    transfer_tool = CdpTool(
        name="transfer_usdc",
        description="Transfer USDC to a specified wallet address",
        cdp_agentkit_wrapper=agentkit,
        args_schema=TransferInput,
        func=transfer_usdc,
    )

    sign_tool = CdpTool(
        name="sign_message",
        description="Sign a message using EIP-191",
        cdp_agentkit_wrapper=agentkit,
        args_schema=SignMessageInput,
        func=sign_message,
    )

    all_tools = tools + [transfer_tool, sign_tool]
    all_tools = add_reward_tool(all_tools, agentkit)
    memory = MemorySaver()

    return create_react_agent(
        llm,
        tools=all_tools,
        checkpointer=memory,
        state_modifier="You are a helpful agent that can interact onchain using the Coinbase Developer Platform Agentkit. You are empowered to interact onchain using your tools. If you ever need funds, you can request them from the faucet if you are on network ID `base-sepolia`. If not, you can provide your wallet details and request funds from the user. If someone asks you to do something you can't do with your currently available tools, you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, recommend they go to docs.cdp.coinbase.com for more informaton. Be concise and helpful with your responses. Refrain from restating your tools' descriptions unless it is explicitly requested.",
    )

def run_autonomous_mode(agent_executor, config, interval=10):
    print("Starting autonomous mode...")
    while True:
        try:
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)

def run_chat_mode(agent_executor, config):
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() == "exit":
                break

            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)

def run_rewards_mode(agent_executor, config):
    print("Starting rewards distribution mode...")
    try:
        reward_amount = "0.003"  # Default reward amount (0.001 USDC per wallet for top 3)
        thought = f"Please distribute {reward_amount} as daily rewards to the top 3 wallets in the leaderboard and sign the leaderboard data."

        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=thought)]}, config):
            if "agent" in chunk:
                print(chunk["agent"]["messages"][0].content)
            elif "tools" in chunk:
                print(chunk["tools"]["messages"][0].content)
            print("-------------------")

    except KeyboardInterrupt:
        print("Goodbye Agent!")
        sys.exit(0)

def choose_mode():
    print("\nAvailable modes:")
    print("1. chat    - Interactive chat mode")
    print("2. auto    - Autonomous action mode")
    print("3. rewards - Distribute daily rewards")

    choice = input("\nChoose a mode (enter number or name): ").lower().strip()
    if choice in ["1", "chat"]:
        return "chat"
    elif choice in ["2", "auto"]:
        return "auto"
    elif choice in ["3", "rewards"]:
        return "rewards"
    print("Invalid choice. Please try again.")

def main():
    agent_executor = initialize_agent()
    config = {
        "configurable": {
            "thread_id": "CDP Agentkit Chatbot Example!",
            "checkpoint_ns": "default_namespace",
            "checkpoint_id": "default_checkpoint"
        }
    }

    run_rewards_mode(agent_executor=agent_executor, config=config)

if __name__ == "__main__":
    print("Starting Agent...")
    main()