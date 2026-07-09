; =====================================================================
;  3D Color Palette Matcher - Windows Installer (Inno Setup script)
;
;  This produces a proper Windows installer that:
;    * Installs the app into "Program Files"
;    * Creates a Desktop shortcut (with the custom icon)
;    * Creates a Start Menu shortcut
;    * Registers the app in "Apps & features" / "Programs and Features"
;      with a working Uninstaller
;
;  It is compiled automatically by GitHub Actions (see build.yml), but you
;  can also compile it locally with Inno Setup 6:
;    1. Build the exe:  pyinstaller build.spec --noconfirm
;    2. Open this file in Inno Setup and click "Compile" (or run ISCC.exe).
; =====================================================================

#define MyAppName "3D Color Palette Matcher"
#define MyAppVersion "2.0"
#define MyAppPublisher "Netspecs"
#define MyAppURL "https://github.com/Netspecs/3d-color-palette-matcher"
#define MyAppExeName "3DColorPaletteMatcher.exe"

[Setup]
; A unique ID for this app. Keep this the SAME across versions so Windows
; recognises updates and shows a single entry in Programs and Features.
AppId={{F5A9849B-0217-4354-9208-6E018A4217F1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Install for the current user only, so no admin rights are required.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; OutputDir is relative to THIS script's folder (installer/), so ".." puts the
; finished installer in a top-level "installer_output" folder at the repo root.
OutputDir=..\installer_output
OutputBaseFilename=3DColorPaletteMatcher-Setup
SetupIconFile=..\docs\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Windows 7 SP1 and newer.
MinVersion=6.1sp1

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; The standalone PyInstaller executable (built by build.spec).
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; A copy of the icon, in case shortcuts want to reference it directly.
Source: "..\docs\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
; "Uninstall" entry inside the Start Menu group
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Optional Desktop shortcut (controlled by the checkbox on the Tasks page)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
; Offer to launch the app right after installation finishes.
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
