"""
Основное Flask приложение 
"""
from flask import Flask, render_template, jsonify, request
import json
import time
from threading import Thread, Lock
from datetime import datetime

from config import Config
from core.simulator import SocialSimulator

# Инициализация Flask
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация симулятора
simulator = SocialSimulator()
simulation_lock = Lock()
is_simulating = False

def simulation_thread():
    """Поток для генерации данных"""
    global is_simulating
    while is_simulating:
        with simulation_lock:
            simulator.generate_post()
        time.sleep(0.5)  # Пауза между постами

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Запуск симуляции"""
    global is_simulating
    if not is_simulating:
        is_simulating = True
        thread = Thread(target=simulation_thread)
        thread.daemon = True
        thread.start()
    return jsonify({'status': 'started', 'message': 'Симуляция запущена'})

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Остановка симуляции"""
    global is_simulating
    is_simulating = False
    return jsonify({'status': 'stopped', 'message': 'Симуляция остановлена'})

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    """Сброс симуляции"""
    global is_simulating
    is_simulating = False
    time.sleep(0.1)  # Даем время остановиться
    with simulation_lock:
        simulator.reset()
    return jsonify({'status': 'reset', 'message': 'Симуляция сброшена'})

@app.route('/api/stats')
def get_stats():
    """Получение статистики"""
    with simulation_lock:
        stats = simulator.get_stats()
        trending = simulator.get_trending_hashtags(5)
        metrics = simulator.metrics_history[-20:] if simulator.metrics_history else []
    
    return jsonify({
        'stats': stats,
        'trending': trending,
        'metrics': metrics,
        'is_simulating': is_simulating,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

@app.route('/api/check_user', methods=['POST'])
def check_user():
    """Проверка пользователя через Bloom Filter"""
    data = request.json
    user = data.get('user', '')
    
    with simulation_lock:
        exists = user in simulator.bloom
        exact = user in [p['user'] for p in simulator.posts_history]
    
    return jsonify({
        'user': user,
        'bloom_result': exists,
        'exact_result': exact,
        'is_false_positive': exists and not exact
    })

@app.route('/api/test_algorithms')
def test_algorithms():
    """Тестирование точности алгоритмов"""
    test_users = [f"ТестовыйПользователь{i}" for i in range(100)]
    
    with simulation_lock:
        # Добавляем тестовых пользователей
        for user in test_users:
            simulator.bloom.add(user)
            simulator.hll.add(user)
        
        # Считаем точность
        bloom_accuracy = sum(1 for u in test_users if u in simulator.bloom) / len(test_users) * 100
        
        # Тест HLL
        simulator.hll.add("дополнительный_пользователь")
        hll_estimate = simulator.hll.count()
        hll_actual = len(set(test_users + ["дополнительный_пользователь"]))
        hll_error = abs(hll_estimate - hll_actual) / hll_actual * 100 if hll_actual > 0 else 0
    
    return jsonify({
        'bloom_accuracy': round(bloom_accuracy, 2),
        'hll_estimate': hll_estimate,
        'hll_actual': hll_actual,
        'hll_error': round(hll_error, 2)
    })

if __name__ == '__main__':
    print("Запуск приложения...")
    print("Откройте http://localhost:5000 в браузере")
    app.run(debug=True, host='0.0.0.0', port=5000)