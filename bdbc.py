"""
Listen to windows focus changes, and close Dropbox Preference window
when opened.
"""

def only_one():
    from tendo import singleton
    me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

def kill_window():
    from pywinauto import Application, findwindows
    try:
        for handle in findwindows.find_windows(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
            app = Application.connect(Application(), handle=handle)
            for window in app.windows_(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
                window.Close()
    except findwindows.WindowNotFoundError:
        pass

def foreground_window_hook():
    import sys
    import time
    import ctypes
    import ctypes.wintypes

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
        print('SetWinEventHook failed')
        sys.exit(1)

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    user32.UnhookWinEvent(hook)
    ole32.CoUninitialize()

only_one()
foreground_window_hook()
