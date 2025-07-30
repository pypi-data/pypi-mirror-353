import os
from voicecrypt import encrypt_audio, decrypt_audio

def test_encrypt_decrypt(tmp_path):
    # Create a dummy audio file
    audio_path = tmp_path / "test.wav"
    with open(audio_path, "wb") as f:
        f.write(os.urandom(1024))  # 1KB random bytes
    enc_path = tmp_path / "enc.txt"
    dec_path = tmp_path / "dec.wav"
    password = "testpass"
    encrypt_audio(str(audio_path), str(enc_path), password)
    decrypt_audio(str(enc_path), str(dec_path), password)
    # Check that decrypted file matches original
    with open(audio_path, "rb") as f1, open(dec_path, "rb") as f2:
        assert f1.read() == f2.read() 