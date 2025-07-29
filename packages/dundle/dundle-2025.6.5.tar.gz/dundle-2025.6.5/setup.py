import setuptools
import dundle

setuptools.setup(
    name = "dundle",
    version = "2025.6.5",
    description = dundle.__doc__.splitlines()[0],
    long_description = dundle.__doc__,
    long_description_content_type = "text/plain",
    classifiers = [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    license = "0BSD",
)
