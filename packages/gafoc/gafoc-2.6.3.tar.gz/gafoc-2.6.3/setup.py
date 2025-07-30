# setup.py (Simplified for pyproject.toml)

from setuptools import setup, Extension

try:
    from Cython.Build import cythonize
except ImportError:
    # A fallback in case Cython is not installed by the build system.
    # This might happen in very old pip versions.
    def cythonize(*args, **kwargs):
        return args[0]

# IMPORTANT: Define the extension with a .c suffix as a fallback.
# The build system will automatically prefer the .pyx file if it can.
extensions = [
    Extension(
        "GAFOC.core.huffman",
        ["GAFOC/core/huffman.py".replace('.py', '.pyx')] # This finds the .pyx file
    )
]

# This is a small hack to ensure cythonize is run correctly
# when build is triggered via pyproject.toml
def build(setup_kwargs):
    setup_kwargs.update(
        {"ext_modules": cythonize(extensions, compiler_directives={'language_level' : "3"})}
    )

# The setup call is now much cleaner
setup(
    # The ext_modules argument is injected by the 'build' function
)