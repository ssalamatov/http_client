# -*- coding: utf-8 -*-

import io
import csv


def import_from_csv(fields, data):
    data = data.strip('\n')
    reader = csv.DictReader(io.StringIO(data),
                            fieldnames=fields, delimiter=';')
    reader.__next__()
    return reader
