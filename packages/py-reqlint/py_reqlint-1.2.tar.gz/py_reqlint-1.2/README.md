# ReqLint

Quickly lint your python files to detect if you're using requests library without specifying a timeout value

## Quick Start
* `pip install py-reqlint`
* `python -m reqlint --help`
```python
from reqlint import ReqLint

with open('your_file.py', 'r') as f:
    code = f.read()

for issue in ReqLint.lint(code):
    print(issue)
```


### Why?
- [Nearly all production code should use this parameter in nearly all requests. Failure to do so can cause your program to hang indefinitely](https://docs.python-requests.org/en/latest/user/quickstart/#timeouts)
