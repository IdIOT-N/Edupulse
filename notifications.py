"""
Notifications Module
Manages daily notification reminders
"""

import threading
import time
from datetime import datetime, timedelta
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Warning: plyer not installed. Notifications will be simulated.")


class NotificationManager:
    """Handles notification scheduling and delivery"""
    
    def __init__(self):
        self.notifications_enabled = True
        self.morning_time = "07:00"
        self.evening_time = "21:00"
        self.notification_thread = None
    
    def send_notification(self, title, message, timeout=10):
        """Send a system notification"""
        if not self.notifications_enabled:
            print("Notifications are disabled")
            return
        
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name='EduPulse',
                    timeout=timeout
                )
                print(f"Notification sent: {title}")
            except Exception as e:
                print(f"Error sending notification: {e}")
                self._fallback_notification(title, message)
        else:
            self._fallback_notification(title, message)
    
    def _fallback_notification(self, title, message):
        """Fallback notification when plyer is not available"""
        print("\n" + "=" * 50)
        print(f"📱 NOTIFICATION: {title}")
        print(f"   {message}")
        print("=" * 50 + "\n")
    
    def send_morning_reminder(self):
        """Send morning reminder notification"""
        title = "🌅 Good Morning from EduPulse!"
        message = "Check today's top educational insights and stay updated."
        self.send_notification(title, message)
    
    def send_evening_reminder(self):
        """Send evening reminder notification"""
        title = "🌙 Evening Recap - EduPulse"
        message = "Let's see what you missed today. Catch up on the latest news!"
        self.send_notification(title, message)
    
    def schedule_notifications(self):
        """Start background thread for scheduled notifications"""
        if self.notification_thread is None or not self.notification_thread.is_alive():
            self.notification_thread = threading.Thread(
                target=self._notification_scheduler,
                daemon=True
            )
            self.notification_thread.start()
            print("Notification scheduler started")
    
    def _notification_scheduler(self):
        """Background scheduler for daily notifications"""
        print("Notification scheduler running...")
        
        morning_sent_today = False
        evening_sent_today = False
        
        while self.notifications_enabled:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # Check for morning notification
            if current_time >= self.morning_time and not morning_sent_today:
                self.send_morning_reminder()
                morning_sent_today = True
            
            # Check for evening notification
            if current_time >= self.evening_time and not evening_sent_today:
                self.send_evening_reminder()
                evening_sent_today = True
            
            # Reset flags at midnight
            if current_time == "00:00":
                morning_sent_today = False
                evening_sent_today = False
            
            time.sleep(60)
    
    def stop_notifications(self):
        """Stop notification scheduler"""
        self.notifications_enabled = False