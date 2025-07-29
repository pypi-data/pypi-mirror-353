"""
Contains the layout and functionality of the main
application window.
"""

import os
import sys
import numpy as np
import pyqtgraph as pg

from qtpy import API_NAME

from qtpy.QtCore import (
    QRect,
    QSettings,
    Qt,
    QUrl,
)
from qtpy.QtGui import (
    QDesktopServices,
    QIcon,
    QKeySequence,
)
from qtpy.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .widgets.file_selector import FileSelectorDock
from .widgets.data_plotter import DataPlotterTab
from .widgets.results import ResultsDock


pg.setConfigOptions(antialias=True)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.init_actions()
        self.init_menus()
        self.init_statusbar()
        self.init_central_widget()
        self.init_dock_widgets()

    
    def init_actions(self):
        """Initialize actions."""
        self.quit_action = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
            "&Quit",
            self,
            shortcut=QKeySequence.Quit,
            statusTip="Exit application",
            triggered=self.close,
        )

        self.about_qt_action = QAction(
            QIcon("icons:Qt_logo_neon_2022.png"),
            "&About Qt",
            self,
            triggered=QApplication.aboutQt,
        )

    def init_menus(self):
        """Initialize menus."""
        menu = self.menuBar()

        # File menu
        self.file_menu = menu.addMenu("&File")
        self.file_menu.addAction(self.quit_action)

        self.view_menu = menu.addMenu("&View")

        self.about_menu = menu.addMenu("&About")
        self.about_menu.addAction(self.about_qt_action)
    
    def init_statusbar(self):
        """Initialise statusbar."""
        self.status_bar = self.statusBar()
    

    def init_central_widget(self):
        """Initialise the central widget."""
        
        # Tabs
        data_tabs = DataPlotterTab(self.status_bar)

        self.data_m = data_tabs.data_widget_m
        self.data_r = data_tabs.data_widget_r

        self.setCentralWidget(data_tabs)


    def init_dock_widgets(self):
        """Initialize the dock widgets."""

        self.results_dock = ResultsDock()

        self.file_selector_dock = FileSelectorDock(data_m=self.data_m, data_r=self.data_r, results_dock=self.results_dock)
                

        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_selector_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.results_dock)

        self.view_menu.addActions(
            [
                self.file_selector_dock.toggleViewAction(),
                self.results_dock.toggleViewAction(),
            ]
        )
    
    # def init_dock_results(self):



    def init_window_results(self, window):
        # Initialize window of results (VV, VH, VH/VV, VH+VV)
        plot_item_vv_theta = window.addPlot(viewBox=CustomMenu())
        plot_item_vv_theta.addLegend()
        plot_item_vv_theta.setDefaultPadding(0.0)
        plot_item_vv_theta.setLabel(axis='bottom', text="θ", units="°")
        plot_item_vv_theta.setLabel(axis='left', text="VV", units="")

        plot_item_vv_wl = window.addPlot(viewBox=CustomMenu())
        plot_item_vv_wl.addLegend()
        plot_item_vv_wl.setDefaultPadding(0.0)
        plot_item_vv_wl.setLabel(axis='bottom', text="λ", units="m")
        plot_item_vv_wl.setLabel(axis='left', text="VV", units="")

        window.nextRow()

        plot_item_vh_theta = window.addPlot(viewBox=CustomMenu())
        plot_item_vh_theta.addLegend()
        plot_item_vh_theta.setDefaultPadding(0.0)
        plot_item_vh_theta.setLabel(axis='bottom', text="θ", units="°")
        plot_item_vh_theta.setLabel(axis='left', text="VH", units="")

        plot_item_vh_wl = window.addPlot(viewBox=CustomMenu())
        plot_item_vh_wl.addLegend()
        plot_item_vh_wl.setDefaultPadding(0.0)
        plot_item_vh_wl.setLabel(axis='bottom', text="λ", units="m")
        plot_item_vh_wl.setLabel(axis='left', text="VH", units="")

        window.nextRow()

        plot_item_vh_vv_theta = window.addPlot(viewBox=CustomMenu())
        plot_item_vh_vv_theta.addLegend()
        plot_item_vh_vv_theta.setDefaultPadding(0.0)
        plot_item_vh_vv_theta.setLabel(axis='bottom', text="θ", units="°")
        plot_item_vh_vv_theta.setLabel(axis='left', text="VH/VV", units="")

        plot_item_vh_vv_wl = window.addPlot(viewBox=CustomMenu())
        plot_item_vh_vv_wl.addLegend()
        plot_item_vh_vv_wl.setDefaultPadding(0.0)
        plot_item_vh_vv_wl.setLabel(axis='bottom', text="λ", units="m")
        plot_item_vh_vv_wl.setLabel(axis='left', text="VH/VV", units="")

        window.nextRow()

        plot_item_vh_p_vv_theta = window.addPlot(viewBox=CustomMenu())
        plot_item_vh_p_vv_theta.addLegend()
        plot_item_vh_p_vv_theta.setDefaultPadding(0.0)
        plot_item_vh_p_vv_theta.setLabel(axis='bottom', text="θ", units="°")
        plot_item_vh_p_vv_theta.setLabel(axis='left', text="VH + VV", units="")

        plot_item_vh_p_vv_wl = window.addPlot(viewBox=CustomMenu())
        plot_item_vh_p_vv_wl.addLegend()
        plot_item_vh_p_vv_wl.setDefaultPadding(0.0)
        plot_item_vh_p_vv_wl.setLabel(axis='bottom', text="λ", units="m")
        plot_item_vh_p_vv_wl.setLabel(axis='left', text="VH + VV", units="")

        return plot_item_vv_theta, plot_item_vv_wl, plot_item_vh_theta, plot_item_vh_wl, plot_item_vh_vv_theta, plot_item_vh_vv_wl, plot_item_vh_p_vv_theta, plot_item_vh_p_vv_wl


    def init_results(self, plot_item_results):
        plot_vv_theta = plot_item_results[0].plot(self.theta, np.zeros(len(self.theta)))
        plot_vv_wl = plot_item_results[1].plot(self.wl, np.zeros(len(self.wl)))
        plot_vh_theta = plot_item_results[2].plot(self.theta, np.zeros(len(self.theta)))
        plot_vh_wl = plot_item_results[3].plot(self.wl, np.zeros(len(self.wl)))
        plot_vv_vh_theta = plot_item_results[4].plot(self.theta, np.zeros(len(self.theta)))
        plot_vv_vh_wl = plot_item_results[5].plot(self.wl, np.zeros(len(self.wl)))
        plot_vv_p_vh_theta = plot_item_results[6].plot(self.theta, np.zeros(len(self.theta)))
        plot_vv_p_vh_wl = plot_item_results[7].plot(self.wl, np.zeros(len(self.wl)))

        return {
            'vv_theta': plot_vv_theta,
            'vv_wl': plot_vv_wl,
            'vh_theta': plot_vh_theta,
            'vh_wl': plot_vh_wl,
            'vv_vh_theta': plot_vv_vh_theta,
            'vv_vh_wl': plot_vv_vh_wl,
            'vv_p_vh_theta': plot_vv_p_vh_theta,
            'vv_p_vh_wl':plot_vv_p_vh_wl
        }
        
    
    def update_sub(self, dict_sub, count_phi_wl):
        if dict_sub is None:
            return

        count_phi, count_wl = self.get_count_phi_count_wl(count_phi_wl, self.wl_ind, self.phi_ind)

        dict_sub["plot_phi"].setData(self.phi - min(self.phi), count_phi)

        params = fit_count_phi(self.phi, count_phi)
        dict_sub["plot_phi_fit"].setData(self.phi_precise - min(self.phi), fit_function(self.phi_precise*np.pi/180, *params))

        dict_sub["plot_wl"].setData(self.wl, count_wl)
    

    def update_results_theta(self, dict_results):
        
        wl_index = 1000

        # Sample measurement
        abc_vv, abc_vh = fit_count_phi_along_thetas(self.theta, self.phi, self.count_array, wl_index)

        # Reference measurement
        abc_vv_ref, abc_vh_ref = fit_count_phi_along_thetas(self.theta, self.phi, self.count_array_ref, wl_index)

        b_vv = abc_vv[:, 1]  # abc_xx.shape = (29, 3) we select b parameter at all gonio angles
        b_vh = abc_vh[:, 1]

        b_vv_ref = abc_vv_ref[:, 1]
        b_vh_ref = abc_vh_ref[:, 1]

        VV = b_vv/b_vv_ref
        VH = b_vh/b_vv_ref

        dict_results['vv_theta'].setData(self.theta, VV)
        dict_results['vh_theta'].setData(self.theta, VH)
        dict_results['vv_vh_theta'].setData(self.theta, VH/VV)
        dict_results['vv_p_vh_theta'].setData(self.theta, VH + VV)
        

    def update_results_wl(self, dict_results):
        
        theta_index = self.slider_gonio.value()

        # Sample measurement
        abc_vv, abc_vh = fit_count_phi_along_wavelengths(self.wl, self.phi, self.count_array, theta_index)

        # Reference measurement
        abc_vv_ref, abc_vh_ref = fit_count_phi_along_wavelengths(self.wl, self.phi, self.count_array_ref, theta_index)

        b_vv = abc_vv[:, 1]  # abc_xx.shape = (29, 3) we select b parameter at all gonio angles
        b_vh = abc_vh[:, 1]

        b_vv_ref = abc_vv_ref[:, 1]
        b_vh_ref = abc_vh_ref[:, 1]

        VV = b_vv/b_vv_ref
        VH = b_vh/b_vv_ref

        dict_results['vv_wl'].setData(self.wl, VV)
        dict_results['vh_wl'].setData(self.wl, VH)
        dict_results['vv_vh_wl'].setData(self.wl, VH/VV)
        dict_results['vv_p_vh_wl'].setData(self.wl, VH + VV)


    def update_all(self, dict_img, dict_sub, count_phi_wl):
        self.update_img(dict_img, count_phi_wl)
        self.update_sub(dict_sub, count_phi_wl)

    ### IDK how to call yet
    @staticmethod
    def get_count_phi_count_wl(count_phi_wl, wl_ind, phi_ind):
        count_phi = count_phi_wl[wl_ind, :]
        count_wl = count_phi_wl[:, phi_ind]
        return count_phi, count_wl

    ### Signal triggered functions ###
    def plot_fit_param(self, count_phi_wl, v_or_h):
        if v_or_h == 'VV':
            if self.window_fit_vv is None:
                self.window_fit_vv = WidgetFit(self.phi, self.wl, self.count_array, self.theta_ind)
                self.window_fit_vv.show()
            elif not self.window_fit_vv.isVisible():
                self.window_fit_vv.setVisible(True)
                
        if v_or_h == 'VH':
            if self.window_fit_vh is None:
                self.window_fit_vh = WidgetFit(self.phi, self.wl, self.count_array, self.theta_ind)
                self.window_fit_vh.show()
            elif not self.window_fit_vh.isVisible():
                self.window_fit_vh.setVisible(True)
