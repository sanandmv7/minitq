
#!/usr/bin/env python3
import random
import time
import os
from utils import clear_screen, format_eth
from replit import db
from typing import Dict, List
from cdp import Cdp

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from cdp import *

class TransferInput(BaseModel):
    recipient_address: str = Field(..., description="The recipient wallet address")
    amount: str = Field(..., description="The amount to transfer")

QUIZ_QUESTIONS = [
    {
        "question": "What is Harry Potter's Patronus?",
        "answer": "stag",
        "options": ["stag", "doe", "wolf", "phoenix"]
    },
    {
        "question": "What house is Harry Potter in at Hogwarts?",
        "answer": "gryffindor",
        "options": ["gryffindor", "slytherin", "ravenclaw", "hufflepuff"]
    },
    {
        "question": "What is the core of Harry's wand?",
        "answer": "phoenix feather",
        "options": ["phoenix feather", "dragon heartstring", "unicorn hair", "basilisk fang"]
    },
    {
        "question": "Who killed Dumbledore?",
        "answer": "snape",
        "options": ["snape", "malfoy", "voldemort", "bellatrix"]
    },
    {
        "question": "What is the name of Harry's owl?",
        "answer": "hedwig",
        "options": ["hedwig", "errol", "fawkes", "pigwidgeon"]
    }
]

class QuizGame:
    def __init__(self):
        self.reward_multiplier = 10  # 10 MNTQ tokens per correct answer
        self.token_address = "0xc90278252098de206ae85A4cb879123d50a05456"
        self.questions = QUIZ_QUESTIONS
        self.wallet_address = ""
        
        try:
            # Configure CDP SDK
            Cdp.configure(
                api_key_name=os.getenv("CDP_API_KEY_NAME"),
                api_key_private_key=os.getenv("CDP_API_KEY_PRIVATE_KEY")
            )
        except Exception as e:
            print("Failed to configure CDP SDK:", str(e))
        
    def get_wallet_address(self):
        while True:
            address = input("\nPlease enter your wallet address: ").strip()
            if len(address) > 0:  # Basic validation
                self.wallet_address = address
                return
                
    def ask_question(self, q_data: Dict) -> bool:
        print(f"\n{q_data['question']}")
        for i, option in enumerate(q_data['options'], 1):
            print(f"{i}. {option}")
            
        while True:
            try:
                choice = int(input("\nEnter your choice (1-4): "))
                if 1 <= choice <= 4:
                    return q_data['options'][choice-1].lower() == q_data['answer'].lower()
            except ValueError:
                pass
            print("Please enter a valid number between 1 and 4")

    def update_leaderboard(self, score: int):
        if 'leaderboard' not in db:
            db['leaderboard'] = []
            
        leaderboard = list(db['leaderboard'])
        
        # Update existing score or add new entry
        entry_found = False
        for entry in leaderboard:
            if entry['wallet'] == self.wallet_address:
                entry['score'] = max(entry['score'], score)
                entry_found = True
                break
                
        if not entry_found:
            leaderboard.append({
                'wallet': self.wallet_address,
                'score': score
            })
            
        # Sort by score and keep top 10
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        db['leaderboard'] = leaderboard[:10]

    def show_leaderboard(self):
        if 'leaderboard' not in db:
            print("\nNo scores yet!")
            return
            
        print("\n🏆 LEADERBOARD 🏆")
        print("-" * 50)
        for i, entry in enumerate(db['leaderboard'], 1):
            print(f"{i}. Wallet: {entry['wallet'][:8]}... - Score: {entry['score']}")
        print("-" * 50)

    def play_round(self) -> bool:
        clear_screen()
        print("\n🧙 Welcome to MinitQ - Harry Potter Edition! 🧙")
        
        if not self.wallet_address:
            self.get_wallet_address()
            
        score = 0
        for question in self.questions:
            if self.ask_question(question):
                score += 1
                print("✨ Correct!")
            else:
                print("❌ Wrong!")
                
        print(f"\nYou got {score} out of {len(self.questions)} questions correct!")
        earned_eth = (score / len(self.questions)) * self.reward_eth
        print(f"You earned {format_eth(earned_eth)} ETH!")
        
        self.update_leaderboard(score)
        self.show_leaderboard()
        
        return self.play_again()

    def play_again(self) -> bool:
        while True:
            choice = input("\nWould you like to play again? (y/n): ").lower()
            if choice in ['y', 'n']:
                return choice == 'y'
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    game = QuizGame()
    while game.play_round():
        pass
    
    print("\nThanks for playing! Final leaderboard:")
    game.show_leaderboard()

if __name__ == "__main__":
    main()
