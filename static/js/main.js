document.addEventListener('DOMContentLoaded', function() {
    // Load scores when page loads
    loadScores();

    // Add event listener for generate report button
    document.getElementById('generateReport').addEventListener('click', generateReport);
});

function loadScores() {
    fetch('/api/scores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayScores(data.data);
            } else {
                showError('Failed to load scores: ' + data.error);
            }
        })
        .catch(error => {
            showError('Error loading scores: ' + error.message);
        });
}

function displayScores(scores) {
    const tableBody = document.getElementById('scoresTableBody');
    tableBody.innerHTML = '';

    scores.forEach(player => {
        const row = document.createElement('tr');
        
        // Create cells for each round with appropriate styling
        const roundCells = ['round1', 'round2', 'round3', 'round4'].map(roundKey => {
            const roundData = player.rounds[roundKey];
            let cellContent = '';
            let cellClass = '';
            
            if (roundData.status === 'Finished') {
                cellContent = roundData.score;
                cellClass = 'text-success';
            } else if (roundData.status === 'Playing') {
                cellContent = roundData.relative_to_par;
                cellClass = 'text-primary fw-bold';
            } else {
                cellContent = '-';
                cellClass = 'text-muted';
            }
            
            return `<td class="${cellClass}">${cellContent}</td>`;
        }).join('');

        row.innerHTML = `
            <td>${player.position}</td>
            <td>${player.name}</td>
            <td>${player.total_score}</td>
            ${roundCells}
        `;
        tableBody.appendChild(row);
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
    // You can implement a more sophisticated error display
    alert('Error: ' + message);
}

function showSuccess(message) {
    // You can implement a more sophisticated success display
    alert(message);
} 