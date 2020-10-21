# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import os
import subprocess
from datetime import date,timedelta

from aion.microservice import main_decorator, Options
from aion.kanban import Kanban
from aion.logger import lprint, initialize_logger

SERVICE_NAME = os.environ.get("SERVICE", "transfer-mongo-kanban-backup")
initialize_logger(SERVICE_NAME)

@main_decorator(SERVICE_NAME)
def main_without_kanban(opt: Options):
    lprint("start main_without_kanban()")
    # get cache kanban
    conn = opt.get_conn()
    num = opt.get_number()
    #kanban: Kanban = conn.set_kanban(SERVICE_NAME, num)
    kanban = conn.get_one_kanban(SERVICE_NAME, num)
    device_name = os.environ["TRANSFER_DEVICE"]

    ######### main function #############

    yesterday = date.today() - timedelta(days=1)
    file_name = yesterday.strftime('%Y%m%d') + '.json'
    backup_dir = f'/var/lib/aion/Data/{SERVICE_NAME}_{num}/output/'
    backup_file = backup_dir + file_name

    os.makedirs(backup_dir, exist_ok=True)
    subprocess.run(['mongoexport', '-h', 'mongo', '--db', 'AionCore', 
        '--collection', 'kanban', '-o', backup_file, 
        '--query', r'{"finishAt": /^'+yesterday.strftime('%Y-%m-%d')+'/}'])

    # output after kanban
    conn.output_kanban(
        result=True,
        connection_key="default",
        file_list=[backup_file],
        metadata={"file_name": file_name},
        device_name=device_name,
    )

