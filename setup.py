from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
extensions = [
    Extension(
        "shop.recommendation_cython",
        ["shop/recommendation_cython.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-O3'],
    )
]
setup(
    name="recommendation_cython",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
)