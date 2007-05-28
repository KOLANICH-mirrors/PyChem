
[Setup]
AppName=PyChem
AppVerName=PyChem 3.0.1 Beta
DefaultDirName={pf}\PyChem
DefaultGroupName=PyChem
UninstallDisplayIcon={app}\Uninstall PyChem
Compression=lzma
SolidCompression=yes
OutputDir=userdocs:PyChem Setup

[Files]
Source: "PyChemApp.exe"; DestDir: "{app}"
Source: "python24.dll"; DestDir: "{app}"
Source: "w9xpopen.exe"; DestDir: "{app}"
Source: "msvcr71.dll"; DestDir: "{app}"
Source: "library.zip"; DestDir: "{app}"
Source: "/ico/pychem.ico"; DestDir: "{app}\ico"
Source: "/bmp/addclass.png"; DestDir: "{app}\bmp"
Source: "/bmp/addlabel.png"; DestDir: "{app}\bmp"
Source: "/bmp/addvalidation.png"; DestDir: "{app}\bmp"
Source: "/bmp/arrown.png"; DestDir: "{app}\bmp"
Source: "/bmp/arrows.png"; DestDir: "{app}\bmp"
Source: "/bmp/export.png"; DestDir: "{app}\bmp"
Source: "/bmp/import.png"; DestDir: "{app}\bmp"
Source: "/bmp/insertxvar.png"; DestDir: "{app}\bmp"
Source: "/bmp/params.png"; DestDir: "{app}\bmp"
Source: "/bmp/pychemsplash.png"; DestDir: "{app}\bmp"
Source: "/bmp/run.png"; DestDir: "{app}\bmp"
Source: "/bmp/addclass.png"; DestDir: "{app}\bmp"
Source: "/examples/ftir-ga3-raw-data.txt"; DestDir: "{app}\examples"
Source: "/examples/ftir-ga3-bioprocess-indvars-import.csv"; DestDir: "{app}\examples"
Source: "/examples/ftir-ga3-bioprocess-expsetup-import.csv"; DestDir: "{app}\examples"
Source: "/docs/PAChelp.hhc"; DestDir: "{app}\docs"
Source: "/docs/PAChelp.hhk"; DestDir: "{app}\docs"
Source: "/docs/PAChelp.hhp"; DestDir: "{app}\docs"
Source: "/docs/Intro.htm"; DestDir: "{app}\docs"
Source: "/docs/Intro_files/filelist.xml"; DestDir: "{app}\docs\Intro_files"
Source: "/docs/Intro_files/image001.jpg"; DestDir: "{app}\docs\Intro_files"
Source: "/docs/Intro_files/image002.jpg"; DestDir: "{app}\docs\Intro_files"

[Icons]
Name: "{group}\PyChem"; Filename: "{app}\PyChemApp.exe"; IconFilename: "{app}\ico\pychem.ico"
Name: "{group}\Uninstall PyChem"; Filename: "{uninstallexe}"
Name: "{commondesktop}\PyChem"; Filename: "{app}\PyChemApp.exe"; IconFilename: "{app}\ico\pychem.ico"


