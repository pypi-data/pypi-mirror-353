'''
# Clean and rebuild (note twine needs to be installed (see requirements.txt))
rm -rf build/ dist/ SurvSet.egg-info/
python -m build

# Check the pickle files are included
tar -tzf dist/SurvSet-0.2.9.tar.gz | grep 'pickle'
tar -tzf dist/SurvSet-0.2.9.tar.gz | grep 'df_ds.csv'
unzip -l dist/SurvSet-0.2.9-py3-none-any.whl | grep 'pickle'

# Try the Test PyPI upload
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Go to a different folder (e.g. ~/Downloads)

# in main folder
rm dist/SurvSet* 
python setup.py bdist_wheel --universal

# on some test conda env
twine upload --repository-url https://test.pypi.org/legacy/ dist/SurvSet*
pip uninstall SurvSet
pip install --index-url https://test.pypi.org/simple/ SurvSet --user

# Upload to PyPI: https://pypi.org/project/SurvSet/
twine upload dist/SurvSet*
pip uninstall SurvSet
pip install SurvSet
'''


from setuptools import setup, find_packages

setup(
    name="SurvSet",
    version="0.2.9",  # remember to change this in the __init_.py too!
    description="SurvSet: A Python package for loading survival datasets",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/ErikinBC/SurvSet',
    author='Erik Drysdale',
    author_email='erikinwest@gmail.com',
    license='GPLv3',
    license_files = ('LICENSE.txt'),
    packages=find_packages(include=["SurvSet", "SurvSet.*"]),
    include_package_data=True,
    package_data={
        "SurvSet.resources.pickles": ["*.pickle", "df_ds.csv"],
    },
    python_requires=">=3.7",
    install_requires=[
        'numpy', 'pandas'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
    ],
)
