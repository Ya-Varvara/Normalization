import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from ui.NewMainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pixmap = QPixmap('ek.png')
    splash = QSplashScreen(pixmap)
    splash.show()

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
