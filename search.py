import os
import re
from typing import List, Dict, Any, Tuple

import utils  # Функции архитектора
import navigation  # Функции инженера навигации
import analysis


def find_files_windows(pattern: str, path: str, case_sensitive: bool = False) -> List[str]:
    """Поиск файлов по шаблону в Windows"""
    # TODO: Использовать navigation.list_directory() для рекурсивного обхода
    # Реализовать поддержку Windows wildcards: *, ?
    # Учесть регистр (по умолчанию - регистронезависимый поиск)
    # Использовать analysis.count_files() для отслеживания прогресса

    file_list = navigation.list_directory(path)[1]

    reg_ex_l = ''
    for latter in pattern:
        if latter.lower() == '*':
            reg_ex_l += '(.)*'
        elif latter.lower() == '?':
            reg_ex_l += '(.)'
        else:
            reg_ex_l += latter.lower()
    reg_ex = fr'{reg_ex_l}'

    name_list = []
    for file_data in file_list:
        name = file_data['name'].lower()

        for r_item in re.finditer(reg_ex, name):
            if r_item.group() == name:
                name_list.append(name)

    return name_list



def find_by_windows_extension(extensions: List[str], path: str) -> List[str]:
    """Поиск файлов по списку расширений Windows"""
    # TODO: Использовать analysis.analyze_windows_file_types() для оптимизации
    # Поддерживать поиск по нескольким расширениям: ['.exe', '.msi', '.dll']
    # Автоматически добавлять точку если нужно

    for index in range(len(extensions)):
        if extensions[index][0] != '.':
            extensions[index] = '.' + extensions[index]

    search_result = []
    catalog_info = navigation.list_directory(path)[1]
    for file_info in catalog_info:
        if file_info['type'] in extensions:
            search_result.append(file_info['name'])

    return search_result




    pass

def find_large_files_windows(min_size_mb: float, path: str) -> List[Dict[str, Any]]:
    """Поиск крупных файлов в Windows"""
    # TODO: Использовать analysis.count_bytes() для расчета размеров
    # Вернуть список словарей с информацией о файлах:
    # [{'path': '...', 'size_mb': 150.5, 'type': '.zip'}, ...]

    path_list = utils.safe_windows_listdir(path)[1]
    list_info = []
    for path in path_list:
        if (analysis.count_files(path)[0] and
                analysis.count_files(path)[1] >= min_size_mb):
            info = {'path' : path, 
                    'size' : analysis.count_files(path)[1], 
                    'type' : navigation.list_directory(path)[1][0]['type']}
            list_info.append(info)
    return list_info

def find_windows_system_files() -> List[str]:
    """Поиск системных файлов Windows"""
    # TODO: Найти файлы характерные для Windows системы
    # .exe, .dll, .sys в каталогах Windows, System32 и т.д.
    # Использовать navigation.get_windows_special_folders()

    system_files = []
    system_cotolog = {
        'windows' : 'C:\\Windows',
        'system32': 'C:\\Windows\\System32',
        'syswow64': 'C:\\Windows\\SysWOW64',
        'program_files': 'C:\\Program Files',
        'program_files_x86': 'C:\\Program Files (x86)'
    }

    key = list(system_cotolog.keys())
    for catalog in key:
        path_catalog = system_cotolog[catalog]

        system_files_by_cotolog = (
            find_by_windows_extension(['.exe', '.dll', '.sys'], path_catalog))
        system_files += system_files_by_cotolog

    return system_files


def search_menu_handler(current_path: str) -> bool:
    """Обработчик меню поиска для Windows"""
    # TODO: Реализовать интерактивное меню используя ВСЕ функции поиска
    # Использовать match case для навигации по меню
    # Интегрировать функции из analysis для показа статистики поиска
    # Вернуть True если пользователь хочет продолжить поиск
    pass

def format_windows_search_results(results: List, search_type: str) -> None:
    """Форматированный вывод результатов поиска для Windows"""
    # TODO: Красиво отформатировать вывод в зависимости от типа поиска
    # Использовать utils.format_size() для размеров
    # Показывать атрибуты файлов через analysis.get_windows_file_attributes_stats()
    pass
