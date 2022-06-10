from main import FileEncryptor
import argparse
import sys
import os


def main():
    try:
        parser = argparse.ArgumentParser(
            prog='crypt', description='example: crypt mypassword file_path', add_help=False)
        parser.add_argument('key', metavar='key', type=str,
                            help='Key for encrypting and decrypting files. Key is saved once and verified on consequent uses. Key can be changed using --reset option.', nargs='?' if '--reset' in sys.argv else None, default='')
        parser.add_argument('--decrypt', dest='task', action='store_const',
                            const='decrypt', default='encrypt', help='Set the program to decryption mode, the default is encryption.')
        parser.add_argument('file', metavar='file', type=str,
                            help='Path of the file to process. Supports wildcard (*).', nargs='?' if '--reset' in sys.argv else None, default=None)
        parser.add_argument('--reset', dest='reset',
                            help='Changes the password and re-creates the key test file. (Might be changed in the future)', metavar='NEW_PASSWORD')
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')

        args = parser.parse_args()
        crypt = FileEncryptor(args.key)

        if args.reset:
            crypt.change_password(args.reset)
            exit(0)

        """ if not args.key or not args.file:
            parser.print_usage()
            if not args.key and not args.file:
                print(
                    f'{parser.prog}: error: missing positional arguments: key, file')
            else:
                print(f'{parser.prog}: error: missing positional argument: file')
            exit(1) """
        method = getattr(crypt, args.task)
        if args.file == '*':
            for file in [i for i in os.listdir('.') if os.path.isfile(i)]:
                method.__call__(file)
        else:
            method.__call__(args.file)

    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            sys.exit('\n')
        if not isinstance(exc, SystemExit):
            print(f'{exc.__class__.__name__}: {exc}')


if __name__ == '__main__':
    main()
