from pywinauto import application
from pywinauto import timings

import time
import os
import time



import sys
def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)

    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    # sys.exit(1)


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


app = application.Application()
app.start(r"C:\KiwoomFlash3\Bin\NKMiniStarter.exe", wait_for_idle=False)
dlg = app.top_window()
#
pass_ctrl = dlg.Edit2
pass_ctrl.set_focus()
pass_ctrl.type_keys('han1984')


time.sleep(0.1)
pass_ctrl = dlg.Edit3
pass_ctrl.set_focus()
pass_ctrl.type_keys('hanhonghee1984{%}')


time.sleep(0.1)
btn_ctrl = dlg.Button0
btn_ctrl.click()



time.sleep(50)
os.system("taskkill /im nkmini.exe")