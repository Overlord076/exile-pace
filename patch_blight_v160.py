from pathlib import Path

p = Path.home() / "exile-pace" / "heist_stats.py"
txt = p.read_text(encoding="utf-8")

txt = txt.replace('VERSION = "1.5.1"', 'VERSION = "1.6.0"').replace('VERSION = "1.5.0"', 'VERSION = "1.6.0"')

old_cassia_rx = 'cassia_rx = re.compile(r"^(\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2}:\\d{2}).*?(?:Sister Cassia:|Сестра Кассия:)")'
new_cassia_rx = '''cassia_rx = re.compile(r"^(\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2}:\\d{2}).*?(?:Sister Cassia:|Сестра Кассия:)\\s*(.*)")
oil_rx = re.compile(r"(Golden Oil|Silver Oil|Tainted Oil|Prismatic Oil|Reflective Oil|Золотое масло|Серебряное масло|Осквернённое масло|Оскверненное масло|Призматическое масло|Отражающее масло)", re.IGNORECASE)'''

txt = txt.replace(old_cassia_rx, new_cassia_rx)

old_blight_func = '''def stats_blight():
    events, cur = [], "—"
    with open(log_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = rx.search(line)
            if m:
                ts = datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
                z = m.group(2) or m.group(3)
                cur = z
                if not start_date or ts.date() >= start_date:
                    events.append(("zone", ts, z))
                continue
            cm = cassia_rx.search(line)
            if cm:
                ts = datetime.strptime(cm.group(1), "%Y/%m/%d %H:%M:%S")
                if not start_date or ts.date() >= start_date:
                    events.append(("cassia", ts, ""))

    bl_maps = rav_maps = enc_cnt = 0
    z_cnt = defaultdict(int)
    bl_rec, rav_rec = [], []
    t_run = t_ho = 0.0
    in_blight_map = False
    cassia_seen_in_zone = False

    zone_list = [(ts, z) for kind, ts, z in events if kind == "zone"]
    z_idx = 0

    for kind, ts, val in events:
        if kind == "cassia":
            if not in_blight_map and not cassia_seen_in_zone:
                enc_cnt += 1
                cassia_seen_in_zone = True
                z_cnt["Встречи Кассии на картах"] += 1
            continue

        cassia_seen_in_zone = False
        zl = val.lower()
        dur = (zone_list[z_idx + 1] - ts).total_seconds() if z_idx + 1 < len(zone_list) else 0
        z_idx += 1
        valid_d = 30 <= dur <= 1800

        if "hideout" in zl or "убежище" in zl:
            in_blight_map = False
            if 1 <= dur <= 900: t_ho += dur
            continue

        is_rav = zl.startswith("blight-ravaged ") or zl.startswith("осквернённая ") or zl.startswith("оскверненная ")
        is_bl = zl.startswith("blight ") or zl.startswith("blighted ") or zl.startswith("заражённая ") or zl.startswith("зараженная ")

        if is_rav:
            in_blight_map = True
            rav_maps += 1
            if valid_d: rav_rec.append((dur, val, ts)); t_run += dur
            z_cnt[val] += 1
        elif is_bl:
            in_blight_map = True
            bl_maps += 1
            if valid_d: bl_rec.append((dur, val, ts)); t_run += dur
            z_cnt[val] += 1
        else:
            in_blight_map = False

    tot = bl_maps + rav_maps + enc_cnt
    tf = t_run + t_ho
    return {
        "cur": cur, "bl": bl_maps, "rav": rav_maps, "enc": enc_cnt, "tot": tot,
        "ab": sum(x for x in bl_rec)/len(bl_rec) if bl_rec else 0,
        "bb": min(bl_rec, key=itemgetter(0)) if bl_rec else None,
        "ar": sum(x for x in rav_rec)/len(rav_rec) if rav_rec else 0,
        "br": min(rav_rec, key=itemgetter(0)) if rav_rec else None,
        "rph": (bl_maps + rav_maps)/(tf/3600) if tf > 0 else 0,
        "tr": t_run, "th": t_ho, "sh": (t_run/tf*100) if tf > 0 else 0, "zc": z_cnt
    }'''

new_blight_func = '''def stats_blight():
    events, cur = [], "—"
    oil_mentions = defaultdict(int)
    with open(log_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = rx.search(line)
            if m:
                ts = datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
                z = m.group(2) or m.group(3)
                cur = z
                if not start_date or ts.date() >= start_date:
                    events.append(("zone", ts, z))
                continue
            cm = cassia_rx.search(line)
            if cm:
                ts = datetime.strptime(cm.group(1), "%Y/%m/%d %H:%M:%S")
                if not start_date or ts.date() >= start_date:
                    events.append(("cassia", ts, cm.group(2)))
                continue
            om = oil_rx.search(line)
            if om and len(line) >= 19:
                try:
                    ts = datetime.strptime(line[:19], "%Y/%m/%d %H:%M:%S")
                    if not start_date or ts.date() >= start_date:
                        oil_mentions[om.group(1).title()] += 1
                except Exception:
                    pass

    bl_maps = rav_maps = enc_cnt = pump_wins = pump_fails = 0
    z_cnt = defaultdict(int)
    bl_rec, rav_rec = [], []
    t_run = t_ho = 0.0
    in_blight_map = False
    cassia_seen_in_zone = False
    outcome_seen_in_zone = False

    zone_list = [(ts, z) for kind, ts, z in events if kind == "zone"]
    z_idx = 0

    for kind, ts, val in events:
        if kind == "cassia":
            speech = val.lower()
            if not in_blight_map and not cassia_seen_in_zone:
                enc_cnt += 1
                cassia_seen_in_zone = True
                z_cnt["Встречи Кассии на картах"] += 1
            if not outcome_seen_in_zone:
                if any(k in speech for k in ("destroyed", "уничтожен", "о нет! насос", "oh, no! the pump")):
                    pump_fails += 1
                    outcome_seen_in_zone = True
                elif any(k in speech for k in ("wonderful", "turned to ash", "чудесно", "обратились в прах", "очищена")):
                    pump_wins += 1
                    outcome_seen_in_zone = True
            continue

        cassia_seen_in_zone = False
        outcome_seen_in_zone = False
        zl = val.lower()
        dur = (zone_list[z_idx + 1] - ts).total_seconds() if z_idx + 1 < len(zone_list) else 0
        z_idx += 1
        valid_d = 30 <= dur <= 1800

        if "hideout" in zl or "убежище" in zl:
            in_blight_map = False
            if 1 <= dur <= 900: t_ho += dur
            continue

        is_rav = zl.startswith("blight-ravaged ") or zl.startswith("осквернённая ") or zl.startswith("оскверненная ")
        is_bl = zl.startswith("blight ") or zl.startswith("blighted ") or zl.startswith("заражённая ") or zl.startswith("зараженная ")

        if is_rav:
            in_blight_map = True
            rav_maps += 1
            if valid_d: rav_rec.append((dur, val, ts)); t_run += dur
            z_cnt[val] += 1
        elif is_bl:
            in_blight_map = True
            bl_maps += 1
            if valid_d: bl_rec.append((dur, val, ts)); t_run += dur
            z_cnt[val] += 1
        else:
            in_blight_map = False

    tot = bl_maps + rav_maps + enc_cnt
    tf = t_run + t_ho
    total_outcomes = pump_wins + pump_fails
    winrate = (pump_wins / total_outcomes * 100) if total_outcomes > 0 else 0
    return {
        "cur": cur, "bl": bl_maps, "rav": rav_maps, "enc": enc_cnt, "tot": tot,
        "wins": pump_wins, "fails": pump_fails, "winrate": winrate,
        "oils": sum(oil_mentions.values()), "oil_detail": dict(oil_mentions),
        "ab": sum(x for x, _, _ in bl_rec)/len(bl_rec) if bl_rec else 0,
        "bb": min(bl_rec, key=itemgetter(0)) if bl_rec else None,
        "ar": sum(x for x, _, _ in rav_rec)/len(rav_rec) if rav_rec else 0,
        "br": min(rav_rec, key=itemgetter(0)) if rav_rec else None,
        "rph": (bl_maps + rav_maps)/(tf/3600) if tf > 0 else 0,
        "tr": t_run, "th": t_ho, "sh": (t_run/tf*100) if tf > 0 else 0, "zc": z_cnt
    }'''

txt = txt.replace(old_blight_func, new_blight_func)

old_blight_out = '''    if blight_mode:
        s = stats_blight()
        bb = fmt(s["bb"]) if s["bb"] else "н/д"
        br = fmt(s["br"]) if s["br"] else "н/д"
        return (
            f"Зона: {s['cur'][:24]}\\n"
            f"──────────────────────────────\\n"
            f"Заражённые:   {s['bl']} карт (ср. {fmt(s['ab'])})\\n"
            f"Осквернённые: {s['rav']} карт (ср. {fmt(s['ar'])})\\n"
            f"Кассия (карт): {s['enc']} встреч | Рекорды: {bb} / {br}\\n"
            f"──────────────────────────────\\n"
            f"Темп карт:    {s['rph']:.1f} карт/час\\n"
            f"В Скверне:    {fmt(s['tr'])} ({s['sh']:.0f}%) | Убежище: {fmt(s['th'])}"
        )'''

new_blight_out = '''    if blight_mode:
        s = stats_blight()
        bb = fmt(s["bb"][0]) if s["bb"] else "н/д"
        br = fmt(s["br"][0]) if s["br"] else "н/д"
        wr_str = f"{s['winrate']:.0f}%" if (s["wins"] + s["fails"]) > 0 else "н/д"
        return (
            f"Зона: {s['cur'][:24]}\\n"
            f"──────────────────────────────\\n"
            f"Заражённые:   {s['bl']} карт (ср. {fmt(s['ab'])})\\n"
            f"Осквернённые: {s['rav']} карт (ср. {fmt(s['ar'])})\\n"
            f"Кассия (карт): {s['enc']} встр. | Насос: {s['wins']}W / {s['fails']}L ({wr_str})\\n"
            f"Рекорды:      {bb} / {br} | Топ-масла (чат): {s['oils']}\\n"
            f"──────────────────────────────\\n"
            f"Темп карт:    {s['rph']:.1f} карт/час\\n"
            f"В Скверне:    {fmt(s['tr'])} ({s['sh']:.0f}%) | Убежище: {fmt(s['th'])}"
        )'''

txt = txt.replace(old_blight_out, new_blight_out)

# Также выводим разбивку по топ-маслам в терминале при запуске без --overlay
old_term_end = '''else:
    print(out_text() + "\\n\\nТоп локаций:")'''

new_term_end = '''else:
    print(out_text())
    if blight_mode:
        od = stats_blight()["oil_detail"]
        if od:
            print("\\nУпоминания топ-масел (торговля/чат):")
            for k, v in sorted(od.items(), key=itemgetter(1), reverse=True):
                print(f"  {k}: {v}")
    print("\\nТоп локаций:")'''

txt = txt.replace(old_term_end, new_term_end)


cat << 'EOF' > ~/exile-pace/patch_v160.py
import re
from pathlib import Path

p = Path.home() / "exile-pace" / "heist_stats.py"
txt = p.read_text(encoding="utf-8")
txt = txt.replace('VERSION = "1.5.1"', 'VERSION = "1.6.0"').replace('VERSION = "1.5.0"', 'VERSION = "1.6.0"')

old_rx = 'cassia_rx = re.compile(r"^(\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2}:\\d{2}).*?(?:Sister Cassia:|Сестра Кассия:)")'
new_rx = 'cassia_rx = re.compile(r"^(\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2}:\\d{2}).*?(?:Sister Cassia:|Сестра Кассия:)\\s*(.*)")\noil_rx = re.compile(r"(Golden Oil|Silver Oil|Tainted Oil|Prismatic Oil|Reflective Oil|Золотое масло|Серебряное масло|Осквернённое масло|Оскверненное масло|Призматическое масло|Отражающее масло)", re.I)'
txt = txt.replace(old_rx, new_rx)
