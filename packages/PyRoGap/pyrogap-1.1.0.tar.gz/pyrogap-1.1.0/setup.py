from setuptools import setup, find_packages

setup(
    name='PyRoGap',
    version='1.1.0',
    author='MohammadReza',
    author_email='narnama.room@gmail.com',
    description='This library helps you in building bots on the Gap messenger. PyRoGap is one of the best bot development libraries for Gap, and with it, you can create various types of bots. 🐍✨',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=[
        'requests',
        'beautifulsoup4'
    ],
    url='https://pyrogap.pythonanywhere.com/',
    project_urls={
        'مستندات کتابخانه 📚': 'https://pyrogap.pythonanywhere.com/',
        'صفحه من ❤️': 'https://apicode.pythonanywhere.com/',
        'مستندات ربات های گپ 📚' : 'https://my.gap.im/doc/botplatform',
        'کانال مستندات 📜' : 'https://gap.im/PyRoGap'
    },
)
