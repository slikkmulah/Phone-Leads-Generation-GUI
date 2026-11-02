#define AppVersion "1.1.0"
[Setup]
AppId={{C7AA0516-5F34-4D0B-877F-5A1DA2D46D36}
AppName=Phone Number Generator
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\PhoneNumberGenerator
DefaultGroupName=Phone Number Generator
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=PhoneNumberGenerator-Windows-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\PhoneNumberGenerator.exe
LicenseFile=..\LICENSE
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "..\dist\PhoneNumberGenerator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Phone Number Generator"; Filename: "{app}\PhoneNumberGenerator.exe"
Name: "{autodesktop}\Phone Number Generator"; Filename: "{app}\PhoneNumberGenerator.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PhoneNumberGenerator.exe"; Description: "Open Phone Number Generator"; Flags: nowait postinstall skipifsilent
