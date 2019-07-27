# -*- coding: utf-8 -*-

import os
import logging


loggers = {}


def init_parser(config_parser):
    dir_path = config_parser.dir_path()
    cfg = config_parser.parse_config()
    return dir_path


def set_logging(logname, config_parser, level=logging.DEBUG):
    global loggers

    if loggers.get(logname):
        return loggers.get(logname)
    else:
        log_dir = getattr(init_parser(config_parser), 'log')
        log_format = '[%(asctime)s]' \
                     '[%(processName)s]' \
                     '%(message)s'
        formatter = logging.Formatter(log_format)

        log_handler = logging.FileHandler(os.path.join(log_dir, '%s.log' % logname).format(log_dir), mode='a')
        log_handler.setFormatter(formatter)

        log = logging.getLogger(logname)
        log.setLevel(level)
        log.addHandler(log_handler)
        loggers.update(dict(name=log))

        return log
