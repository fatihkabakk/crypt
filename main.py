from cryptography.fernet import Fernet, InvalidToken
from functools import wraps
from hashlib import sha512
import base64
import os


class FileEncryptor:
    def __init__(self, key: str) -> None:
        self._verified = False
        self._fernet = self._generate_fernet(key)
        self._verification_string = 'Verification sample'.encode()
        self._key_file = 'key.key'
        self.create_or_verify_key_file()
        # Workaround for wrapping methods
        self.encrypt = self.verification_required(self.encrypt)
        self.decrypt = self.verification_required(self.decrypt)

    def change_password(self, new_key: str):
        self._fernet = self._generate_fernet(new_key)
        self.create_key_file()

    def verification_required(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self._verified:
                return
            return func(*args, **kwargs)
        return wrapper

    def create_or_verify_key_file(self):
        """ If file exists, verifies the key, else creates a key file. """
        if os.path.isfile(self._key_file):
            if self.verify_key():
                self._verified = True
        else:
            self.create_key_file()

    def create_key_file(self):
        with open(self._key_file, 'wb') as f:
            f.write(self._fernet.encrypt(self._verification_string))
        print('New password saved!')

    def verify_key(self):
        with open(self._key_file, 'rb') as f:
            try:
                self._fernet.decrypt(f.read())
                return True
            except InvalidToken:
                return False

    @staticmethod
    def check_existing_file(original_file: str, created_file: str, operation: str):
        """ Checks if the existing file passes the given `operation` threshold-applied file size test.\n
            Threshold is `%120` for 'encryption' and `%70` for 'decryption'.\n
            Threshold can be set up to `%133 - 21944 bytes`, and `%74 - 16384 bytes`.
        """
        if not os.path.isfile(created_file):
            return False
        threshold = 1.2
        if operation == 'decrypt':
            threshold = 0.7
            # * DEBUG MESSAGES
            # print(f'File: {original_file}, Original: {os.stat(original_file).st_size}, Thresholded: {os.stat(original_file).st_size * threshold}, Created: {os.stat(created_file).st_size}')
            # print(f'[NEW] File: {original_file}, Original: {os.stat(original_file).st_size - 99}, Thresholded: {(os.stat(original_file).st_size - 99) * threshold}, Created: {os.stat(created_file).st_size}')
        # * -99 is for mini files ~100 bytes.
        return (os.stat(original_file).st_size - 99) * threshold < os.stat(created_file).st_size

    def encrypt(self, file_name: str):
        print('Current File:', file_name)
        read_bytes = 0
        file_size = os.stat(file_name).st_size
        new_file = self.construct_new_filename(file_name, 'Encrypted')
        if self.check_existing_file(file_name, new_file, 'encrypt'):
            self._progress(file_size, file_size)
            return new_file
        with open(file_name, 'rb', buffering=16384) as inp, open(new_file, 'wb', buffering=21944) as out:
            data = inp.read(16384)
            while data:
                encrypted_data = self._fernet.encrypt(data)
                out.write(encrypted_data)
                read_bytes += len(data)
                self._progress(file_size, read_bytes)
                data = inp.read(16384)
        return new_file

    def decrypt(self, file_name: str):
        read_bytes = 0
        file_size = os.stat(file_name).st_size
        new_file = self.construct_new_filename(file_name, 'Decrypted')
        if self.check_existing_file(file_name, new_file, 'decrypt'):
            self._progress(file_size, file_size)
            return new_file
        with open(file_name, 'rb', buffering=21944) as inp, open(new_file, 'wb', buffering=16384) as out:
            data = inp.read(21944)
            while data:
                decrypted_data = self._fernet.decrypt(data)
                out.write(decrypted_data)
                read_bytes += len(data)
                self._progress(file_size, read_bytes)
                data = inp.read(21944)
        return new_file

    @staticmethod
    def _progress(file_size: int, total_read: int):
        filler, empty = ('█', '░')
        end = '\r'
        if total_read == file_size:
            end = '\n'
        percentage = 100 * total_read / file_size
        divider = 2
        rounded = round(percentage // divider)
        remaining = (100 // divider) - rounded
        bar = f"{' ' * 32}\rProgress: {rounded * filler}{remaining * empty} %{rounded * divider}"
        print(bar, end=end, flush=True)

    @staticmethod
    def _generate_fernet(key: str):
        def generate_hash(text: 'bytes | str'):
            if not isinstance(text, bytes):
                text = text.encode()
            return sha512(text).digest()

        hash_32_chars = generate_hash(key)[:32]
        base64_encoded_hash = base64.urlsafe_b64encode(hash_32_chars)
        return Fernet(base64_encoded_hash)

    def construct_new_filename(self, path_like, prefix: str):
        splitted = path_like.split(os.sep)
        path = os.sep.join(splitted[:-1])
        if not path:
            path = '.'
        filename = splitted[-1]
        final_file_path = f'{path}{os.sep}{prefix}-{filename}'
        return final_file_path
