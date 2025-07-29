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


class DataPlotterTab(QTabWidget):
    def __init__(self, status_bar):
        super().__init__()

        self.setTabPosition(QTabWidget.South)

        # self.status_bar = status_bar

        self.data_widget_m = DataPlotter(status_bar)
        self.data_widget_r = DataPlotter(status_bar)

        self.addTab(self.data_widget_m, "Measurement file")
        self.addTab(self.data_widget_r, "Reference file")


class DataPlotter(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        
        graphics_layout_widget = pg.GraphicsLayoutWidget()
        graphics_layout_widget.setBackground('w')

        # Set colormap and plot color
        self.color = (50, 10, 90)
        self.cmap = pg.colormap.get('inferno')

        self.status_bar = status_bar

        ### Update parameters/data
        self.theta = None
        self.ana = None
        self.phi = None
        self.wl = None
        self.data = None
        self.bkg = None  # Not used
        self.fit = None

        self.dict_img = None
        self.dict_sub = None

        self.phi_ind = 0
        self.wl_ind = 0




        ### 2D image plot of A/D count vs φ vs λ
        # title = self.objectName()[-2:].upper()  # Return 'VV' or 'VH' depending on window
        self.plot_item_img = graphics_layout_widget.addPlot(row=0, col=0, colspan=3, viewBox=CustomMenu())  # title=title,  (removed),      
        self.plot_item_img.ctrlMenu.menuAction().setVisible(False)
        self.plot_item_img.addLegend()
        self.plot_item_img.setDefaultPadding(0.0)
        self.plot_item_img.setLabel(axis='bottom', text="Wavelength", units="m")
        self.plot_item_img.setLabel(axis='left', text="Polarizer angle φ", units="°")
        self.cb = pg.ColorBarItem(interactive=False, values=(0, 2**16-1), label="A/D count", width=10)
        self.cb.setImageItem(pg.ImageItem(), insert_in=self.plot_item_img)


        ### Cross-section plots
        graphics_layout_widget.ci.layout.setRowStretchFactor(0, 3)
        graphics_layout_widget.ci.layout.setRowStretchFactor(1, 1)

        graphics_layout_widget.nextRow()  # Go on next row within window (QGraphicsLayout)

        # Plot of A/D count vs φ with fit
        self.plot_item_phi = graphics_layout_widget.addPlot(row=1, col=0, viewBox=CustomMenu())
        self.plot_item_phi.addLegend()
        self.plot_item_phi.setDefaultPadding(0.0)
        self.plot_item_phi.setLabel(axis='bottom', text="Polarizer angle φ", units="°")
        self.plot_item_phi.setLabel(axis='left', text="A/D count", units="")
        
        # Plot of A/D count vs λ
        self.plot_item_wl = graphics_layout_widget.addPlot(row=1, col=1, viewBox=CustomMenu())
        self.plot_item_wl.addLegend()
        self.plot_item_wl.setDefaultPadding(0.0)
        self.plot_item_wl.setLabel(axis='bottom', text="Wavelength", units="m")
        self.plot_item_wl.setLabel(axis='left', text="A/D count", units="")

        # self.plot_item_phi.setVisible(False)
        # self.plot_item_wl.setVisible(False)


        # Gonio slider
        gonio_layout = QHBoxLayout()

        self.gonio_slider = QSlider(Qt.Orientation.Horizontal)
        self.gonio_value_label = QLabel("")

        self.gonio_slider.setFixedWidth(150)
        self.gonio_slider.setDisabled(True)

        gonio_layout.addWidget(self.gonio_slider)
        gonio_layout.addWidget(self.gonio_value_label)


        # Analyzer slider
        ana_layout = QHBoxLayout()

        self.ana_radio_0 = QRadioButton("VV")
        self.ana_radio_1 = QRadioButton("VH")

        self.ana_radio_0.setDisabled(True)
        self.ana_radio_1.setDisabled(True)

        ana_layout.addWidget(self.ana_radio_0)
        ana_layout.addWidget(self.ana_radio_1)
        ana_layout.addStretch()


        # Parameters form
        parameters_layout = QFormLayout()

        parameters_layout.addRow("Goniometer angle", gonio_layout)
        parameters_layout.addRow("Analyzer angle", ana_layout)


        widget_layout = QVBoxLayout()
        widget_layout.addWidget(graphics_layout_widget)
        widget_layout.addLayout(parameters_layout)


        self.setLayout(widget_layout)

        self.ana_radio_0.toggled.connect(self.update_plots)
        self.gonio_slider.valueChanged.connect(self.update_plots)

        # print("SignalPlotter initialized:", title)

    def init_plots(self):
        ### Image item
        # Fill plot item with zeros
        img_count_phi_wl = pg.ImageItem(np.zeros((len(self.wl)-1, len(self.phi)-1)))
        
        img_count_phi_wl.setRect(self.wl_start, self.phi_start, self.wl_width, self.phi_width)

        vline = pg.InfiniteLine(pos=self.wl_start, angle=90, pen=(255, 255, 255, 200))  # Define vertical line
        hline = pg.InfiniteLine(angle=0, pen=(255, 255, 255, 200))  # Define horizontal line
        vline.setVisible(False)
        hline.setVisible(False)

        self.plot_item_img.addItem(img_count_phi_wl)
        self.plot_item_img.addItem(vline)
        self.plot_item_img.addItem(hline)

        self.cb.setImageItem(img_count_phi_wl)

        self.dict_img = {
            "img": img_count_phi_wl,
            "cb": self.cb,
            "vline": vline,
            "hline": hline
            }
        
        ### Sub items
        # Fill plot item with zeros
        a, b, c = 0, 0, 0
        plot_phi = self.plot_item_phi.plot(self.phi - min(self.phi), np.zeros(len(self.phi)), pen=None, brush=None, symbolPen=None, symbolBrush=self.color, symbolSize=6)
        # plot_phi_fit = self.plot_item_phi.plot(self.phi_precise - min(self.phi), self.fit_function(self.phi_precise*np.pi/180, a, b, c), pen=self.color, name="fit")

        # Fill plot item with zeros
        plot_wl = self.plot_item_wl.plot(self.wl, np.zeros(len(self.wl)), pen=self.color)
                
        self.dict_sub = {
            "plot_phi": plot_phi,
            # "plot_phi_fit": plot_phi_fit,
            "plot_wl": plot_wl
            }
        
        self.ana_radio_0.setEnabled(True)
        self.ana_radio_1.setEnabled(True)
        self.gonio_slider.setEnabled(True)

        self.ana_radio_0.blockSignals(True)
        self.ana_radio_0.setChecked(True)
        self.ana_radio_0.blockSignals(False)

        self.dict_img['img'].hoverEvent = self.imageHoverEvent


    def update_data(self, theta=None, ana=None, phi=None, wl=None, data=None, bkg=None, fit=None):
        ### Update parameters/data
        self.theta = theta
        self.ana = ana
        self.phi = phi
        self.wl = wl
        self.data = data
        self.bkg = bkg  # Not used
        self.fit = fit  # Not used

        # Set axis
        self.phi_precise = np.linspace(min(self.phi), max(self.phi), 100)  # Create a copy of polarizer data with higher resolution (for later plotting) 
        self.phi_start = 0  # Find initial value and width for setRect() function later
        self.phi_width = self.phi[-1] - self.phi[0]
        self.phi_step = self.phi[1] - self.phi[0]

        self.wl_start = self.wl[0]  # Find itial value and width for setRect() function later
        self.wl_width = self.wl[-1] - self.wl[0]
        self.wl_step = self.wl[1] - self.wl[0]

        self.gonio_slider.setMinimum(0)
        self.gonio_slider.setMaximum(len(self.theta)-1)  # If gonio is array[20, 30] slider will move from 0 (set in designer) to len=2 - 1 = 1)


    def update_plots(self):

        if self.dict_img == None or self.dict_sub == None:
            self.init_plots()

        self.ana_radio_0.setText(str(self.ana[0]) + "°")
        self.ana_radio_1.setText(str(self.ana[1]) + "°")

        gonio_index = self.gonio_slider.value()

        vv_or_vh = 0 if self.ana_radio_0.isChecked() else 1

        self.data_ready = self.data[gonio_index, vv_or_vh, :, :]  # data_ready is the ready-to-be-plotted data that has been selected within data

        self.gonio_value_label.setText(str(int(self.theta[gonio_index])) + "°")
        
        ### Img plot
        self.dict_img["img"].setImage(self.data_ready.T)
        self.dict_img["cb"].values = 0, np.max(self.data_ready.T)  # Use self.max_count for mirror colorbar between vv and vh
        self.dict_img["cb"].setColorMap(self.cmap)

        ### Sub plots
        self.dict_sub["plot_phi"].setData(self.phi - min(self.phi), self.data_ready.T[self.wl_ind])

        # params = fit_count_phi(np.array(self.phi), data.T[0])

        # self.dict_sub["plot_phi_fit"].setData(self.phi_precise - min(self.phi), self.fit_function(self.phi_precise*np.pi/180, *params))

        self.dict_sub["plot_wl"].setData(self.wl, self.data_ready.T[:, self.phi_ind])
    
    def imageHoverEvent(self, event):
        """
        Show the position, pixel, and value under mouse cursor.
        """
        pos = event.pos()
        i, j = min(int(pos.x()+0.5), len(self.wl)-1), min(int(pos.y()+0.5), len(self.phi)-1)  # +0.5 for the cursor to feel more natural
                                                                                              # min(value, 36) prevents value to go above 36
        x_val = self.wl[i]
        y_val = self.phi[j] - self.phi[0]
        val = self.data_ready.T[i, j-1]

        self.wl_ind = i
        self.phi_ind = j

        # Update cursor position display on status bar
        self.status_bar.showMessage("x = %i nm, y = %i°, value = %i" % (x_val*1e9, y_val, val))

        # Display crosshair pattern
        self.dict_img['hline'].setPos(y_val)
        self.dict_img['vline'].setPos(x_val)

        self.update_plots()

        if event.isEnter():
            self.dict_img["hline"].setVisible(True)
            self.dict_img["vline"].setVisible(True)
            return
        
        if event.isExit():
            self.dict_img['hline'].setVisible(False)
            self.dict_img['vline'].setVisible(False)
            self.status_bar.clearMessage()
            return

    @staticmethod
    def fit_function(x, a, b, c):
        return a + b * (np.cos(2*x + c)) ** 2

