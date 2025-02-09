#!/usr/bin/env python3
import random
import time
from utils import clear_screen, format_eth

class NumberGuessingGame:
    def __init__(self):
        self.min_number = 0
        self.max_number = 100
        self.max_attempts = 10
        self.reward_eth = 0.01  # Mock ETH reward for winning
        self.total_rewards = 0
        self.games_won = 0
        self.games_played = 0

    def generate_number(self):
        return random.randint(self.min_number, self.max_number)

    def get_valid_guess(self):
        while True:
            try:
                guess = input(f"\nEnter your guess ({self.min_number}-{self.max_number}): ")
                guess = int(guess)
                if self.min_number <= guess <= self.max_number:
                    return guess
                print(f"Please enter a number between {self.min_number} and {self.max_number}")
            except ValueError:
                print("Please enter a valid number!")

    def play_round(self):
        clear_screen()
        print("\n🎮 Welcome to the Crypto Number Guessing Game! 🎮")
        print(f"Guess the number between {self.min_number} and {self.max_number}")
        print(f"You have {self.max_attempts} attempts to win {format_eth(self.reward_eth)} ETH!")
        
        target_number = self.generate_number()
        attempts = 0

        while attempts < self.max_attempts:
            attempts += 1
            remaining = self.max_attempts - attempts
            
            print(f"\nAttempts remaining: {remaining}")
            guess = self.get_valid_guess()

            if guess == target_number:
                print("\n🎉 Congratulations! You've won! 🎉")
                print(f"You earned {format_eth(self.reward_eth)} ETH!")
                self.total_rewards += self.reward_eth
                self.games_won += 1
                break
            elif guess < target_number:
                print("Too low! Try a higher number.")
            else:
                print("Too high! Try a lower number.")

            if remaining == 0:
                print(f"\n😢 Game Over! The number was {target_number}")

        self.games_played += 1
        self.show_stats()
        return self.play_again()

    def show_stats(self):
        print("\n📊 Game Statistics:")
        print(f"Games Played: {self.games_played}")
        print(f"Games Won: {self.games_won}")
        print(f"Total Mock ETH Rewards: {format_eth(self.total_rewards)}")
        if self.games_played > 0:
            win_rate = (self.games_won / self.games_played) * 100
            print(f"Win Rate: {win_rate:.1f}%")

    def play_again(self):
        while True:
            choice = input("\nWould you like to play again? (y/n): ").lower()
            if choice in ['y', 'n']:
                return choice == 'y'
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    game = NumberGuessingGame()
    while game.play_round():
        pass
    
    print("\nThanks for playing! Final stats:")
    game.show_stats()

if __name__ == "__main__":
    main()
