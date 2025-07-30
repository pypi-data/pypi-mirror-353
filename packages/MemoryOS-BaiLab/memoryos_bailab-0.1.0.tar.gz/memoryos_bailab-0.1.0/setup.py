from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="MemoryOS-BaiLab",
    version="0.1.0",
    author="Jiazheng Kang",
    author_email="2457516191@qq.com",
    description="一个智能记忆管理系统，支持短期、中期和长期记忆存储与检索",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["memdemo", "memdemo.*", "tests", "tests.*"]),
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai",
        "numpy",
        "sentence-transformers",
        "faiss-gpu",
        "Flask",
        "httpx[socks]",
    ],
    keywords=["memory", "ai", "llm", "conversation", "chatbot", "openai"],
) 