import os
import h5py
import json
import numpy as np

import pyqtgraph as pg

from qtpy.QtCore import (
    Qt,
)
from qtpy.QtGui import (
    QIcon,
    QBrush,
)
from qtpy.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..modules.fitter import fit_count_phi


class CustomMenu(pg.ViewBox):
    def __init__(self, parent=None):
        super().__init__()

        self.myMenuEdit() 

    def myMenuEdit(self):
        """Custom viewbox to display a simplified menu when right-clicking a plot.
        We get rid of the following menu options:
            - View all: Does a similar thing (thus redundant) as clicking on the small "A" at the bottom left
                        of a plotWidget (for resetting viewbox position)
            - Mouse Mode: Never used the "1 button" option, the "3 button" option is great in this case.
        """
        # Hide Default Actions
        MenusToHide = ["View All", "Mouse Mode", "Plot Options"] #Names of menus to hide
        w = self.menu.actions()
        for m in w:
            for mhs in MenusToHide:
                if (m.text().startswith(mhs)):
                    m.setVisible(False)
                    break


class ResultsDock(QDockWidget):
    def __init__(self):
        super().__init__()
        print("Initializing results plotter dock")

        # self.data_m = data_m.data
        # self.data_r = data_r.data

        self.theta = None
        self.ana = None
        self.phi = None
        self.wl = None
        self.data_m = None
        self.data_r = None
        self.fit_m = None
        self.fit_r = None

        self.setWindowTitle("Results")
        self.setObjectName("results_dock")
        self.setMinimumWidth(300)

        self.results_plots_theta_initialized = False
        self.results_plots_wl_initialized = False

        # Tabs
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.South)

        ## Tab 1 →  Results vs Theta + wavelength slider
        tab_theta_widget = QWidget()
        tab_theta_layout = QVBoxLayout()

        ### Graphs displaying results vs theta
        glw_theta = self.glw_theta()  # glw → GraphicsLayoutWidget
        
        ### Wavelength slider
        wl_slider_layout = QHBoxLayout()

        wl_slider_label = QLabel("Wavelength")
        self.wl_slider = QSlider(Qt.Orientation.Horizontal)
        self.wl_slider.setFixedWidth(150)
        self.wl_slider.setDisabled(True)
        self.wl_value_label = QLabel("")

        wl_slider_layout.addWidget(wl_slider_label)
        wl_slider_layout.addWidget(self.wl_slider)
        wl_slider_layout.addWidget(self.wl_value_label)
        wl_slider_layout.addStretch()


        tab_theta_layout.addWidget(glw_theta)
        tab_theta_layout.addLayout(wl_slider_layout)

        tab_theta_widget.setLayout(tab_theta_layout)

        ## Tab 2 → Results vs wavelength + goniometer slider
        tab_wl_widget = QWidget()
        tab_wl_layout = QVBoxLayout()
        
        ### Results vs wavelength
        glw_wl = self.glw_wl()

        ### Gonio angle slider
        gonio_slider_layout = QHBoxLayout()

        gonio_slider_label = QLabel("Goniometer angle")
        self.gonio_slider = QSlider(Qt.Orientation.Horizontal)
        self.gonio_slider.setFixedWidth(150)
        self.gonio_slider.setDisabled(True)
        self.gonio_value_label = QLabel("")

        gonio_slider_layout.addWidget(gonio_slider_label)
        gonio_slider_layout.addWidget(self.gonio_slider)
        gonio_slider_layout.addWidget(self.gonio_value_label)
        gonio_slider_layout.addStretch()

        tab_wl_layout.addWidget(glw_wl)
        tab_wl_layout.addLayout(gonio_slider_layout)

        tab_wl_widget.setLayout(tab_wl_layout)


        tab_widget.addTab(tab_theta_widget, "VV && VH vs θ")
        tab_widget.addTab(tab_wl_widget, "VV && VH vs λ")

        self.setWidget(tab_widget)

        # Connect signals to slots
        self.wl_slider.valueChanged.connect(self.update_plots_tab_theta)
        self.gonio_slider.valueChanged.connect(self.update_plots_tab_wl)
    
    def glw_theta(self):
        glw = pg.GraphicsLayoutWidget()
        glw.setBackground('w')

        # Initialize window of results (VV, VH, VH/VV, VH+VV)
        self.plot_item_vv_theta = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vv_theta.addLegend()
        self.plot_item_vv_theta.setDefaultPadding(0.0)
        self.plot_item_vv_theta.setLabel(axis='bottom', text="θ", units="°")
        self.plot_item_vv_theta.setLabel(axis='left', text="VV", units="")

        glw.nextRow()

        self.plot_item_vh_theta = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vh_theta.addLegend()
        self.plot_item_vh_theta.setDefaultPadding(0.0)
        self.plot_item_vh_theta.setLabel(axis='bottom', text="θ", units="°")
        self.plot_item_vh_theta.setLabel(axis='left', text="VH", units="")

        glw.nextRow()

        self.plot_item_vh_vv_theta = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vh_vv_theta.addLegend()
        self.plot_item_vh_vv_theta.setDefaultPadding(0.0)
        self.plot_item_vh_vv_theta.setLabel(axis='bottom', text="θ", units="°")
        self.plot_item_vh_vv_theta.setLabel(axis='left', text="VH/VV", units="")

        glw.nextRow()

        self.plot_item_vh_p_vv_theta = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vh_p_vv_theta.addLegend()
        self.plot_item_vh_p_vv_theta.setDefaultPadding(0.0)
        self.plot_item_vh_p_vv_theta.setLabel(axis='bottom', text="θ", units="°")
        self.plot_item_vh_p_vv_theta.setLabel(axis='left', text="VH + VV", units="")

        return glw
    
    def glw_wl(self):
        glw = pg.GraphicsLayoutWidget()
        glw.setBackground('w')

        # Initialize window of results (VV, VH, VH/VV, VH+VV)
        self.plot_item_vv_wl = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vv_wl.addLegend()
        self.plot_item_vv_wl.setDefaultPadding(0.0)
        self.plot_item_vv_wl.setLabel(axis='bottom', text="Wavelength", units="m")
        self.plot_item_vv_wl.setLabel(axis='left', text="VV", units="")

        glw.nextRow()

        self.plot_item_vh_wl = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vh_wl.addLegend()
        self.plot_item_vh_wl.setDefaultPadding(0.0)
        self.plot_item_vh_wl.setLabel(axis='bottom', text="Wavelength", units="m")
        self.plot_item_vh_wl.setLabel(axis='left', text="VH", units="")

        glw.nextRow()

        self.plot_item_vh_vv_wl = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vh_vv_wl.addLegend()
        self.plot_item_vh_vv_wl.setDefaultPadding(0.0)
        self.plot_item_vh_vv_wl.setLabel(axis='bottom', text="Wavelength", units="m")
        self.plot_item_vh_vv_wl.setLabel(axis='left', text="VH/VV", units="")

        glw.nextRow()

        self.plot_item_vh_p_vv_wl = glw.addPlot(viewBox=CustomMenu())
        self.plot_item_vh_p_vv_wl.addLegend()
        self.plot_item_vh_p_vv_wl.setDefaultPadding(0.0)
        self.plot_item_vh_p_vv_wl.setLabel(axis='bottom', text="Wavelength", units="m")
        self.plot_item_vh_p_vv_wl.setLabel(axis='left', text="VH + VV", units="")

        return glw

    def update_data(self, m_or_r, info, data):

        self.theta = data["theta"]
        self.ana = data["ana"]
        self.phi = data["phi"]
        self.wl = data["wl"]

        self.fit_status = info["fit_status"]

        self.wl_slider.setMinimum(0)
        self.wl_slider.setMaximum(len(self.wl) - 1)

        self.gonio_slider.setMinimum(0)
        self.gonio_slider.setMaximum(len(self.theta) - 1)

        if m_or_r == "Measurement file":  # Check title of file selector to determine which data to update (m or r)
            if self.fit_status == "Done":
                self.fit_m = data["fit"]
                self.b_vv_m = self.fit_m[:, 0, :, 1]  # 0 is VV
                self.b_vh_m = self.fit_m[:, 1, :, 1]  # 1 is VH

            else:
                self.fit_m = None
                self.b_vv_m = np.zeros(len(self.theta))
                self.b_vh_m = np.zeros(len(self.theta))

        if m_or_r == "Reference file":
            if self.fit_status == "Done":
                self.fit_r = data["fit"]
                self.b_vv_r = self.fit_r[:, 0, :, 1]
                self.b_vh_r = self.fit_r[:, 1, :, 1]  # unused
            else:
                self.fit_r = None
                self.b_vv_r = np.zeros(len(self.theta))
                self.b_vh_r = np.zeros(len(self.theta))



        # Check if both fit variables are set before updating/displaying results
        if self.fit_m is not None and self.fit_r is not None:
            self.wl_slider.setEnabled(True)
            self.gonio_slider.setEnabled(True)

            self.update_plots_tab_theta(self.wl_slider.value())
            self.update_plots_tab_wl(self.gonio_slider.value())
        
        # If one of the fit_ is not ready, disable sliders 
        else:
            self.wl_slider.setDisabled(True)
            self.gonio_slider.setDisabled(True)

            self.plot_item_vv_theta.clear()
            self.plot_item_vh_theta.clear()
            self.plot_item_vh_vv_theta.clear()
            self.plot_item_vh_p_vv_theta.clear()

            self.plot_item_vv_wl.clear()
            self.plot_item_vh_wl.clear()
            self.plot_item_vh_vv_wl.clear()
            self.plot_item_vh_p_vv_wl.clear()

            self.results_plots_theta_initialized = False  # Set initialization value to false
            self.results_plots_wl_initialized = False     # when plot items have been cleared




    
    def update_plots_tab_theta(self, wl_index):
        # Create plot object from plot_item
        if not self.results_plots_theta_initialized:
            self.plot_vv_theta = self.plot_item_vv_theta.plot(self.theta, np.zeros(len(self.theta)), pen=(31, 119, 180))
            self.plot_vh_theta = self.plot_item_vh_theta.plot(self.theta, np.zeros(len(self.theta)), pen=(31, 119, 180))
            self.plot_vh_vv_theta = self.plot_item_vh_vv_theta.plot(self.theta, np.zeros(len(self.theta)), pen=(31, 119, 180))
            self.plot_vh_p_vv_theta = self.plot_item_vh_p_vv_theta.plot(self.theta, np.zeros(len(self.theta)), pen=(31, 119, 180))
        
            self.results_plots_theta_initialized = True

        self.wl_value_label.setText(str(round(self.wl[wl_index] * 1e9, 1)) + " nm")

        VV = self.b_vv_m[:, wl_index] / self.b_vv_r[:, wl_index]
        VH = self.b_vh_m[:, wl_index] / self.b_vv_r[:, wl_index]

        self.plot_vv_theta.setData(self.theta, VV)
        self.plot_vh_theta.setData(self.theta, VH)
        self.plot_vh_vv_theta.setData(self.theta, VH/VV)
        self.plot_vh_p_vv_theta.setData(self.theta, VH + VV)

    def update_plots_tab_wl(self, gonio_index):
        # Create plot object from plot_item
        if not self.results_plots_wl_initialized:
            self.plot_vv_wl = self.plot_item_vv_wl.plot(self.wl, np.zeros(len(self.wl)), pen=(44, 160, 44))
            self.plot_vh_wl = self.plot_item_vh_wl.plot(self.wl, np.zeros(len(self.wl)), pen=(44, 160, 44))
            self.plot_vh_vv_wl = self.plot_item_vh_vv_wl.plot(self.wl, np.zeros(len(self.wl)), pen=(44, 160, 44))
            self.plot_vh_p_vv_wl = self.plot_item_vh_p_vv_wl.plot(self.wl, np.zeros(len(self.wl)), pen=(44, 160, 44))

            self.results_plots_wl_initialized = True
        
        self.gonio_value_label.setText(str(self.theta[gonio_index]) + "°")  # theta is gonio

        VV = self.b_vv_m[gonio_index, :] / self.b_vv_r[gonio_index, :]
        VH = self.b_vh_m[gonio_index, :] / self.b_vv_r[gonio_index, :]

        self.plot_vv_wl.setData(self.wl, VV)
        self.plot_vh_wl.setData(self.wl, VH)
        self.plot_vh_vv_wl.setData(self.wl, VH/VV)
        self.plot_vh_p_vv_wl.setData(self.wl, VH + VV)

