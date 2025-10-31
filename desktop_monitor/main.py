#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Husqvarna Svartpilen 401 OBD2 Monitor
Main application entry point

Author: Your Name
Date: October 2025
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from gui.main_window import OBD2MonitorMainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Husqvarna Svartpilen 401 OBD2 Monitor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Husqvarna Community")
    app.setOrganizationDomain("github.com/sybinh")
    
    # Create and show main window
    window = OBD2MonitorMainWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())