$host.ui.RawUI.WindowTitle = "MYSQL資料庫備份中..."
echo 開始備份MySQL資料庫...

$fileName = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$filePath = "D:\MySQL備份"

mysqldump --login-path=local --all-databases > "$filePath\$fileName.sql"

[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
$objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$objNotifyIcon.BalloonTipIcon = "Info" 
$objNotifyIcon.BalloonTipTitle = "MySQL資料庫備份完成" 
$objNotifyIcon.BalloonTipText = "檔案名稱: $fileName.sql    檔案位置: $filePath"
$objNotifyIcon.Visible = $True 
$objNotifyIcon.ShowBalloonTip(10000)