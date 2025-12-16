"""
Все вероятностные алгоритмы в одном файле
"""
import math
import random
import hashlib
import mmh3
from typing import Any, List, Dict
from collections import defaultdict


class BloomFilter:
    """Bloom Filter для вероятностной проверки принадлежности"""
    
    def __init__(self, capacity: int, error_rate: float = 0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        self.size = self._calculate_size(capacity, error_rate)
        self.hash_count = self._calculate_hash_count(self.size, capacity)
        self.bit_array = [0] * self.size
        self.count = 0
    
    def _calculate_size(self, n: int, p: float) -> int:
        return int(-(n * math.log(p)) / (math.log(2) ** 2))
    
    def _calculate_hash_count(self, m: int, n: int) -> int:
        return int((m / n) * math.log(2))
    
    def _hashes(self, item: str) -> List[int]:
        return [mmh3.hash(item, i) % self.size for i in range(self.hash_count)]
    
    def add(self, item: str) -> None:
        for h in self._hashes(str(item)):
            self.bit_array[h] = 1
        self.count += 1
    
    def contains(self, item: str) -> bool:
        return all(self.bit_array[h] for h in self._hashes(str(item)))
    
    def __contains__(self, item: str) -> bool:
        return self.contains(item)
    
    def stats(self) -> Dict:
        return {
            'capacity': self.capacity,
            'size': self.size,
            'hash_count': self.hash_count,
            'count': self.count,
            'memory_kb': self.size / 8 / 1024,
            'load': self.count / self.capacity
        }


class HyperLogLog:
    """HyperLogLog для оценки количества уникальных элементов"""
    
    def __init__(self, p: int = 10):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m) if p > 6 else [0.673, 0.697, 0.709][p-4]
    
    def _hash(self, item: str) -> int:
        return int(hashlib.md5(item.encode()).hexdigest()[:16], 16)
    
    def add(self, item: str) -> None:
        x = self._hash(str(item))
        idx = x & (self.m - 1)
        w = x >> self.p
        
        zeros = 1
        while (w & 1) == 0 and zeros <= 32:
            w >>= 1
            zeros += 1
        
        if zeros > self.registers[idx]:
            self.registers[idx] = zeros
    
    def count(self) -> int:
        Z = sum(2.0 ** -r for r in self.registers)
        E = self.alpha * (self.m ** 2) / Z
        
        if E <= 2.5 * self.m:
            zeros = sum(1 for r in self.registers if r == 0)
            if zeros > 0:
                E = self.m * math.log(self.m / zeros)
        
        return int(E)
    
    def stats(self) -> Dict:
        return {
            'precision': self.p,
            'registers': self.m,
            'estimate': self.count(),
            'memory_kb': self.m / 1024
        }


class CountMinSketch:
    """Count-Min Sketch для оценки частоты элементов"""
    
    def __init__(self, width: int, depth: int):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        self._total_count = 0  # Счетчик фактических добавлений
    
    def _hash(self, item: str, seed: int) -> int:
        """Хэш-функция"""
        hash_val = mmh3.hash(item, seed) & 0xffffffff
        return hash_val % self.width
    
    def add(self, item: str, count: int = 1):
        """Добавить элемент"""
        for i in range(self.depth):
            index = self._hash(item, i)
            self.table[i][index] += count
        self._total_count += count  # Учитываем только реальное количество
    
    def estimate(self, item: str) -> int:
        """Оценить частоту элемента"""
        min_count = float('inf')
        for i in range(self.depth):
            index = self._hash(item, i)
            min_count = min(min_count, self.table[i][index])
        return int(min_count)
    
    def top_items(self, k: int, candidates: list[str]) -> list[dict[str, any]]:
        """Найти k наиболее частых элементов"""
        items = []
        for item in candidates:
            count = self.estimate(item)
            if count > 0:
                items.append({"item": item, "count": count})
        
        items.sort(key=lambda x: x["count"], reverse=True)
        return items[:k]
    
    def stats(self) -> dict[str, any]:
        """Статистика Count-Min Sketch"""
        filled_cells = 0
        for row in self.table:
            for cell in row:
                if cell > 0:
                    filled_cells += 1
        
        total_cells = self.width * self.depth
        
        return {
            "width": self.width,
            "depth": self.depth,
            "total_cells": total_cells,
            "filled_cells": filled_cells,
            "fill_percentage": round((filled_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
            "total_count": self._total_count,  
            "memory_kb": (total_cells * 8) / 1024  
        }
