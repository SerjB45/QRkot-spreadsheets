import io
from datetime import UTC, datetime, timedelta

import xlsxwriter

from app.core.config import settings
from app.core.constants import (BORDER_SIZE, COLUMN_WIDTH, SECONDS_IN_HOUR,
                                SECONDS_IN_MINUTE, TITLE_SIZE)
from app.core.yandex_client import YandexDiskClient


async def format_time_delta(time_delta: timedelta) -> str:
    '''Утилита для форматирования времени'''
    days = time_delta.days
    hours = time_delta.seconds // SECONDS_IN_HOUR
    minutes = (time_delta.seconds % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE

    if days > 0:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    client: YandexDiskClient,
    projects: list,
    folder: str = 'Reports'
) -> str:
    '''Создаёт отчёт в формате Excel и возвращает публичную ссылку на него'''
    now_date_time = datetime.now(UTC).strftime(settings.report_format)
    safe_filename = f'report_{now_date_time}'
    upload_url, file_path = await client.create_excel_file(
        title=safe_filename, folder=folder
    )

    excel_data = b''
    with io.BytesIO() as output:
        with xlsxwriter.Workbook(output) as workbook:
            worksheet = workbook.add_worksheet('Отчет')

            title_format = workbook.add_format(
                {'bold': True, 'font_size': TITLE_SIZE}
            )
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2F75B5',
                'font_color': 'white',
                'border': BORDER_SIZE,
                'align': 'center'
            })
            cell_format = workbook.add_format(
                {'border': BORDER_SIZE, 'align': 'center'}
            )
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

            worksheet.set_column('A:C', COLUMN_WIDTH)
        excel_data = output.getvalue()

    await client.upload_file(upload_url, excel_data)
    return await client.publish_file(file_path)
