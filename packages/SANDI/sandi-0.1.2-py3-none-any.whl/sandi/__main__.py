from smartheattable.application import MainWindow

print(f"executing {__file__}")
from smartheattable.application import *

app = QApplication(sys.argv)
app.setApplicationName('SANDI')
window = MainWindow()
window.setWindowTitle(app.applicationName())
window.show()
app.exec()