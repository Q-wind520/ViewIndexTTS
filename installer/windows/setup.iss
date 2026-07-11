; ViewIndexTTS — Inno Setup 6 installer script
;
; Usage: iscc /DMyAppVersion="v1.1.0" setup.iss
;   or call from CI with the version tag injected.

#define MyAppName "ViewIndexTTS"
#define MyAppPublisher "ViewIndexTTS Contributors"
#define MyAppURL "https://github.com/Q-wind520/ViewIndexTTS"

; MyAppVersion is injected at build time via CLI /DMyAppVersion="..."
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

#define MyAppExeName "ViewIndexTTS.exe"

[Setup]
AppId={{F8A3B6D1-9E2C-4A5F-8D7E-1C4B6A8F9E3D}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=ViewIndexTTS-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
PrivilegesRequiredOverridesAllowed=dialog

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\..\dist\main.dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
