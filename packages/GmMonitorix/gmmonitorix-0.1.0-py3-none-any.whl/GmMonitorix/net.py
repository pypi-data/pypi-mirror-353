from pathlib import Path
from typing import Tuple

import rrdtool
from brasciichart import *

from . import (
    IMG_FORMAT, THEME_BLACK, LBL_UNITS, COLOR_RESET, XAXIS_CFG, GraphSize,
    human_size, lbl_size, min_max_last_avg, conf, lstrip_column, ceil_scaled, Params,
)


def net_cgi(params: Params, db_dir: Path, out_dir: Path, cfg: dict) -> str:
    rrd = str(db_dir / 'net.rrd')
    cfg_net = cfg.get('net')
    ifaces = cfg_net.get('list').split(',')
    descs = list(map(lambda i: cfg_net.get('desc').get(i.strip()).split(','),
                     ifaces))
    text = ''
    for n, iface in enumerate(ifaces):
        text += netX_cgi(params, out_dir, cfg,
                         rrd, n, iface.strip(), descs[n])
    return text


def netX_cgi(params: Params, out_dir: Path, cfg: dict,
             rrd, n, iface, desc) -> str:
    title_net, pic_net = _traffic_pic(params, out_dir, cfg,
                                      rrd, n, iface, desc)
    title_packs, pic_packs = _packets_pic(params, out_dir, cfg,
                                          rrd, n, iface, desc)
    title_errs, pic_errs = _errors_pic(params, out_dir, cfg,
                                       rrd, n, iface, desc)
    #
    xport = [
        # traffic
        f'DEF:in={rrd}:net{n}_bytes_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_bytes_out:AVERAGE',
        'CDEF:allvalues=in,out,+',
        'CDEF:K_in=in,1024,/',
        'CDEF:K_out=out,1024,/',
        'XPORT:in:in',  # 0
        'XPORT:out:out',
        'XPORT:K_in:K_in',
        'XPORT:K_out:K_out',
        # packets
        f'DEF:pin={rrd}:net{n}_packs_in:AVERAGE',
        f'DEF:pout={rrd}:net{n}_packs_out:AVERAGE',
        'CDEF:p_in=pin',
        'CDEF:p_out=pout,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:p_out=pout',
        'XPORT:p_in:p_in',  # 4
        'XPORT:p_out:p_out',
        # errors
        f'DEF:ein={rrd}:net{n}_error_in:AVERAGE',
        f'DEF:eout={rrd}:net{n}_error_out:AVERAGE',
        'CDEF:e_in=ein',
        'CDEF:e_out=eout,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:e_out=eout',
        'XPORT:e_in:e_in',  # 6
        'XPORT:e_out:e_out',
    ]
    # noinspection PyArgumentList
    data = rrdtool.xport('--start', f'-{params.when}',
                         '--step', '60',
                         *xport)
    data_lists = list(zip(*data['data']))
    # region Traffic
    fmt = '{:6.0f} '
    #
    net_in_b = list(data_lists[0])
    net_in_kb = list(data_lists[2])
    min_in, max_in, last_in, avg_in = min_max_last_avg(fmt, net_in_kb)

    net_out_b = list(data_lists[1])
    net_out_kb = list(data_lists[3])
    min_out, max_out, last_out, avg_out = min_max_last_avg(fmt, net_out_kb)

    _, max_in_b, _, _ = min_max_last_avg(fmt, net_in_b)
    _, max_out_b, _, _ = min_max_last_avg(fmt, net_out_b)
    lbl_max = lbl_size(max(int(max_in_b), int(max_out_b))).split(' ')
    lbl_max_val = ceil_scaled(float(lbl_max[0]))
    unit_idx = LBL_UNITS.index(lbl_max[1])
    lbl_max_val = lbl_max_val if not lbl_max[1] \
        else lbl_max_val * (1024 ** unit_idx)

    plt_cfg = {'colors': [lightgreen, lightblue],
               'offset': 2, 'min': 0, 'max': lbl_max_val, 'trim': False,
               'format': '{:>6} ', 'format_func': lbl_size,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.main_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_net = plot([net_in_b, net_out_b], plt_cfg)
    plt_net = lstrip_column(plt_net)

    min_len = max(len(min_in), len(min_out))
    max_len = max(len(max_in), len(max_out))
    last_len = max(len(last_in), len(last_out))
    avg_len = max(len(avg_in), len(avg_out))

    plt_net = plt_net.split('\n')
    plt_net_width = len(plt_net[-1])
    plt_net.insert(0, title_net.center(plt_net_width))

    plt_net += [
        f'{lightgreen}KB/s Input{reset} '
        f'  Cur: {last_in:<{last_len}}  Avg: {avg_in:<{avg_len}}'
        f'  Min: {min_in:<{min_len}}  Max: {max_in:<{max_len}}'
        f''.center(plt_net_width + COLOR_RESET),
        #
        f'{lightblue}KB/s Output{reset}'
        f'  Cur: {last_out:<{last_len}}  Avg: {avg_out:<{avg_len}}'
        f'  Min: {min_out:<{min_len}}  Max: {max_out:<{max_len}}'
        f''.center(plt_net_width + COLOR_RESET),
    ]
    # endregion Traffic

    # region Packets
    packs_in = list(data_lists[4])  # p_in
    packs_out = list(data_lists[5])  # p_out
    _, max_p_in, _, _ = min_max_last_avg('{:<.0f}', packs_in)
    _, max_p_out, _, _ = min_max_last_avg('{:<.0f}', packs_out)

    plt_cfg = {'colors': [lightgreen, lightblue], 'offset': 2,
               'min': 0, 'max': ceil_scaled(max(int(max_p_in or '0'),
                                                int(max_p_out or '0'))),
               'format': '{:>5.0f} ', 'trim': False,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.small_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_cfg['xrows'] = 1
    plt_packs = plot([packs_in, packs_out], plt_cfg)
    plt_packs = lstrip_column(plt_packs)
    plt_packs = plt_packs.split('\n')
    plt_packs.insert(0, title_packs.center(len(plt_packs[-1])))
    plt_packs += [
        f'{lightgreen}Input{reset}'
        + f'{lightblue}Output{reset}'.rjust(len(plt_packs[-1])
                                            - len('Input') + COLOR_RESET),
    ]
    # endregion Packets

    # region Errors
    errs_in = list(data_lists[6])  # p_in
    errs_out = list(data_lists[7])  # p_out
    _, max_e_in, _, _ = min_max_last_avg('{:<.0f}', errs_in)
    _, max_e_out, _, _ = min_max_last_avg('{:<.0f}', errs_out)

    plt_cfg = {'colors': [lightgreen, lightblue], 'offset': 2,
               'min': 0, 'max': ceil_scaled(max(int(max_e_in or '1') or 0.9,
                                                int(max_e_out or '1') or 0.9)),
               'format': '{:>5.1f} ', 'trim': False,
               'xfrom': data['meta']['start'],
               'xto': data['meta']['end']}
    plt_cfg = conf.merge(GraphSize.small_ascii, plt_cfg)
    plt_cfg = conf.merge(XAXIS_CFG.get(params.twhen, {}), plt_cfg)
    plt_cfg['xrows'] = 1
    plt_errs = plot([errs_in, errs_out], plt_cfg)
    plt_errs = lstrip_column(plt_errs)
    plt_errs = plt_errs.split('\n')
    plt_errs.insert(0, title_errs.center(len(plt_errs[-1])))
    plt_errs += [
        f'{lightgreen}Input{reset}'
        + f'{lightblue}Output{reset}'.rjust(len(plt_errs[-1])
                                            - len('Input') + COLOR_RESET),
    ]
    # endregion Packets

    plt_packs_errs = plt_packs + plt_errs
    if len(plt_net) < len(plt_packs_errs):
        plt_net += ([' ' * plt_net_width] * (len(plt_packs_errs) - len([plt_net])))
    elif len(plt_net) > len(plt_packs_errs):
        plt_packs_errs += [''] * (len(plt_net) - len(plt_packs_errs))

    plt_net_packs_errs = list(map(lambda t: f'{t[0]}   {t[1]}',
                                  zip(plt_net, plt_packs_errs)))
    plt_net_packs_errs = '\n'.join(plt_net_packs_errs)

    pics_net = '\n'
    if params.picUrls:
        pics_net = (
            f'=> {pic_net.name} {title_net}'
            f' ({IMG_FORMAT}, {human_size(pic_net.stat().st_size)})\n'
            f'=> {pic_packs.name} {title_packs}'
            f' ({IMG_FORMAT}, {human_size(pic_packs.stat().st_size)})\n'
            f'=> {pic_errs.name} {title_errs}'
            f' ({IMG_FORMAT}, {human_size(pic_errs.stat().st_size)})\n'
        )

    return (f'{pics_net}'
            f'```{title_net}, {title_packs}, {title_errs}\n'
            f'{plt_net_packs_errs}\n'
            f'```\n')


def _traffic_pic(params: Params, out_dir: Path, cfg: dict,
                 rrd, n, iface, desc) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_net1")} {desc[0]} ({iface})'
    if not params.picUrls:
        return title, Path('no-image')
    # TODO: Support net traffic bit/s
    graphv = [
        f'DEF:in={rrd}:net{n}_bytes_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_bytes_out:AVERAGE',
        'CDEF:allvalues=in,out,+',
        'CDEF:B_in=in',
        'CDEF:B_out=out',
        'CDEF:K_in=B_in,1024,/',
        'CDEF:K_out=B_out,1024,/',
        'AREA:B_in#44EE44:KB/s Input',
        'GPRINT:K_in:LAST:     Current\\: %5.0lf',
        'GPRINT:K_in:AVERAGE: Average\\: %5.0lf',
        'GPRINT:K_in:MIN:    Min\\: %5.0lf',
        'GPRINT:K_in:MAX:    Max\\: %5.0lf\\n',
        'AREA:B_out#4444EE:KB/s Output',
        'GPRINT:K_out:LAST:    Current\\: %5.0lf',
        'GPRINT:K_out:AVERAGE: Average\\: %5.0lf',
        'GPRINT:K_out:MIN:    Min\\: %5.0lf',
        'GPRINT:K_out:MAX:    Max\\: %5.0lf\\n',
        'AREA:B_out#4444EE:',
        'AREA:B_in#44EE44:',
        'LINE1:B_out#0000EE',
        'LINE1:B_in#00EE00',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'net_traffic_{n}.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}  {params.when}',
                   '--vertical-label=bytes/s',
                   *GraphSize.main,
                   *graphv,
                   *THEME_BLACK)
    return title, pic


def _packets_pic(params: Params, out_dir: Path, cfg: dict,
                 rrd: str, n, iface, desc) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_net2")} {desc[0]} ({iface})'
    if not params.picUrls:
        return title, Path('no-image')
    graphv = [
        f'DEF:in={rrd}:net{n}_packs_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_packs_out:AVERAGE',
        'CDEF:p_in=in',
        'CDEF:p_out=out,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:p_out=out',
        'AREA:p_in#44EE44:Input',
        'AREA:p_out#4444EE:Output',
        'AREA:p_out#4444EE:',
        'AREA:p_in#44EE44:',
        'LINE1:p_out#0000EE',
        'LINE1:p_in#00EE00',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'net_packs_{n}.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={cfg.get("graphs").get("_net2")}'
                   f'  ({params.when})\n{desc[0]} ({iface})',
                   '--vertical-label=Packets/s',
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return title, pic


def _errors_pic(params: Params, out_dir: Path, cfg: dict,
                rrd: str, n, iface, desc) -> Tuple[str, Path]:
    title = f'{cfg.get("graphs").get("_net3")} {desc[0]} ({iface})'
    if not params.picUrls:
        return title, Path('no-image')
    graphv = [
        f'DEF:in={rrd}:net{n}_error_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_error_out:AVERAGE',
        'CDEF:e_in=in',
        'CDEF:e_out=out,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:e_out=out',
        'AREA:e_in#44EE44:Input',
        'AREA:e_out#4444EE:Output',
        'AREA:e_out#4444EE:',
        'AREA:e_in#44EE44:',
        'LINE1:e_out#0000EE',
        'LINE1:e_in#00EE00',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'net_errs_{n}.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={cfg.get("graphs").get("_net3")}'
                   f'  ({params.when})\n{desc[0]} ({iface})',
                   '--vertical-label=Errors/s',
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return title, pic
