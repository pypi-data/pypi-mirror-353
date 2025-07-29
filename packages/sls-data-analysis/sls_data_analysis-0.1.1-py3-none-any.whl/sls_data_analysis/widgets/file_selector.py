import os
import sys
import h5py
import json
import traceback

from qtpy.QtCore import (
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    Signal,
    Slot,
)

from qtpy.QtGui import (
    QIcon,
)

from qtpy.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,

)

from ..modules.h5_parser import get_scan_data
from ..modules.fitter import generate_fit_array

class WorkerSignals(QObject):
    """Signals from a running worker thread.

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc())

    result
        object data returned from processing, anything

    progress
        float indicating % progress
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(float)


class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class FileSelectorDock(QDockWidget):
    def __init__(self, data_m, data_r, results_dock, parent=None):
        super().__init__()
        self.setWindowTitle("File selector")
        self.setObjectName("file_selector_dock")
        self.setMinimumWidth(250)

        file_selector_widget = QWidget()

        self.file_selector_groupbox_m = FileSelectorGroupBox(title="Measurement file", data=data_m, results_dock=results_dock)
        self.file_selector_groupbox_r = FileSelectorGroupBox(title="Reference file", data=data_r, results_dock=results_dock)

        file_selector_widget_layout = QVBoxLayout()
        file_selector_widget_layout.addWidget(self.file_selector_groupbox_m)
        file_selector_widget_layout.addWidget(self.file_selector_groupbox_r)
        file_selector_widget_layout.addStretch()

        file_selector_widget.setLayout(file_selector_widget_layout)

        self.setWidget(file_selector_widget)


class FileSelectorGroupBox(QGroupBox):
    """
    Groupbox widget displaying the "open file" button, the name of the hdf5 file, a combobox in order
    to select the scan number within the provided file and the information of the selected scan.

    Attributes
    ----------
    title : string
        The title of the groupbox. It should either be "Measurement..." or "Reference...".
    """
    def __init__(self, title, data, results_dock):
        super().__init__()
        
        self._title = title
        self.setTitle(self._title)
        self.set_groupbox_layout()

        self.file = None
        self.file_name = None
        self.scan_data = None

        self.data = data
        self.results_dock = results_dock

        self.open_button.clicked.connect(self.handle_open_file)
        self.scan_combobox.currentIndexChanged.connect(self.handle_scan_selection_changed)
        self.fit_button.clicked.connect(self.handle_fit_clicked)

        print("FileSelectorGB initialized:", title)

    def set_groupbox_layout(self):
        """
        Define the layouts contained in the groupbox in order to display all elements.
        """
        # Layout for scan number selection info (1st element is "Scan", 2nd element is a Combo Box)
        scan_layout = QHBoxLayout()

        scan_label = QLabel("Scan")
        self.scan_combobox = QComboBox()

        scan_layout.addWidget(scan_label)
        scan_layout.addWidget(self.scan_combobox)
        scan_layout.addStretch()

        # Layout for file_name + scan number selection layout
        file_name_layout = QVBoxLayout()

        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        file_name_layout.addWidget(self.file_name_label)
        file_name_layout.addLayout(scan_layout)

        # Layout for open button + file_name_layout 
        open_button_layout = QHBoxLayout()

        self.open_button = QPushButton(" Open")
        self.open_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.open_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        open_button_layout.addWidget(self.open_button)
        open_button_layout.addLayout(file_name_layout)

        ### Scan info widget
        self.scan_info_widget = QWidget()  # Set scan info as a widget to be able to show/hide it later
        self.scan_info_widget.setVisible(False)
        # Layout
        scan_info_layout = QVBoxLayout()
        
        self.scan_info_widget.setLayout(scan_info_layout)
        # self.scan_info_widget.setVisible(False)

        scan_info_form = QFormLayout()  # scan_info_form is a layout

        scan_info_layout.addWidget(QLabel("<b>Scan information<\b>"))
        scan_info_layout.addLayout(scan_info_form)

        # Define a dictionnary to contain all scan info (used for updating values later)
        self.scan_info = {
            "date": QLabel(),
            "author": QLabel(),
            "description": QLabel(),
            "shape": QLabel(),
            "fit status": QLabel(),
        }

        self.scan_info['description'].setWordWrap(True)

        # Go through all QLabels to make them selectable by user
        for key, qlabel in self.scan_info.items():
            qlabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Add rows and elements to the form layout
        scan_info_form.addRow(QLabel("Date:"), self.scan_info["date"])
        scan_info_form.addRow(QLabel("Author:"), self.scan_info["author"])
        scan_info_form.addRow(QLabel("Description:"), self.scan_info["description"])
        scan_info_form.addRow(QLabel("Shape:"), self.scan_info["shape"])
        
        # Fit info
        fit_info_layout = QHBoxLayout()

        self.fit_button = QPushButton("Fit")
        fit_info_layout.addWidget(self.scan_info["fit status"])
        fit_info_layout.addWidget(self.fit_button)
        fit_info_layout.addStretch()

        scan_info_form.addRow(QLabel("Fit status:"), fit_info_layout)

        # Fit progress bar
        self.fit_progress_bar = QProgressBar()
        scan_info_form.addRow(None, self.fit_progress_bar)

        # self.fit_progress_bar.setFixedWidth(200)
        self.fit_progress_bar.setVisible(False)

        # Layout for groupbox with open_button_layout + scan info
        groupbox_layout = QVBoxLayout()

        groupbox_layout.addLayout(open_button_layout)
        groupbox_layout.addWidget(self.scan_info_widget)

        self.setLayout(groupbox_layout)


    def handle_open_file(self):
        """
        Triggered when open button is clicked. It displays a QFileDialog widget for retrieving
        the path of the selected hdf5 file.
        """
        if self.file is not None:
            self.file.close()

        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file with " + self.title().lower() + " scan",
            "",
            "HDF5 Files (*.hdf *.h5 *.hdf5);; All Files (*.*)",
            options=options,
        )

        if self.file_path:
            self.file_name = os.path.basename(self.file_path)
            self.open_file()


    def open_file(self):
        """Count number of available scans and add them in the scan selection combobox."""
        self.file = h5py.File(self.file_path, 'r')

        self.file_name_label.setText(self.file_name)

        self.scan_combobox.blockSignals(True)
        self.scan_combobox.clear()
        self.scan_combobox.blockSignals(False)
        
        # scan_count = get_scan_count(file=self.file)

        self.scan_count = len([i for i in self.file["RawData"] if "Scan" in i])  # Count the number of scans in the file

        # add scans into combobox
        if self.scan_count > 0:
            for scan_nb in range(self.scan_count):
                self.scan_combobox.addItem(str(scan_nb))
        
        else:
            print("No scan found")
            self.scan_info_widget.setVisible(False)
        
        self.file.close()

    def handle_scan_selection_changed(self, index):
        """
        Display scan information in the groupbox when a scan is selected.

        Parameters
        ----------
        index : int
            Index of scan, 0 is for Scan000, 1 is for Scan001...
        """
        self.scan_index = index

        self.scan_info_widget.setVisible(True)

        self.file = h5py.File(self.file_path, 'r')

        selected_scan = self.file[f"RawData/Scan{self.scan_index:03}"]  # 1:03 returns 001

        scan_info, self.scan_data = get_scan_data(selected_scan)

        self.scan_info["date"].setText(scan_info["date"])
        self.scan_info["author"].setText(scan_info["author"])
        self.scan_info["description"].setText(scan_info["description"])
        self.scan_info["shape"].setText(scan_info["shape"])
        self.scan_info["fit status"].setText(scan_info["fit_status"])

        self.data.update_data(**self.scan_data)
        self.data.update_plots()

        self.results_dock.update_data(m_or_r=self._title, info=scan_info, data=self.scan_data)
        # self.results_dock.update_plots_tab_theta(wl_index=0)

        self.file.close()


    def handle_fit_clicked(self):

        self.file = h5py.File(self.file_path, 'r')

        selected_scan = self.file[f"RawData/Scan{self.scan_index:03}"]  # 1:03 returns 001

        _, scan_data = get_scan_data(selected_scan)

        # Check if scan has already been fitted and if user wishes to refit
        if "Detector000/Data1D/CH00/Fit00" in selected_scan:
            already_fitted_box = QMessageBox()
            already_fitted_box.setIcon(QMessageBox.Warning)
            already_fitted_box.setWindowTitle("Confirmation")
            already_fitted_box.setText(f"Data has already been fitted.\n\nDo you want to fit again?")
            already_fitted_box.setStandardButtons(QMessageBox.Yes | QMessageBox.StandardButton.Cancel)
            already_fitted_box.setDefaultButton(QMessageBox.StandardButton.Cancel)

            already_fitted_ret = already_fitted_box.exec()

            if already_fitted_ret == QMessageBox.StandardButton.Cancel:
                return

        self.threadpool = QThreadPool()
        thread_count = self.threadpool.maxThreadCount()-2

        # print(f"Multithreading with maximum {thread_count} threads")

        # Ask if user wants to fit (because it can take a bit of time)
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle("Confirmation")
        message_box.setText(f"Fitting data can be long (max 30 min).\nYou will have maximum {thread_count} threads available.\n\nDo you want to continue?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.StandardButton.Cancel)
        message_box.setDefaultButton(QMessageBox.StandardButton.Cancel)

        ret = message_box.exec()

        if ret == QMessageBox.Yes:
            self.open_button.setDisabled(True)
            self.scan_combobox.setDisabled(True)
            self.fit_button.setDisabled(True)
            self.fit_progress_bar.setVisible(True)
            self.fit_progress_bar.setValue(0)
            self.scan_info["fit status"].setText("In progress")
            
            # Pass the function to execute
            worker = Worker(generate_fit_array, scan_data)  # Any other args, kwargs are passed to the run function

            worker.signals.result.connect(self.write_fit_to_h5)
            worker.signals.finished.connect(self.fit_complete)
            worker.signals.progress.connect(self.progress_fn)

            # Execute
            self.threadpool.start(worker)


    def write_fit_to_h5(self, fit_array):

        # Close and reopen file in "append" mode
        self.file.close()
        self.file = h5py.File(self.file_path, 'a')

        selected_scan = self.file[f"RawData/Scan{self.scan_index:03}"]  # 1:03 returns 001

        data_group = selected_scan["Detector000/Data1D/CH00"]

        if "Fit00" in data_group:
            del data_group["Fit00"]
        
        data_group.create_dataset("Fit00", data=fit_array)

        self.file.close()

        self.handle_scan_selection_changed(self.scan_index)
    
    def progress_fn(self, n):
        percentage = n*100/(len(self.scan_data["theta"])-1)
        self.fit_progress_bar.setValue(int(percentage))
        print(f"{percentage:.1f}% done")

    def fit_complete(self):
        self.file.close()
        self.open_button.setEnabled(True)
        self.scan_combobox.setEnabled(True)
        self.fit_button.setEnabled(True)
        self.fit_progress_bar.setVisible(False)
        
        print(self.title(), f"scan n°{self.scan_index}", "has been susccesfully fitted!")






    # def print_fit_progress(self, n):
    #     print(f"{n:.1f}% done")





