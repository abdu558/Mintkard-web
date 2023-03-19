def hash_password(password):
    # Start with a random seed
    seed = 0xcafebabe

    # Iterate over each character in the password
    for c in password:
        # Convert the character to a number
        n = ord(c)

        # Rotate the seed left by 4 bits
        seed = (seed << 4) | (seed >> 28)

        # XOR the seed with the character code
        seed = seed ^ n

    # Convert the seed to a hex string and return it
    return hex(seed)[2:]

print(hash_password('hello'))