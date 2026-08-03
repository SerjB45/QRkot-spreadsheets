import io
from datetime import datetime, timedelta

import xlsxwriter

from app.core.yandex_client import YandexDiskClient
from app.core.config import settings


async def format_time_delta(time_delta: timedelta) -> str:
    '''Утилита для форматирования времени'''
    days = time_delta.days
    hours = time_delta.seconds // 3600
    minutes = (time_delta.seconds % 3600) // 60

    if days > 0:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    client: YandexDiskClient,
    projects: list,
    folder: str = 'Reports'
) -> str:
    """Создаёт отчёт в формате Excel и возвращает публичную ссылку на него"""
    now_date_time = datetime.now().strftime(settings.report_format)
    safe_filename = f'report_{now_date_time}.xlsx'
    print(safe_filename)
    print(folder)
    upload_url, file_path = await client.create_excel_file(
        title=safe_filename, folder=folder
    )

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Отчет")

    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2F75B5',
        'font_color': 'white',
        'border': 1,
        'align': 'center'
    })
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})
    worksheet.merge_range(
        'A1:C1', f'Отчет по проектам на {now_date_time}', title_format
    )

    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col_num, header in enumerate(headers):
        worksheet.write(1, col_num, header, header_format)

    for row, project in enumerate(projects, start=2):
        worksheet.write(row, 0, project.name, cell_format)
        time_delta = project.close_date - project.create_date
        formatted_time = await format_time_delta(time_delta)
        worksheet.write(row, 1, formatted_time, cell_format)
        worksheet.write(row, 2, project.description, cell_format)
    total_projects = len(projects)
    worksheet.write(
        total_projects + 2, 0,
        f'Итого проектов: {total_projects}', cell_format
    )

    worksheet.set_column('A:C', 30)

    workbook.close()
    output.seek(0)
    await client.upload_file(upload_url, output.read())
    return await client.publish_file(file_path)
