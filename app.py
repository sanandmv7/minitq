
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import game
from replit import db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Answer(BaseModel):
    wallet_address: str
    answer: int

class Score(BaseModel):
    wallet: str
    score: int

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/questions")
def get_questions():
    return game.QUIZ_QUESTIONS

@app.post("/api/submit/{question_index}")
def submit_answer(question_index: int, answer: Answer):
    if not 0 <= question_index < len(game.QUIZ_QUESTIONS):
        raise HTTPException(status_code=400, detail="Invalid question index")
        
    question = game.QUIZ_QUESTIONS[question_index]
    is_correct = question['options'][answer.answer - 1].lower() == question['answer'].lower()
    
    return {"correct": is_correct}

@app.post("/api/finish")
def finish_game(score: Score):
    quiz = game.QuizGame()
    quiz.wallet_address = score.wallet
    quiz.update_leaderboard(score.score)
    earned_tokens = score.score * quiz.reward_multiplier
    
    try:
        leaderboard = list(db.get('leaderboard', []))
        
        # Update existing score or add new entry
        entry_exists = False
        for entry in leaderboard:
            if entry['wallet'] == score.wallet:
                entry['score'] = max(entry['score'], score.score)
                entry_exists = True
                break
                
        if not entry_exists:
            leaderboard.append({
                'wallet': score.wallet,
                'score': score.score
            })
            
        # Sort and keep top 10
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        leaderboard = leaderboard[:10]
        db['leaderboard'] = leaderboard
    except Exception as e:
        print(f"Error handling leaderboard: {e}")
        leaderboard = []
    
    return {
        "earned_tokens": earned_tokens,
        "token_address": quiz.token_address,
        "leaderboard": leaderboard
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
