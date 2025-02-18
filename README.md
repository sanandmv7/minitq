# MinitQ

MinitQ is an interactive quiz game that combines trivia knowledge with blockchain rewards. Players answer themed questions to earn MNTQ tokens for correct answers.

## Technical Overview

MinitQ is a full-stack web application that combines traditional quiz gameplay with blockchain rewards. Built using FastAPI for the backend and vanilla JavaScript for the frontend, it demonstrates the integration of Web3 functionality using the Coinbase Developer Platform (CDP).

### Core Features:

1. Quiz Mechanics:
   Multiple-choice questions
   Score tracking
   Interactive web interface
   Persistent leaderboard system

2. Web3 Integration:
   Custom ERC20 token (MNTQ) for rewards
   Smart contract integration for token minting
   Automated reward distribution (10 MNTQ tokens per correct answer)
   Token contract deployed at 0xc90278252098de206ae85A4cb879123d50a05456 on base sepolia

3. Architecture:
   Frontend: HTML5, CSS3, and vanilla JavaScript
   Backend: FastAPI (Python)
   Database: Replit DB for leaderboard storage
   Blockchain: CDP SDK for Web3 interactions
   AI Agent: Custom TokenAgent for reward distribution

4. User Flow:
   User input their Web3 wallet address
   Answers 5 themed questions
   Receives MNTQ tokens based on performance
   Views their position on the global leaderboard
   Option to play again

5. Technical Features:
   Asynchronous API endpoints
   Secure token minting system
   Real-time score updates
   Optimized smart contract interactions
   Automated reward calculations
   Persistent leaderboard rankings
   Clean separation of concerns (MVC pattern)

The project serves as an example of how traditional web applications can be enhanced with Web3 and AI Agent functionalities, providing both entertainment and rewards for user participation. The modular architecture allows for easy expansion of both quiz content and reward mechanisms.

## Future Works

1. Quiz theme and questions generations using AI Agents
2. Wallet Connection and Management features in the frontend
3. Enhance UI/UX
4. Conduct live events using AI Agents
