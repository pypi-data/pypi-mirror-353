from pathlib import Path
from typing import Tuple

import rrdtool
from brasciichart import *

from . import (
    THEME_BLACK, IMG_FORMAT, COLOR_RESET, XAXIS_CFG, GraphSize, Params,
    human_size, lbl_size, min_max_last_avg, conf, lstrip_column,
    ceil_scaled, floor_scaled,
)


def _load_pic(params: Params, out_dir: Path, cfg: dict,
              rrd: str) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_system1")}'
    if not params.picUrls:
        return title, Path('no-image')
    graphv = [
        f'DEF:load1={rrd}:system_load1:AVERAGE',
        f'DEF:load5={rrd}:system_load5:AVERAGE',
        f'DEF:load15={rrd}:system_load15:AVERAGE',
        'CDEF:allvalues=load1,load5,load15,+,+',
        'AREA:load1#4444EE: 1 min average',
        'GPRINT:load1:LAST:  Current\\: %4.2lf',
        'GPRINT:load1:AVERAGE:   Average\\: %4.2lf',
        'GPRINT:load1:MIN:   Min\\: %4.2lf',
        'GPRINT:load1:MAX:   Max\\: %4.2lf\\n',
        'LINE1:load1#0000EE',
        'LINE1:load5#EEEE00: 5 min average',
        'GPRINT:load5:LAST:  Current\\: %4.2lf',
        'GPRINT:load5:AVERAGE:   Average\\: %4.2lf',
        'GPRINT:load5:MIN:   Min\\: %4.2lf',
        'GPRINT:load5:MAX:   Max\\: %4.2lf\\n',
        'LINE1:load15#00EEEE:15 min average',
        'GPRINT:load15:LAST:  Current\\: %4.2lf',
        'GPRINT:load15:AVERAGE:   Average\\: %4.2lf',
        'GPRINT:load15:MIN:   Min\\: %4.2lf',
        'GPRINT:load15:MAX:   Max\\: %4.2lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    title = f'{cfg.get("graphs").get("_system1")}'
    pic = out_dir / f'system_load.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}  ({params.when})',
                   '--vertical-label=Load average',
                   *GraphSize.main,
                   *graphv,
                   *THEME_BLACK)
    return title, pic


def _mem_pic(params: Params, out_dir: Path, cfg: dict,
             rrd: str) -> Tuple[str, Path, int]:
    meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1]))
                   for i in open('/proc/meminfo').readlines())
    # TODO: Support FreeBSD, OpenBSD, NetBSD total memory bytes
    total_mem = meminfo['MemTotal']  # in KB
    total_mem_bytes = int(total_mem) * 1024
    total_mem = int(total_mem / 1024)  # in MB
    title = f'{cfg.get("graphs").get("_system2")} ({total_mem}MB)'
    if not params.picUrls:
        return title, Path('no-image'), total_mem_bytes
    graphv = [
        f'DEF:mtotl={rrd}:system_mtotl:AVERAGE',
        f'DEF:mbuff={rrd}:system_mbuff:AVERAGE',
        f'DEF:mcach={rrd}:system_mcach:AVERAGE',
        f'DEF:mfree={rrd}:system_mfree:AVERAGE',
        f'DEF:macti={rrd}:system_macti:AVERAGE',
        f'DEF:minac={rrd}:system_minac:AVERAGE',
        'CDEF:m_mtotl=mtotl,1024,*',
        'CDEF:m_mbuff=mbuff,1024,*',
        'CDEF:m_mcach=mcach,1024,*',
        'CDEF:m_mused=m_mtotl,mfree,1024,*,-,m_mbuff,-,m_mcach,-',
        'CDEF:m_macti=macti,1024,*',
        'CDEF:m_minac=minac,1024,*',
        'CDEF:allvalues=mtotl,mbuff,mcach,mfree,macti,minac,+,+,+,+,+',
        'AREA:m_mused#EE4444:Used',
        'AREA:m_mcach#44EE44:Cached',
        'AREA:m_mbuff#CCCCCC:Buffers',
        'AREA:m_macti#E29136:Active',
        'AREA:m_minac#448844:Inactive',
        'LINE2:m_minac#008800',
        'LINE2:m_macti#E29136',
        'LINE2:m_mbuff#CCCCCC',
        'LINE2:m_mcach#00EE00',
        'LINE2:m_mused#EE0000',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'system_memory.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}  ({params.when})',
                   '--vertical-label=bytes',
                   f'--upper-limit={total_mem_bytes}',
                   '--lower-limit=0',
                   '--rigid',
                   '--base=1024',
                   *GraphSize.main,
                   *graphv,
                   *THEME_BLACK)
    return title, pic, total_mem_bytes


def _processes_pic(params: Params, out_dir: Path, cfg: dict,
                   rrd: str) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_system3")}'
    if not params.picUrls:
        return title, Path('no-image')
    graphv = [
        f'DEF:nproc={rrd}:system_nproc:AVERAGE',
        f'DEF:npslp={rrd}:system_npslp:AVERAGE',
        f'DEF:nprun={rrd}:system_nprun:AVERAGE',
        f'DEF:npwio={rrd}:system_npwio:AVERAGE',
        f'DEF:npzom={rrd}:system_npzom:AVERAGE',
        f'DEF:npstp={rrd}:system_npstp:AVERAGE',
        f'DEF:npswp={rrd}:system_npswp:AVERAGE',
        'AREA:npslp#448844:Sleeping',
        'GPRINT:npslp:LAST:             Current\\:%5.0lf\\n',
        'LINE2:npwio#EE44EE:Wait I/O',
        'GPRINT:npwio:LAST:             Current\\:%5.0lf\\n',
        'LINE2:npzom#00EEEE:Zombie',
        'GPRINT:npzom:LAST:               Current\\:%5.0lf\\n',
        'LINE2:npstp#EEEE00:Stopped',
        'GPRINT:npstp:LAST:              Current\\:%5.0lf\\n',
        'LINE2:npswp#0000EE:Paging',
        'GPRINT:npswp:LAST:               Current\\:%5.0lf\\n',
        'LINE2:nprun#EE0000:Running',
        'GPRINT:nprun:LAST:              Current\\:%5.0lf\\n',
        'COMMENT: \\n',
        'LINE2:nproc#888888:Total Processes',
        'GPRINT:nproc:LAST:      Current\\:%5.0lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'system_processes.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}  ({params.when})',
                   '--vertical-label=Processes',
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return title, pic


def _entropy_pic(params: Params, out_dir: Path, cfg: dict,
                 rrd: str) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_system4")}'
    if not params.picUrls:
        return title, Path('no-image')
    graphv = [
        f'DEF:entropy={rrd}:system_entrop:AVERAGE',
        'LINE2:entropy#EEEE00:Entropy',
        'GPRINT:entropy:LAST:              Current\\:%5.0lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'system_entropy.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}  ({params.when})',
                   '--vertical-label=Size',
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return title, pic


def _uptime_pic(params: Params, out_dir: Path, cfg: dict,
                rrd: str) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_system5")}'
    if not params.picUrls:
        return title, Path('no-image')
    graphv = [
        f'DEF:uptime={rrd}:system_uptime:AVERAGE',
        # TODO: Support uptime units: minutes, hours
        f'CDEF:uptime_days=uptime,86400,/',
        'LINE2:uptime_days#EE44EE:Uptime',
        'GPRINT:uptime_days:LAST:               Current\\:%5.1lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'system_uptime.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}  ({params.when})',
                   '--vertical-label=Days',
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return title, pic


def system_cgi(params: Params, db_dir: Path, out_dir: Path, cfg: dict) -> str:
    rrd = str(db_dir / 'system.rrd')
    title_load, pic_load = _load_pic(params, out_dir, cfg, rrd)
    title_mem, pic_mem, total_mem_bytes = _mem_pic(params, out_dir, cfg, rrd)
    title_proc, pic_proc = _processes_pic(params, out_dir, cfg, rrd)
    title_ent, pic_ent = _entropy_pic(params, out_dir, cfg, rrd)
    title_upt, pic_upt = _uptime_pic(params, out_dir, cfg, rrd)
    #
    xport = [
        # system load
        f'DEF:load1={rrd}:system_load1:AVERAGE',
        f'DEF:load5={rrd}:system_load5:AVERAGE',
        f'DEF:load15={rrd}:system_load15:AVERAGE',
        'XPORT:load1:load1',  # 0
        'XPORT:load5:load5',
        'XPORT:load15:load15',
        # memory
        # TODO: Support OpenBSD, NetBSD with m_mused, m_macti only
        f'DEF:mtotl={rrd}:system_mtotl:AVERAGE',
        f'DEF:mbuff={rrd}:system_mbuff:AVERAGE',
        f'DEF:mcach={rrd}:system_mcach:AVERAGE',
        f'DEF:mfree={rrd}:system_mfree:AVERAGE',
        f'DEF:macti={rrd}:system_macti:AVERAGE',
        f'DEF:minac={rrd}:system_minac:AVERAGE',
        'CDEF:m_mtotl=mtotl,1024,*',
        'CDEF:m_mbuff=mbuff,1024,*',
        'CDEF:m_mcach=mcach,1024,*',
        'CDEF:m_mused=m_mtotl,mfree,1024,*,-,m_mbuff,-,m_mcach,-',
        'CDEF:m_macti=macti,1024,*',
        'CDEF:m_minac=minac,1024,*',
        'XPORT:m_mbuff:m_mbuff',  # 3
        'XPORT:m_mcach:m_mcach',
        'XPORT:m_mused:m_mused',
        'XPORT:m_macti:m_macti',
        'XPORT:m_minac:m_minac',
        # processes
        f'DEF:nproc={rrd}:system_nproc:AVERAGE',
        f'DEF:npslp={rrd}:system_npslp:AVERAGE',
        f'DEF:nprun={rrd}:system_nprun:AVERAGE',
        f'DEF:npwio={rrd}:system_npwio:AVERAGE',
        f'DEF:npzom={rrd}:system_npzom:AVERAGE',
        f'DEF:npstp={rrd}:system_npstp:AVERAGE',
        f'DEF:npswp={rrd}:system_npswp:AVERAGE',
        f'XPORT:nproc:nproc',  # 8
        f'XPORT:npslp:npslp',
        f'XPORT:nprun:nprun',
        f'XPORT:npwio:npwio',
        f'XPORT:npzom:npzom',
        f'XPORT:npstp:npstp',
        f'XPORT:npswp:npswp',
        # entropy
        f'DEF:entropy={rrd}:system_entrop:AVERAGE',  #
        f'XPORT:entropy:entropy',  # 15
        # uptime
        f'DEF:uptime={rrd}:system_uptime:AVERAGE',
        f'CDEF:uptime_days=uptime,86400,/',
        f'XPORT:uptime_days:uptime_days',  # 16
    ]
    # noinspection PyArgumentList
    data = rrdtool.xport('--start', f'-{params.when}',
                         '--step', '60',
                         *xport)
    data_lists = list(zip(*data['data']))

    # region System load
    fmt = '{:6.2f} '
    # @formatter:off
    load1  = list(data_lists[0])  # noqa
    load5  = list(data_lists[1])  # noqa
    load15 = list(data_lists[2])  # noqa
    min1,  max1,  last1,  avg1  = min_max_last_avg(fmt, load1)  # noqa
    min5,  max5,  last5,  avg5  = min_max_last_avg(fmt, load5)  # noqa
    min15, max15, last15, avg15 = min_max_last_avg(fmt, load15) # noqa
    # @formatter:on

    plt_cfg = {'colors': [lightblue, lightyellow, lightcyan],
               'offset': 2, 'min': 0, 'max': ceil_scaled(max(max1, max5, max15)),
               'format': fmt, 'trim': False,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.main_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_load = plot([load1, load5, load15], plt_cfg)
    plt_load = lstrip_column(plt_load)

    min_len = max(len(min1), len(min5), len(min15))
    max_len = max(len(max1), len(max5), len(max15))
    last_len = max(len(last1), len(last5), len(last15))
    avg_len = max(len(avg1), len(avg5), len(avg15))
    plt_load = plt_load.split('\n')
    plt_load_width = len(plt_load[-1])
    plt_load.insert(0, title_load.center(plt_load_width))
    plt_load += [
        f' {lightblue}1 min avg{reset}'
        f' Cur: {last1:<{last_len}} Avg: {avg1:<{avg_len}}'
        f' Min: {min1:<{min_len}} Max: {max1:<{max_len}}'
        f''.ljust(plt_load_width + COLOR_RESET),
        #
        f' {lightyellow}5 min avg{reset}'
        f' Cur: {last5:<{last_len}} Avg: {avg5:<{avg_len}}'
        f' Min: {min5:<{min_len}} Max: {max5:<{max_len}}'
        f''.ljust(plt_load_width + COLOR_RESET),
        #
        f'{lightcyan}15 min avg{reset}'
        f' Cur: {last15:<{last_len}} Avg: {avg15:<{avg_len}}'
        f' Min: {min15:<{min_len}} Max: {max15:<{max_len}}'
        f''.ljust(plt_load_width + COLOR_RESET),
    ]
    # endregion System load

    # region Memory
    # @formatter:off
    mem_buf   = list(data_lists[3])  # noqa, m_mbuff
    mem_cache = list(data_lists[4])  # noqa, m_mcach
    mem_used  = list(data_lists[5])  # noqa, m_mused
    mem_act   = list(data_lists[6])  # noqa, m_macti
    mem_inact = list(data_lists[7])  # noqa, m_minac
    # @formatter:on

    plt_cfg = {'colors': [lightred, lightgreen, white, lightyellow, green],
               'offset': 2, 'min': 0, 'max': total_mem_bytes, 'trim': False,
               'format': '{:>6} ', 'format_func': lbl_size,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.main_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_mem = plot([mem_used, mem_cache, mem_buf, mem_act, mem_inact], plt_cfg)
    plt_mem = lstrip_column(plt_mem)
    plt_mem = plt_mem.split('\n')
    plt_mem_width = len(plt_mem[-1])
    plt_mem.insert(0, title_mem.center(plt_mem_width))
    plt_mem += [
        ' ' * plt_mem_width,
        #
        f'{lightred}Used{reset}  {lightgreen}Cached{reset}'
        f'  {white}Buffers{reset}  {lightyellow}Active{reset}'
        f'  {green}Inactive{reset}'.center(plt_mem_width + 5 * COLOR_RESET),
    ]
    # endregion Memory

    # region Processes
    # @formatter:off
    proc_total    = list(data_lists[8])   # noqa, nproc
    proc_sleeping = list(data_lists[9])   # noqa, npslp
    proc_running  = list(data_lists[10])  # noqa, nprun
    proc_wait_io  = list(data_lists[11])  # noqa, npwio
    proc_zombie   = list(data_lists[12])  # noqa, npzom
    proc_stopped  = list(data_lists[13])  # noqa, npstp
    proc_paging   = list(data_lists[14])  # noqa, npswp

    _, max_total, last_total,    _ = min_max_last_avg('{:<.0f}', proc_total)     # noqa
    _, _,         last_sleeping, _ = min_max_last_avg('{:<.0f}', proc_sleeping)  # noqa
    _, _,         last_running,  _ = min_max_last_avg('{:<.0f}', proc_running)   # noqa
    _, _,         last_wait_io,  _ = min_max_last_avg('{:<.0f}', proc_wait_io)   # noqa
    _, _,         last_zombie,   _ = min_max_last_avg('{:<.0f}', proc_zombie)    # noqa
    _, _,         last_stopped,  _ = min_max_last_avg('{:<.0f}', proc_stopped)   # noqa
    _, _,         last_paging,   _ = min_max_last_avg('{:<.0f}', proc_paging)    # noqa
    # @formatter:on

    plt_cfg = {'colors': [lightgray, green, lightred, lightmagenta,
                          lightcyan, lightyellow, blue],
               'offset': 2, 'min': 0, 'max': ceil_scaled(max_total),
               'format': '{:>3.0f} ', 'trim': False,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.small_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_proc = plot([proc_total, proc_sleeping, proc_running, proc_wait_io,
                     proc_zombie, proc_stopped, proc_paging],
                    plt_cfg)
    plt_proc = lstrip_column(plt_proc)
    plt_proc = plt_proc.split('\n')
    plt_proc.insert(0, title_proc.center(len(plt_proc[-1])))
    plt_proc += [
        f'',
        f'{green}Sleeping{reset}         Cur: {last_sleeping}',
        f'{lightmagenta}Wait I/O{reset}         Cur: {last_wait_io}',
        f'{lightcyan}Zombie{reset}           Cur: {last_zombie}',
        f'{lightyellow}Stopped{reset}          Cur: {last_stopped}',
        f'{blue}Paging{reset}           Cur: {last_paging}',
        f'{lightred}Running{reset}          Cur: {last_running}',
        f'',
        f'{lightgray}Total Processes{reset}  Cur: {last_total}'
    ]
    # endregion Processes

    # region Entropy
    ent = list(data_lists[15])  # entropy
    min_ent, max_ent, last_ent, _ = min_max_last_avg('{:<.0f}', ent)

    plt_cfg = {'colors': [lightyellow], 'offset': 2,
               'min': floor_scaled(min_ent), 'max': ceil_scaled(max_ent),
               'format': '{:>4.0f} ', 'trim': False,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.small_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_cfg['xrows'] = 1
    plt_ent = plot([ent], plt_cfg)
    plt_ent = lstrip_column(plt_ent)
    plt_ent = plt_ent.split('\n')
    plt_ent.insert(0, title_ent.center(len(plt_ent[-1])))
    plt_ent += [
        f'{lightyellow}Entropy{reset}'
        + f'Cur: {last_ent}'.rjust(len(plt_ent[-1]) - len('Entropy'))
    ]
    # endregion Entropy

    # region Uptime
    upt = list(data_lists[16])  # uptime_days
    min_upt, max_upt, last_upt, _ = min_max_last_avg('{:<.1f}', upt)

    plt_cfg = {'colors': [lightmagenta], 'offset': 2,
               'min': floor_scaled(min_upt), 'max': ceil_scaled(max_upt),
               'format': '{:>4.0f} ', 'trim': False,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.small_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_cfg['xrows'] = 1
    plt_upt = plot([upt], plt_cfg)
    plt_upt = lstrip_column(plt_upt)
    plt_upt = plt_upt.split('\n')
    plt_upt.insert(0, title_upt.center(len(plt_upt[-1])))
    plt_upt += [
        f'{lightmagenta}Uptime{reset}'
        + f'Cur: {last_upt}'.rjust(len(plt_upt[-1]) - len('Uptime'))
    ]
    # endregion Uptime

    # System Load + Processes
    plt_proc += [''] * (len(plt_load) - len(plt_proc))
    plt_load_proc = list(map(lambda t: f'{t[0]}   {t[1]}',
                             zip(plt_load, plt_proc)))
    plt_load_proc = '\n'.join(plt_load_proc)

    # Memory + Entropy + Uptime
    plt_ent_upt = plt_ent + plt_upt
    if len(plt_mem) < len(plt_ent_upt):
        plt_mem += ([' ' * plt_mem_width] * (len(plt_ent_upt) - len([plt_mem])))
    elif len(plt_mem) > len(plt_ent_upt):
        plt_ent_upt += [''] * (len(plt_mem) - len(plt_ent_upt))

    plt_mem_ent_upt = list(map(lambda t: f'{t[0]}   {t[1]}',
                               zip(plt_mem, plt_ent_upt)))
    plt_mem_ent_upt = '\n'.join(plt_mem_ent_upt)

    pics_load = ''
    if params.picUrls:
        pics_load = (
            f'=> {pic_load.name} {title_load}'
            f' ({IMG_FORMAT}, {human_size(pic_load.stat().st_size)})\n'
            f'=> {pic_proc.name} {title_proc}'
            f' ({IMG_FORMAT}, {human_size(pic_proc.stat().st_size)})\n'
        )
    pics_mem = '\n'
    if params.picUrls:
        pics_mem = (
            f'=> {pic_mem.name} {title_mem}'
            f' ({IMG_FORMAT}, {human_size(pic_mem.stat().st_size)})\n'
            f'=> {pic_ent.name} {title_ent}'
            f' ({IMG_FORMAT}, {human_size(pic_ent.stat().st_size)})\n'
            f'=> {pic_upt.name} {title_upt}'
            f' ({IMG_FORMAT}, {human_size(pic_upt.stat().st_size)})\n'
        )
    return (f'{pics_load}'
            f'```{title_load}, {title_proc}\n'
            f'{plt_load_proc}\n'
            f'```\n'
            #
            f'{pics_mem}'
            f'```{title_mem}, {title_ent}\n'
            f'{plt_mem_ent_upt}\n'
            f'```\n')
