import os
import re
from typing import List, Dict, Any, Tuple

import utils  # Функции архитектора
import navigation  # Функции инженера навигации
import analysis
from analysis import show_windows_directory_stats


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
    """Обработчик меню поиска для Windows
    Поиск файла по шаблону
    По списку расширений
    Поиск крупных файлов
    Поиск системных файлов
    """
    # TODO: Реализовать интерактивное меню используя ВСЕ функции поиска
    # Использовать match case для навигации по меню
    # Интегрировать функции из analysis для показа статистики поиска
    # Вернуть True если пользователь хочет продолжить поиск
    print('Меню поиска:'
    '1. Поиск файлов по имени/шаблону'
    '2. Поиск по расширению файла'
    '3. Поиск крупных файлов'
    '4. Поиск системных файлов Windows'
    '5. Статистика текущей директории'
    '0. Не хочу продолжать поиск')
    choice = input('\nВыберите действие (0-7):')

    match choice:
        case 1:
            print('Поиск файлов по имени/шаблону\n'
                  'Доступные шаблоны:'
                  '* - любое количество символов'
                  '? - один любой символ'
                  'Примеры: *.txt, document?.docx, report_*.pdf')
            pattern = input('\nВведите шаблон для поиска: ')
            case_sensitive = input('Чувствительность к регистру? (y/N): ')
            file_count = find_files_windows(pattern, current_path, case_sensitive == 'y')
            print(f'Результаты поиска:'
                  f'{file_count}'
                  f'')#Докинуть статистику
        case 2:
            print('Поиск по расширению файла'
                  'Пример ввода: .txt, .exe, .pdf')
            ext = input('добавьте расширения через запятую').split(',')
            print(f'Результаты поиска:'
                  f'find_by_windows_extension(ext, current_path)'
                  f'')#Докинуть статистику
        case 3:
            print('Поиск крупных файлов')
            min_size = input('Минимальный размер файлов в MB'
                             '(по умолчанию 10)')
            min_size_mb = float(min_size) if min_size else 10.0
            print(f'Файлы размером больше {min_size_mb} MB:')
            large_files = find_large_files_windows(min_size_mb, current_path)
            print(large_files.sort(key=lambda x: x['size_mb'], reverse=True))
            # Добавить инфо
        case 4:
            print('Поиск системных файлов'
                  '\n !!!ВНИМАНИЕ!!!'
                  'Системные файлы Windows важны для работы ОС.'
                  'Не изменяйте и не удаляйте их без необходимости!')
            try:
                system_files = find_windows_system_files(current_path)
                if system_files:
                    print(f'Найденные системные файлы:'
                          f'{system_files}')
                else:
                    print('Системные файлы не найдены в текущей директории')
            except Exception as e:
                print(f'Ошибка при поиске: {e}')
        case 5:
            print(f'Статистика текущей директории:'
                  f'{show_windows_directory_stats(current_path)}')
        case 0:
            confirm = input('Вы уверены, что хотите выйти? (y/N):')
            if confirm == 'y': print('До свидания!')
            return False
    return True


def format_windows_search_results(results: List, search_type: str) -> None:
    import analysis as al
    import utils as ut
    """Форматированный вывод результатов поиска для Windows
    Допустим, список это список директорий???
    """
    # TODO: Красиво отформатировать вывод в зависимости от типа поиска
    # Использовать utils.format_size() для размеров
    # Показывать атрибуты файлов через analysis.get_windows_file_attributes_stats()
    print('Результаты поиска:'
          '='*60)
    for result in results:
        print(f'Путь - {result}')
        if al.count_files(result)[0]:
            print(f'Количество файлов = {al.count_files(result)[1]}')
        if al.count_bytes(result)[0]:
            print(f'Размер файлов={ut.format_size(al.count_bytes(result)[1])}')
        print('Атрибуты:')
        attributes = al.get_windows_file_attributes_stats(result)
        print(f'hidden = {attributes.get('hidden', 0)}')
        print(f'system = {attributes.get('system', 0)}')
        print(f'readonly = {attributes.get('readonly', 0)}')
