# Author: MuonSuzuki | Created with AI assistance
import sys
VERSION = "1.8.1"
blight_mode = any(a.strip().lower() in ("--blight", "-b", "blight") for a in sys.argv[1:])
blight_mode = any(a.strip().lower() in ("--blight", "-b", "blight") for a in sys.argv[1:])
AUTHOR = "MuonSuzuki"


import json, os, re, sys, time
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict
from operator import itemgetter

if os.name == "nt" and getattr(sys, "frozen", False):
    try:
        old_f = Path(sys.executable).resolve().with_suffix(".old")
        if old_f.exists(): old_f.unlink()
    except Exception:
        pass

APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
DATA_DIR = Path(__file__).resolve().parent
CONFIG_FILE = DATA_DIR / "config.json"

import logging, platform, traceback
from logging.handlers import RotatingFileHandler

debug_mode = any(a.strip().lower() in ("--debug", "-d", "debug") for a in sys.argv[1:])
LOG_FILE = DATA_DIR / "tracker.log"

logger = logging.getLogger("PoETracker")
logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

try:
    _fh = RotatingFileHandler(LOG_FILE, maxBytes=512*1024, backupCount=1, encoding="utf-8")
    _fh.setFormatter(_fmt)
    logger.addHandler(_fh)
except Exception:
    pass

if debug_mode:
    _sh = logging.StreamHandler(sys.stdout)
    _sh.setFormatter(_fmt)
    logger.addHandler(_sh)

def _global_excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.critical(f"Необработанное исключение (v{VERSION} | {platform.system()} {platform.release()}):\n{tb_str}")
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _global_excepthook
logger.debug(f"Запуск трекера v{VERSION} | Аргументы: {sys.argv[1:]} | ОС: {platform.system()} {platform.release()}")


import urllib.request

GITHUB_REPO = "Overlord076/exile-pace"

def parse_ver(v):
    try:
        return tuple(int(x) for x in v.lstrip("vV").split("."))
    except Exception:
        return (0, 0, 0)

def check_latest_release():
    url = f"https://github.com{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "ExilePace-Updater"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    tag = data.get("tag_name", "").lstrip("vV")
    assets = {a["name"]: a["browser_download_url"] for a in data.get("assets", [])}
    return tag, assets

def perform_self_update():
    print(f"Текущая версия: v{VERSION}. Проверяем обновления на GitHub...")
    try:
        latest, assets = check_latest_release()
    except Exception as e:
        print(f"Не удалось проверить обновления: {e}")
        return False

    if parse_ver(latest) <= parse_ver(VERSION):
        print(f"У вас установлена актуальная версия (v{VERSION}).")
        return False

    print(f"Найдена новая версия: v{latest}! Начинаем загрузку...")
    is_frozen = getattr(sys, "frozen", False)
    try:
        if is_frozen:
            asset_name = "ExilePace-Windows.exe" if os.name == "nt" else "exile-pace-linux"
            dl_url = assets.get(asset_name)
            if not dl_url:
                print(f"Файл {asset_name} не найден в релизе v{latest}.")
                return False
            cur_exe = Path(sys.executable).resolve()
            tmp_exe = cur_exe.with_suffix(".new")
            urllib.request.urlretrieve(dl_url, tmp_exe)
            if os.name == "nt":
                old_exe = cur_exe.with_suffix(".old")
                if old_exe.exists():
                    old_exe.unlink()
                cur_exe.rename(old_exe)
                tmp_exe.rename(cur_exe)
            else:
                os.chmod(tmp_exe, 0o755)
                os.replace(tmp_exe, cur_exe)
            print(f"Бинарник успешно обновлен до v{latest}! Перезапустите программу.")
        else:
            raw_url = f"https://githubusercontent.com{GITHUB_REPO}/main/heist_stats.py"
            cur_py = Path(__file__).resolve()
            tmp_py = cur_py.with_suffix(".py.new")
            urllib.request.urlretrieve(raw_url, tmp_py)
            os.replace(tmp_py, cur_py)
            print(f"Скрипт успешно обновлен до v{latest}!")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        return False

if any(a.strip().lower() in ("--update", "-u", "update") for a in sys.argv[1:]):
    perform_self_update()
    sys.exit(0)

if any(a.strip().lower() in ("--bg", "--daemon", "bg") for a in sys.argv[1:]):
    import subprocess
    clean_args = [a for a in sys.argv[1:] if a.strip().lower() not in ("--bg", "--daemon", "bg")]
    cmd = [sys.executable] + ([str(Path(__file__).resolve())] if not getattr(sys, "frozen", False) else []) + clean_args
    kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "env": os.environ.copy()}
    if os.name == "nt":
        kwargs["creationflags"] = 0x00000008 | 0x00000200
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, **kwargs)
    print("ExilePace запущен в фоновом режиме. Консоль можно закрыть.")
    sys.exit(0)

if any(a.strip().lower() in ("--version", "-v", "version") for a in sys.argv[1:]):
    print(f"PoE Heist & PoE 2 Tracker v{VERSION} (Author: {AUTHOR})")
    sys.exit(0)

poe2_mode = any(a.strip().lower() in ("--poe2", "-2", "poe2") for a in sys.argv[1:])
live_mode = any(a.strip().lower() in ("--live", "-l", "live") for a in sys.argv[1:])
overlay_mode = any(a.strip().lower() in ("--overlay", "-o", "overlay") for a in sys.argv[1:])
start_date = None

for a in sys.argv[1:]:
    a = a.strip().lower()
    if a in ("--poe2", "-2", "poe2", "--blight", "-b", "blight", "--live", "-l", "live", "--overlay", "-o", "overlay"): continue
    if a == "today": start_date = date.today()
    else:
        for f in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
            try: start_date = datetime.strptime(a, f).date(); break
            except ValueError: pass
        if not start_date: sys.exit(f"Неверная дата: {a}")
def find_client_log(is_poe2):
    key = "log_path_poe2" if is_poe2 else "log_path_poe1"
    cfg = {}
    if CONFIG_FILE.exists():
        try: cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception: cfg = {}
    saved = cfg.get(key) or (cfg.get("log_path") if not is_poe2 else None)
    if saved and Path(saved).is_file(): return saved

    folder = "Path of Exile 2" if is_poe2 else "Path of Exile"
    app_id = "2694490" if is_poe2 else "238960"
    candidates = [Path(f"/mnt/A812EF8F12EF60B4/SteamLibrary/steamapps/common/{folder}/logs/Client.txt")]
    if os.name == "nt":
        for d in ("C:", "D:", "E:", "F:"):
            candidates.extend([
                Path(f"{d}/Program Files (x86)/Steam/steamapps/common/{folder}/logs/Client.txt"),
                Path(f"{d}/SteamLibrary/steamapps/common/{folder}/logs/Client.txt"),
                Path(f"{d}/Program Files (x86)/Grinding Gear Games/{folder}/logs/Client.txt"),
                Path(f"{d}/Grinding Gear Games/{folder}/logs/Client.txt"),
            ])
    else:
        h = Path.home()
        candidates.extend([
            h / f".local/share/Steam/steamapps/common/{folder}/logs/Client.txt",
            h / f".local/share/Steam/steamapps/compatdata/{app_id}/pfx/drive_c/Program Files (x86)/Grinding Gear Games/{folder}/logs/Client.txt",
            h / f".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/{folder}/logs/Client.txt",
        ])
    for p in candidates:
        if p.is_file():
            cfg[key] = str(p)
            try: CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception: pass
            return str(p)
    sys.exit(f"Файл Client.txt для {folder} не найден. Укажите \"{key}\" в {CONFIG_FILE}")

log_path = find_client_log(poe2_mode)
logger.info(f"Используется лог игры: {log_path}")
rx = re.compile(r"^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*?(?:You have entered (.+?)\.|Вы вошли в область (.+?)\.)")
def fmt(s):
    if s <= 0: return "н/д"
    h, r = divmod(int(round(s)), 3600)
    m, sec = divmod(r, 60)
    return f"{h}ч {m:02d}м" if h else f"{m}м {sec:02d}с"
heist_zones = {
    "Bunker": "Бункер", "Underbelly": "Подбрюшье", "Mansion": "Особняк",
    "Repository": "Хранилище", "Tunnels": "Туннели", "Laboratory": "Лаборатория",
    "Prohibited Library": "Библиотека", "Smuggler's Den": "Логово", "Records Office": "Архив",
    "Бункер": "Бункер", "Подбрюшье": "Подбрюшье", "Особняк": "Особняк",
    "Хранилище": "Хранилище", "Туннели": "Туннели", "Лаборатория": "Лаборатория",
    "Запретная библиотека": "Библиотека", "Логово контрабандистов": "Логово", "Архив": "Архив"
}
harbour = {"The Rogue Harbour", "Разбойничья гавань"}

poe2_hubs = {
    "The Ziggurat Encampment", "The Ardura Caravan", "Clearfell Encampment",
    "Kingsmarch", "The Refuge", "Лагерь Зиккурата", "Караван Ардуры", "Лагерь у Просеки"
}
poe2_pinnacles = {
    "The Burning Monolith", "Пылающий монолит", "Twisted Domain", "Искажённые владения",
    "Crux of Nothingness", "Средоточие небытия", "The Simulacrum", "Симулякр",
    "Iron Citadel", "Железная цитадель", "Copper Citadel", "Медная цитадель",
    "Stone Citadel", "Каменная цитадель", "Vaal Temple", "Храм Ваал", "Paracosm", "Паракосм"
}

cassia_rx = re.compile(r"^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*?(?:Sister Cassia:|Сестра Кассия:)\s*(.*)")
oil_rx = re.compile(r"(Golden Oil|Silver Oil|Tainted Oil|Prismatic Oil|Reflective Oil|Золотое масло|Серебряное масло|Осквернённое масло|Оскверненное масло|Призматическое масло|Отражающее масло)", re.I)

def open_log_fast(path):
    f = open(path, encoding="utf-8", errors="ignore")
    if start_date:
        try:
            size = os.path.getsize(path)
            # Если файл больше 15 МБ и задана дата, пропускаем старые архивы
            if size > 15 * 1024 * 1024:
                f.seek(size - 15 * 1024 * 1024)
                f.readline()
        except Exception:
            pass
    return f

_render_cache = {}

def stats_blight():
    events, cur = [], "—"
    oils = defaultdict(int)
    with open_log_fast(log_path) as f:
        for line in f:
            m = rx.search(line)
            if m:
                ts = datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
                z = m.group(2) or m.group(3)
                cur = z
                if not start_date or ts.date() >= start_date: events.append(("zone", ts, z))
                continue
            cm = cassia_rx.search(line)
            if cm:
                ts = datetime.strptime(cm.group(1), "%Y/%m/%d %H:%M:%S")
                if not start_date or ts.date() >= start_date: events.append(("cassia", ts, cm.group(2)))
                continue
            om = oil_rx.search(line)
            if om and len(line) >= 19:
                try:
                    ts = datetime.strptime(line[:19], "%Y/%m/%d %H:%M:%S")
                    if not start_date or ts.date() >= start_date: oils[om.group(1).title()] += 1
                except Exception: pass
    bl_m = rav_m = enc = wins = fails = 0
    z_cnt = defaultdict(int)
    bl_rec, rav_rec = [], []
    t_run = t_ho = 0.0
    in_bl = seen_c = seen_out = False
    z_list = [(ts, z) for k, ts, z in events if k == "zone"]
    zi = 0
    for k, ts, val in events:
        if k == "cassia":
            sp = val.lower()
            if not in_bl and not seen_c: enc += 1; seen_c = True; z_cnt["Встречи Кассии"] += 1
            if not seen_out:
                if any(w in sp for w in ("destroyed", "уничтожен", "о нет! насос", "oh, no! the pump")): fails += 1; seen_out = True
                elif any(w in sp for w in ("wonderful", "turned to ash", "чудесно", "обратились в прах", "очищена")): wins += 1; seen_out = True
            continue
        seen_c = seen_out = False
        zl = val.lower()
        dur = (z_list[zi + 1][0] - ts).total_seconds() if zi + 1 < len(z_list) else 0
        zi += 1
        vd = 30 <= dur <= 1800
        if "hideout" in zl or "убежище" in zl:
            in_bl = False
            if 1 <= dur <= 900: t_ho += dur
            continue
        if zl.startswith(("blight-ravaged ", "осквернённая ", "оскверненная ")):
            in_bl = True; rav_m += 1; z_cnt[val] += 1
            if vd: rav_rec.append((dur, val, ts)); t_run += dur
        elif zl.startswith(("blight ", "blighted ", "заражённая ", "зараженная ")):
            in_bl = True; bl_m += 1; z_cnt[val] += 1
            if vd: bl_rec.append((dur, val, ts)); t_run += dur
        else: in_bl = False
    tf = t_run + t_ho
    wr = (wins / (wins + fails) * 100) if (wins + fails) > 0 else 0
    return {"cur": cur, "bl": bl_m, "rav": rav_m, "enc": enc, "wins": wins, "fails": fails, "wr": wr, "oils": sum(oils.values()), "oil_detail": dict(oils), "ab": sum(x for x, _, _ in bl_rec)/len(bl_rec) if bl_rec else 0, "bb": min(bl_rec, key=itemgetter(0)) if bl_rec else None, "ar": sum(x for x, _, _ in rav_rec)/len(rav_rec) if rav_rec else 0, "br": min(rav_rec, key=itemgetter(0)) if rav_rec else None, "rph": (bl_m + rav_m)/(tf/3600) if tf > 0 else 0, "tr": t_run, "th": t_ho, "sh": (t_run/tf*100) if tf > 0 else 0, "zc": z_cnt}


def stats_poe2():
    runs, cur = [], "—"
    with open_log_fast(log_path) as f:
        for line in f:
            m = rx.search(line)
            if not m: continue
            ts = datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
            z = m.group(2) or m.group(3)
            cur = z
            if not start_date or ts.date() >= start_date: runs.append((ts, z))

    sek_runs = sek_floors = chaos_runs = chaos_rooms = pin_cnt = map_cnt = 0
    z_cnt = defaultdict(int)
    map_rec, pin_rec, sek_rec = [], [], []
    t_act = t_hub = 0.0
    i = 0
    while i < len(runs):
        ts, z = runs[i]
        zl = z.lower()
        is_hub = (z in poe2_hubs) or ("hideout" in zl) or ("убежище" in zl)
        if is_hub:
            if i + 1 < len(runs):
                hd = (runs[i+1][0] - ts).total_seconds()
                if 1 <= hd <= 900: t_hub += hd
            i += 1; continue

        dur = (runs[i+1][0] - ts).total_seconds() if i + 1 < len(runs) else 0
        valid_d = 20 <= dur <= 1800
        if valid_d: t_act += dur

        if "sekhema" in zl or "сехем" in zl:
            sek_floors += 1
            if i == 0 or ("sekhema" not in runs[i-1][1].lower() and "сехем" not in runs[i-1][1].lower()):
                sek_runs += 1
            if valid_d: sek_rec.append((dur, z, ts))
            z_cnt["Испытание Сехем"] += 1
        elif "trial of chaos" in zl or "испытание хаоса" in zl:
            chaos_rooms += 1
            if i == 0 or ("chaos" not in runs[i-1][1].lower() and "хаос" not in runs[i-1][1].lower()):
                chaos_runs += 1
            z_cnt["Испытание Хаоса"] += 1
        elif z in poe2_pinnacles or "citadel" in zl or "цитадель" in zl:
            pin_cnt += 1
            if valid_d: pin_rec.append((dur, z, ts))
            z_cnt[z] += 1
        else:
            map_cnt += 1
            if valid_d: map_rec.append((dur, z, ts))
            z_cnt[z] += 1
        i += 1

    tot = map_cnt + pin_cnt + sek_runs + chaos_runs
    tf = t_act + t_hub
    return {
        "cur": cur, "maps": map_cnt, "pins": pin_cnt,
        "sek_r": sek_runs, "sek_f": sek_floors, "ch_r": chaos_runs, "ch_f": chaos_rooms,
        "am": sum(x[0] for x in map_rec)/len(map_rec) if map_rec else 0,
        "bm": min(map_rec, key=itemgetter(0)) if map_rec else None,
        "as": sum(x[0] for x in sek_rec)/len(sek_rec) if sek_rec else 0,
        "rph": tot/(tf/3600) if tf > 0 else 0,
        "ta": t_act, "th": t_hub, "sh": (t_act/tf*100) if tf > 0 else 0, "zc": z_cnt
    }
def stats_poe1():
    runs, cur = [], "—"
    with open_log_fast(log_path) as f:
        for line in f:
            m = rx.search(line)
            if not m: continue
            ts = datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
            z = m.group(2) or m.group(3)
            cur = heist_zones.get(z, z)
            if not start_date or ts.date() >= start_date: runs.append((ts, z))

    c_cnt = bp_cnt = w_cnt = 0
    z_cnt = defaultdict(int)
    c_rec, w_rec, h_rec = [], [], []
    t_heist = t_harb = 0.0
    i = 0
    while i < len(runs):
        ts, z = runs[i]
        if z in harbour and 0 < i < len(runs) - 1:
            if runs[i-1][1] in heist_zones or runs[i+1][1] in heist_zones:
                hd = (runs[i+1][0] - ts).total_seconds()
                if 1 <= hd <= 900: t_harb += hd; h_rec.append(hd)
        if z in heist_zones:
            nz = heist_zones[z]
            wings, last_t, w_durs = 1, ts, []
            if i + 1 < len(runs):
                d = (runs[i+1][0] - ts).total_seconds()
                if 25 <= d <= 1200: w_durs.append((d, nz, ts)); t_heist += d
            j = i + 1
            while j < len(runs):
                nts, nz2 = runs[j]
                if nz2 in harbour:
                    if j + 1 < len(runs) and runs[j+1][1] in heist_zones:
                        hd = (runs[j+1][0] - nts).total_seconds()
                        if 1 <= hd <= 900: t_harb += hd; h_rec.append(hd)
                    j += 1; continue
                if nz2 in heist_zones and heist_zones[nz2] == nz and (nts - last_t).total_seconds() < 1500:
                    wings += 1; last_t = nts
                    if j + 1 < len(runs):
                        wd = (runs[j+1][0] - nts).total_seconds()
                        if 25 <= wd <= 1200: w_durs.append((wd, nz, nts)); t_heist += wd
                    j += 1
                else: break
            if wings > 1: bp_cnt += 1; w_cnt += wings; w_rec.extend(w_durs)
            else: c_cnt += 1; c_rec.extend(w_durs)
            z_cnt[nz] += wings; i = j
        else: i += 1

    tot = c_cnt + w_cnt
    tf = t_heist + t_harb
    return {
        "cur": cur, "c": c_cnt, "bp": bp_cnt, "w": w_cnt,
        "ac": sum(x[0] for x in c_rec)/len(c_rec) if c_rec else 0,
        "bc": min(c_rec, key=itemgetter(0)) if c_rec else None,
        "aw": sum(x[0] for x in w_rec)/len(w_rec) if w_rec else 0,
        "bw": min(w_rec, key=itemgetter(0)) if w_rec else None,
        "rph": tot/(tf/3600) if tf > 0 else 0,
        "th": t_heist, "tb": t_harb,
        "ah": sum(h_rec)/len(h_rec) if h_rec else 0,
        "sh": (t_heist/tf*100) if tf > 0 else 0, "zc": z_cnt
    }

def out_text():
    try:
        fs = os.stat(log_path)
        ckey = (log_path, fs.st_mtime, fs.st_size, blight_mode, poe2_mode, start_date)
        if ckey in _render_cache:
            return _render_cache[ckey]
    except Exception:
        ckey = None
    if blight_mode:
        s = stats_blight()
        bb = fmt(s["bb"]) if s["bb"] else "н/д"
        br = fmt(s["br"]) if s["br"] else "н/д"
        wr = f"{s['wr']:.0f}%" if (s["wins"] + s["fails"]) > 0 else "н/д"
        lines = [
            f"Зона: {s['cur'][:24]}",
            "──────────────────────────────",
            f"Заражённые:   {s['bl']} карт (ср. {fmt(s['ab'])})",
            f"Осквернённые: {s['rav']} карт (ср. {fmt(s['ar'])})",
            f"Кассия:       {s['enc']} встр. | Насос: {s['wins']}W / {s['fails']}L ({wr})",
            f"Рекорды:      {bb} / {br} | Топ-масла: {s['oils']}",
            "──────────────────────────────",
            f"Темп карт:    {s['rph']:.1f} карт/час",
            f"В Скверне:    {fmt(s['tr'])} ({s['sh']:.0f}%) | Убежище: {fmt(s['th'])}"
        ]
        return chr(10).join(lines)
    if poe2_mode:
        s = stats_poe2()
        bm = fmt(s["bm"][0]) if s["bm"] else "н/д"
        _res = (
            f"Зона: {s['cur'][:24]}\n"
            f"──────────────────────────────\n"
            f"Сехем:     {s['sek_r']} заб. / {s['sek_f']} эт. (ср. {fmt(s['as'])})\n"
            f"Хаос:      {s['ch_r']} заб. / {s['ch_f']} комн.\n"
            f"Пинаклы:   {s['pins']} | Карты: {s['maps']} (ср. {fmt(s['am'])})\n"
            f"Рекорд к.: {bm}\n"
            f"──────────────────────────────\n"
            f"Темп:      {s['rph']:.1f} забегов/час\n"
            f"В забегах: {fmt(s['ta'])} ({s['sh']:.0f}%) | Хаб: {fmt(s['th'])}"
        )
        if ckey: _render_cache[ckey] = _res
        return _res
    s = stats_poe1()
    bc = fmt(s["bc"][0]) if s["bc"] else "н/д"
    bw = fmt(s["bw"][0]) if s["bw"] else "н/д"
    _res = (
        f"Зона: {s['cur'][:24]}\n"
        f"──────────────────────────────\n"
        f"Контракты: {s['c']} (ср. {fmt(s['ac'])})\n"
        f"Чертежи:   {s['bp']} / {s['w']} кр. (ср. {fmt(s['aw'])})\n"
        f"Рекорды:   контр. {bc} | кр. {bw}\n"
        f"──────────────────────────────\n"
        f"Темп:      {s['rph']:.1f} забегов/час\n"
        f"В забегах: {fmt(s['th'])} ({s['sh']:.0f}%)\n"
        f"В Гавани:  {fmt(s['tb'])} (стоп {fmt(s['ah'])})"
    )
    if ckey: _render_cache[ckey] = _res
    return _res

if __name__ == "__main__":
  if overlay_mode:
    import tkinter as tk
    r = tk.Tk()
    r.overrideredirect(True); r.attributes("-topmost", True)
    try: r.attributes("-alpha", 0.85)
    except Exception: pass
    r.configure(bg="#121417", highlightbackground="#3a3f4b", highlightthickness=1); r.geometry("+20+120")
    d = {"x": 0, "y": 0}
    h = tk.Frame(r, bg="#1e2229", cursor="fleur"); h.pack(fill="x")
    def get_title():
        return f" EXILEPACE: BLIGHT v{VERSION}" if blight_mode else (f" EXILEPACE: POE 2 v{VERSION}" if poe2_mode else f" EXILEPACE: HEIST v{VERSION}")

    def get_btn_label():
        return "⇄ HEIST" if (blight_mode or poe2_mode) else "⇄ BLIGHT"

    t = tk.Label(h, text=get_title(), bg="#1e2229", fg="#dfcf99", font=("Sans", 9, "bold"))
    t.pack(side="left", padx=4)

    x = tk.Label(h, text="✕", bg="#1e2229", fg="#8b949e", font=("Sans", 9, "bold"), cursor="hand2")
    x.pack(side="right", padx=6)
    x.bind("<Button-1>", lambda e: r.destroy())

    sw = tk.Label(h, text=get_btn_label(), bg="#2b313c", fg="#a3be8c", font=("Sans", 8, "bold"), padx=5, pady=1, cursor="hand2")
    sw.pack(side="right", padx=4, pady=2)

    def switch_mode(event=None):
        global blight_mode, poe2_mode, log_path
        if poe2_mode:
            poe2_mode = False
            blight_mode = False
            log_path = find_client_log(False)
        else:
            blight_mode = not blight_mode
        t.config(text=get_title())
        sw.config(text=get_btn_label())
        lbl.config(text=out_text())

    sw.bind("<Button-1>", switch_mode)
    for w in (h, t):
        w.bind("<Button-1>", lambda e: d.update(x=e.x, y=e.y))
        w.bind("<B1-Motion>", lambda e: r.geometry(f"+{r.winfo_x()+e.x-d['x']}+{r.winfo_y()+e.y-d['y']}"))
    lbl = tk.Label(r, text="...", bg="#121417", fg="#e6e6e6", justify="left", anchor="w", font=("Monospace", 9), padx=8, pady=6)
    lbl.pack()
    st = {"m": 0, "s": 0}
    def upd():
        try:
            fs = os.stat(log_path)
            if fs.st_mtime != st["m"] or fs.st_size != st["s"]:
                st["m"], st["s"] = fs.st_mtime, fs.st_size
                t0 = time.perf_counter()
                lbl.config(text=out_text())
                logger.debug(f"Оверлей обновлен за {(time.perf_counter()-t0)*1000:.1f} мс")
        except Exception as e:
            logger.error(f"Ошибка обновления оверлея: {e}", exc_info=True)
            lbl.config(text=f"Ошибка чтения лога (см. tracker.log):\n{e}")
        r.after(1500, upd)
    def setup_tray():
        try:
            import threading, pystray
            from PIL import Image
            ico_file = APP_DIR / "icon.png"
            if not ico_file.is_file():
                return
            img = Image.open(ico_file)
            visible = {"state": True}

            def toggle_overlay(icon, item):
                if visible["state"]:
                    r.after(0, r.withdraw)
                    visible["state"] = False
                else:
                    r.after(0, r.deiconify)
                    visible["state"] = True

            def quit_app(icon, item):
                icon.stop()
                r.after(0, r.destroy)

            def run_upd_from_tray(icon, item):
                if perform_self_update():
                    icon.stop()
                    r.after(0, r.destroy)
                    os.execv(sys.executable, [sys.executable] + sys.argv)

            def open_log_file(icon, item):
                try:
                    if os.name == "nt":
                        os.startfile(str(LOG_FILE))
                    else:
                        import subprocess
                        subprocess.Popen(["xdg-open", str(LOG_FILE)])
                except Exception as e:
                    logger.error(f"Не удалось открыть лог: {e}")

            menu = pystray.Menu(
                pystray.MenuItem("Показать / Скрыть оверлей", toggle_overlay, default=True),
                pystray.MenuItem("Переключить режим (Heist / Blight)", lambda icon, item: r.after(0, switch_mode)),
                pystray.MenuItem("Открыть лог отладки", open_log_file),
                pystray.MenuItem("Проверить обновления", run_upd_from_tray),
                pystray.MenuItem("Выход", quit_app)
            )
            tray = pystray.Icon("poe_tracker", img, "PoE Tracker", menu)
            threading.Thread(target=tray.run, daemon=True).start()
        except Exception as e:
            logger.warning(f"Трей не инициализирован: {e}")

    def bg_update_check():
        try:
            latest, _ = check_latest_release()
            if parse_ver(latest) > parse_ver(VERSION):
                r.after(0, lambda: t.config(text=f"{get_title()} [Новая v{latest}!]"))
        except Exception as e:
            logger.warning(f"Трей не инициализирован: {e}")

    import threading as _th
    _th.Thread(target=bg_update_check, daemon=True).start()
    r.after(400, setup_tray)
    upd(); r.mainloop()
  elif live_mode:
    lm = ls = 0
    try:
        while True:
            fs = os.stat(log_path)
            if fs.st_mtime != lm or fs.st_size != ls:
                lm, ls = fs.st_mtime, fs.st_size
                sys.stdout.write("\033[H\033[J" + out_text() + "\n")
            time.sleep(1.5)
    except KeyboardInterrupt: pass
  else:
    print(out_text() + "\n\nТоп локаций:")
    zc = (stats_poe2() if poe2_mode else stats_poe1())["zc"]
    for z, c in sorted(zc.items(), key=itemgetter(1), reverse=True)[:15]: print(f"  {z}: {c}")
