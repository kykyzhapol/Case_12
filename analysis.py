# analysis.py - Анализ Windows файловой системы

import os
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import utils  # Функции архитектора
import navigation  # Функции инженера навигации


def count_files(path: str) -> Tuple[bool, int]:
    """Рекурсивный подсчет файлов в Windows каталоге"""
    try:
        result = utils.safe_windows_listdir(path)
        if not isinstance(result, list):
            return False, 0  # Ошибка доступа

        file_count = 0
        success, items = navigation.list_directory(path)
        if not success:
            return False, 0

        for item in items:
            full_path = os.path.join(path, item['name'] + item['type'])
            if item['type'] == '':  # Это папка (в Windows директории не имеют расширения)
                sub_success, sub_count = count_files(full_path)
                if sub_success:
                    file_count += sub_count
                # Игнорируем ошибки в подкаталогах, но продолжаем
            else:
                # Это файл
                file_count += 1

        return True, file_count

    except Exception:
        return False, 0


def count_bytes(path: str) -> Tuple[bool, int]:
    """Рекурсивный подсчет размера файлов в Windows"""
    try:
        result = utils.safe_windows_listdir(path)
        if not isinstance(result, list):
            return False, 0

        total_size = 0
        success, items = navigation.list_directory(path)
        if not success:
            return False, 0

        for item in items:
            full_path = os.path.join(path, item['name'] + item['type'])
            if item['type'] == '':  # Папка
                sub_success, sub_size = count_bytes(full_path)
                if sub_success:
                    total_size += sub_size
            else:
                # Проверим, не является ли файл символической ссылкой или junction point
                try:
                    # В Windows symlink/junction можно проверить через os.path.islink()
                    if os.path.islink(full_path):
                        continue
                    total_size += item['size']
                except (OSError, ValueError):
                    # Недоступен размер — пропускаем
                    continue

        return True, total_size

    except Exception:
        return False, 0


def analyze_windows_file_types(path: str) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
    """Анализ типов файлов с учетом Windows расширений"""
    try:
        success, items = navigation.list_directory(path)
        if not success:
            return False, {}

        # Словарь для агрегации: {'.exe': {'count': 0, 'size': 0}, ...}
        stats = defaultdict(lambda: {'count': 0, 'size': 0})

        for item in items:
            full_path = os.path.join(path, item['name'] + item['type'])
            ext = item['type'].lower()  # Учитываем расширение как есть, в нижнем регистре

            if item['type'] == '':  # Папка — рекурсивно обрабатываем
                sub_success, sub_stats = analyze_windows_file_types(full_path)
                if sub_success:
                    for sub_ext, sub_data in sub_stats.items():
                        stats[sub_ext]['count'] += sub_data['count']
                        stats[sub_ext]['size'] += sub_data['size']
            else:
                # Это файл
                stats[ext]['count'] += 1
                stats[ext]['size'] += item['size']

        # Преобразуем defaultdict в обычный dict
        return True, dict(stats)

    except Exception:
        return False, {}


def get_windows_file_attributes_stats(path: str) -> Dict[str, int]:
    """Статистика по атрибутам файлов Windows"""
    try:
        stats = {'hidden': 0, 'system': 0, 'readonly': 0}
        success, items = navigation.list_directory(path)
        if not success:
            return stats

        for item in items:
            full_path = os.path.join(path, item['name'] + item['type'])
            if item['type'] == '':  # Папка
                sub_stats = get_windows_file_attributes_stats(full_path)
                stats['hidden'] += sub_stats['hidden']
                stats['system'] += sub_stats['system']
                stats['readonly'] += sub_stats['readonly']
            else:
                # Файл
                if utils.is_hidden_windows_file(full_path):
                    stats['hidden'] += 1

                # Получим атрибуты через ctypes (как в is_hidden_windows_file)
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(full_path)
                if attrs == -1:  # Ошибка
                    continue

                if attrs & 0x4:  # FILE_ATTRIBUTE_SYSTEM
                    stats['system'] += 1
                if attrs & 0x1:  # FILE_ATTRIBUTE_READONLY
                    stats['readonly'] += 1

        return stats

    except Exception:
        return {'hidden': 0, 'system': 0, 'readonly': 0}


def _get_largest_files(path: str, n: int = 5) -> List[Tuple[str, int]]:
    """Вспомогательная функция: получение n крупнейших файлов"""
    try:
        largest = []

        def collect_files(current_path):
            nonlocal largest
            success, items = navigation.list_directory(current_path)
            if not success:
                return

            for item in items:
                full_path = os.path.join(current_path, item['name'] + item['type'])
                if item['type'] == '':  # Папка
                    collect_files(full_path)
                else:
                    largest.append((full_path, item['size']))

        collect_files(path)
        largest.sort(key=lambda x: x[1], reverse=True)
        return largest[:n]

    except Exception:
        return []


def show_windows_directory_stats(path: str) -> bool:
    """Комплексный вывод статистики Windows каталога"""
    try:
        print(f"\n=== Анализ каталога: {path} ===\n")

        # 1. Общее количество файлов
        success, file_count = count_files(path)
        if success:
            print(f"Общее количество файлов: {file_count}")
        else:
            print("Не удалось подсчитать файлы")

        # 2. Общий размер
        success, total_bytes = count_bytes(path)
        if success:
            print(f"Общий размер файлов: {utils.format_size(total_bytes)}")
        else:
            print("Не удалось определить общий размер")

        # 3. Распределение по типам
        success, file_types = analyze_windows_file_types(path)
        if success and file_types:
            print("\nРаспределение по расширениям:")
            # Сортируем по количеству файлов
            for ext, data in sorted(file_types.items(), key=lambda x: x[1]['count'], reverse=True):
                if ext == '':
                    ext = '<папка>'  # Хотя папки не должны попадать сюда
                print(f"  {ext}: {data['count']} файл(ов), {utils.format_size(data['size'])}")
        else:
            print("\nНе удалось проанализировать типы файлов")

        # 4. Атрибуты
        attr_stats = get_windows_file_attributes_stats(path)
        print(f"\nАтрибуты файлов:")
        print(f"  Скрытых: {attr_stats['hidden']}")
        print(f"  Системных: {attr_stats['system']}")
        print(f"  Только для чтения: {attr_stats['readonly']}")

        # 5. Крупнейшие файлы
        largest = _get_largest_files(path, 5)
        if largest:
            print(f"\nКрупнейшие файлы:")
            for full_path, size in largest:
                print(f"  {full_path} — {utils.format_size(size)}")
        else:
            print("\nНе удалось определить крупнейшие файлы")

        return True

    except Exception as e:
        print(f"Ошибка при анализе: {e}")
        return False
