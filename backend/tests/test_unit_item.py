import pytest
from models.item import Item
from api.routs.item import find_similar_items

# Модуль управления товарами
class TestFindSimilarItems:    
    def test_find_similar_items_success(self):
        """Тест 1: Проверить возврат списка похожих товаров по категории и цене."""
        target_item = Item(id=1, name="Товар 1", category_id=10, price=100)
        
        all_items = [
            Item(id=1, name="Товар 1", category_id=10, price=100),
            Item(id=2, name="Товар 2", category_id=10, price=105),  # +5
            Item(id=3, name="Товар 3", category_id=10, price=90),   # -10
            Item(id=4, name="Товар 4", category_id=10, price=120),  # +20
            Item(id=5, name="Товар 5", category_id=20, price=95),   # Другая категория
            Item(id=6, name="Товар 6", category_id=10, price=100),  # +0
        ]
        
        result = find_similar_items(all_items, target_item, limit=5)
        
        assert len(result) == 4
        assert result[0].id == 6
        assert result[1].id == 2
        assert result[2].id == 3
        assert result[3].id == 4
        assert all(item.id != 1 for item in result)
        assert all(item.category_id == 10 for item in result)

    def test_find_similar_items_limit(self):
        """Тест 2: Проверить ограничение количества возвращаемых товаров."""
        target_item = Item(id=1, name="Товар 1", category_id=10, price=100)
        
        all_items = [
            Item(id=1, name="Товар 1", category_id=10, price=100),
            Item(id=2, name="Товар 2", category_id=10, price=102),  # +2
            Item(id=3, name="Товар 3", category_id=10, price=103),  # +3
            Item(id=4, name="Товар 4", category_id=10, price=104),  # +4
            Item(id=5, name="Товар 5", category_id=10, price=105),  # +5
            Item(id=6, name="Товар 6", category_id=10, price=106),  # +6
        ]
        
        result = find_similar_items(all_items, target_item, limit=2)
        
        assert len(result) == 2
        assert result[0].id == 2
        assert result[1].id == 3

    def test_find_similar_items_exclude_original(self):
        """Тест 3: Проверить исключение исходного товара из результатов"""
        target_item = Item(id=1, name="Товар 1", category_id=10, price=100)
        
        all_items = [
            Item(id=1, name="Товар 1", category_id=10, price=100),
            Item(id=2, name="Товар 2", category_id=10, price=105),
            Item(id=3, name="Товар 3", category_id=10, price=95),
        ]
        
        result = find_similar_items(all_items, target_item, limit=5)
        
        assert len(result) == 2
        assert all(item.id != 1 for item in result)

    def test_find_similar_items_no_similar(self):
        """Тест 4: Проверить работу при отсутствии товаров в категории"""
        target_item = Item(id=1, name="Товар 1", category_id=10, price=100)
        
        all_items = [
            Item(id=1, name="Товар 1", category_id=10, price=100),
            Item(id=2, name="Товар 2", category_id=20, price=105),
            Item(id=3, name="Товар 3", category_id=30, price=95),
        ]
        
        result = find_similar_items(all_items, target_item, limit=5)
        
        assert len(result) == 0

    def test_find_similar_items_empty_list(self):
        """Тест 5: Проверить работу с пустым списком товаров"""
        target_item = Item(id=1, name="Товар 1", category_id=10, price=100)
        all_items = []
        
        result = find_similar_items(all_items, target_item, limit=5)
        
        assert len(result) == 0

    def test_find_similar_items_none_target(self):
        """Тест 6: Проверить работу с None target_item."""
        all_items = [
            Item(id=1, name="Товар 1", category_id=10, price=100),
            Item(id=2, name="Товар 2", category_id=10, price=105),
        ]
        
        result = find_similar_items(all_items, None, limit=5)
        
        assert len(result) == 0

    def test_find_similar_items_price_sorting(self):
        """Тест 7: Проверить точную сортировку по разнице цен"""
        target_item = Item(id=1, name="Товар 1", category_id=10, price=100)
        
        all_items = [
            Item(id=1, name="Товар 1", category_id=10, price=100),
            Item(id=2, name="Товар 2", category_id=10, price=50),   # 50
            Item(id=3, name="Товар 3", category_id=10, price=150),  # 50
            Item(id=4, name="Товар 4", category_id=10, price=99),   # 1
            Item(id=5, name="Товар 5", category_id=10, price=101),  # 1
            Item(id=6, name="Товар 6", category_id=10, price=200),  # 100
        ]
        
        result = find_similar_items(all_items, target_item, limit=10)
        
        prices = [item.price for item in result]
        assert 99 in prices[:2] or 101 in prices[:2]
        assert 99 in prices[:2] or 101 in prices[:2]
        assert prices[-1] == 200
