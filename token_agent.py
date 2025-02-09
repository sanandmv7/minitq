
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_sdk import Wallet
from typing import Tuple
import os

class TokenAgent:
    def __init__(self):
        self.contract_address = "0xc90278252098de206ae85A4cb879123d50a05456"
        self.agentkit = CdpAgentkitWrapper()
        self.wallet = self.agentkit.get_wallet()
        print(f"Agent Wallet Address: {self.wallet.get_address()}")
        
    def mint_tokens(self, player_address: str, amount: int) -> Tuple[bool, str]:
        try:
            # Convert amount to wei (multiply by 10^18)
            amount_in_wei = amount * 10**18
            
            # ABI for the mint function
            mint_abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "to", "type": "address"},
                        {"internalType": "uint256", "name": "amount", "type": "uint256"}
                    ],
                    "name": "mint",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            # Invoke mint function
            tx = self.wallet.invoke_contract(
                contract_address=self.contract_address,
                method="mint",
                args={"to": player_address, "amount": amount_in_wei},
                abi=mint_abi
            ).wait()
            
            return True, f"Successfully minted {amount} MINITQ tokens ({amount_in_wei} wei) to {player_address}"
        except Exception as e:
            return False, f"Failed to mint tokens: {str(e)}"
