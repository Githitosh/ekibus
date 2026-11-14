#!/usr/bin/env python3
"""北鉄バスの路線別時刻表を、アプリ内検索用の busdata/hk.txt にまとめる。

出典: 北陸鉄道 時刻・運賃検索（路線別時刻表）令和8年10月1日改正
https://arj.hokutetsu.co.jp/timetable/busline.php
"""
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape

BASE = 'https://arj.hokutetsu.co.jp/timetable/'
DIA = '139,20261001'
UA = 'ekibus/1.0 (personal timetable; +https://github.com/Githitosh/ekibus)'
OUT = os.path.join(os.path.dirname(__file__), '..', 'busdata', 'hk.txt')
CACHE = '/tmp/hkcache'
WORKERS = 4

# 公式の路線一覧で、その路線だけの系統番号が書かれているもの
LINE_NO = {
    '医王山線': '13・14', '花里線': '18', '寺町線': '26', '光が丘住宅線': '30', '額住宅線': '31',
    '四十万線': '33', '辰口線': '33', '久安線': '37', '野々市円光寺線': '39', '松任線': '40',
    '千代野線': '41・49', '金沢寺井線': '42', '錦町野々市線': '43', '野々市線': '44・48',
    '松任中奥線': '47', '示野線': '52', '西金沢線': '53・96', '金石線': '60', '鳴和・増泉線': '82',
    '石引線': '83', '田中医大線': '86', '津幡線': '87', '東山線': '88', '卯辰山線': '90',
    '鈴見線': '92', '北陸大学線': '95', '内灘線': '08', '湯涌線': '12', '錦町Ｂ線': '11',
    '笠舞駅西線': '04・05・19',
}


def post(path, fields, tries=4):
    body = urllib.parse.urlencode(fields).encode()
    key = path + '?' + body.decode()
    os.makedirs(CACHE, exist_ok=True)
    import hashlib
    cpath = os.path.join(CACHE, hashlib.sha1(key.encode()).hexdigest())
    if os.path.exists(cpath):
        return open(cpath, encoding='utf-8').read()
    last = None
    for i in range(tries):
        req = urllib.request.Request(
            BASE + path, data=body,
            headers={'User-Agent': UA, 'Content-Type': 'application/x-www-form-urlencoded',
                     'Referer': BASE + 'busline.php'})
        try:
            html = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
            open(cpath, 'w', encoding='utf-8').write(html)
            return html
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def line_names(area):
    html = post('phpscript/hpjpp0140.php', {'diaseq': '139', 'areakbn': str(area)})
    return re.findall(r'<option[^>]*>([^<]+)</option>', html)


def text_of(cell):
    t = re.sub(r'<[^>]+>', '', cell)
    return unescape(t).replace('\u3000', ' ').strip()


def hhmm(cell):
    m = re.search(r'(\d{1,2}):(\d{2})', text_of(cell))
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def parse_tables(html, line):
    trips = []
    for table in re.findall(r'<table class="busline">(.*?)</table>', html, re.S):
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.S)
        if not rows:
            continue
        parsed = []
        for row in rows:
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.S)
            parsed.append(cells)
        n = max((len(c) for c in parsed), default=0) - 1
        if n < 1:
            continue
        dest = [''] * n
        note = [''] * n
        stops = [[] for _ in range(n)]
        for cells in parsed:
            label = text_of(cells[0]) if cells else ''
            vals = cells[1:]
            if label == '終点停留所':
                for i in range(n):
                    dest[i] = text_of(vals[i]) if i < len(vals) else ''
            elif label == '備考':
                for i in range(n):
                    raw = vals[i] if i < len(vals) else ''
                    raw = re.sub(r'<input\b[^>]*>', '', raw)
                    note[i] = text_of(raw)
            elif label in ('始発停留所', '始発時間', '終点時間'):
                continue
            else:
                for i in range(n):
                    cell = vals[i] if i < len(vals) else ''
                    t = hhmm(cell)
                    if t is None or not label:
                        continue
                    if stops[i] and t < stops[i][-1][1] - 60:
                        t += 1440
                    elif stops[i] and t < stops[i][-1][1]:
                        t = stops[i][-1][1]
                    stops[i].append((label, t))
        for i in range(n):
            if len(stops[i]) < 2:
                continue
            trips.append((line, dest[i], note[i], stops[i]))
    return trips


def route_code(name, area):
    html = post('busline_timetable.php', {
        'diaseq': DIA, 'area': str(area), 'ros_mei': name, 'page': '1',
    })
    # 初期表示が「時刻がありません」でも roscd はある。曜日と方向を変えると時刻表が出る
    m = re.search(r'name="roscd" value="([^"]+)"', html)
    if not m:
        return ''
    return m.group(1)


def fetch_combo(name, area, day, direction, roscd):
    if not roscd:
        return []
    page = 1
    found = []
    label = LINE_NO.get(name, '')
    line = f'{label} {name}'.strip() if label else name
    while page <= 12:
        # 路線名を一緒に送ると曜日・方向が無視される。roscd だけで送る
        html = post('busline_timetable.php', {
            'diaseq': DIA, 'roscd': roscd, 'weekday': str(day),
            'ofukukbn': str(direction), 'page': str(page), 'smparrow': '-4',
        })
        if 'table class="busline"' not in html:
            break
        found.extend((day, *t) for t in parse_tables(html, line))
        pm = re.search(r'id="arrowf"[\s\S]{0,600}?（\d+／(\d+)件）', html)
        total = int(pm.group(1)) if pm else page
        if page >= total:
            break
        page += 1
    return found


def main():
    only = set(sys.argv[1:])
    jobs = []
    codes = {}
    for area in (1, 2):
        names = line_names(area)
        print(f'area {area}: {len(names)} lines', flush=True)
        for name in names:
            if only and name not in only:
                continue
            try:
                codes[(name, area)] = route_code(name, area)
            except Exception as e:
                print(f'FAIL code {name} {e}', flush=True)
                codes[(name, area)] = ''
            for day in (0, 1, 2):
                for direction in (1, 2):
                    jobs.append((name, area, day, direction, codes[(name, area)]))
    print(f'fetch {len(jobs)} pagesets', flush=True)
    trips = []
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch_combo, *job): job for job in jobs}
        for fut in as_completed(futs):
            job = futs[fut]
            done += 1
            try:
                got = fut.result()
            except Exception as e:
                print(f'FAIL {job[0]} day={job[2]} dir={job[3]} {e}', flush=True)
                continue
            trips.extend(got)
            if done % 30 == 0 or done == len(jobs):
                print(f'{done}/{len(jobs)} trips {len(trips)}', flush=True)
    # 停留所番号
    stops = []
    idx = {}
    def sid(name):
        if name not in idx:
            idx[name] = len(stops)
            stops.append(name)
        return idx[name]
    lines_out = ['# rev=2026-10-01', '# label=令和8年10月1日改正', '# src=https://arj.hokutetsu.co.jp/timetable/busline.php']
    packed = []
    seen = set()
    for day, line, dest, note, seq in trips:
        did = sid(dest) if dest else -1
        pairs = []
        for name, minute in seq:
            pairs.append(f'{sid(name)}:{minute}')
        key = (day, line, tuple(pairs))
        if key in seen:
            continue
        seen.add(key)
        note = (note or '-').replace('\t', ' ').replace('\n', ' ')
        packed.append(f'T\t{day}\t{line}\t{did}\t{note}\t{",".join(pairs)}')
    for name in stops:
        lines_out.append('S\t' + name.replace('\t', ' '))
    lines_out.extend(packed)
    text = '\n'.join(lines_out) + '\n'
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(text)
    print(f'wrote {OUT} stops={len(stops)} trips={len(packed)} bytes={len(text.encode())}', flush=True)


if __name__ == '__main__':
    main()
