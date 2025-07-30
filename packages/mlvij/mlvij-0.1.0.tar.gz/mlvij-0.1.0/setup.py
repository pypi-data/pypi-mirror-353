from setuptools import setup, find_packages
setup(
    name='mlvij',
    version='0.1.0',
    description='ML Short programs: 10 mini machine learning/data analysis scripts',
    author='Vijay C S',
    author_email='vijaygowdavijaygowda838@gmail.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'scikit-learn'
    ],
    python_requires='>=3.7',
)
