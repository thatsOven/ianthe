![](logo.png)
# Ianthe
Ianthe is a Python executables build tool that generates PyInstaller commands and executes them, aiming to achieve more compact executables with a simpler syntax.
# Installation
```
pip install ianthe
```
# Terminal usage
```
python -m ianthe project_file.iproj
```
# Command line arguments
- `--export`: Prints out the generated PyInstaller arguments and quits.
- `--generate-build-script`: Generates a Python script that executes the given project file.
# Python usage
```py
from ianthe import Ianthe

Ianthe("project_file.iproj").execute()
```
# Setting up a project file
## The structure
A Ianthe project file gets interpreted as a Python `dict` (outermost curly braces get added by Ianthe itself). It's composed of options, all of which (aside `source`) are optional. The order of options doesn't matter. Example:
```
source:       "test.py",
destination:  "my_folder",
display_mode: console,
icon:         "icon.ico"
```
## The options
### `source` or `"source"`
Specifies which file should be built. Requires a `str` or a path-like argument.
### `destination` or `"destination"`
Specifies where the result should be saved. Requires a `str` or a path-like argument.
### `onefile` or `"onefile"`
Equivalent to PyInstaller's `--onefile` argument. Specifies whether a single executable should be built instead of a folder. Requires a `bool` argument (`True`, `False`, `yes` or `no`)
### `scan` or `"scan"`
Enables (`True` or `yes`) or disables (`False` or `no`) used modules scanning and keeps Python's standard library. Default is `True`.
### `keep` or `"keep"`
Tells Ianthe to keep some specific modules. Useful when the result of an application built using Ianthe is broken due to some missing modules that Ianthe can't find. Requires a `list` argument containing module names.
### `copy` or `"copy"`
If data needs to be copied to the result folder, you can specify which files and folders need to be copied. Requires a `dict` argument containing the file or folder path as key and `file`, `"file"`, `folder` or `"folder"` as value to specify the type of data. Example:
```
copy: {
	"my_folder": folder,
	"my_file.txt": file
}
```
### `embed` or `"embed"`
Equivalent to PyInstaller's `--add-data` and `--add-binary` arguments. Requires a `dict` argument containing the file path as key and `file`, `"file"`, `binary` or `"binary"` as value to specify the type of data.
### `hidden_imports` or `"hidden-imports"`
Equivalent to PyInstaller's `--hidden-import` argument. Requires a `list` argument containing module names.
### `collect` or `"collect"`
Requires a `dict` argument specifying the type of `collect` command, and a list of modules that needs that type of data as value:
- `data` or `"data"`
	- Equivalent to PyInstaller's `--collect-data` argument.
- `submodules` or `"submodules"`
	- Equivalent to PyInstaller's `--collect-submodules` argument.
- `binaries` or `"binaries"`
	- Equivalent to PyInstaller's `--collect-binaries` argument.
- `all` or `"all"`
	- Equivalent to PyInstaller's `--collect-all` argument.
### `copy_metadata` or `"copy-metadata"`
Requires a `dict` argument that contains a `modules` or `"modules"` argument as key and a `list` containing module names as value. Equivalent to PyInstaller's `--copy-metadata` unless a `recursive` or `"recursive"` option is used and set to a `True` (or `yes`) value. In that case, it's equivalent to `--recursive-copy-metadata`. Example:
```
copy_metadata: {
	recursive: yes,
	modules: [
		"my_module0",
		"my_module1"
	]
}
```
### `display_mode` or `"display-mode"`
Requires either `console`, `"console"`, `windowed` or `"windowed"`. 
### `icon` or `"icon"`
Sets the program's icon. Requires a `str` or a path-like argument.
### `windows`, `win` or `"win"`
Requires a `dict` containing Windows specific options.
- `version_file` or `"version-file"`
	- Equivalent to PyInstaller's `--version-file` argument.
- `manifest` or `"manifest"`
	- Equivalent to PyInstaller's `--manifest` argument.
- `embed_manifest` or `"embed-manifest"`
	- If set to a `False` (or `no`) value, it's equivalent to PyInstaller's `--no-embed-manifest` argument.
- `requires_admin` or `"requires-admin"`
	- If set to a `True` (or `yes`) value, it's equivalent to PyInstaller's `--uac-admin`  and `--uac-uiaccess` arguments.
### `osx`, `macOS` or `"osx"`
Requires a `dict` containing macOS specific options.
- `emul_argv` or `"emul-argv"`
	- If set to a `True` (or `yes`) value, it's equivalent to PyInstaller's `--argv-emulation` argument.
- `target_arch` or `"target-arch"`
	- Equivalent to PyInstaller's `--target-architecture` argument. It only accepts as values: "x86_64", "arm64" and "universal2".
- `bundle_id` or `"bundle-id"`
	- Equivalent to PyInstaller's `--osx-bundle-identifier` argument.
- `entitlements` or `"entitlements"`
	- Equivalent to PyInstaller's `--osx-entitlements-file` argument.
- `codesign_id` or `"codesign-id"`
	- Equivalent to PyInstaller's `--codesign-identity` argument.
### `pyinstaller_args` or `"pyinstaller-args"`
Adds additional PyInstaller arguments. Requires a `list` argument containing PyInstaller arguments.