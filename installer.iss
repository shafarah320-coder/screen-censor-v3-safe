[Setup]
AppId={{A5E8C8F3-1F24-4D81-9D33-8F6A3C9A3003}
AppName=Screen Censor 3.0 Safe Preview
AppVersion=3.0.0
DefaultDirName={autopf}\Screen Censor 3.0
DefaultGroupName=Screen Censor 3.0
OutputDir=Output
OutputBaseFilename=ScreenCensor_3_Safe_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\ScreenCensor\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Screen Censor 3.0 Safe Preview"; Filename: "{app}\ScreenCensor.exe"
Name: "{autodesktop}\Screen Censor 3.0 Safe Preview"; Filename: "{app}\ScreenCensor.exe"
