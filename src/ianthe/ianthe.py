import PyInstaller.__main__ as PyInst, os, pkgutil, shutil, sys, platform
from modulefinder import ModuleFinder
from pathlib      import Path

VERSION = "2023.12.17"

source           = "source"
destination      = "destination"
onefile          = "onefile"
keep             = "keep"
copy             = "copy"
folder           = "folder"
embed            = "embed"
file             = "file"
binary           = "binary"
hidden_imports   = "hidden-imports"
collect          = "collect"
data             = "data"
submodules       = "submodules"
binaries         = "binaries"
all              = "all"
copy_metadata    = "copy-metadata"
recursive        = "recursive"
modules          = "modules"
display_mode     = "display-mode"
windowed         = "windowed"
console          = "console"
icon             = "icon"
windows          = "win"
win              = "win"
version_file     = "version-file"
manifest         = "manifest"
embed_manifest   = "embed-manifest"
requires_admin   = "requires-admin"
osx              = "osx"
macOS            = "osx"
emul_argv        = "emul-argv"
target_arch      = "target-arch"
bundle_id        = "bundle-id"
entitlements     = "entitlements"
codesign_id      = "codesign-id"
pyinstaller_args = "pyinstaller-args"
scan             = "scan"
yes              = True
no               = False

_BASE_SCRIPT = """from os import chdir
from pathlib import Path
chdir(str(Path(__file__).parent.absolute()))
from ianthe import Ianthe
ianthe = Ianthe()
ianthe.config={}
ianthe.execute()
"""

_PY_STDLIB = {x: None for x in sys.stdlib_module_names}

HOME_DIR = os.getcwd()
PLATFORM = platform.system()

print(f"Ianthe source builder v{VERSION} - thatsOven")

class Ianthe:
    PATH = str(Path(__file__).parent.absolute())

    def __init__(self, fileName = None):
        global HOME_DIR

        if fileName is not None:
            try:
                config = eval("{" + self.__readFile(fileName) + "}")
            except Exception as e:
                print("invalid Ianthe project file. Error:\n", str(e))
                return
            
            if source not in config:
                print("invalid Ianthe project file. Missing source.")
                return
            
            HOME_DIR = str(Path(fileName).parent.absolute())
            self.config = config
        else:
            self.config = {}

    def __readFile(self, fileName):
        with open(fileName, "r", encoding = "utf-8") as f:
            return f.read()
        
    def generateScript(self):
        os.chdir(HOME_DIR)

        with open("build.py", "w", encoding = "utf-8") as f:
            f.write(_BASE_SCRIPT.format(str(self.config)))

        print(f"Build script saved to {os.path.join(HOME_DIR, 'build.py')}.")
        
    def __handleCollect(self, key, args, command):
        if key in self.config[collect]:
            if type(self.config[collect][key]) is not list:
                print(f'"collect: {key}" option requires a list as argument.\n Build aborted.')
                return
                
            for name in self.config[collect][key]:
                args += [
                    command, name
                ]

            del self.config[collect][key]

    def __handleOSXbasic(self, key, args, command):
        if key in self.config[osx]:
            args += [
                command, self.config[osx][key]
            ]

            del self.config[osx][key]
            
    def execute(self, export = False):
        os.chdir(HOME_DIR)
    
        print("Listing installed modules...")
        installed = [x.name for x in pkgutil.iter_modules()]

        if scan in self.config and not self.config[scan]:
            print("Scan is disabled. Including Python standard library.")
            used = _PY_STDLIB
        else:
            print("Looking for modules used by source...")
            try:
                modFinder = ModuleFinder()
                modFinder.run_script(self.config[source])
            except Exception as e:
                print("Something went wrong. Error:\n", str(e))
                return
            
            used = modFinder.modules

        if scan in self.config:
            del self.config[scan]
        
        print("Excluding unused modules...")

        workPath = os.path.join(Ianthe.PATH, "tmp")

        if os.path.exists(workPath):
            shutil.rmtree(workPath)

        args = [
            f"--workpath={workPath}",
            f"--specpath={workPath}",
            "--clean"
        ]

        if keep in self.config:
            if type(self.config[keep]) is not list:
                print('"keep" option requires a list as argument.\n Build aborted.')
                return
            
            for item in self.config[keep]:
                used[item] = None
            
            del self.config[keep]

        for name in installed:
            if name not in used:
                args += [
                    "--exclude-module", name
                ]

        print("Applying project settings...")

        if embed in self.config:
            if type(self.config[embed]) is not dict:
                print('"embed" option requires a dict as argument.\n Build aborted.')
                return
            
            for item in self.config[embed]:
                match self.config[embed][item]:
                    case "file":
                        args += [
                            "--add-data", item
                        ]
                    case "binary":
                        args += [
                            "--add-binary", item
                        ]
                    case _:
                        print(f'Unrecognized embed type "{item}".\nBuild aborted.')
                        return
            
            del self.config[embed]
                    
        if hidden_imports in self.config:
            if type(self.config[hidden_imports]) is not list:
                print('"hidden-imports" option requires a list as argument.\n Build aborted.')
                return
            
            for name in self.config[hidden_imports]:
                args += [
                    "--hiddenimport", name
                ]

            del self.config[hidden_imports]

        if collect in self.config:
            if type(self.config[collect]) is not dict:
                print('"collect" option requires a dict as argument.\n Build aborted.')
                return
            
            self.__handleCollect(      data, args, "--collect-data")
            self.__handleCollect(submodules, args, "--collect-submodules")
            self.__handleCollect(  binaries, args, "--collect-binaries")
            self.__handleCollect(       all, args, "--collect-all")

            if len(self.config[collect]) != 0:
                print('Unrecognized options in "collect".\nBuild aborted.')
                return
            
            del self.config[collect]
            
        if copy_metadata in self.config:
            if type(self.config[copy_metadata]) is not dict:
                print('"copy-metadata" option requires a dict as argument.\n Build aborted.')
                return
            
            if recursive in self.config[copy_metadata]:
                if type(self.config[copy_metadata][recursive]) is not bool:
                    print('"copy-metadata: recursive" option requires a boolean argument.\n Build aborted.')
                    return
                
                recursive = True
            else: recursive = False

            if modules not in self.config[copy_metadata]:
                print('"copy-metadata" option requires a "modules" option.\n Build aborted.')
                return
            
            if recursive:
                for name in self.config[copy_metadata][modules]:
                    args += [
                        "--recursive-copy-metadata", name
                    ]
            else:
                for name in self.config[copy_metadata][modules]:
                    args += [
                        "--copy-metadata", name
                    ]

            del self.config[copy_metadata]

        if display_mode in self.config:
            match self.config[display_mode]:
                case "windowed":
                    args.append("--windowed")
                case "console":
                    args.append("--console")
                case _:
                    print('unrecognized option in "display-mode".\nBuild aborted.')
                    return
                
            del self.config[display_mode]
        
        os.mkdir(workPath)
        if icon in self.config:
            iconName = os.path.basename(self.config[icon])
            shutil.copy(self.config[icon], os.path.join(workPath, iconName))

            args.append(f"--icon={iconName}")
            del self.config[icon]
        else:
            shutil.copy(
                os.path.join(Ianthe.PATH, "icon.ico"), 
                os.path.join(   workPath, "icon.ico")
            )

            args.append(f"--icon=icon.ico")

        if windows in self.config:
            if type(self.config[windows]) is not dict:
                print('"windows" option requires a dict as argument.\n Build aborted.')
                return
            
            if version_file in self.config[windows]:
                args += [
                    "--version-file", self.config[windows][version_file]
                ]

                del self.config[windows][version_file]

            if manifest in self.config[windows]:
                args += [
                    "--manifest", self.config[windows][version_file]
                ]

                del self.config[windows][manifest]

            if embed_manifest in self.config[windows]:
                if type(self.config[windows][embed_manifest]) is not bool:
                    print('"windows: embed-manifest" option requires a boolean argument.\n Build aborted.')
                    return
                
                if not self.config[windows][embed_manifest]:
                    args.append("--no-embed-manifest")

                del self.config[windows][embed_manifest]

            if requires_admin in self.config[windows]:
                if type(self.config[windows][requires_admin]) is not bool:
                    print('"windows: requires-admin" option requires a boolean argument.\n Build aborted.')
                    return
                
                if self.config[windows][requires_admin]:
                    args += [
                        "--uac-admin",
                        "--uac-uiaccess"
                    ]

                del self.config[windows][requires_admin]

            if len(self.config[windows]) != 0:
                print('Unrecognized options in "windows".\nBuild aborted.')
                return
            
            del self.config[windows]

        if osx in self.config:
            if type(self.config[osx]) is not dict:
                print('"osx" option requires a dict as argument.\n Build aborted.')
                return
            
            if emul_argv in self.config[osx]:
                if type(self.config[osx][emul_argv]) is not bool:
                    print('"osx: emul-argv" option requires a boolean argument.\n Build aborted.')
                    return
                
                if self.config[osx][emul_argv]:
                    args.append("--argv-emulation")

                del self.config[osx][emul_argv]

            if target_arch in self.config[osx]:
                if self.config[osx][target_arch] not in ("x86_64", "arm64", "universal2"):
                    print('"osx: target-arch" requires either "x86_64", "arm64" or "universal2".\n Build aborted.')
                    return
                
                args += [
                    "--target-architecture", self.config[osx][target_arch]
                ]

                del self.config[osx][target_arch]

            self.__handleOSXbasic(   bundle_id, args, "--osx-bundle-identifier")
            self.__handleOSXbasic(entitlements, args, "--osx-entitlements-file")
            self.__handleOSXbasic( codesign_id, args, "--codesign-identity")

            if len(self.config[osx]) != 0:
                print('Unrecognized options in "osx".\nBuild aborted.')
                return
            
            del self.config[osx]

        toCopy = []
        if copy in self.config:
            if type(self.config[copy]) is not dict:
                print('"copy" option requires a dict as argument.\n Build aborted.')
                return
            
            for item in self.config[copy]:
                if self.config[copy][item] not in (file, folder):
                    print('unrecognized option in "copy".\nBuild aborted.')
                    return
                
                toCopy.append((
                    self.config[copy][item],
                    item
                ))

            del self.config[copy]

        if pyinstaller_args in self.config:
            if type(self.config[pyinstaller_args]) is not list:
                print('"pyinstaller-args" option requires a list as argument.\n Build aborted.')
                return
            
            args += self.config[pyinstaller_args]

            del self.config[pyinstaller_args]

        distPath = None
        if destination in self.config:
            distPath = self.config[destination]
            args.append(f"--distpath={distPath}")
            del self.config[destination]

        if onefile in self.config:
            if type(self.config[onefile]) is not bool:
                print('"onefile" option requires a boolean argument.\n Build aborted.')
                return

            if self.config[onefile]:
                args.append("--onefile")

            del self.config[onefile]
            onefile_ = True
        else: onefile_ = False

        args.append(self.config[source])
        dirName = os.path.basename(self.config[source]).split(".")[0]
        del self.config[source]

        if len(self.config) != 0:
            print('Unrecognized options in project file.\nBuild aborted.')
            return
        
        if export:
            print("Final arguments:\n", str(args))
            return
            
        print("Done. Calling PyInstaller.")
        PyInst.run(args)

        print("Finished. Cleaning up...")
        shutil.rmtree(os.path.join(Ianthe.PATH, "tmp"))

        print("Copying data...")
        for item in toCopy:
            if onefile_:
                  joined = os.path.join(distPath, os.path.basename(item[1]))
            else: joined = os.path.join(distPath, dirName, os.path.basename(item[1]))

            if item[0] == file:
                shutil.copy(item[1], joined)
            else:
                shutil.copytree(item[1], joined)

        print("Done.")

def _main():
    generateScrip = False
    export        = False

    if "--generate-build-script" in sys.argv:
        sys.argv.remove("--generate-build-script")
        generateScrip = True
    elif "--export" in sys.argv:
        sys.argv.remove("--export")
        export = True

    if len(sys.argv) < 2:
        quit()
    
    if generateScrip:
        Ianthe(sys.argv[1]).generateScript()
    else:
        Ianthe(sys.argv[1]).execute(export)
    