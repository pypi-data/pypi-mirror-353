from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Powerful web pentester suite developed by BLACK SPAMMER BD."

setup(
    name="blackspammerbd-webmaster",
    version="1.0.0",
    author="BLACK SPAMMER BD",
    author_email="shawponsp6@gmail.com",
    description="A powerful and modular web penetration testing toolkit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlackSpammerBd/blackspammerbd_webmaster",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.20.0",
        "beautifulsoup4>=4.9.0",
        "colorama>=0.4.3"
    ],
    entry_points={
        "console_scripts": [
            "sp=blackspammerbd_webmaster.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.6',
    keywords="pentest blackspammerbd web-security hacking toolkit",  # ⭐ searchable keywords
    project_urls={  # ⭐ extra links
        "Source Code": "https://github.com/BlackSpammerBd/blackspammerbd_webmaster",
        "Bug Tracker": "https://github.com/BlackSpammerBd/blackspammerbd_webmaster/issues",
        "Team": "https://facebook.com/original.Typeboss.ur.father"
    },
)
