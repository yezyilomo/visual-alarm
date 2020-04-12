import sys
import time
import datetime

from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QMenu, QMainWindow, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread, QEventLoop, QTimer
from fbs_runtime.application_context import ApplicationContext

import config
from ui import Notification


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

    def should_fire_today(self, alarm):
        today = datetime.datetime.now()

        alarm_date = []
        if alarm['date']:
            alarm_date = alarm['date']
        if today.isoweekday() in alarm['repeat'] or not alarm['date']:
            alarm_date = [today.year, today.month, today.day]

        datetime_args = alarm_date + alarm['time']
        alarm = datetime.datetime(*datetime_args)
        if alarm.date() == today.date() and alarm.time() > today.time():
            return True
        return False

    def get_alarms(self):
        alarms = config.read()["alarms"]
        for alarm in alarms:
            if self.should_fire_today(alarm):
                yield datetime.time(*alarm['time']), alarm['title']

    def create_timer(self, time_str, message):
        # create Worker and Thread
        def fire_alarm():
            self.fire_alarm.emit(time_str, message)

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(fire_alarm)
        return timer

    def start_timers(self):
        alarms = self.get_alarms()

        if self.timers:
            # All timers have been started already
            return

        now = datetime.datetime.now()
        prev_alarm_sec = 0
        for alarm_time, alarm_title in alarms:
            current_alarm_sec = (datetime.datetime.combine(now.date(), alarm_time) - now).total_seconds()
            actual_sec = current_alarm_sec - prev_alarm_sec
            prev_alarm_sec = current_alarm_sec
        
            time_str = alarm_time.strftime('%H:%M:%S')
            timer = self.create_timer(time_str, alarm_title)
            self.timers.append(timer)
            timer.start(actual_sec*1000)

    @pyqtSlot()
    def start(self):  # A slot takes no params
        print("Starting......")
        self.is_running = True
        self.timers = []
        self.start_timers()


class Application():
    def __init__(self, get_resources):
        self.get_resources = get_resources # Get resources
        config.initiate()  # Initiate configurations
        self.start_timer_thread()  # Start timer on separate thread
        self.start_application()  # Start application

    def start_timer_thread(self):
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

    def start_application(self):
        app = QApplication(sys.argv)

        self.trayIcon = QSystemTrayIcon(QIcon("src/main/resources/base/alarm-clock.svg"), app)
        self.menu = QMenu()

        self.configureAction = self.menu.addAction('Configure')
        self.configureAction.triggered.connect(self.configure)

        self.notifyAction = self.menu.addAction('Notification')
        self.notifyAction.triggered.connect(self.restart_timer)

        self.quitAction = self.menu.addAction('Quit')
        self.quitAction.triggered.connect(self.exit)

        self.trayIcon.setContextMenu(self.menu)
        self.trayIcon.show()
        sys.exit(app.exec_())

    def restart_timer(self):  
        for timer in self.worker.timers:
            # Stop all timers
            timer.stop()

        self.thread.disconnect()
        self.thread.quit()  # This is very important(Quit thread b4 restarting it)
        self.thread.started.connect(self.worker.start)
        while self.thread.isRunning():
            pass
        else:
            self.thread.start()

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
        Application(self.get_resource)
        stylesheet = self.get_resource('styles.qss')
        self.app.setStyleSheet(open(stylesheet).read())
        return self.app.exec_()             # 3. End run() with this line


def main():
    appctxt = AppContext()                  # 4. Instantiate the subclass
    exit_code = appctxt.run()               # 5. Invoke run()
    sys.exit(exit_code)

if __name__ == "__main__":
  main()
