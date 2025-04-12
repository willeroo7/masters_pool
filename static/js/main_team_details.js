document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, fetching team scores...');
    // Load team scores when page loads
    loadTeamScores();

    // Add event listener for generate report button
    document.getElementById('generateReport').addEventListener('click', generateReport);
});

function loadTeamScores() {
    console.log('Making API request to /api/team-scores');
    fetch('/api/team-scores')
        .then(response => response.json())
        .then(data => {
            console.log('Received team scores:', data);
            if (data.success) {
                displayTeamScores(data.data);
            } else {
                showError('Failed to load team scores: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error loading team scores:', error);
            showError('Error loading team scores: ' + error.message);
        });
}

function getScoreClass(score) {
    if (!score && score !== 0) return '';
    if (score < 0) return 'negative-score';
    if (score > 0) return 'positive-score';
    return 'even-score';
}

function displayTeamScores(teams) {
    console.log('Displaying team scores:', teams);
    const tableBody = document.getElementById('teamScoresTableBody');
    tableBody.innerHTML = '';

    teams.forEach(team => {
        // Create team row
        const teamRow = document.createElement('tr');
        teamRow.classList.add('team-row');
        teamRow.innerHTML = `
            <td>${team.rank || ''}</td>
            <td>${team.team || ''}</td>
            <td class="${getScoreClass(team.score)}">${team.score || ''}</td>
            <td colspan="7"></td>
        `;
        tableBody.appendChild(teamRow);

        // Add player rows
        team.players.forEach(player => {
            const playerRow = document.createElement('tr');
            playerRow.classList.add('player-row');
            
            // Get score classes for each round
            const roundClasses = player.rounds.map(score => getScoreClass(score));
            const totalClass = getScoreClass(player.total);

            playerRow.innerHTML = `
                <td></td>
                <td></td>
                <td></td>
                <td>${player.name || ''}</td>
                <td>${player.tier || ''}</td>
                <td class="${roundClasses[0]}">${player.rounds[0] || ''}</td>
                <td class="${roundClasses[1]}">${player.rounds[1] || ''}</td>
                <td class="${roundClasses[2]}">${player.rounds[2] || ''}</td>
                <td class="${roundClasses[3]}">${player.rounds[3] || ''}</td>
                <td class="${totalClass}">${player.total || ''}</td>
            `;

            // Add styling for best scores (top 4)
            const playerScores = team.players.map(p => p.total).sort((a, b) => a - b);
            const bestScores = playerScores.slice(0, 4);
            if (bestScores.includes(player.total)) {
                playerRow.classList.add('best-score');
            }

            tableBody.appendChild(playerRow);
        });
    });
}

function generateReport() {
    const button = document.getElementById('generateReport');
    button.disabled = true;
    button.innerHTML = 'Generating...';

    fetch('/api/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Report generated successfully!');
        } else {
            showError('Failed to generate report: ' + data.error);
        }
    })
    .catch(error => {
        showError('Error generating report: ' + error.message);
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = 'Generate Excel Report';
    });
}

function showError(message) {
    console.error('Error:', message);
    alert('Error: ' + message);
}

function showSuccess(message) {
    console.log('Success:', message);
    alert(message);
} 