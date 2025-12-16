; ============================================================================
; Perfect STT - Inno Setup Installer Script
; ============================================================================
; This script creates a professional Windows installer with:
; - Desktop shortcut
; - Start Menu entry
; - Uninstaller
; - Program Files installation
;
; Prerequisites:
; 1. Build the app with PyInstaller first (creates dist\PerfectSTT folder)
; 2. Install Inno Setup from: https://jrsoftware.org/isdl.php
; 3. Open this file in Inno Setup Compiler
; 4. Click Build > Compile
;
; Output: Output\PerfectSTT_Setup.exe
; ============================================================================

#define MyAppName "Perfect STT"
#define MyAppVersion "2.2.0"
#define MyAppPublisher "Perfect STT"
#define MyAppURL "https://github.com/perfectstt"
#define MyAppExeName "PerfectSTT.exe"
#define MyAppDescription "Local, Private Speech-to-Text Transcription"

[Setup]
; Basic installer info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output settings
OutputDir=Output
OutputBaseFilename=PerfectSTT_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression (LZMA2 for best compression)
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Installer appearance
WizardStyle=modern
WizardSizePercent=120

; Privileges (don't require admin for per-user install)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Minimum Windows version (Windows 10)
MinVersion=10.0

; License and info pages (optional - uncomment if you have these files)
; LicenseFile=LICENSE.txt
; InfoBeforeFile=README.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files (from PyInstaller dist folder)
Source: "dist\PerfectSTT\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Create empty folders for user data
; Models and Outputs folders will be created in app directory

[Dirs]
; Create writable folders for models and outputs
Name: "{app}\models"; Permissions: users-modify
Name: "{app}\Outputs"; Permissions: users-modify

[Icons]
; Start Menu shortcut
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"

; Desktop shortcut (if selected)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{#MyAppDescription}"

; Quick Launch shortcut (legacy, if selected)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data folders on uninstall (optional - comment out to keep user data)
; Type: filesandordirs; Name: "{app}\models"
; Type: filesandordirs; Name: "{app}\Outputs"

[Messages]
; Custom welcome message
WelcomeLabel2=This will install [name/ver] on your computer.%n%n{#MyAppDescription}%n%nAll transcription happens locally on your machine - your audio files never leave your computer.%n%nClick Next to continue.

[Code]
// Check if .NET or other prerequisites are needed (optional)
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add any prerequisite checks here
end;

// Show a message about first run
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Could add post-install actions here
  end;
end;
