#!/usr/bin/env python3
# Code snippets I load into REPL while testing and figuring out stuff

import os
import sys
from pprint import pprint as pp
import time

import psutil
import win32gui
import win32process

PROCS = {
    'crunchyroll': 'CR.WinApp.exe',
    'funimation': 'Funimation.exe',
    'netflix': 'WWAHost.exe',
}


def get_process(name: str) -> psutil.Process:
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            return proc


def get_procs(name: str) -> psutil.Process:
    procs = []
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            procs.append(proc)
    return procs

dsps = get_procs("Discord.exe")
# p = get_process("Discord.exe")


