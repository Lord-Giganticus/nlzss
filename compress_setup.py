from cx_Freeze import setup, Executable

base = None    

executables = [Executable("compress.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Compress",
    options = options,
    version = "1.0.0.0",
    description = "Compresses a file using Nintendo's lz11 compression.",
    executables = executables
)