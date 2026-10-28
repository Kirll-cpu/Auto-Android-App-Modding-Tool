# -*- coding: utf-8 -*-
"""Разбор таблиц из PDF «Исходные таблицы (Практика_06)» в чистые структуры."""
import json
import re

RAW = json.load(open('/home/user/.build/raw_tables.json'))


def cell_lines(cell):
    if not cell:
        return []
    return [l.strip() for l in cell.split('\n') if l.strip()]


# Пары «конец строки + начало следующей строки», где перенос НЕ является концом слова.
NEEDS_SPACE = {
    ('для', 'офиса'), ('для', 'школы'), ('для', 'мышело'),
    ('Управления', 'предприятием'),
    ('100', 'м'), ('500', 'м'),
    ('в', 'длину'), ('в', 'высоту'), ('в', 'двух'), ('в', 'горной'),
    ('ьной', 'техники'),
    ('ванных', 'систем'), ('систем', 'управления'),
    ('метание', 'диска'),
    ('Экономики', 'и'), ('и', 'менеджмен'), ('и', 'информаци'),
    ('и', 'информатика'), ('и', 'рассказ'), ('и', 'маргари'),
    ('Лучшая', 'канцеляри'),
    ('мической', 'деятельности'), ('деятельности', 'предприятий'),
    ('жмент', 'в'),
    ('ы', 'управл'), ('ы', 'номер'), ('ы', 'модели'),
    ('трех', 'томах'),
    ('на', 'снегу'), ('Танцы', 'на'),
    ('Война', 'мага'), ('том', '3'),
    ('Образ', 'врага'), ('Башня', 'шутов'),
    ('Выбери', 'себе'), ('себе', 'смерть'),
    ('Пружина', 'для'),
    ('Шахты', 'и….'),
    ('ика', 'предпр'),
    ('Горное', 'дело'), ('Горная', 'промы'),
    ('Год', 'пост'), ('Год', 'издан'), ('Год', 'выпу'), ('Год', 'приобр'),
    ('Дата', 'рождени'), ('Дата', 'выдачи'), ('Дата', 'защиты'),
    ('Тема', 'курсов'), ('Тема', 'книги'), ('ой', 'работы'),
    ('Место', 'издания'),
    ('Марка', 'машины'), ('Буквы', 'номер'), ('Цвет', 'машины'),
    ('Вид', 'осадко'), ('Сила', 'ветра'), ('На', 'сумму'), ('Страна', 'импорте'),
    ('Продавец', '(фирма)'), ('Покупатель', '(фирма)'),
    ('Обработка', 'металлов'), ('металлов', 'давлением'),
    ('мм', 'ртутного'), ('ртутного', 'столба'),
    ('ый', 'норматив'), ('ый', 'руково'),
    ('во', 'осад'), ('онных', 'технологий'), ('выдачи', 'задания'),
    ('двух', 'томах'), ('Том', 'первый'), ('ство', 'страни'),
    ('Дата', 'рождени'),
}

# Слова, «склеенные» переносом, которые всё же нужно поправить.
POST_FIX = [
    ('Резу-льтат', 'Результат'),
    ('Физико -металлургический', 'Физико-металлургический'),
    ('Сила ветра , м/с', 'Сила ветра, м/с'),
    ('Ростов-на дону', 'Ростов-на-Дону'),
    ('на дону', 'на-Дону'),
]


def join_lines(lines):
    """Склеивает строки одной ячейки, восстанавливая пробелы на местах переносов."""
    if not lines:
        return ''
    out = lines[0]
    for prev, nxt in zip(lines, lines[1:]):
        a = prev.split()[-1] if prev.split() else ''
        b = nxt.split()[0] if nxt.split() else ''
        sep = ''
        if a.endswith('-'):
            sep = ''
        elif a.endswith('…'):
            sep = ' '
        elif nxt[0].isupper() or nxt[0] in '(…':
            sep = ' '
        elif a == 'и' or a == 'в' or a == 'ы' or a == 'для' or a == 'на':
            sep = ' '
        elif (a, b) in NEEDS_SPACE:
            sep = ' '
        out = out + sep + nxt
    out = re.sub(r'\s+', ' ', out).strip()
    out = re.sub(r'(?<=\w) +-(?=\w)', '-', out)      # «Физико - металлургический»
    out = re.sub(r'\s+([,.;:])', r'\1', out)          # пробел перед знаком
    for bad, good in POST_FIX:
        out = out.replace(bad, good)
    return out


def clean_table(raw_rows):
    header = [join_lines(cell_lines(c)) for c in raw_rows[0]]
    rows = []
    for r in raw_rows[1:]:
        vals = [join_lines(cell_lines(c)) for c in r]
        if not any(v for v in vals):
            continue
        rows.append(vals)
    return header, rows


# ---------------------------------------------------------------- сборка таблиц
T = {}
T['1'] = clean_table([r for t in RAW if t['page'] == 1 for r in [t['rows']]][0])

t2a = [t['rows'] for t in RAW if t['page'] == 2][0]
t2b = [t['rows'] for t in RAW if t['page'] == 3][0]
h2, r2a = clean_table(t2a)
h2b, r2b = clean_table(t2b)
# на странице 3 шапка «съехала»: дата попала в заголовок -> берём даты из шапки
dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', h2b[0])
assert len(dates) == len(r2b) == 2, (dates, r2b)
for d, row in zip(dates, r2b):
    row[0] = d
T['2'] = (h2, r2a + r2b)

t3a = [t['rows'] for t in RAW if t['page'] == 3][1]
t3b = [t['rows'] for t in RAW if t['page'] == 4][0]
h3, r3a = clean_table(t3a)
_, r3b = clean_table(t3b)
T['3'] = (h3, r3a + r3b)

t4a = [t['rows'] for t in RAW if t['page'] == 4][1]
t4b = [t['rows'] for t in RAW if t['page'] == 5][0]
h4, r4a = clean_table(t4a)
_, r4b = clean_table(t4b)
T['4'] = (h4, r4a + r4b)

t5a = [t['rows'] for t in RAW if t['page'] == 6][0]
t5b = [t['rows'] for t in RAW if t['page'] == 7][0]
h5, r5a = clean_table(t5a)
_, r5b = clean_table(t5b)
T['5'] = (h5, r5a + r5b)

t6a = [t['rows'] for t in RAW if t['page'] == 8][0]
t6b = [t['rows'] for t in RAW if t['page'] == 9][0]
h6, r6a = clean_table(t6a)
_, r6b = clean_table(t6b)
# в исходнике данные в колонках «Место издания» и «Издательство» перепутаны местами
for row in r6a + r6b:
    row[4], row[5] = row[5], row[4]
T['6'] = (h6, r6a + r6b)

if __name__ == '__main__':
    for k, (h, rows) in T.items():
        print('=' * 100)
        print('ТАБЛИЦА', k, '| строк:', len(rows), '| колонок:', len(h))
        print(' | '.join(h))
        for r in rows:
            print(' | '.join(r))
