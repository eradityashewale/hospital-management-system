; Inno Setup Installer Script for Hospital Management System
; This script creates a professional Windows installer

#define MyAppName "Hospital Management System"
#define MyAppNameShort "MediFlow"
#define MyAppVersion "1.0"
#define MyAppPublisher "Hospital Management"
#define MyAppURL "https://www.example.com/"
#define MyAppExeName "HospitalManagementSystem.exe"
#define MyAppId "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
; App Information
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer_output
OutputBaseFilename=HospitalManagementSystem_Setup
; Icon for the installer - build script will convert PNG to ICO if needed
; SetupIconFile should point to an ICO file (created from PNG if needed)
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=no
DisableReadyPage=no
DisableFinishedPage=no

; Installation Options
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Desktop shortcut will be created via popup at the end, not during installation
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Note: Database file (hospital.db) will be created automatically when the application runs
; Note: Logs directory will be created automatically when the application runs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop shortcut will be created via popup at the end
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Ask user if they want to run the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom function to check if source file exists
function FileExistsCheck(FileName: String): Boolean;
var
  FullPath: String;
begin
  FullPath := ExpandConstant('{src}\' + FileName);
  Result := FileExists(FullPath);
end;

// Custom function to check if source directory exists
function DirExistsCheck(DirName: String): Boolean;
var
  FullPath: String;
begin
  FullPath := ExpandConstant('{src}\' + DirName);
  Result := DirExists(FullPath);
end;

var
  ShortcutCreated: Boolean;

// Custom message after installation
procedure CurStepChanged(CurStep: TSetupStep);
var
  CreateShortcut: Boolean;
begin
  if CurStep = ssPostInstall then
  begin
    // Note: Logs and database will be created automatically in AppData by the application
    // This prevents permission errors when running from Program Files
    
    // Show popup to create desktop shortcut after installation completes
    CreateShortcut := MsgBox('Installation completed successfully!' + #13#10 + #13#10 + 
      'Would you like to create a desktop shortcut for Hospital Management System?', 
      mbConfirmation, MB_YESNO) = IDYES;
    
    if CreateShortcut then
    begin
      try
        // Create desktop shortcut
        CreateShellLink(
          ExpandConstant('{userdesktop}\Hospital Management System.lnk'),
          'Hospital Management System',
          ExpandConstant('{app}\{#MyAppExeName}'),
          '',
          ExpandConstant('{app}'),
          '',
          0,
          SW_SHOWNORMAL
        );
        ShortcutCreated := True;
        MsgBox('Desktop shortcut created successfully!', mbInformation, MB_OK);
      except
        MsgBox('Could not create desktop shortcut. You can create it manually from the Start Menu.', 
          mbError, MB_OK);
      end;
    end
    else
    begin
      ShortcutCreated := False;
    end;
  end;
end;

// Initialize shortcut flag
procedure InitializeWizard();
begin
  ShortcutCreated := False;
end;

