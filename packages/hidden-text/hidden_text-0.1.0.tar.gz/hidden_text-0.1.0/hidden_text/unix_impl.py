import sys
import tty
import termios

def hidden_text(prompt='Password: '):
    """
    Securely prompts the user for a password with masked input (using asterisks '*') on Windows.
    >>> hidden_text('Enter your secreat text: ')
    """
    print(prompt, end='--> ', flush=True)
    password = ''
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch in ('\r', '\n'):
                print()
                break
            elif ch == '\x7f':  # Backspace
                if password:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif ch == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write('*')
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password
