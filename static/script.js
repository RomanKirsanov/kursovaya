
// Глобальные переменные
let charts = {};
let isSimulating = false;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadStats();
    
    // Назначение обработчиков событий
    document.getElementById('startBtn').addEventListener('click', startSimulation);
    document.getElementById('stopBtn').addEventListener('click', stopSimulation);
    document.getElementById('resetBtn').addEventListener('click', resetSimulation);
    document.getElementById('testBtn').addEventListener('click', testAlgorithms);
    document.getElementById('checkBtn').addEventListener('click', checkBloomFilter);
    
    // Обновление времени
    updateTime();
    setInterval(updateTime, 1000);
    
    // Автообновление каждые 2 секунды
    setInterval(loadStats, 2000);
});

// Функция обновления времени
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ru-RU');
    document.getElementById('currentTime').textContent = timeString;
}

// Инициализация графиков
function initCharts() {
    const ctx1 = document.getElementById('usersChart').getContext('2d');
    charts.users = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Уникальные пользователи',
                data: [],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество'
                    }
                }
            }
        }
    });

    const ctx2 = document.getElementById('postsChart').getContext('2d');
    charts.posts = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Посты',
                data: [],
                backgroundColor: '#2196F3',
                borderColor: '#0D47A1',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество постов'
                    }
                }
            }
        }
    });

    const ctx3 = document.getElementById('accuracyChart').getContext('2d');
    charts.accuracy = new Chart(ctx3, {
        type: 'doughnut',
        data: {
            labels: ['Bloom Filter', 'HyperLogLog', 'Count-Min Sketch'],
            datasets: [{
                data: [99, 98, 97],
                backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    position: 'bottom',
                    labels: {
                        color: '#333',
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Точность алгоритмов (%)',
                    color: '#333',
                    font: {
                        size: 14
                    }
                }
            }
        }
    });
}

// Загрузка статистики
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        updateDashboard(data);
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// Обновление панели управления
function updateDashboard(data) {
    // Обновление статуса
    isSimulating = data.is_simulating;
    document.getElementById('status').textContent = isSimulating ? 'Запущено' : 'Остановлено';
    document.getElementById('status').className = `badge bg-${isSimulating ? 'success' : 'secondary'}`;
    
    // Обновление счетчика постов
    document.getElementById('postCount').textContent = data.stats.posts_count;
    
    // Обновление графиков
    updateCharts(data.metrics);
    
    // Обновление статистики алгоритмов
    updateAlgorithmStats(data.stats);
    
    // Обновление трендовых хештегов
    updateTrendingHashtags(data.trending);
    
    // Обновление последних постов
    updateRecentPosts(data.stats.recent_posts);
}

// Обновление графиков
function updateCharts(metrics) {
    if (!metrics || metrics.length === 0) return;
    
    // График уникальных пользователей
    const times = metrics.map(m => m.time);
    const users = metrics.map(m => m.unique_users);
    
    charts.users.data.labels = times.slice(-15);
    charts.users.data.datasets[0].data = users.slice(-15);
    charts.users.update();
    
    // График постов
    const posts = metrics.map(m => m.total_posts);
    charts.posts.data.labels = times.slice(-10);
    charts.posts.data.datasets[0].data = posts.slice(-10);
    charts.posts.update();
}

// Обновление статистики алгоритмов
function updateAlgorithmStats(stats) {
    const container = document.getElementById('algorithmStats');
    let html = '';
    
    // Bloom Filter
    if (stats.bloom) {
        html += `
            <h6 class="mt-3">🌼 Bloom Filter</h6>
            <div class="stat-item"><span class="stat-label">Вместимость:</span><span class="stat-value">${stats.bloom.capacity}</span></div>
            <div class="stat-item"><span class="stat-label">Элементов:</span><span class="stat-value">${stats.bloom.count}</span></div>
            <div class="stat-item"><span class="stat-label">Память:</span><span class="stat-value">${stats.bloom.memory_kb.toFixed(2)} КБ</span></div>
            <div class="stat-item"><span class="stat-label">Загрузка:</span><span class="stat-value">${(stats.bloom.load * 100).toFixed(1)}%</span></div>
        `;
    }
    
    // HyperLogLog
    if (stats.hll) {
        html += `
            <h6 class="mt-3">📈 HyperLogLog</h6>
            <div class="stat-item"><span class="stat-label">Оценка:</span><span class="stat-value">${stats.hll.estimate}</span></div>
            <div class="stat-item"><span class="stat-label">Регистров:</span><span class="stat-value">${stats.hll.registers}</span></div>
            <div class="stat-item"><span class="stat-label">Память:</span><span class="stat-value">${stats.hll.memory_kb.toFixed(2)} КБ</span></div>
        `;
    }
    
    // Count-Min Sketch
    if (stats.cms) {
        html += `
            <h6 class="mt-3">📊 Count-Min Sketch</h6>
            <div class="stat-item"><span class="stat-label">Всего элементов:</span><span class="stat-value">${stats.cms.total_count}</span></div>
            <div class="stat-item"><span class="stat-label">Память:</span><span class="stat-value">${stats.cms.memory_kb.toFixed(2)} КБ</span></div>
        `;
    }
    
    container.innerHTML = html;
}

// Обновление популярных хештегов
function updateTrendingHashtags(hashtags) {
    const container = document.getElementById('hashtagsList');
    
    if (!hashtags || hashtags.length === 0) {
        container.innerHTML = '<p class="text-muted">Хештегов пока нет</p>';
        return;
    }
    
    let html = '<div class="hashtags-container">';
    hashtags.forEach((item, index) => {
        const width = Math.min(100, (item.count / (hashtags[0].count || 1)) * 100);
        html += `
            <div class="hashtag-item">
                <div class="hashtag-info">
                    <span class="hashtag-rank">${index + 1}.</span>
                    <span class="hashtag-name">${item.item}</span>
                </div>
                <div class="hashtag-stats">
                    <span class="badge bg-dark">${item.count}</span>
                    <div class="hashtag-bar" style="width: ${width}%"></div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Обновление последних постов
function updateRecentPosts(posts) {
    const container = document.getElementById('recentPosts');
    
    if (!posts || posts.length === 0) {
        container.innerHTML = '<p class="text-muted">Постов пока нет</p>';
        return;
    }
    
    let html = '';
    posts.forEach(post => {
        html += `
            <div class="post-item">
                <div class="post-header">
                    <span class="post-user">${post.user}</span>
                    <span class="post-platform">${post.platform}</span>
                </div>
                <div class="post-content">
                    ${post.text}
                </div>
                <div class="post-footer">
                    <span class="post-hashtag">${post.hashtag}</span>
                    <span class="post-time">${post.timestamp}</span>
                    <span class="post-likes">❤️ ${post.likes}</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Управление симуляцией
async function startSimulation() {
    try {
        await fetch('/api/start', { method: 'POST' });
        showNotification('Симуляция запущена!', 'success');
    } catch (error) {
        showNotification('Ошибка запуска симуляции', 'error');
    }
}

async function stopSimulation() {
    try {
        await fetch('/api/stop', { method: 'POST' });
        showNotification('Симуляция остановлена!', 'info');
    } catch (error) {
        showNotification('Ошибка остановки симуляции', 'error');
    }
}

async function resetSimulation() {
    try {
        await fetch('/api/reset', { method: 'POST' });
        showNotification('Симуляция сброшена!', 'warning');
        loadStats();
    } catch (error) {
        showNotification('Ошибка сброса симуляции', 'error');
    }
}

async function testAlgorithms() {
    try {
        const response = await fetch('/api/test_algorithms');
        const data = await response.json();
        
        // Обновляем график точности
        charts.accuracy.data.datasets[0].data = [
            data.bloom_accuracy,
            100 - data.hll_error,
            97 // CMS остается примерным
        ];
        charts.accuracy.update();
        
        showNotification(`Bloom Filter: ${data.bloom_accuracy}% | HyperLogLog ошибка: ${data.hll_error}%`, 'info');
    } catch (error) {
        showNotification('Ошибка тестирования алгоритмов', 'error');
    }
}

async function checkBloomFilter() {
    const userInput = document.getElementById('userInput').value.trim();
    if (!userInput) {
        showNotification('Пожалуйста, введите имя пользователя', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/check_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user: userInput })
        });
        
        const data = await response.json();
        const container = document.getElementById('bloomResult');
        
        let className = 'bloom-false';
        let message = `"${data.user}" НЕ найден в Bloom Filter`;
        
        if (data.bloom_result) {
            if (data.is_false_positive) {
                className = 'bloom-fp';
                message = `⚠️ ЛОЖНОЕ СРАБАТЫВАНИЕ: "${data.user}" найден в Bloom Filter, но не в реальных данных`;
            } else {
                className = 'bloom-true';
                message = `✓ "${data.user}" найден в Bloom Filter`;
            }
        }
        
        container.className = className;
        container.innerHTML = `
            <h5>${message}</h5>
            <small>Точный поиск: ${data.exact_result ? 'Найден' : 'Не найден'}</small>
        `;
        
    } catch (error) {
        showNotification('Ошибка проверки пользователя', 'error');
    }
}

// Вспомогательные функции
function showNotification(message, type = 'info') {
    // Создаем уведомление
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Автоматическое удаление через 3 секунды
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Автоматическое обновление при запущенной симуляции
setInterval(() => {
    if (isSimulating) {
        loadStats();
    }
}, 1000);