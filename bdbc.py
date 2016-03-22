"""
Listen to windows focus changes, and close Dropbox Preference window
when opened.
"""
import logging
import ctypes
from sys import exit
from pywinauto import Application, findwindows
from fasteners import InterProcessLock
from tempfile import gettempdir

logger = logging.getLogger()
ch = logging.FileHandler(gettempdir() + '/bdbc.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def kill_window():
    try:
        for handle in findwindows.find_windows(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
            app = Application.connect(Application(), handle=handle)
            for window in app.windows_(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
                logger.warning('Configuration window for Dropbox detected')
                window.Close()
                logger.warning('Configuration window for Dropbox closed')
    except findwindows.WindowNotFoundError:
        pass

def foreground_window_hook():

    EVENT_SYSTEM_FOREGROUND = 0x0003
    WINEVENT_OUTOFCONTEXT = 0x0000

    user32 = ctypes.windll.user32
    ole32 = ctypes.windll.ole32

    ole32.CoInitialize(0)

    WinEventProcType = ctypes.WINFUNCTYPE(
        None,
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.HWND,
        ctypes.wintypes.LONG,
        ctypes.wintypes.LONG,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD
    )

    def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        length = user32.GetWindowTextLengthA(hwnd)
        buff = ctypes.create_string_buffer(length + 1)
        user32.GetWindowTextA(hwnd, buff, length + 1)
        if b"Dropbox" in buff.value:
            logger.info('Dropbox window detected')
            kill_window()

    WinEventProc = WinEventProcType(callback)

    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
    hook = user32.SetWinEventHook(
        EVENT_SYSTEM_FOREGROUND,
        EVENT_SYSTEM_FOREGROUND,
        0,
        WinEventProc,
        0,
        0,
        WINEVENT_OUTOFCONTEXT
    )
    if hook == 0:
        exit(1)

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    user32.UnhookWinEvent(hook)
    ole32.CoUninitialize()

logger.info('Acquiring lock')
lock = InterProcessLock(gettempdir() + '/bdbc_lock_file')
gotten = lock.acquire(timeout=10)

if gotten:
    logger.info('Lock acquired')
    foreground_window_hook()
else:
    logger.info('Lock failed')
