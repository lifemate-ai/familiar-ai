; familiar-ai Inno Setup script
; Build with: ISCC.exe /DMyAppVersion=0.2.0 familiar-ai.iss
; Or via:     build.bat --installer
;
; Requires PyInstaller output at dist\familiar-ai\ (run build.bat first without --installer,
; or use scripts\build_release.py to do both steps automatically).

#ifndef MyAppVersion
  #define MyAppVersion "0.2.0"
#endif

#define MyAppName      "familiar-ai"
#define MyAppPublisher "lifemate-ai"
#define MyAppURL       "https://github.com/lifemate-ai/familiar-ai"
#define MyAppExeName   "familiar-ai.exe"
#define MyAppId        "{B8E4F5A2-3C71-4D9E-A6B0-8F2D1E7C4950}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases

; Install to per-user AppData — no UAC prompt required
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output
OutputDir=dist
OutputBaseFilename=familiar-ai-setup
SetupIconFile=assets\app.ico

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
DiskSpanning=no

; UI
WizardStyle=modern
WizardSizePercent=110
ShowLanguageDialog=auto

; Privileges — per-user install, no admin required
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Minimum Windows version: Windows 10
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; PyInstaller onedir output — all files and subdirectories
Source: "dist\familiar-ai\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}";       Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Desktop (optional, unchecked by default)
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up .env and logs written at runtime (optional — only if user agrees)
; Type: filesandordirs; Name: "{app}"
