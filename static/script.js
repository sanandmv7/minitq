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
        `You earned ${result.earned_tokens} MNTQ tokens!`;

    const leaderboardDiv = document.getElementById('leaderboard-entries');
    if (result.leaderboard && Array.isArray(result.leaderboard) && result.leaderboard.length > 0) {
        const leaderboardHtml = `
            <table class="leaderboard-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Wallet</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    ${result.leaderboard.map((entry, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${entry.wallet.slice(0, 8)}...</td>
                            <td>${entry.score}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>`;
        leaderboardDiv.innerHTML = leaderboardHtml;
    } else {
        leaderboardDiv.innerHTML = 'No entries in leaderboard yet';
    }
}

function resetQuiz() {
    currentQuestion = 0;
    score = 0;
    walletAddress = '';

    document.getElementById('result-screen').classList.add('hidden');
    document.getElementById('wallet-screen').classList.remove('hidden');
    document.getElementById('wallet-input').value = '';
}