from setuptools import setup, find_packages

setup(
    name="blackspammerbd_termux",  # PyPI তে "-" এর বদলে "_" ব্যবহার ভালো
    version="1.0.1",                # আপডেট ভার্সন
    author="BLACK SPAMMER BD",
    author_email="shawponsp6@gmail.com",  # এখানে তোমার ইমেইল দিতে পারো
    description="Auto Telegram backup tool for Termux",
    long_description=open("README.md", encoding="utf-8").read(),  # রিডমি ফাইল থেকে বিস্তারিত বর্ণনা
    long_description_content_type="text/markdown",
    url="https://github.com/BlackSpammerBd/blackspammerbd-termux",  # তোমার গিটহাব লিঙ্ক
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'blackspammerbd=blackspammerbd.monitor:main',  # তোমার মেইন ফাংশন যেখানে আছে
        ],
    },
)
