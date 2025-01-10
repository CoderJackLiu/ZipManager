; 定义安装包的基本信息
[Setup]
AppName=ZipManager                     
AppVersion=1.0                         
DefaultDirName=C:\ZipManager           
DefaultGroupName=ZipManager            
OutputBaseFilename=ZipManagerSetup


; 定义安装文件
[Files]
Source: "dist\ZipManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion

; 定义快捷方式
[Icons]
Name: "{group}\ZipManager"; Filename: "{app}\ZipManager.exe"
Name: "{group}\Uninstall ZipManager"; Filename: "{uninstallexe}"
Name: "{userdesktop}\ZipManager"; Filename: "{app}\ZipManager.exe"; Tasks: desktopicon

; 选择性任务
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; 安装完成后运行程序的设置
[Run]
Filename: "{app}\ZipManager.exe"; Description: "运行 ZipManager"; Flags: nowait postinstall skipifsilent; 
