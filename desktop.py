import ctypes
from ctypes import wintypes

user32=ctypes.windll.user32

def _find_workerw():
    progman=user32.FindWindowW("Progman",None)
    user32.SendMessageTimeoutW(
        progman,
        0x052C,
        0,
        0,
        0,
        1000,
        None
    )

    workerw=wintypes.HWND()

    def enum_proc(hwnd,lparam):
        shell=user32.FindWindowExW(hwnd,None,"SHELLDLL_DefView",None)
        if shell:
            nonlocal workerw
            workerw=user32.FindWindowExW(None,hwnd,"WorkerW",None)
        return True

    EnumProc=ctypes.WINFUNCTYPE(ctypes.c_bool,wintypes.HWND,wintypes.LPARAM)

    user32.EnumWindows(EnumProc(enum_proc),0)

    return workerw

def attach(hwnd):
    worker=_find_workerw()
    if worker:
        user32.SetParent(hwnd,worker)