import threading
import subprocess
import sys
import time

class WindowsPushNotifier:
    def __init__(self):
        self.available = True
    
    def show_notification(self, title, message, duration=10):
        """Надежные Push-уведомления через PowerShell"""
        def show():
            try:
                self._show_powershell_toast(title, message, duration)
            except Exception as e:
                print(f"Notification error: {e}")
                self._fallback_notification(title, message)
        
        thread = threading.Thread(target=show, daemon=True)
        thread.start()
    
    def _show_powershell_toast(self, title, message, duration):
        """PowerShell тосты - самый надежный метод"""
        try:
            # Конвертируем duration в миллисекунды
            duration_ms = duration * 1000
            
            # Экранируем специальные символы
            title_escaped = title.replace('"', '`"').replace("'", "`'")
            message_escaped = message.replace('"', '`"').replace("'", "`'")
            
            # PowerShell скрипт для современных тостов
            ps_script = '''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$notify.BalloonTipTitle = "''' + title_escaped + '''"
$notify.BalloonTipText = "''' + message_escaped + '''"
$notify.Visible = $true
$notify.ShowBalloonTip(''' + str(duration_ms) + ''')
'''
            
            # Запускаем PowerShell в скрытом режиме
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            
            process = subprocess.Popen([
                'powershell', 
                '-WindowStyle', 'Hidden',
                '-ExecutionPolicy', 'Bypass',
                '-Command', ps_script
            ], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ждем завершения немного, затем убиваем процесс
            time.sleep(0.5)
            try:
                process.terminate()
            except:
                pass
                
        except Exception as e:
            raise Exception(f"PowerShell toast failed: {e}")
    
    def _show_modern_toast(self, title, message, duration):
        """Современные тосты для Windows 10/11"""
        try:
            # Экранируем для XML
            title_escaped = self._escape_xml(title)
            message_escaped = self._escape_xml(message)
            
            ps_script = '''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$xmlTemplate = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">''' + title_escaped + '''</text>
            <text id="2">''' + message_escaped + '''</text>
        </binding>
    </visual>
</toast>
"@

try {
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($xmlTemplate)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("RestaurantApp")
    $notifier.Show($toast)
} catch {
    # Fallback to legacy method
    Add-Type -AssemblyName System.Windows.Forms
    $notify = New-Object System.Windows.Forms.NotifyIcon
    $notify.Icon = [System.Drawing.SystemIcons]::Information
    $notify.BalloonTipTitle = "''' + title_escaped + '''"
    $notify.BalloonTipText = "''' + message_escaped + '''"
    $notify.Visible = $true
    $notify.ShowBalloonTip(10000)
}
'''
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            
            subprocess.run([
                'powershell', 
                '-WindowStyle', 'Hidden',
                '-ExecutionPolicy', 'Bypass',
                '-Command', ps_script
            ], startupinfo=startupinfo, capture_output=True, timeout=5)
            
        except Exception as e:
            raise Exception(f"Modern toast failed: {e}")
    
    def _escape_xml(self, text):
        """Экранирование XML символов"""
        return (text.replace('&', '&amp;')
                  .replace('<', '&lt;')
                  .replace('>', '&gt;')
                  .replace('"', '&quot;')
                  .replace("'", '&apos;'))
    
    def _fallback_notification(self, title, message):
        """Резервный метод через ctypes"""
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"{message}", f"{title}", 0x40)
        except:
            print(f"🔔 {title}: {message}")

# Глобальный экземпляр
notifier = WindowsPushNotifier()