from pywinauto import Application, findwindows
from tendo import singleton

me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

while True:
    try:
        for handle in findwindows.find_windows(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
            app = Application.connect(Application(), handle=handle)
            for window in app.windows_(title_re="(Dropbox Preferences|Preferencias de Dropbox)"):
                window.Close()
    except findwindows.WindowNotFoundError:
        pass
