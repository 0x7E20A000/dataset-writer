import sys
from PyQt5.QtWidgets import QApplication
from src.gui import FineTuningGUI

def main():
    app = QApplication(sys.argv)
    ex = FineTuningGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
