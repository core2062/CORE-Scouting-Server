from passlib.context import CryptContext

pwd_context = CryptContext(
    # replace this list with the hash(es) you wish to support.
    # this example sets pbkdf2_sha256 as the default,
    # with support for legacy des_crypt hashes.
    schemes=["sha512_crypt"],
    default="sha512_crypt",

    # vary rounds parameter randomly when creating new hashes...
    all__vary_rounds = 0.1
    )