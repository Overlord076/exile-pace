new_blight = '''def stats_blight():
    events, cur = [], "—"
    oils = defaultdict(int)
    with open(log_path, encoding="utf-8", errors="ignore") as f:
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
            if not in_bl and not seen_c:
                enc += 1; seen_c = True; z_cnt["Встречи Кассии"] += 1
            if not seen_out:
                if any(w in sp for w in ("destroyed", "уничтожен", "о нет! насос", "oh, no! the pump")):
                    fails += 1; seen_out = True
                elif any(w in sp for w in ("wonderful", "turned to ash", "чудесно", "обратились в прах", "очищена")):
                    wins += 1; seen_out = True
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
        is_rav = zl.startswith(("blight-ravaged ", "осквернённая ", "оскверненная "))
        is_bl = zl.startswith(("blight ", "blighted ", "заражённая ", "зараженная "))
        if is_rav:
            in_bl = True; rav_m += 1; z_cnt[val] += 1
            if vd: rav_rec.append((dur, val, ts)); t_run += dur
        elif is_bl:
            in_bl = True; bl_m += 1; z_cnt[val] += 1
            if vd: bl_rec.append((dur, val, ts)); t_run += dur
        else: in_bl = False
    tf = t_run + t_ho
    wr = (wins / (wins + fails) * 100) if (wins + fails) > 0 else 0
    return {
        "cur": cur, "bl": bl_m, "rav": rav_m, "enc": enc,
        "wins": wins, "fails": fails, "wr": wr,
        "oils": sum(oils.values()), "oil_detail": dict(oils),
        "ab": sum(x[0] for x in bl_rec)/len(bl_rec) if bl_rec else 0,
        "bb": min(bl_rec, key=itemgetter(0)) if bl_rec else None,
        "ar": sum(x[0] for x in rav_rec)/len(rav_rec) if rav_rec else 0,
        "br": min(rav_rec, key=itemgetter(0)) if rav_rec else None,
        "rph": (bl_m + rav_m)/(tf/3600) if tf > 0 else 0,
        "tr": t_run, "th": t_ho, "sh": (t_run/tf*100) if tf > 0 else 0, "zc": z_cnt
    }'''

txt = re.sub(r"def stats_blight\(\):.*?def stats_poe2\(\):", new_blight + "\n\ndef stats_poe2():", txt, flags=re.S)
new_out = '''    if blight_mode:
        s = stats_blight()
        bb = fmt(s["bb"][0]) if s["bb"] else "н/д"
        br = fmt(s["br"][0]) if s["br"] else "н/д"
        wr_s = f"{s['wr']:.0f}%" if (s["wins"] + s["fails"]) > 0 else "н/д"
        return (
            f"Зона: {s['cur'][:24]}\\n"
            f"──────────────────────────────\\n"
            f"Заражённые:   {s['bl']} карт (ср. {fmt(s['ab'])})\\n"
            f"Осквернённые: {s['rav']} карт (ср. {fmt(s['ar'])})\\n"
            f"Кассия:       {s['enc']} встр. | Насос: {s['wins']}W / {s['fails']}L ({wr_s})\\n"
            f"Рекорды:      {bb} / {br} | Топ-масла: {s['oils']}\\n"
            f"──────────────────────────────\\n"
            f"Темп карт:    {s['rph']:.1f} карт/час\\n"
            f"В Скверне:    {fmt(s['tr'])} ({s['sh']:.0f}%) | Убежище: {fmt(s['th'])}"
        )'''

txt = re.sub(r"    if blight_mode:.*?    if poe2_mode:", new_out + "\n    if poe2_mode:", txt, flags=re.S)
p.write_text(txt, encoding="utf-8")
print("Патч v1.6.0 успешно применён!")
