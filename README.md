# FILE ENCRYPTION APPLICATION

## Details about the app;

- Uses `Fernet` from `cryptography` library.
- Hashes the key with `SHA512` algorithm before using in encryption.
- Verifies the key before using in encryption or decryption to eliminate false results.
- Verification is based on using the key file created in first use.
- Exify.cmd can be used to build an exe application.
- Add the exe to the path to use from command line.

## Usage examples;

- Encryption: `crypt mypassword file.txt`
- Decryption: `crypt mypassword --decrypt encrypted_file.txt`
- Key reset: `crypt --reset mynewpassword`
- Help: `crypt -h` or `crypt --help`
