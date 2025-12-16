"""
Тесты для алгоритмов
"""
import pytest
import sys
import os

# Полный путь к корневой директории
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"Python path: {sys.path}")
print(f"Current dir: {current_dir}")
print(f"Parent dir: {parent_dir}")

try:
    from core.algorithms import BloomFilter, HyperLogLog, CountMinSketch
    print("✓ Все модули успешно импортированы")
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    raise


# Тесты BloomFilter
def test_bloom_filter_creation():
    bf = BloomFilter(1000, 0.01)
    assert bf.capacity == 1000
    assert bf.error_rate == 0.01
    assert bf.count == 0


def test_bloom_filter_add_and_check():
    bf = BloomFilter(100, 0.1)
    bf.add("test1")
    bf.add("test2")
    
    assert bf.contains("test1") is True
    assert bf.contains("test2") is True
    assert bf.contains("test3") is False
    assert bf.count == 2


def test_bloom_filter_stats():
    bf = BloomFilter(500, 0.05)
    bf.add("item1")
    stats = bf.stats()
    
    assert 'capacity' in stats
    assert 'size' in stats
    assert 'memory_kb' in stats
    assert stats['count'] == 1


# Тесты HyperLogLog
def test_hyperloglog_creation():
    hll = HyperLogLog(10)
    assert hll.p == 10
    assert hll.m == 1024


def test_hyperloglog_count_unique():
    hll = HyperLogLog(8)
    
    for i in range(100):
        hll.add(f"item{i}")
    
    estimate = hll.count()
    assert 80 <= estimate <= 120


def test_hyperloglog_duplicates():
    hll = HyperLogLog(10)
    
    for _ in range(10):
        hll.add("same_item")
    
    estimate = hll.count()
    assert 1 <= estimate <= 2


def test_hyperloglog_stats():
    hll = HyperLogLog(10)
    hll.add("test")
    stats = hll.stats()
    
    assert 'precision' in stats
    assert 'estimate' in stats
    assert stats['estimate'] >= 1


# Тесты CountMinSketch
def test_count_min_sketch_creation():
    cms = CountMinSketch(100, 3)
    assert cms.width == 100
    assert cms.depth == 3


def test_count_min_sketch_add_and_estimate():
    cms = CountMinSketch(50, 4)
    
    cms.add("item1", 3)
    cms.add("item2", 1)
    cms.add("item1", 2)
    
    assert cms.estimate("item1") >= 5
    assert cms.estimate("item2") >= 1
    assert cms.estimate("item3") == 0


def test_count_min_sketch_top_items():
    cms = CountMinSketch(100, 4)
    candidates = ["A", "B", "C", "D", "E"]
    
    for i in range(10):
        cms.add("A")
    for i in range(5):
        cms.add("B")
    
    top = cms.top_items(2, candidates)
    assert len(top) == 2
    assert top[0]['item'] == "A"
    assert top[0]['count'] >= 10
    assert top[1]['item'] == "B"
    assert top[1]['count'] >= 5


def test_count_min_sketch_stats():
    cms = CountMinSketch(200, 5)
    cms.add("test", 5)
    stats = cms.stats()
    
    assert 'width' in stats
    assert 'depth' in stats
    assert 'total_count' in stats
    assert stats['total_count'] == 5
    assert 'memory_kb' in stats


def test_integration():
    bf = BloomFilter(1000, 0.01)
    for i in range(100):
        bf.add(f"item{i}")
    assert bf.contains("item0") is True
    
    hll = HyperLogLog(10)
    for i in range(1000):
        hll.add(f"item{i % 100}")
    estimate = hll.count()
    assert 90 <= estimate <= 110
    
    cms = CountMinSketch(100, 4)
    for i in range(100):
        cms.add(f"word{i % 10}")
    assert cms.estimate("word0") >= 10


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
