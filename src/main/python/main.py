import datetime
from ui import Notification
import time

import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QMenu, QMainWindow, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread
from fbs_runtime.application_context import ApplicationContext


class Preferences(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set some main window's properties
        self.setWindowTitle('Preferences')
        self.setFixedSize(235, 235)

        # Set the central widget
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)


class Worker(QObject):
    fire_alarm = pyqtSignal(str, str) # (time, message)

    @pyqtSlot()
    def start(self):  # A slot takes no params
        # Get alarms from config file
        alarms = [datetime.time(5, 22, sec) for sec in range(0, 10)]

        now = datetime.datetime.now()
        prev_alarm_sec = 0
        for alarm_time in alarms:
            current_alarm_sec = (datetime.datetime.combine(now.date(), alarm_time) - now).total_seconds()
            actual_sec = current_alarm_sec - prev_alarm_sec
            prev_alarm_sec = current_alarm_sec

            time.sleep(actual_sec)
            time_str = alarm_time.strftime('%H:%M:%S')
            message = f"Hello there, {time_str}"
            print(f"Firing the alarm {time_str}")
            self.fire_alarm.emit(time_str, message)


class TrayMenu():
    def __init__(self, get_resources):
        self.get_resources = get_resources

        # create Worker and Thread
        self.worker = Worker()  # no parent!
        self.thread = QThread()  # no parent!

        # Move the Worker object to the Thread object
        self.worker.moveToThread(self.thread)

        # Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.worker.start)

        # Connect Worker`s Signals to update progressbar.
        self.worker.fire_alarm.connect(self.fire_alarm)
        self.thread.start()
        
        self.main()
    
    def main(self):
        app = QApplication(sys.argv)

        self.trayIcon = QSystemTrayIcon(QIcon("src/main/resources/base/alarm-clock.svg"), app)
        self.menu = QMenu()

        self.configureAction = self.menu.addAction('Configure')
        self.configureAction.triggered.connect(self.configure)

        self.notifyAction = self.menu.addAction('Notification')
        self.notifyAction.triggered.connect(self.fire_alarm)

        self.quitAction = self.menu.addAction('Quit')
        self.quitAction.triggered.connect(self.exit)

        self.trayIcon.setContextMenu(self.menu)
        self.trayIcon.show()
        sys.exit(app.exec_())

    def fire_alarm(self, time, message):
        alarm_data = {
            'time': time,
            'message': message
        }
        self.notification = Notification(self.get_resources, alarm_data)
        self.notification.show()

    def configure(self):
        self.preference = Preferences()
        self.preference.show()
        
    def exit(self):
        sys.exit()

class AppContext(ApplicationContext):       # 1. Subclass ApplicationContext
    def run(self):                          # 2. Implement run()
        window = TrayMenu(self.get_resource)
        stylesheet = self.get_resource('styles.qss')
        self.app.setStyleSheet(open(stylesheet).read())
        return self.app.exec_()             # 3. End run() with this line


def main():
    appctxt = AppContext()                  # 4. Instantiate the subclass
    exit_code = appctxt.run()               # 5. Invoke run()
    sys.exit(exit_code)

if __name__ == "__main__":
  main()
