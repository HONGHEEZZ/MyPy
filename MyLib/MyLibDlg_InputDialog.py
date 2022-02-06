
#MyLibDlg_InputDialog.py
from PyQt5.QtWidgets import QInputDialog

def f_make_QInputDialog(self, my_title, my_label, echo=None, my_text = '', x= 800, y=100):
    rtn = None

    dlg = QInputDialog(self)
    dlg.setInputMode(QInputDialog.TextInput)

    dlg.setWindowTitle(my_title)
    dlg.setLabelText(my_label)
    dlg.setTextValue(my_text)
    dlg.resize(x, y)
    ok = dlg.exec_()
    text = dlg.textValue()

    return text, ok