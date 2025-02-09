
let currentQuestion = 0;
let score = 0;
let questions = [];
let walletAddress = '';

async function startQuiz() {
    walletAddress = document.getElementById('wallet-input').value.trim();
    if (!walletAddress) {
        alert('Please enter a wallet address');
        return;
    }

    const response = await fetch('/api/questions');
    questions = await response.json();
    
    document.getElementById('wallet-screen').classList.add('hidden');
    document.getElementById('quiz-screen').classList.remove('hidden');
    showQuestion();
}

function showQuestion() {
    const question = questions[currentQuestion];
    document.getElementById('question-text').textContent = question.question;
    
    const optionsHtml = question.options.map((option, index) => 
        `<button onclick="submitAnswer(${index + 1})">${index + 1}. ${option}</button>`
    ).join('');
    
    document.getElementById('options').innerHTML = optionsHtml;
}

async function submitAnswer(choice) {
    const response = await fetch(`/api/submit/${currentQuestion}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            wallet_address: walletAddress,
            answer: choice
        })
    });
    
    const result = await response.json();
    if (result.correct) score++;
    
    currentQuestion++;
    if (currentQuestion < questions.length) {
        showQuestion();
    } else {
        finishQuiz();
    }
}

async function finishQuiz() {
    const response = await fetch('/api/finish', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            wallet: walletAddress,
            score: score
        })
    });
    
    const result = await response.json();
    
    document.getElementById('quiz-screen').classList.add('hidden');
    document.getElementById('result-screen').classList.remove('hidden');
    
    document.getElementById('score-text').textContent = 
        `You got ${score} out of ${questions.length} questions correct!`;
    document.getElementById('eth-earned').textContent = 
        `You earned Ξ${result.earned_eth.toFixed(3)} ETH!`;
        
    const leaderboardHtml = result.leaderboard.map((entry, index) => 
        `<p>${index + 1}. Wallet: ${entry.wallet?.slice(0, 8) || 'Unknown'}... - Score: ${entry.score}</p>`
    ).join('');
    
    document.getElementById('leaderboard-entries').innerHTML = leaderboardHtml;
}

function resetQuiz() {
    currentQuestion = 0;
    score = 0;
    walletAddress = '';
    
    document.getElementById('result-screen').classList.add('hidden');
    document.getElementById('wallet-screen').classList.remove('hidden');
    document.getElementById('wallet-input').value = '';
}
