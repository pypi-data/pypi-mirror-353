from setuptools import setup, find_packages

setup(
    name='chinese_lunar_calendar_converter',
    version='0.1.0',
    author='VerNe', # 请替换为您的名字
    author_email='yuu_seeing@foxmail.com', # 请替换为您的邮箱
    description='A Python package for converting between Gregorian and Lunar calendars.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ID-VerNe/lunar_calendar', # 请替换为您的项目URL
    packages=find_packages(),
    install_requires=[
        'ephem',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
