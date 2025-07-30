from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='calc_figure_area',
    version='0.0.6',
    description='This library is test library.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=['calc_figure_area'],
    author='VasilekN',
    author_email='',
    keywords=['calc figure area'],
    url='https://github.com/VasilekN/MB_tasks'
)
