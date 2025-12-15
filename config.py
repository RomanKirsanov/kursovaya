"""
Конфигурация приложения
"""
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ключ-разработки-вероятностные-алгоритмы'
    
    # Настройки алгоритмов
    BLOOM_CAPACITY = 5000
    BLOOM_ERROR_RATE = 0.01
    HLL_PRECISION = 10
    CMS_WIDTH = 500
    CMS_DEPTH = 4
    
    # Настройки симуляции
    SIMULATION_ENABLED = True
    SIMULATION_SPEED = 1.0
    MAX_HISTORY = 100
    
    # Пути
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    
    # Настройки языка
    LANGUAGE = 'ru'
    TIMEZONE = 'Europe/Moscow'