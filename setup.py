import setuptools
import os

with open(os.path.abspath('./req_freeze.txt'), encoding='utf-8') as f:
    requirements = f.readlines()
requires = [x.strip() for x in requirements]

# Taken from https://github.com/psf/requests/blob/main/setup.py#L76
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "askyourdocs", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)


# https://stackoverflow.com/a/36693250
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths
extra_files = package_files('resources')


setuptools.setup(
    name='askyourdocs',
    version=about["__version__"],
    author="LLM Taskforce",
    description="Ask your documents project by the international llm taskforce",
    packages=setuptools.find_packages(),
    package_dir={'askyourdocs': 'askyourdocs'},
    entry_points={
        'console_scripts': [
            'ayd = askyourdocs.main:main',
        ],
    },
    package_data={'askyourdocs': extra_files},
    install_requires=requires
)

