from cx_Freeze import setup, Executable

base = None    

executables = [Executable("lzss3.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Decompress",
    options = options,
    version = "1.0.0.0",
    description = "Decompress a file that uses Nintendo's lz11 compression.",
    executables = executables
)