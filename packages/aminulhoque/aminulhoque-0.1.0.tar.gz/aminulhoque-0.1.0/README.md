# aminulhoque

Encrypt and decrypt audio files as text for secure voice messaging.

## Features
- Encrypt audio files (WAV, MP3, etc.) to text files using AES encryption
- Decrypt encrypted text files back to audio
- Password-based encryption (PBKDF2)
- Simple API

## Installation
```sh
pip install aminulhoque
```

## Usage
```python
from aminulhoque import encrypt_audio, decrypt_audio

encrypt_audio('input.wav', 'encrypted.txt', password='mysecret')
decrypt_audio('encrypted.txt', 'restored.wav', password='mysecret')
```

## Author
- **Aminul Hoque**  
  [GitHub: AminulHoquecode](https://github.com/AminulHoquecode)  
  Email: aminul98547@gmail.com

## License
MIT 