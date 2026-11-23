# Author: MuonSuzuki | Created with AI assistance
import sys
VERSION = "1.16.2"
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

_args_low = [a.strip().lower() for a in sys.argv[1:]]
_want_ov = any(a in ("--overlay", "-o", "overlay") for a in _args_low)
_want_bg = any(a in ("--bg", "--daemon", "bg") for a in _args_low)
_stay_fg = any(a in ("--fg", "--foreground", "fg", "--debug", "-d", "debug") for a in _args_low) or os.environ.get("EXILEPACE_DETACHED") == "1"

if (_want_bg or _want_ov) and not _stay_fg:
    import subprocess
    clean_args = [a for a in sys.argv[1:] if a.strip().lower() not in ("--bg", "--daemon", "bg")]
    cmd = [sys.executable] + ([str(Path(__file__).resolve())] if not getattr(sys, "frozen", False) else []) + clean_args
    env_copy = os.environ.copy()
    env_copy["EXILEPACE_DETACHED"] = "1"
    kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "env": env_copy}
    if os.name == "nt":
        kwargs["creationflags"] = 0x00000008 | 0x00000200
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, **kwargs)
    print("ExilePace запущен в фоновом режиме. Консоль можно закрыть.")
    sys.exit(0)

_lock_fp = None
if any(a.strip().lower() in ("--overlay", "-o", "overlay") for a in sys.argv[1:]):
    try:
        _is_p2 = any(a.strip().lower() in ("--poe2", "-2", "poe2") for a in sys.argv[1:])
        _lock_path = APP_DIR / (".lock_poe2" if _is_p2 else ".lock_poe1")
        _lock_fp = open(_lock_path, "w")
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(_lock_fp.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(_lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fp.write(str(os.getpid()))
        _lock_fp.flush()
    except Exception:
        print("ExilePace уже запущен в фоновом режиме (проверьте значок в трее).")
        sys.exit(0)

if any(a.strip().lower() in ("--version", "-v", "version") for a in sys.argv[1:]):
    print(f"PoE Heist & PoE 2 Tracker v{VERSION} (Author: {AUTHOR})")
    sys.exit(0)

poe2_mode = any(a.strip().lower() in ("--poe2", "-2", "poe2") for a in sys.argv[1:])
live_mode = any(a.strip().lower() in ("--live", "-l", "live") for a in sys.argv[1:])
overlay_mode = any(a.strip().lower() in ("--overlay", "-o", "overlay") for a in sys.argv[1:])
ultimatum_mode = any(a.strip().lower() in ("--ultimatum", "--chaos", "ultimatum", "chaos") for a in sys.argv[1:])
LEAGUES_POE1 = [
    ("3.30 Covens (Текущая)", date(2026, 11, 13), None, "3.30"),
    ("3.29 Allflame (24.07–10.11.26)", date(2026, 7, 24), date(2026, 11, 10), "3.29"),
    ("3.28 Mirage (06.03–20.07.26)", date(2026, 3, 6), date(2026, 7, 20), "3.28"),
    ("3.27 Keepers (31.10.25–02.03.26)", date(2025, 10, 31), date(2026, 3, 2), "3.27"),
    ("3.26 Mercenaries (13.06–27.10.25)", date(2025, 6, 13), date(2025, 10, 27), "3.26"),
    ("3.25 Settlers (26.07.24–09.06.25)", date(2024, 7, 26), date(2025, 6, 9), "3.25"),
]
LEAGUES_POE2 = [
    ("0.5.5 Forbidden Rites (Текущая)", date(2026, 9, 4), None, "0.5.5"),
    ("0.5.0 Runes of Aldur (29.05–01.09.26)", date(2026, 5, 29), date(2026, 9, 1), "0.5.0"),
    ("0.4.0 Fate of the Vaal (12.12.25–25.05.26)", date(2025, 12, 12), date(2026, 5, 25), "0.4.0"),
    ("0.3.0 The Third Edict (29.08–08.12.25)", date(2025, 8, 29), date(2025, 12, 8), "0.3.0"),
    ("0.2.0 Dawn of the Hunt (04.04–26.08.25)", date(2025, 4, 4), date(2025, 8, 26), "0.2.0"),
]

league_mode = any(a.strip().lower() in ("league", "--league", "лига") for a in sys.argv[1:])
cur_league = (LEAGUES_POE2[0] if poe2_mode else LEAGUES_POE1[0]) if league_mode else None
start_date = cur_league[1] if cur_league else None
end_date = cur_league[2] if cur_league else None

for a in sys.argv[1:]:
    a = a.strip().lower()
    if a in ("--poe2", "-2", "poe2", "--blight", "-b", "blight", "--ultimatum", "--chaos", "ultimatum", "chaos", "--live", "-l", "live", "--overlay", "-o", "overlay", "--fg", "--foreground", "fg", "--debug", "-d", "debug", "--bg", "--daemon", "bg"): continue
    if a in ("league", "--league", "лига"): pass
    elif a == "today": start_date = date.today()
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
    "Bunker": "Бункер", "Underbelly": "Подполье", "Mansion": "Особняк",
    "Repository": "Хранилище", "Tunnels": "Тоннели", "Laboratory": "Лаборатория",
    "Prohibited Library": "Библиотека", "Smuggler's Den": "Логово", "Records Office": "Архив",
    "Бункер": "Бункер", "Подполье": "Подполье", "Подбрюшье": "Подполье",
    "Особняк": "Особняк", "Хранилище": "Хранилище",
    "Тоннели": "Тоннели", "Туннели": "Тоннели", "Лаборатория": "Лаборатория",
    "Запретная библиотека": "Библиотека",
    "Притон контрабандистов": "Логово", "Логово контрабандистов": "Логово",
    "Референтура": "Архив", "Архив": "Архив",
    "Heart of Glory": "Уник: Сердце славы", "Сердце славы": "Уник: Сердце славы",
    "The Twins": "Уник: Близнецы", "Близнецы": "Уник: Близнецы",
    "Death to Darnaw": "Уник: Смерть Дарно", "Смерть Дарно": "Уник: Смерть Дарно",
    "Breaking the Unbreakable": "Уник: Разрушение Нерушимого", "Разрушение Нерушимого": "Уник: Разрушение Нерушимого",
    "The Slaver King": "Уник: Король работорговцев", "Король работорговцев": "Уник: Король работорговцев"
}
heist_area_ids = {
    "HeistBunker": "Бункер", "HeistSewers": "Подполье", "HeistMansion": "Особняк",
    "HeistVault": "Хранилище", "HeistRobotTunnels": "Тоннели", "HeistDungeon": "Лаборатория",
    "HeistLibrary": "Библиотека", "HeistSmugglersDen": "Логово", "HeistCourts": "Архив",
    "HeistBoss_AdmiralDarnaw": "Уник: Смерть Дарно", "HeistBoss_TheTwins": "Уник: Близнецы",
    "HeistBoss_Vox": "Уник: Разрушение Нерушимого", "HeistBoss_Nashta": "Уник: Сердце славы",
    "HeistBoss_SlaverKing": "Уник: Король работорговцев"
}
gen_rx = re.compile(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*?Generating level \d+ area "([^"]+)" with seed (\d+)')
STATS_CACHE_FILE = APP_DIR / "stats_cache.json"
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
            target_str = start_date.strftime("%Y/%m/%d")
            size = os.path.getsize(path)
            lo, hi = 0, size
            while hi - lo > 65536:
                mid = (lo + hi) // 2
                f.seek(mid)
                f.readline()
                line = f.readline()
                if not line:
                    hi = mid
                    continue
                if line[:10] < target_str:
                    lo = mid
                else:
                    hi = mid
            f.seek(lo)
            if lo > 0:
                f.readline()
        except Exception:
            f.seek(0)
    return f

_render_cache = {}
_active_zone_start = None  # datetime входа в текущую боевую зону (None, если в хабе/убежище)

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
                if (not start_date or ts.date() >= start_date) and (not end_date or ts.date() <= end_date): events.append(("zone", ts, z))
                continue
            cm = cassia_rx.search(line)
            if cm:
                ts = datetime.strptime(cm.group(1), "%Y/%m/%d %H:%M:%S")
                if (not start_date or ts.date() >= start_date) and (not end_date or ts.date() <= end_date): events.append(("cassia", ts, cm.group(2)))
                continue
            om = oil_rx.search(line)
            if om and len(line) >= 19:
                try:
                    ts = datetime.strptime(line[:19], "%Y/%m/%d %H:%M:%S")
                    if (not start_date or ts.date() >= start_date) and (not end_date or ts.date() <= end_date): oils[om.group(1).title()] += 1
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
    global _active_zone_start
    if not poe2_mode and blight_mode:
        if z_list:
            lts, lz = z_list[-1]
            lzl = lz.lower()
            if ("hideout" not in lzl and "убежище" not in lzl and lz not in harbour
                    and (datetime.now() - lts).total_seconds() <= 1800):
                _active_zone_start = lts
            else:
                _active_zone_start = None
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
            if (not start_date or ts.date() >= start_date) and (not end_date or ts.date() <= end_date):
                runs.append((ts, z))

    sek_hubs = set()
    sek_floors_kw = ("test of strength", "test of will", "test of cunning", "test of time", "испытание силы", "испытание воли", "испытание хитрости", "испытание времени", "sekhema", "сехем")
    chaos_hubs = {"the temple of chaos", "temple of chaos", "храм хаоса"}
    chaos_kw = ("trial of chaos", "испытание хаоса", "испытания хаоса", "ultimatum", "ультиматум")

    sek_runs = sek_floors = chaos_runs = chaos_rooms = pin_cnt = map_cnt = 0
    z_cnt = defaultdict(int)
    map_rec, pin_rec, sek_rec, chaos_rec = [], [], [], []
    t_act = t_hub = 0.0
    i = 0
    while i < len(runs):
        ts, z = runs[i]
        zl = z.lower()
        is_hub = (z in poe2_hubs) or (zl in sek_hubs) or (zl in chaos_hubs) or ("hideout" in zl) or ("убежище" in zl)
        if is_hub:
            if i + 1 < len(runs):
                hd = (runs[i+1][0] - ts).total_seconds()
                if 1 <= hd <= 900: t_hub += hd
            i += 1; continue

        if zl not in sek_hubs and any(k in zl for k in sek_floors_kw):
            sek_runs += 1
            floors = 0
            run_dur = 0.0
            j = i
            while j < len(runs):
                fts, fz = runs[j]
                fzl = fz.lower()
                if fzl not in sek_hubs and any(k in fzl for k in sek_floors_kw):
                    floors += 1
                    z_cnt["Испытание Сехем"] += 1
                    if j + 1 < len(runs):
                        fd = (runs[j+1][0] - fts).total_seconds()
                        if 10 <= fd <= 1800:
                            run_dur += fd
                            t_act += fd
                    j += 1
                else:
                    break
            sek_floors += floors
            if run_dur >= 20:
                sek_rec.append((run_dur, f"Сехем ({floors} эт.)", ts))
            i = j
            continue

        if zl not in chaos_hubs and any(k in zl for k in chaos_kw):
            chaos_runs += 1
            rooms = 0
            run_dur = 0.0
            j = i
            while j < len(runs):
                cts, cz = runs[j]
                czl = cz.lower()
                if czl not in chaos_hubs and any(k in czl for k in chaos_kw):
                    rooms += 1
                    z_cnt["Ультиматум (Хаос)"] += 1
                    if j + 1 < len(runs):
                        cd = (runs[j+1][0] - cts).total_seconds()
                        if 10 <= cd <= 1800:
                            run_dur += cd
                            t_act += cd
                    j += 1
                else:
                    break
            chaos_rooms += rooms
            if run_dur >= 20:
                chaos_rec.append((run_dur, f"Ультиматум ({rooms} комн.)", ts))
            i = j
            continue

        dur = (runs[i+1][0] - ts).total_seconds() if i + 1 < len(runs) else 0
        valid_d = 20 <= dur <= 1800
        if valid_d: t_act += dur

        if z in poe2_pinnacles or "citadel" in zl or "цитадель" in zl:
            pin_cnt += 1
            if valid_d: pin_rec.append((dur, z, ts))
            z_cnt[z] += 1
        else:
            map_cnt += 1
            if valid_d: map_rec.append((dur, z, ts))
            z_cnt[z] += 1
        i += 1

    global _active_zone_start
    if poe2_mode:
        if runs:
            lts, lz = runs[-1]
            lzl = lz.lower()
            is_h = (lz in poe2_hubs) or (lzl in chaos_hubs) or ("hideout" in lzl) or ("убежище" in lzl)
            if not is_h and (datetime.now() - lts).total_seconds() <= 1800:
                _active_zone_start = lts
            else:
                _active_zone_start = None
    tot = sek_runs + chaos_runs + pin_cnt + map_cnt
    tf = t_act + t_hub
    return {
        "cur": cur,
        "sek_r": sek_runs, "sek_f": sek_floors,
        "as": sum(x[0] for x in sek_rec)/len(sek_rec) if sek_rec else 0,
        "bs": min(sek_rec, key=itemgetter(0)) if sek_rec else None,
        "ch_r": chaos_runs, "ch_f": chaos_rooms,
        "ac": sum(x[0] for x in chaos_rec)/len(chaos_rec) if chaos_rec else 0,
        "bc": min(chaos_rec, key=itemgetter(0)) if chaos_rec else None,
        "pins": pin_cnt, "maps": map_cnt,
        "am": sum(x[0] for x in map_rec)/len(map_rec) if map_rec else 0,
        "bm": min(map_rec, key=itemgetter(0)) if map_rec else None,
        "rph": tot/(tf/3600) if tf > 0 else 0,
        "ta": t_act, "th": t_hub, "sh": (t_act/tf*100) if tf > 0 else 0, "zc": z_cnt
    }
def load_heist_events_cached(path):
    events, offset, mtime = [], 0, 0.0
    try:
        st = os.stat(path); mtime = st.st_mtime
        if STATS_CACHE_FILE.exists():
            cd = json.loads(STATS_CACHE_FILE.read_text(encoding="utf-8"))
            if cd.get("path") == str(path) and cd.get("offset", 0) <= st.st_size:
                events, offset = cd.get("events", []), cd.get("offset", 0)
                if offset == st.st_size: return events
    except Exception: events, offset = [], 0
    try:
        with open(path, "rb") as fb:
            fb.seek(offset); chunk = fb.read(); new_off = fb.tell()
        for ln in chunk.decode("utf-8", errors="ignore").splitlines():
            if "LOG FILE OPENING" in ln: events.append((ln[:19], "LOG_OPEN", "", "")); continue
            gm = gen_rx.search(ln)
            if gm: events.append((gm.group(1), "GEN", gm.group(2), gm.group(3))); continue
            m = rx.search(ln)
            if m: events.append((m.group(1), "ENTER", (m.group(2) or m.group(3)).strip(), ""))
        try: STATS_CACHE_FILE.write_text(json.dumps({"path": str(path), "offset": new_off, "mtime": mtime, "events": events}, ensure_ascii=False), encoding="utf-8")
        except Exception: pass
    except Exception: pass
    return events

def map_heist_area(aid, zname):
    if aid:
        for pref, lbl in heist_area_ids.items():
            if aid.startswith(pref): return lbl
    return heist_zones.get(zname)

def stats_poe1():
    runs, cur, last_aid, last_seed, p_brk = [], "—", "", "", False
    for ts_s, kind, val, extra in load_heist_events_cached(log_path):
        if kind == "LOG_OPEN": p_brk = True; continue
        if kind == "GEN": last_aid, last_seed = val, extra; continue
        if kind == "ENTER":
            try: ts = datetime.strptime(ts_s, "%Y/%m/%d %H:%M:%S")
            except Exception: continue
            nz = map_heist_area(last_aid, val)
            cur = nz if nz else val
            if (not start_date or ts.date() >= start_date) and (not end_date or ts.date() <= end_date):
                runs.append((ts, val, last_aid, last_seed, p_brk))
            p_brk = False

    c_cnt = bp_cnt = w_cnt = 0
    z_cnt = defaultdict(int); c_rec, w_rec, h_rec = [], [], []; t_heist = t_harb = 0.0; i = 0
    while i < len(runs):
        ts, z, aid, seed, brk = runs[i]; nz = map_heist_area(aid, z)
        if z in harbour and 0 < i < len(runs) - 1:
            p_ts, p_z, p_a, _, _ = runs[i-1]
            n_ts, n_z, n_a, _, n_brk = runs[i+1]
            if (map_heist_area(p_a, p_z) or map_heist_area(n_a, n_z)) and not n_brk:
                hd = (n_ts - ts).total_seconds()
                if 1 <= hd <= 900: t_harb += hd; h_rec.append(hd)
        if nz:
            wings, last_t, w_durs = 1, ts, []
            if i + 1 < len(runs):
                nx_ts, _, _, _, nx_brk = runs[i+1]
                if not nx_brk:
                    d = (nx_ts - ts).total_seconds()
                    if 35 <= d <= 1200: w_durs.append((d, nz, ts)); t_heist += d
            z_cnt[nz] += 1; j = i + 1
            while j < len(runs):
                nts, nzone, naid, nseed, nbrk = runs[j]
                if nbrk: break
                nnz = map_heist_area(naid, nzone)
                if nzone in harbour:
                    if j + 1 < len(runs):
                        ats, azone, aaid, aseed, abrk = runs[j+1]
                        anz = map_heist_area(aaid, azone); hp = (ats - nts).total_seconds()
                        if not abrk and anz and (ats - last_t).total_seconds() < 2700 and (hp <= 55 or anz == nz):
                            if 1 <= hp <= 900: t_harb += hp; h_rec.append(hp)
                            wings += 1; z_cnt[anz] += 1
                            if j + 2 < len(runs):
                                e_ts, _, _, _, e_brk = runs[j+2]
                                if not e_brk:
                                    wd = (e_ts - ats).total_seconds()
                                    if 35 <= wd <= 1200: w_durs.append((wd, anz, ats)); t_heist += wd
                            last_t = ats; j += 2; continue
                    break
                elif nnz and (nts - last_t).total_seconds() < 2700:
                    wings += 1; z_cnt[nnz] += 1
                    if j + 1 < len(runs):
                        e_ts, _, _, _, e_brk = runs[j+1]
                        if not e_brk:
                            wd = (e_ts - nts).total_seconds()
                            if 35 <= wd <= 1200: w_durs.append((wd, nnz, nts)); t_heist += wd
                    last_t = nts; j += 1; continue
                else: break
            if wings > 1: bp_cnt += 1; w_cnt += wings; w_rec.extend(w_durs)
            else: c_cnt += 1; c_rec.extend(w_durs)
            i = j
        else: i += 1

    global _active_zone_start
    if not poe2_mode and not blight_mode and runs:
        lts, lz, laid, _, _ = runs[-1]
        _active_zone_start = lts if (map_heist_area(laid, lz) and (datetime.now() - lts).total_seconds() <= 1800) else None
    tot = c_cnt + w_cnt; tf = t_heist + t_harb
    return {"cur": cur, "c": c_cnt, "bp": bp_cnt, "w": w_cnt, "ac": sum(x[0] for x in c_rec)/len(c_rec) if c_rec else 0, "bc": min(c_rec, key=itemgetter(0)) if c_rec else None, "aw": sum(x[0] for x in w_rec)/len(w_rec) if w_rec else 0, "bw": min(w_rec, key=itemgetter(0)) if w_rec else None, "ah": sum(h_rec)/len(h_rec) if h_rec else 0, "rph": tot/(tf/3600) if tf > 0 else 0, "th": t_heist, "tb": t_harb, "sh": (t_heist/tf*100) if tf > 0 else 0, "zc": z_cnt}

def out_text(b_override=None, u_override=None):
    _bm = blight_mode if b_override is None else b_override
    _um = ultimatum_mode if u_override is None else u_override
    try:
        fs = os.stat(log_path)
        ckey = (log_path, fs.st_mtime, fs.st_size, _bm, poe2_mode, _um, start_date, end_date)
        if ckey in _render_cache:
            return _render_cache[ckey]
    except Exception:
        ckey = None
    if not poe2_mode and _bm:
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
        if _um:
            bc = fmt(s["bc"][0]) if s["bc"] else "н/д"
            _res = (
                f"Зона: {s['cur'][:24]}\n"
                f"──────────────────────────────\n"
                f"Ультиматум: {s['ch_r']} заб. / {s['ch_f']} комн.\n"
                f"Среднее:    {fmt(s['ac'])} | Рекорд: {bc}\n"
                f"Карты/Босс: {s['maps']} / {s['pins']} (ср. {fmt(s['am'])})\n"
                f"──────────────────────────────\n"
                f"Темп:       {s['rph']:.1f} забегов/час\n"
                f"В забегах:  {fmt(s['ta'])} ({s['sh']:.0f}%) | Хаб: {fmt(s['th'])}"
            )
        else:
            bs = fmt(s["bs"][0]) if s["bs"] else "н/д"
            _res = (
                f"Зона: {s['cur'][:24]}\n"
                f"──────────────────────────────\n"
                f"Сехем:      {s['sek_r']} заб. / {s['sek_f']} эт.\n"
                f"Среднее:    {fmt(s['as'])} | Рекорд: {bs}\n"
                f"Карты/Босс: {s['maps']} / {s['pins']} (ср. {fmt(s['am'])})\n"
                f"──────────────────────────────\n"
                f"Темп:       {s['rph']:.1f} забегов/час\n"
                f"В забегах:  {fmt(s['ta'])} ({s['sh']:.0f}%) | Хаб: {fmt(s['th'])}"
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
    r.configure(bg="#121417", highlightbackground="#3a3f4b", highlightthickness=1)
    def read_cfg():
        try:
            if CONFIG_FILE.exists(): return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception: pass
        return {}

    def write_cfg(upd):
        try:
            c = read_cfg(); c.update(upd)
            CONFIG_FILE.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception: pass

    _ic = read_cfg()
    ui_state = {"font_size": int(_ic.get("font_size", 9)), "alpha": float(_ic.get("alpha", 0.85))}
    try: r.attributes("-alpha", ui_state["alpha"])
    except Exception: pass

    def load_overlay_pos():
        pos = _ic.get("overlay_pos_poe2" if poe2_mode else "overlay_pos_poe1")
        if isinstance(pos, list) and len(pos) == 2:
            px, py = int(pos[0]), int(pos[1])
            if 0 <= px <= max(0, r.winfo_screenwidth()-80) and 0 <= py <= max(0, r.winfo_screenheight()-40):
                return f"+{px}+{py}"
        return "+20+120"

    def save_overlay_pos(event=None):
        try:
            cfg = {}
            if CONFIG_FILE.exists():
                cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            key = "overlay_pos_poe2" if poe2_mode else "overlay_pos_poe1"
            cfg[key] = [r.winfo_x(), r.winfo_y()]
            CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Не удалось сохранить позицию окна: {e}")

    r.geometry(load_overlay_pos())
    d = {"x": 0, "y": 0}
    h = tk.Frame(r, bg="#1e2229", cursor="fleur"); h.pack(fill="x")
    def get_title():
        if poe2_mode:
            base = f" EXILEPACE: ULTIMATUM v{VERSION}" if ultimatum_mode else f" EXILEPACE: SEKHEMAS v{VERSION}"
        else:
            base = f" EXILEPACE: BLIGHT v{VERSION}" if blight_mode else f" EXILEPACE: HEIST v{VERSION}"
        tag = f" [{cur_league[3]}]" if cur_league else (" [СЕГОДНЯ]" if start_date == date.today() else (" [ВСЁ]" if start_date is None else f" [{start_date:%d.%m}]"))
        return base + tag

    def get_btn_label():
        if poe2_mode:
            return "⇄ SEKHEMAS" if ultimatum_mode else "⇄ ULTIMATUM"
        return "⇄ HEIST" if blight_mode else "⇄ BLIGHT"

    t = tk.Label(h, text=get_title(), bg="#1e2229", fg="#dfcf99", font=("Sans", ui_state["font_size"], "bold"))
    t.pack(side="left", padx=4)

    x = tk.Label(h, text="✕", bg="#1e2229", fg="#8b949e", font=("Sans", ui_state["font_size"], "bold"), cursor="hand2")
    x.pack(side="right", padx=6)
    x.bind("<Button-1>", lambda e: r.destroy())

    sw = tk.Label(h, text=get_btn_label(), bg="#2b313c", fg="#a3be8c", font=("Sans", 8, "bold"), padx=5, pady=1, cursor="hand2")
    sw.pack(side="right", padx=4, pady=2)

    import threading as _bg_th

    def render_async(force_prewarm=False):
        snap_b, snap_u = blight_mode, ultimatum_mode
        def _job():
            try:
                cur_txt = out_text(snap_b, snap_u)
                r.after(0, lambda: lbl.config(text=cur_txt))
                if force_prewarm:
                    if poe2_mode:
                        out_text(snap_b, not snap_u)
                    else:
                        out_text(not snap_b, snap_u)
            except Exception as e:
                logger.error(f"Ошибка фонового рендера: {e}")
        _bg_th.Thread(target=_job, daemon=True).start()

    def switch_mode(event=None):
        global blight_mode, ultimatum_mode
        if poe2_mode:
            ultimatum_mode = not ultimatum_mode
        else:
            blight_mode = not blight_mode
        t.config(text=get_title())
        sw.config(text=get_btn_label())
        # Если в кэше уже есть готовый текст — ставим мгновенно без ожидания диска
        try:
            fs = os.stat(log_path)
            ckey = (log_path, fs.st_mtime, fs.st_size, blight_mode, poe2_mode, ultimatum_mode, start_date, end_date)
            if ckey in _render_cache:
                lbl.config(text=_render_cache[ckey])
                return
        except Exception:
            pass
        render_async()

    def on_sw_click(e):
        if 0 <= e.x <= sw.winfo_width() and 0 <= e.y <= sw.winfo_height():
            switch_mode()
    sw.bind("<ButtonRelease-1>", on_sw_click)
    def start_drag(e):
        d.update(rx=e.x_root, ry=e.y_root, wx=r.winfo_x(), wy=r.winfo_y())

    def do_drag(e):
        r.geometry(f"+{d['wx'] + e.x_root - d['rx']}+{d['wy'] + e.y_root - d['ry']}")

    for w in (h, t):
        w.bind("<Button-1>", start_drag)
        w.bind("<B1-Motion>", do_drag)
        w.bind("<ButtonRelease-1>", save_overlay_pos)
    lbl = tk.Label(r, text="...", bg="#121417", fg="#e6e6e6", justify="left", anchor="w", font=("Monospace", ui_state["font_size"]), padx=8, pady=6)
    lbl.pack()
    st = {"m": 0, "s": 0, "base_txt": ""}
    def apply_live_timer(raw_txt):
        nl = chr(10)
        if _active_zone_start is not None and nl in raw_txt:
            sec = max(0, int((datetime.now() - _active_zone_start).total_seconds()))
            if sec <= 1800:
                mm, ss = divmod(sec, 60)
                first_line, rest = raw_txt.split(nl, 1)
                z_base, *_ = first_line.split(" (")
                return f"{z_base[:18]} ({mm:02d}:{ss:02d}){nl}{rest}"
        return raw_txt

    # Оборачиваем вывод в lbl, чтобы сохранять базовый текст и тикать секундомер поверх него
    _orig_render_async = render_async
    def render_async(force_prewarm=False):
        snap_b, snap_u = blight_mode, ultimatum_mode
        def _job():
            try:
                cur_txt = out_text(snap_b, snap_u)
                st["base_txt"] = cur_txt
                r.after(0, lambda: lbl.config(text=apply_live_timer(cur_txt)))
                if force_prewarm:
                    if poe2_mode:
                        out_text(snap_b, not snap_u)
                    else:
                        out_text(not snap_b, snap_u)
            except Exception as e:
                logger.error(f"Ошибка фонового рендера: {e}")
        _bg_th.Thread(target=_job, daemon=True).start()

    def upd():
        try:
            fs = os.stat(log_path)
            if fs.st_mtime != st["m"] or fs.st_size != st["s"]:
                st["m"], st["s"] = fs.st_mtime, fs.st_size
                t0 = time.perf_counter()
                render_async(force_prewarm=True)
                logger.debug(f"Оверлей обновлен за {(time.perf_counter()-t0)*1000:.1f} мс")
            elif st["base_txt"] and _active_zone_start is not None:
                lbl.config(text=apply_live_timer(st["base_txt"]))
        except Exception as e:
            logger.error(f"Ошибка обновления оверлея: {e}", exc_info=True)
            lbl.config(text=f"Ошибка чтения лога (см. tracker.log):\n{e}")
        r.after(400, upd)

    def setup_tray():
        try:
            import threading, pystray
            from PIL import Image
            ico_file = APP_DIR / "icon.png"
            if not ico_file.is_file():
                logger.warning(f"Иконка не найдена: {ico_file}")
                return
            img = Image.open(ico_file)
            visible = {"state": True}

            def toggle_overlay(icon, item):
                if visible["state"]:
                    r.after(0, r.withdraw); visible["state"] = False
                else:
                    r.after(0, r.deiconify); visible["state"] = True

            def open_log_file(icon, item):
                try:
                    if os.name == "nt": os.startfile(str(LOG_FILE))
                    else:
                        import subprocess
                        subprocess.Popen(["xdg-open", str(LOG_FILE)])
                except Exception as e:
                    logger.error(f"Не удалось открыть лог: {e}")

            def run_upd_from_tray(icon, item):
                if perform_self_update():
                    icon.stop(); r.after(0, r.destroy)
                    os.execv(sys.executable, [sys.executable] + sys.argv)

            def quit_app(icon, item):
                icon.stop(); r.after(0, r.destroy)

            def apply_filter(lg_obj, s_dt, e_dt):
                def _apply(icon, item):
                    def _ui():
                        global league_mode, cur_league, start_date, end_date
                        cur_league = lg_obj
                        league_mode = lg_obj is not None
                        start_date, end_date = s_dt, e_dt
                        t.config(text=get_title())
                        lbl.config(text="Загрузка...")
                        render_async(force_prewarm=True)
                    r.after(0, _ui)
                return _apply

            def build_period_items():
                items = [
                    pystray.MenuItem("Сегодня", apply_filter(None, date.today(), None), checked=lambda item: (cur_league is None and start_date == date.today()), radio=True),
                    pystray.MenuItem("Всё время", apply_filter(None, None, None), checked=lambda item: (cur_league is None and start_date is None), radio=True),
                    pystray.Menu.SEPARATOR,
                ]
                for lg in (LEAGUES_POE2 if poe2_mode else LEAGUES_POE1):
                    items.append(
                        pystray.MenuItem(
                            lg[0],
                            apply_filter(lg, lg[1], lg[2]),
                            checked=lambda item, target=lg: cur_league == target,
                            radio=True
                        )
                    )
                return items

            period_menu = pystray.Menu(lambda: build_period_items())

            def set_fs(sz):
                def _f(icon, item):
                    def _u():
                        ui_state["font_size"] = sz
                        t.config(font=("Sans", sz, "bold")); lbl.config(font=("Monospace", sz))
                        write_cfg({"font_size": sz})
                    r.after(0, _u)
                return _f

            def set_al(al):
                def _f(icon, item):
                    def _u():
                        ui_state["alpha"] = al
                        try: r.attributes("-alpha", al)
                        except Exception: pass
                        write_cfg({"alpha": al})
                    r.after(0, _u)
                return _f

            def open_cfg(icon, item):
                if not CONFIG_FILE.exists(): write_cfg({})
                if os.name == "nt": os.startfile(str(CONFIG_FILE))
                else: import subprocess; subprocess.Popen(["xdg-open", str(CONFIG_FILE)])

            font_m = pystray.Menu(
                pystray.MenuItem("Мелкий (8)", set_fs(8), checked=lambda i: ui_state["font_size"] == 8, radio=True),
                pystray.MenuItem("Обычный (9)", set_fs(9), checked=lambda i: ui_state["font_size"] == 9, radio=True),
                pystray.MenuItem("Крупный (11)", set_fs(11), checked=lambda i: ui_state["font_size"] == 11, radio=True),
                pystray.MenuItem("Огромный (13)", set_fs(13), checked=lambda i: ui_state["font_size"] == 13, radio=True),
            )
            alpha_m = pystray.Menu(
                pystray.MenuItem("100%", set_al(1.0), checked=lambda i: abs(ui_state["alpha"] - 1.0) < 0.01, radio=True),
                pystray.MenuItem("85%", set_al(0.85), checked=lambda i: abs(ui_state["alpha"] - 0.85) < 0.01, radio=True),
                pystray.MenuItem("70%", set_al(0.70), checked=lambda i: abs(ui_state["alpha"] - 0.70) < 0.01, radio=True),
                pystray.MenuItem("55%", set_al(0.55), checked=lambda i: abs(ui_state["alpha"] - 0.55) < 0.01, radio=True),
            )
            cfg_m = pystray.Menu(
                pystray.MenuItem("Размер шрифта", font_m),
                pystray.MenuItem("Прозрачность", alpha_m),
                pystray.MenuItem("Сбросить позицию окна", lambda i, it: r.after(0, lambda: (r.geometry("+20+120"), save_overlay_pos()))),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Открыть config.json", open_cfg),
                pystray.MenuItem("Открыть лог отладки", open_log_file),
                pystray.MenuItem("Проверить обновления", run_upd_from_tray),
            )
            sw_title = "Переключить режим (Сехем / Ультиматум)" if poe2_mode else "Переключить режим (Heist / Blight)"
            menu = pystray.Menu(
                pystray.MenuItem("Показать / Скрыть оверлей", toggle_overlay, default=True),
                pystray.MenuItem("Период / Лига", period_menu),
                pystray.MenuItem(sw_title, lambda i, it: r.after(0, switch_mode)),
                pystray.MenuItem("Настройки", cfg_m),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Выход", quit_app)
            )
            tray = pystray.Icon("exile_pace", img, "ExilePace", menu)
            threading.Thread(target=tray.run, daemon=True).start()
            logger.info("Значок Разбойничьего жетона запущен в трее")
        except Exception as e:
            logger.warning(f"Ошибка трея: {e}", exc_info=True)

    setup_tray()
    upd(); r.mainloop()
  elif live_mode:
    lm = ls = 0
    try:
        while True:
            fs = os.stat(log_path)
            if fs.st_mtime != lm or fs.st_size != ls:
                lm, ls = fs.st_mtime, fs.st_size
                sys.stdout.write("\033[H\033[J" + out_text() + "\n")
            time.sleep(0.4)
    except KeyboardInterrupt: pass
  else:
    print(out_text() + "\n\nТоп локаций:")
    zc = (stats_poe2() if poe2_mode else stats_poe1())["zc"]
    for z, c in sorted(zc.items(), key=itemgetter(1), reverse=True)[:15]: print(f"  {z}: {c}")
