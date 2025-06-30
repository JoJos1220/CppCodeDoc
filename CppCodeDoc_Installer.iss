
#define AppName "CppCodeDoc"
#define AppVersion "1.0.1"
#define AppExeName "CppCodeDoc"
#define AppExeNameWithIndex "CppCodeDoc.exe"
#define AppFileIdentifier "cppdoc"

[Setup]
AppId={#AppName}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher="Jojos1220"
AppComments="Generating Documentation out of C++-Files."
AppSupportURL="https://github.com/Jojos1220/CppCodeDoc"
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=.\Installer
OutputBaseFilename={#AppExeName}_{#AppVersion}_Installer
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
AlwaysShowDirOnReadyPage=yes
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeNameWithIndex}
LicenseFile={#AppName}\_internal\assets\LICENSE\LICENSE.txt
VersionInfoProductVersion={#AppVersion}
VersionInfoVersion={#AppVersion}
VersionInfoCopyright="@ Jojos1220 2025"
VersionInfoCompany="Jojos1220"

[Files]
Source: "{#AppName}\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppName}.exe"
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppName}.exe"

[Registry]
; Mapping extension key ".cppdoc" to App-File-Identifier
Root: HKCR; Subkey: ".{#AppFileIdentifier}"; ValueType: string; ValueName: ""; ValueData: "{#AppName}File"; Flags: uninsdeletevalue

; Definition of App-File-Identifier
Root: HKCR; Subkey: "{#AppName}File"; ValueType: string; ValueName: ""; ValueData: "{#AppName}File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "{#AppName}File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\_internal\assets\FileExtension.ico"
Root: HKCR; Subkey: "{#AppName}File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeNameWithIndex}"" --config ""%1"""

; contextmenu - "open with CppCodeDoc"
Root: HKCR; Subkey: "{#AppName}File\shell\open"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Open with {#AppName}"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "{#AppName}File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeNameWithIndex}"" --config ""%1"""

[Run]
Filename: "{app}\{#AppName}.exe"; Description: "Start {#AppName}"; Flags: nowait postinstall skipifsilent

; Setup Icon-Cache to avoid system restart
; Running on x64 Bit systems
Filename: "{sysnative}\ie4uinit.exe"; Parameters: "-ClearIconCache"; StatusMsg: "Clearing Icon-Cache..."; Flags: runhidden; Check: IsWin64
Filename: "{sysnative}\ie4uinit.exe"; Parameters: "-show"; StatusMsg: "Refreshing Explorer-Icons..."; Flags: runhidden; Check: IsWin64
; Running on x32 Bit systems
Filename: "{sys}\ie4uinit.exe"; Parameters: "-ClearIconCache"; StatusMsg: "Clearing Icon-Cache..."; Flags: runhidden; Check: not IsWin64
Filename: "{sys}\ie4uinit.exe"; Parameters: "-show"; StatusMsg: "Refreshing Explorer-Icons..."; Flags: runhidden; Check: not IsWin64
