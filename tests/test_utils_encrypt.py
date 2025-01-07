def test_encrypt_decrypt(mock_fernet_encryption_key):
    from edutap.wallet_google.utils import decrypt_data
    from edutap.wallet_google.utils import encrypt_data

    data = "hypoknapsenverdraller"
    encrypted_data = encrypt_data(data)
    assert encrypted_data != data
    assert data == decrypt_data(encrypted_data)


def test_generate_fernet_key(capsys):
    from edutap.wallet_google.utils import generate_fernet_key

    generate_fernet_key()
    captured = capsys.readouterr()
    assert captured.out.endswith("=\n")
