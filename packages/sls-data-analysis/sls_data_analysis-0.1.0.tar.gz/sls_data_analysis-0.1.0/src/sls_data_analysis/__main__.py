"""
File containg the main application.
"""

import argparse
import os
import sys

# import traceback
import qtpy
from qtpy.QtCore import (
    Qt,
    QDir,
)
from qtpy.QtGui import (
    QIcon,
)
from qtpy.QtWidgets import (
    QApplication,
)

os.environ["PYQTGRAPH_QT_LIB"] = qtpy.API_NAME

from . import __version__
from .mainwindow import MainWindow

basedir = os.path.dirname(__file__)
resource_path = os.path.join(basedir, "resources", "images")
QDir.addSearchPath("icons", resource_path)

def main():

    """Define the main application entry point (cli)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-f", "--file", type=str, required=False)
    args = parser.parse_args()

    if qtpy.API_NAME in ["PyQt5", "PySide2"]:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setOrganizationName("sls-data-analysis")
    app.setApplicationName("SLS Data Analysis")
    app.setWindowIcon(QIcon("icons:LOGO_CNRS_BLEU.png"))

    window = MainWindow(app)
    window.show()

    # # Open a file if supplied on command line
    # if args.file:
    #     window.open_file(args.file)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()