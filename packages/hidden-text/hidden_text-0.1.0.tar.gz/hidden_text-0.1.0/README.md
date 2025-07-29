# hidden_text

A simple, cross-platform Python module to securely accept password input in the terminal with masked characters (`*`).

## Features

- Supports Windows, Linux, macOS
- Masks password characters with asterisks
- Works in real-time in the terminal

## Example

```python
from hidden_text import hidden_text

password = hidden_text("Enter your password: ")
print("You entered:", password)
