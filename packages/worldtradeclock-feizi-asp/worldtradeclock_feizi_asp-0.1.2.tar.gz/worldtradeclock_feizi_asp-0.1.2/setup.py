from setuptools import setup, find_packages

setup(
    name="worldtradeclock-feizi-asp",
    version="0.1.2",
    description="World financial market open/close & volume tracker",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Prof.Dr Feizi & Ahad Esmaeilzadeh",
    author_email="taimazus@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pytz", "pandas", "requests", "arabic-reshaper", "python-bidi"
    ],
    license="MIT"
)
