$host.ui.RawUI.WindowTitle = "MYSQL��Ʈw�ƥ���..."
echo �}�l�ƥ�MySQL��Ʈw...

$fileName = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$filePath = "D:\MySQL�ƥ�"

mysqldump --login-path=local --all-databases > "$filePath\$fileName.sql"

[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
$objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$objNotifyIcon.BalloonTipIcon = "Info" 
$objNotifyIcon.BalloonTipTitle = "MySQL��Ʈw�ƥ�����" 
$objNotifyIcon.BalloonTipText = "�ɮצW��: $fileName.sql    �ɮצ�m: $filePath"
$objNotifyIcon.Visible = $True 
$objNotifyIcon.ShowBalloonTip(10000)