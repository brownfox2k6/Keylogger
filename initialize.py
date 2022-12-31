from cryptography.fernet import Fernet
from pickle import dump

fernet = Fernet(Fernet.generate_key())
dump(fernet, open("key.pkl", "wb"))