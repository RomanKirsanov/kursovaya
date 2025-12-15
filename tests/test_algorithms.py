"""
Тесты для алгоритмов
"""
import pytest
from core.algorithms import BloomFilter, HyperLogLog, CountMinSketch


class TestBloomFilter:
    """Тесты для Bloom Filter"""
    
    def test_bloom_creation(self):
        bf = BloomFilter(1000, 0.01)
        assert bf.capacity == 1000
        assert bf.error_rate == 0.01
        assert bf.count == 0
    
    def test_bloom_add_and_check(self):
        bf = BloomFilter(100, 0.1)
        bf.add("test1")
        bf.add("test2")
        
        assert bf.contains("test1")
        assert bf.contains("test2")
        assert not bf.contains("test3")
        assert bf.count == 2
    
    def test_bloom_stats(self):
        bf = BloomFilter(500, 0.05)
        bf.add("item1")
        stats = bf.stats()
        
        assert 'capacity' in stats
        assert 'size' in stats
        assert 'memory_kb' in stats
        assert stats['count'] == 1


class TestHyperLogLog:
    """Тесты для HyperLogLog"""
    
    def test_hll_creation(self):
        hll = HyperLogLog(10)
        assert hll.p == 10
        assert hll.m == 1024
    
    def test_hll_count_unique(self):
        hll = HyperLogLog(8)
        
        # Добавляем 100 уникальных элементов
        for i in range(100):
            hll.add(f"item{i}")
        
        estimate = hll.count()
        assert 80 <= estimate <= 120  # Допускаем погрешность 20%
    
    def test_hll_duplicates(self):
        hll = HyperLogLog(10)
        
        # Добавляем дубликаты
        for _ in range(10):
            hll.add("same_item")
        
        estimate = hll.count()
        assert estimate == 1  # Должен считать как 1 уникальный элемент
    
    def test_hll_stats(self):
        hll = HyperLogLog(10)
        hll.add("test")
        stats = hll.stats()
        
        assert 'precision' in stats
        assert 'estimate' in stats
        assert stats['estimate'] >= 1


class TestCountMinSketch:
    """Тесты для Count-Min Sketch"""
    
    def test_cms_creation(self):
        cms = CountMinSketch(100, 3)
        assert cms.width == 100
        assert cms.depth == 3
    
    def test_cms_add_and_estimate(self):
        cms = CountMinSketch(50, 4)
        
        cms.add("item1", 3)
        cms.add("item2", 1)
        cms.add("item1", 2)
        
        assert cms.estimate("item1") == 5
        assert cms.estimate("item2") == 1
        assert cms.estimate("item3") == 0
    
    def test_cms_top_items(self):
        cms = CountMinSketch(100, 4)
        candidates = ["A", "B", "C", "D", "E"]
        
        for i in range(10):
            cms.add("A")
        for i in range(5):
            cms.add("B")
        
        top = cms.top_items(2, candidates)
        assert len(top) == 2
        assert top[0]['item'] == "A"
        assert top[0]['count'] == 10
        assert top[1]['item'] == "B"
    
    def test_cms_stats(self):
        cms = CountMinSketch(200, 5)
        cms.add("test", 5)
        stats = cms.stats()
        
        assert 'width' in stats
        assert 'total_count' in stats
        assert stats['total_count'] == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])