"""
Симулятор социальной сети 
"""
import random
from datetime import datetime
from typing import Dict, List
from .algorithms import BloomFilter, HyperLogLog, CountMinSketch


class SocialSimulator:
    """Симулятор потока данных из социальной сети"""
    
    def __init__(self):
        self.users = self._generate_users(500)
        self.hashtags = [
            "#ИИ", "#МашинноеОбучение", "#НаукаДанных", "#Python", "#JavaScript",
            "#Технологии", "#Программирование", "#ВебРазработка", "#Облако", "#ИнтернетВещей",
            "#БольшиеДанные", "#Аналитика", "#Стартап", "#Бизнес", "#Новости"
        ]
        self.platforms = ["Твиттер", "Инстаграм", "Фейсбук", "ЛинкедИн"]
        
        # Инициализация алгоритмов
        self.bloom = BloomFilter(5000, 0.01)
        self.hll = HyperLogLog(10)
        self.cms = CountMinSketch(500, 4)
        
        self.posts_history = []
        self.metrics_history = []
        self.max_history = 100
    
    def _generate_users(self, n: int) -> List[str]:
        names = ["Алексей", "Мария", "Иван", "Екатерина", "Дмитрий", 
                "Анна", "Михаил", "Ольга", "Сергей", "Наталья"]
        surnames = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
                   "Попов", "Васильев", "Соколов", "Михайлов", "Новиков"]
        
        return [f"{random.choice(names)}{random.choice(surnames)}{i}" for i in range(n)]
    
    def generate_post(self) -> Dict:
        """Генерирует случайный пост"""
        user = random.choice(self.users)
        platform = random.choice(self.platforms)
        hashtag = random.choice(self.hashtags)
        
        # Тексты постов на русском
        post_templates = [
            f"Только что узнал о новых возможностях {hashtag}!",
            f"Новый пост о {hashtag} от {user}",
            f"Интересные мысли по теме {hashtag}",
            f"Делимся опытом работы с {hashtag}",
            f"Свежие новости из мира {hashtag}",
            f"Обсуждение трендов в области {hashtag}",
            f"Практическое применение {hashtag} в проектах",
            f"Анализ современных подходов к {hashtag}"
        ]
        
        # Обновляем алгоритмы
        self.bloom.add(user)
        self.hll.add(user)
        self.cms.add(hashtag)
        
        post = {
            'id': len(self.posts_history),
            'user': user,
            'platform': platform,
            'hashtag': hashtag,
            'text': random.choice(post_templates),
            'likes': random.randint(0, 100),
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        self.posts_history.append(post)
        
        # Обновляем историю метрик
        self.metrics_history.append({
            'time': post['timestamp'],
            'unique_users': self.hll.count(),
            'total_posts': len(self.posts_history),
            'online_users': self.bloom.count
        })
        
        # Ограничиваем историю
        if len(self.posts_history) > self.max_history:
            self.posts_history.pop(0)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        return post
    
    def get_stats(self) -> Dict:
        """Возвращает статистику по всем алгоритмам"""
        return {
            'bloom': self.bloom.stats(),
            'hll': self.hll.stats(),
            'cms': self.cms.stats(),
            'posts_count': len(self.posts_history),
            'recent_posts': self.posts_history[-10:] if self.posts_history else []
        }
    
    def get_trending_hashtags(self, n: int = 5) -> List[Dict]:
        """Возвращает топ N популярных хештегов"""
        return self.cms.top_items(n, self.hashtags)
    
    def reset(self) -> None:
        """Сброс симуляции"""
        self.posts_history.clear()
        self.metrics_history.clear()
        self.bloom = BloomFilter(5000, 0.01)
        self.hll = HyperLogLog(10)
        self.cms = CountMinSketch(500, 4)