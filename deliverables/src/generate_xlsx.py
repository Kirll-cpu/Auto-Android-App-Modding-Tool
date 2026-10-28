# -*- coding: utf-8 -*-
"""Собирает книгу Excel из разобранных таблиц PDF «Исходные таблицы (Практика_06)»."""
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_tables import T  # noqa: E402

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.worksheet.table import Table, TableStyleInfo

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'Ishodnie-Tablitsi-Practika-06.xlsx')

DARK = '1F4E79'
BAND = 'EAF1F8'
HEAD_FONT = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
BODY_FONT = Font(name='Calibri', size=11)
THIN = Side(style='thin', color='B7C6D6')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# ------------------------------------------------------------------ описания
META = {
    '1': dict(
        title='Таблица 1 — Автомобили',
        desc='Марка, номер, годы выпуска и приобретения, цвет, пробег, цена, владелец',
        pages='стр. 1',
        num_cols=[3, 4, 6, 7],
        int_cols=[3, 4],
        center=[1, 2, 3, 4, 5],
        wide={0: 14, 8: 16},
    ),
    '2': dict(
        title='Таблица 2 — Осадки',
        desc='Дата, город, вид и количество осадков, температура, давление, ветер',
        pages='стр. 2–3',
        num_cols=[3, 4, 5, 7],
        int_cols=[3, 4, 5, 7],
        date_cols=[0],
        center=[0, 3, 4, 5, 7],
        wide={1: 14, 6: 18},
    ),
    '3': dict(
        title='Таблица 3 — Студенты и нормативы',
        desc='Фамилия, имя, отчество, дата рождения, факультет, курс, норматив, оценка',
        pages='стр. 3–4',
        num_cols=[4, 6, 9],
        int_cols=[4, 6, 9],
        date_cols=[3],
        center=[3, 4, 6, 8, 9],
        wide={5: 34},
    ),
    '4': dict(
        title='Таблица 4 — Продажа канцтоваров',
        desc='Продавец, товар, страна, количество, цена, сумма, дата, покупатель',
        pages='стр. 4–5',
        num_cols=[3, 4, 5],
        int_cols=[3],
        date_cols=[6],
        center=[2, 3, 4, 5, 6],
        wide={0: 20, 7: 18},
    ),
    '5': dict(
        title='Таблица 5 — Курсовые работы',
        desc='Студент, курс, группа, тема курсовой, руководитель, кафедра, даты, оценка',
        pages='стр. 6–7',
        num_cols=[3, 10],
        int_cols=[3, 10],
        date_cols=[8, 9],
        center=[3, 4, 10],
        wide={5: 30, 6: 20, 7: 34},
    ),
    '6': dict(
        title='Таблица 6 — Книги',
        desc='Название, автор, тема, год и место издания, издательство, страницы, тираж, цена',
        pages='стр. 8–9',
        num_cols=[3, 6, 7, 8],
        int_cols=[3, 6, 7, 8],
        center=[3, 4, 6, 7, 8],
        wide={0: 34, 1: 18},
    ),
}


def as_number(text):
    s = text.strip().replace('\xa0', '').replace(' ', '').replace(',', '.')
    if re.fullmatch(r'-?\d+(\.\d+)?', s):
        f = float(s)
        return int(f) if f.is_integer() else f
    return None


def as_date(text):
    m = re.fullmatch(r'(\d{2})\.(\d{2})\.(\d{4})', text.strip())
    if not m:
        return None
    d, mo, y = map(int, m.groups())
    try:
        return dt.date(y, mo, d)
    except ValueError:
        return None


def write_table(ws, key):
    header, rows = T[key]
    meta = META[key]
    date_cols = set(meta.get('date_cols', []))
    int_cols = set(meta.get('int_cols', []))
    num_cols = set(meta.get('num_cols', []))
    center = set(meta.get('center', []))
    ncol = len(header)

    # заголовок
    for c, name in enumerate(header, start=1):
        cell = ws.cell(row=1, column=c, value=name)
        cell.font = HEAD_FONT
        cell.fill = PatternFill('solid', fgColor=DARK)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[1].height = 46

    bad_dates = []
    for r, raw in enumerate(rows, start=2):
        for c, text in enumerate(raw, start=1):
            idx = c - 1
            value = text if text != '' else None
            if text:
                if idx in date_cols:
                    d = as_date(text)
                    if d is not None:
                        value = d
                    else:
                        bad_dates.append((r, c, text))
                elif idx in num_cols:
                    n = as_number(text)
                    if n is not None:
                        value = n
            cell = ws.cell(row=r, column=c, value=value)
            cell.font = BODY_FONT
            cell.border = BORDER
            if idx in date_cols:
                cell.number_format = 'DD.MM.YYYY'
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif idx in num_cols:
                fmt = '#,##0' if idx in int_cols else '#,##0.##'
                cell.number_format = fmt
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif idx in center:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            if r % 2 == 1:
                cell.fill = PatternFill('solid', fgColor=BAND)

    # «плохие» даты — подсветить и пояснить
    for r, c, text in bad_dates:
        cell = ws.cell(row=r, column=c)
        cell.fill = PatternFill('solid', fgColor='FDE9D9')
        cell.comment = None
        cell.number_format = '@'
        cell.alignment = Alignment(horizontal='center', vertical='center')

    last_col = get_column_letter(ncol)
    last_row = len(rows) + 1
    ref = f'A1:{last_col}{last_row}'
    table = Table(displayName=f'Table{key}', ref=ref)
    table.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=False,
                                          showColumnStripes=False, showFirstColumn=False,
                                          showLastColumn=False)
    ws.add_table(table)

    ws.freeze_panes = 'A2'   # фильтр даёт сама таблица (Table), дублировать ws.auto_filter нельзя

    # ширины колонок
    for c in range(ncol):
        widest = len(header[c])
        for row in rows:
            val = row[c]
            widest = max(widest, len(val))
        width = min(max(widest + 2, 10), 40)
        width = meta['wide'].get(c, width) if c in meta['wide'] else width
        ws.column_dimensions[get_column_letter(c + 1)].width = max(width, 10)

    ws.sheet_view.showGridLines = False
    # печать: альбомная, по ширине листа, шапка повторяется на каждой странице
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = '1:1'
    ws.print_options.horizontalCentered = True
    return last_row


def main():
    wb = Workbook()
    idx = wb.active
    idx.title = 'Содержание'

    total_rows = {}
    for key in ['1', '2', '3', '4', '5', '6']:
        ws = wb.create_sheet(f'Таблица {key}')
        total_rows[key] = write_table(ws, key) - 1

    # ---------------------------------------------------------- Содержание
    idx.sheet_view.showGridLines = False
    for col, width in {'A': 3, 'B': 5, 'C': 34, 'D': 62, 'E': 11, 'F': 11, 'G': 15}.items():
        idx.column_dimensions[col].width = width

    idx['B2'] = 'Исходные данные для выполнения заданий'
    idx['B2'].font = Font(name='Calibri', size=16, bold=True, color=DARK)
    idx['B3'] = 'Практика № 6 — 6 таблиц, перенесённых из PDF «Ishodnie Tablitsi (Practika_06).pdf»'
    idx['B3'].font = Font(name='Calibri', size=11, italic=True, color='595959')

    heads = ['№', 'Лист', 'Содержание', 'Записей', 'Колонок', 'Страницы PDF']
    for c, h in enumerate(heads, start=2):
        cell = idx.cell(row=5, column=c, value=h)
        cell.font = HEAD_FONT
        cell.fill = PatternFill('solid', fgColor=DARK)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER

    for i, key in enumerate(['1', '2', '3', '4', '5', '6']):
        r = 6 + i
        meta = META[key]
        vals = [key, meta['title'], meta['desc'], total_rows[key], len(T[key][0]), meta['pages']]
        for c, v in enumerate(vals, start=2):
            cell = idx.cell(row=r, column=c, value=v)
            cell.font = BODY_FONT
            cell.border = BORDER
            if c in (2, 4, 5, 6):
                cell.alignment = Alignment(horizontal='center', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            if i % 2 == 1:
                cell.fill = PatternFill('solid', fgColor=BAND)
        idx.row_dimensions[r].height = 30
        link_cell = idx.cell(row=r, column=3)
        link_cell.hyperlink = f"#'Таблица {key}'!A1"
        link_cell.font = Font(name='Calibri', size=11, color='0563C1', underline='single')

    idx['C13'] = 'Всего записей'
    idx['C13'].font = Font(bold=True)
    idx['C13'].alignment = Alignment(horizontal='right')
    idx['E13'] = '=SUM(E6:E11)'
    idx['E13'].font = Font(bold=True)
    idx['E13'].alignment = Alignment(horizontal='center')
    idx['E13'].fill = PatternFill('solid', fgColor=BAND)

    notes = [
        'Как пользоваться: на каждом листе включён автофильтр (стрелки в заголовках) и закреплена шапка.',
        'Числа (пробег, цена, количество, тираж, давление, температура и т. д.) записаны как числа — по ним работают СУММ, СРЗНАЧ, МИН, МАКС и сводные таблицы.',
        'Даты записаны как настоящие даты Excel (формат ДД.ММ.ГГГГ), а не как текст — можно фильтровать по диапазону и сортировать.',
        'Полный список правок и особенностей исходных данных — на листе «Примечания».',
    ]
    r = 15
    idx.cell(row=r, column=2, value='Примечания').font = Font(bold=True, size=12, color=DARK)
    for n, txt in enumerate(notes, start=1):
        cell = idx.cell(row=r + n, column=2, value=f'• {txt}')
        cell.font = Font(size=10, italic=True, color='404040')
        cell.alignment = Alignment(vertical='center')

    # ---------------------------------------------------------- Примечания
    ws = wb.create_sheet('Примечания')
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 4
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 100
    ws['B2'] = 'Что учтено при переносе данных'
    ws['B2'].font = Font(size=14, bold=True, color=DARK)

    items = [
        ('Все 6 таблиц', 'Перенесены полностью, без сокращений: 21 + 24 + 24 + 23 + 24 + 24 = 140 записей.'),
        ('Таблица 2', 'Две последние строки (Мариуполь 25.05.2006 и Славянск 30.04.2006) в PDF попали на страницу 3 с «разорванной» шапкой — даты восстановлены и строки добавлены в общую таблицу.'),
        ('Таблица 3', 'Строка «Сидоров Сидор Сидорович» в исходнике оставлена с пустой ячейкой «Оценка» — так в PDF.'),
        ('Таблица 4', 'Дата «31.06.2006» не существует (в июне 30 дней). Такая дата не может быть датой Excel, поэтому оставлена текстом и подсвечена на листе «Таблица 4». Стоит уточнить у преподавателя.'),
        ('Таблица 6', 'В исходнике колонки «Место издания» и «Издательство» перепутаны (Москва стояла в «Издательство»). Здесь они приведены к правильному смыслу: Место издания = Москва / Киев / Минск, Издательство = Эксмо, АСТ, Правда и т. д.'),
        ('Таблица 6', 'Названия восстановлены после переносов: «Мастер и маргарита», «Избранные произведения в двух томах», «Повести и рассказы. Том 1», «Избранные произведения. Том первый».'),
        ('Описания', 'В таблице 5 темы курсовых в исходнике обрезаны многоточием («Управление…», «Горная ….», «Системы….») — сохранено как есть, дописать их неоткуда.'),
        ('Сортировка', 'Порядок строк сохранён таким же, как в PDF (не сортировался), чтобы номера заданий совпадали с исходником.'),
    ]
    for i, (what, text) in enumerate(items):
        r = 4 + i
        a = ws.cell(row=r, column=2, value=what)
        a.font = Font(bold=True)
        a.alignment = Alignment(vertical='top')
        b = ws.cell(row=r, column=3, value=text)
        b.alignment = Alignment(wrap_text=True, vertical='top')
        b.font = BODY_FONT
        ws.row_dimensions[r].height = 34 if len(text) < 120 else 48

    # порядок листов и цвета
    order = ['Содержание', 'Таблица 1', 'Таблица 2', 'Таблица 3',
             'Таблица 4', 'Таблица 5', 'Таблица 6', 'Примечания']
    wb._sheets = [wb[name] for name in order]
    wb['Содержание'].sheet_properties.tabColor = DARK
    for key, color in zip(['1', '2', '3', '4', '5', '6'],
                          ['2E75B6', '2E75B6', '2E75B6', '548235', '548235', '548235']):
        wb[f'Таблица {key}'].sheet_properties.tabColor = color
    wb['Примечания'].sheet_properties.tabColor = 'A5A5A5'

    wb.properties.title = 'Исходные данные для выполнения заданий — Практика № 6'
    wb.properties.subject = '6 таблиц из Ishodnie Tablitsi (Practika_06).pdf'
    wb.properties.creator = 'Подготовлено в Arena Agent Mode'
    wb.active = 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print('saved:', OUT, os.path.getsize(OUT), 'bytes')
    print('rows per table:', total_rows)


if __name__ == '__main__':
    main()
