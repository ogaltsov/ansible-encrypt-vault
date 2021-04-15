#!/usr/bin/python3

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# heavily borrows from this excellent repo https://github.com/dellis23/ansible-toolkit


import argparse
import errno
import os

from ansible_vault import Vault
from ansible.parsing.vault import AnsibleVaultError
from termcolor import colored


# ===================================================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vault-password-file', type=str,
                        help="Path to vault password file")
    parser.add_argument('-p', '--vault-path', type=str,
                        help="Path to vault password file")
    args = parser.parse_args()

    if args.vault_password_file is None:
        print(colored("Vault password file path is not determined", "red"))
        quit()
    if args.vault_path is None:
        print(colored("Vault path is not determined", "red"))
        quit()

    try:
        encryptCandidates = get_encrypt_candidates_in_vault(args.vault_path)
        decrypt_vault_files(args.vault_password_file, encryptCandidates)

    except Exception as ex:
        print(colored("Unexpected exception: " + str(ex), "red"))
        quit()

# ===================================================================================

# find all files that have the ansible vault header
def get_encrypt_candidates_in_vault(vaultPath):

    if not os.path.exists(vaultPath) or not os.path.isdir(vaultPath):
        raise RuntimeError(
            "Invalid path: there ara no directory at: " + vaultPath)

    vault_encrypt_candidate_files = []

    for dirpath, dirnames, filenames in os.walk(vaultPath):

        for name in filenames:

            filePath = os.path.join(dirpath, name)

            # find all files with the ansible vault header
            with open(filePath, 'rb') as open_file:
                first_line = open_file.readline()

                if first_line.startswith(str.encode('$ANSIBLE_VAULT;')):
                    vault_encrypt_candidate_files.append(filePath)

    return vault_encrypt_candidate_files

# ===================================================================================

def decrypt_vault_files(vaultPasswordPath, encryptCandidatePathList):
    # load vault password into memory
    with open(vaultPasswordPath, 'r') as vault_password_file:
        vaultPassword = vault_password_file.read().strip()

    # create a new Vault instance with the
    vault = RawVault(vaultPassword)

    # iterate over the list of vaulted files
    for vaultedFilePath in encryptCandidatePathList:
        print(colored("Ansible file processing: " + vaultedFilePath, "green"))

        # decrypt the file
        try:
            decryptedFileContents = vault.load_raw(open(vaultedFilePath).read())

            # write the decrypted data to disk
            with open(vaultedFilePath, 'wb') as decryptedVaultFile:
                decryptedVaultFile.write(decryptedFileContents)

        except AnsibleVaultError as ex:
            print(colored("Error file processing: " + ex.message, "red"))

# ===================================================================================

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# ===================================================================================

# extend Vault to allow for raw
# https://stackoverflow.com/a/50859586/1053741
class RawVault(Vault):
    def load_raw(self, stream):
        return self.vault.decrypt(stream)

    def dump_raw(self, text, stream=None):
        encrypted = self.vault.encrypt(text)
        if stream:
            stream.write(encrypted)
        else:
            return encrypted

