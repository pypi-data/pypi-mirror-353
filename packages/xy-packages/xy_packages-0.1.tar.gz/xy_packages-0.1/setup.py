from setuptools import setup, find_packages

setup(
  name='xy_packages',
  version='0.1',
  packages=find_packages(),
  install_requires=[],
  author='Michael xu',
  author_email='kbb@qq.com',
  description='for ai-agent\'s prompt array.',
  classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',  # 许可证类型
    'Operating System :: OS Independent',
  ],
  python_requires='>=3.6',
)
