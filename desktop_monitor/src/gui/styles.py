#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Styles for OBD2 Monitor GUI
Professional dark theme styling
"""

DARK_THEME = """
/* Main application styling */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

/* Group boxes */
QGroupBox {
    font-weight: bold;
    border: 2px solid #555555;
    border-radius: 8px;
    margin: 8px 0px;
    padding-top: 15px;
    font-size: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    color: #ffffff;
}

/* Labels */
QLabel {
    color: #ffffff;
    font-size: 11px;
}

/* Value labels (large numbers) */
QLabel[class="value-label"] {
    font-size: 28px;
    font-weight: bold;
    color: #00ff88;
    background: transparent;
    padding: 4px;
}

/* Buttons */
QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
    border-radius: 6px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

QPushButton:disabled {
    background-color: #666666;
    color: #aaaaaa;
}

/* Combo boxes */
QComboBox {
    padding: 8px 12px;
    border: 2px solid #555555;
    border-radius: 6px;
    background-color: #3b3b3b;
    color: white;
    font-size: 11px;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #777777;
}

QComboBox:focus {
    border-color: #4CAF50;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #3b3b3b;
    border: 2px solid #555555;
    border-radius: 6px;
    color: white;
    selection-background-color: #4CAF50;
}

/* Text edit widgets */
QTextEdit {
    background-color: #1e1e1e;
    border: 2px solid #555555;
    border-radius: 6px;
    color: #ffffff;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 9px;
    padding: 8px;
}

QTextEdit:focus {
    border-color: #4CAF50;
}

/* Scroll bars */
QScrollBar:vertical {
    background-color: #3b3b3b;
    width: 16px;
    border-radius: 8px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    min-height: 20px;
    border-radius: 8px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #777777;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab widget */
QTabWidget::pane {
    border: 2px solid #555555;
    border-radius: 6px;
    background-color: #2b2b2b;
}

QTabBar::tab {
    background-color: #3b3b3b;
    color: #ffffff;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 11px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #4CAF50;
}

QTabBar::tab:hover:!selected {
    background-color: #555555;
}

/* Status bar */
QStatusBar {
    background-color: #1e1e1e;
    border-top: 1px solid #555555;
    color: #ffffff;
    font-size: 10px;
    padding: 4px;
}

/* Menu bar */
QMenuBar {
    background-color: #2b2b2b;
    color: #ffffff;
    border-bottom: 1px solid #555555;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #4CAF50;
}

QMenu {
    background-color: #3b3b3b;
    border: 2px solid #555555;
    border-radius: 6px;
    color: #ffffff;
    padding: 4px;
}

QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #4CAF50;
}

/* Splitter */
QSplitter::handle {
    background-color: #555555;
    border-radius: 2px;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}

QSplitter::handle:hover {
    background-color: #777777;
}

/* Message boxes */
QMessageBox {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}

/* Tooltips */
QToolTip {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 10px;
}
"""

# Light theme (alternative)
LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QWidget {
    background-color: #f5f5f5;
    color: #333333;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 8px;
    margin: 8px 0px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    color: #333333;
}

QLabel[class="value-label"] {
    font-size: 28px;
    font-weight: bold;
    color: #2196F3;
    background: transparent;
    padding: 4px;
}

QPushButton {
    background-color: #2196F3;
    border: none;
    color: white;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
    border-radius: 6px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #1565C0;
}
"""