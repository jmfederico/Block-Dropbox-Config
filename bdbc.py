from pywinauto import Application, findwindows

while True:
    try:
        for handle in findwindows.find_windows(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
            app = Application.connect(Application(), handle=handle)
            for window in app.windows_(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
                window.Close()
    except findwindows.WindowNotFoundError:
        pass
