import sys
import msvcrt

def hidden_text(prompt='Password: '):
    """
    Securely prompts the user for a password with masked input (using asterisks '*') on Windows.
    >>> hidden_text('Enter your secreat text: ')
    """
    print(prompt, end='--> ', flush=True)
    password = ''
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:
            print()
            break
        elif ch == b'\x08':  # Backspace
            if password:
                password = password[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif ch == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            try:
                char = ch.decode('utf-8')
            except UnicodeDecodeError:
                continue
            password += char
            sys.stdout.write('*')
            sys.stdout.flush()
    return password
