import os
import platform
from pathlib import Path
from typing import Union, List, Tuple
import ctypes
import re

PathString = Union[str, Path]


def is_windows_os() -> bool:
    '''Проверка что программа запущена на Windows'''
    # TODO: Вернуть True если операционная система - Windows
    # Использовать platform.system()
    if platform.system() == 'Windows':
        return True
    return False


def validate_windows_path(path: PathString) -> Tuple[bool, str]:
    '''Проверка корректности Windows пути
    Пока работает только с Path форматом
    '''
    # TODO: Проверить путь на соответствие правилам Windows
    # - Запрещенные символы: / : * ? ' < > |
    # - Длина пути (максимум 260 символов для обычных путей)
    # - Проверка существования пути
    # Вернуть (True, '') если путь валиден, (False, 'сообщение об ошибке') если нет
    # Checking on exist.
    if not path.exists():
        return False, 'File is not exist'
    # Checking on prohibited symbols.
    for part in path.parts:
        if re.search(r'[/:*?\'<>|]', part):
            return False, 'Prohibited symbols'
    # Len check.
    if len(str(path)) > 260:
        return False, 'Too long way - maximum 260 characters'
    return True, ''


def format_size(size_bytes: int) -> str:
    '''Форматирование размера файла в читаемом виде для Windows'''
    # TODO: Преобразовать байты в удобочитаемый формат
    # Пример: 1024 -> '1.0 KB', 1500000 -> '1.4 MB'
    # Учесть что в Windows используются единицы: KB, MB, GB (не KiB, MiB)
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < (1024 ** 2):
        return f'{round(size_bytes / 1024, 1)} KB'
    if size_bytes < (1024 ** 3):
        return f'{round(size_bytes / 1024 ** 2, 1)} MB'
    return f'{round(size_bytes / 1024 ** 3, 1)} GB'


def get_parent_path(path: PathString) -> str:
    '''Получение родительского каталога с учетом Windows путей'''
    # TODO: Вернуть путь к родительскому каталогу
    # Учесть особенности: C:\ → C:\, C:\Users → C:\
    # Использовать os.path.dirname с учетом Windows
    path_obj = Path(path)
    try:
        # Получаем родителя
        parent = path_obj.parent

        # Специальная обработка для корней Windows
        if os.name == 'nt':
            # Проверяем, является ли путь корневым
            drive = path_obj.drive
            parts = path_obj.parts

            # C:\ → C:\
            if drive and len(parts) == 2 and parts[1] == '\\':
                return str(path_obj)

        # Преобразуем в строку
        parent_str = str(parent)

        # Если это текущая директория, возвращаем пустую строку
        if parent_str == '.':
            return ''

        return parent_str

    except Exception:
        # В случае ошибки возвращаем пустую строку
        return ''


def safe_windows_listdir(path: PathString) -> List[str]:
    '''Безопасное получение содержимого каталога в Windows'''
    # TODO: Вернуть список элементов каталога или пустой список при ошибке
    # Обрабатывать Windows-specific ошибки:
    # - PermissionError (отказ в доступе)
    # - FileNotFoundError
    # - OSError для длинных путей
    path_obj = Path(path)
    exit_list = []
    try:
        for child in path_obj.iterdir():
            exit_list.append(str(child))
    except (PermissionError, FileNotFoundError, OSError):
        return []
    return exit_list


def is_hidden_windows_file(path: PathString) -> bool:
    '''Проверка является ли файл скрытым в Windows

    kernel32.dll — это основная системная библиотека (DLL) в Windows,
    которая содержит ключевые функции операционной системы
    для управления процессами, памятью, файлами, устройствами ввода-вывода
    и другими низкоуровневыми операциями.

    Если файл скрыт в системе, то True, если не скрыт, то False

    логика условия:
    FILE_ATTRIBUTE_READONLY    = 0x1
    FILE_ATTRIBUTE_HIDDEN      = 0x2
    FILE_ATTRIBUTE_SYSTEM      = 0x4
    FILE_ATTRIBUTE_DIRECTORY   = 0x10
    FILE_ATTRIBUTE_ARCHIVE     = 0x20
    т.е. с & выдаст True только при если файл не только скрытый.
    '''
    # TODO: Проверить атрибуты файла на наличие FILE_ATTRIBUTE_HIDDEN
    # Использовать os.stat или ctypes для проверки атрибутов Windows
    atr = ctypes.windll.kernel32.GetFileAttributesW(str(path))
    if atr & 2:
        print(atr)
        return True
    return False

# print(is_windows_os())
# way = Path('C:\\Users\chirk\OneDrive\Рабочий стол\desktop.ini')
# print(validate_windows_path(way), way.parts)
# print(is_hidden_windows_file(way))
