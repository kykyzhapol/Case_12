import os
import platform
from pathlib import Path
from typing import Union, List, Tuple
import ctypes
import re

PathString = Union[str, Path]


def is_windows_os() -> bool:
    """Проверка что программа запущена на Windows"""
    # TODO: Вернуть True если операционная система - Windows
    # Использовать platform.system()
    if platform.system() == 'Windows':
        return True
    return False


def validate_windows_path(path: PathString) -> Tuple[bool, str]:
    """Проверка корректности Windows пути
    Пока работает только с Path форматом
    """
    # TODO: Проверить путь на соответствие правилам Windows
    # - Запрещенные символы: / : * ? " < > |
    # - Длина пути (максимум 260 символов для обычных путей)
    # - Проверка существования пути
    # Вернуть (True, "") если путь валиден, (False, "сообщение об ошибке") если нет
    # Checking on exist.
    if not path.exists():
        return False, 'File is not exist'
    # Checking on prohibited symbols.
    for part in path.parts:
        if re.search(r'[/:*?"<>|]', part):
            return False, 'Prohibited symbols'
    # Len check.
    if len(str(path)) > 260:
        return False, 'Too long way - maximum 260 characters'
    return True, ''


def format_size(size_bytes: int) -> str:
    """Форматирование размера файла в читаемом виде для Windows"""
    # TODO: Преобразовать байты в удобочитаемый формат
    # Пример: 1024 -> "1.0 KB", 1500000 -> "1.4 MB"
    # Учесть что в Windows используются единицы: KB, MB, GB (не KiB, MiB)
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < (1024 ** 2):
        return f'{round(size_bytes / 1024, 1)} KB'
    if size_bytes < (1024 ** 3):
        return f'{round(size_bytes / 1024**2, 1)} MB'
    return f'{round(size_bytes / 1024**3, 1)} GB'


def get_parent_path(path: PathString) -> str:
    """Получение родительского каталога с учетом Windows путей"""
    # TODO: Вернуть путь к родительскому каталогу
    # Учесть особенности: C:\ → C:\, C:\Users → C:\
    # Использовать os.path.dirname с учетом Windows
    pass


def safe_windows_listdir(path: PathString) -> List[str]:
    """Безопасное получение содержимого каталога в Windows"""
    # TODO: Вернуть список элементов каталога или пустой список при ошибке
    # Обрабатывать Windows-specific ошибки:
    # - PermissionError (отказ в доступе)
    # - FileNotFoundError
    # - OSError для длинных путей
    pass


def is_hidden_windows_file(path: PathString) -> bool:
    """Проверка является ли файл скрытым в Windows"""
    # TODO: Проверить атрибуты файла на наличие FILE_ATTRIBUTE_HIDDEN
    # Использовать os.stat или ctypes для проверки атрибутов Windows
    pass


#print(is_windows_os())
#way = Path('\Program1\example.txt')
#print(validate_windows_path(way), way.parts)
