#!/usr/bin/env python3

from git import Repo

from pgpy.constants import (
    PubKeyAlgorithm,
    EllipticCurveOID,
    KeyFlags,
    CompressionAlgorithm,
    ECPointFormat,
)
from pgpy.packet import PrivKeyV4
from pgpy.packet.types import MPI
from pgpy.packet.fields import ECDSAPriv, ECPoint
from pgpy import PGPKey, PGPUID, PGPSignature

from sdkms.v1 import (
    configuration,
    ApiClient,
    AuthenticationApi,
    SecurityObjectsApi,
    SignAndVerifyApi,
    SignRequest,
    SobjectRequest,
)
from sdkms.v1.models.digest_algorithm import DigestAlgorithm
from sdkms.v1.models.elliptic_curve import EllipticCurve
from sdkms.v1.models.object_type import ObjectType
from sdkms.v1.models.key_operations import KeyOperations
from sdkms.v1.rest import ApiException

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives import hashes

import argparse
import base64
import dateutil.parser
import os
from pathlib import Path
import sys
import traceback
import warnings


# The built-in function `next()` raises an `StopIteration` exception if iterator
# is exhausted which is not desirable when using exceptions for error handling
# in main. This function passes a default value of None so `next()` does not
# raise an exception.
def next_or_none(iter):
    return next(iter, None)


class ECDSASDKMS(ECDSAPriv):
    def __init__(self, api_client, key):
        ECDSAPriv.__init__(self)

        self.sdkms_api_client = api_client
        self.sdkms_uuid = key.kid

        if key.elliptic_curve == EllipticCurve.NISTP256:
            self.oid = EllipticCurveOID(EllipticCurveOID.NIST_P256)
        elif key.elliptic_curve == EllipticCurve.NISTP384:
            self.oid = EllipticCurveOID(EllipticCurveOID.NIST_P384)
        elif key.elliptic_curve == EllipticCurve.NISTP521:
            self.oid = EllipticCurveOID(EllipticCurveOID.NIST_P521)
        else:
            raise NotImplementedError(
                "unsupported elliptic curve: " + str(key.elliptic_curve)
            )
        pn = load_der_public_key(
            bytes(key.pub_key), backend=default_backend()
        ).public_numbers()
        self.p = ECPoint.from_values(self.oid.key_size, ECPointFormat.Standard, MPI(pn.x), MPI(pn.y))
        self._compute_chksum()

    def sign(self, sigdata, hash_alg):
        if hash_alg.name == "sha1":
            api_alg = DigestAlgorithm.SHA1
        elif hash_alg.name == "sha256":
            api_alg = DigestAlgorithm.SHA256
        elif hash_alg.name == "sha384":
            api_alg = DigestAlgorithm.SHA384
        elif hash_alg.name == "sha512":
            api_alg = DigestAlgorithm.SHA512
        else:
            raise NotImplementedError("unsupported hash algorithm: " + str(hash_alg))
        digest = hashes.Hash(hash_alg, backend=default_backend())
        digest.update(sigdata)

        req = SignRequest(hash=bytearray(digest.finalize()), hash_alg=api_alg)
        return (
            SignAndVerifyApi(api_client=self.sdkms_api_client)
            .sign(self.sdkms_uuid, req)
            .signature
        )


class PrivKeySDKMS(PGPKey):
    METADATA_KEY = "pgp-public-key"

    def __init__(self, api_client, uuid):
        PGPKey.__init__(self)

        try:
            k = SecurityObjectsApi(api_client).get_security_object(uuid)
        except ApiException as e:
            raise Exception(
                f"could not get key from server. Status Code: {e.status}. Reason: {e.reason}. Message: {e.body}"
            )
        # Construct the PGPKey object with our customized keymaterial type.
        # This code is based on the PGPKey.new function, which can't be used
        # directly since it always calls `keymaterial._generate`. That function
        # unconditionally raises an error for unknown keymaterial types.
        pk = PrivKeyV4()
        pk.pkalg = PubKeyAlgorithm.ECDSA
        pk.keymaterial = ECDSASDKMS(api_client, k)
        pk.created = dateutil.parser.parse(k.created_at)
        pk.update_hlen()

        self._key = pk

        # Load the PGP Public Key from the key's custom metadata, or create and
        # store a new PGP Public Key if it doesn't exist yet.
        k.custom_metadata = k.custom_metadata or {}
        if PrivKeySDKMS.METADATA_KEY in k.custom_metadata:
            pubk = PGPKey()
            pubk.parse(k.custom_metadata[PrivKeySDKMS.METADATA_KEY])
            if pubk.fingerprint != self.fingerprint:
                raise ValueError("invalid public key found in metadata")
            self |= next_or_none(iter(pubk.userids))
        else:
            uid = PGPUID.new(k.name)
            self.add_uid(
                uid,
                usage={KeyFlags.Sign},
                hashes=[pk.keymaterial.oid.kdf_halg],
                ciphers=[],
                compression=[CompressionAlgorithm.Uncompressed],
            )
            k.custom_metadata[PrivKeySDKMS.METADATA_KEY] = str(self.pubkey)
            SecurityObjectsApi(api_client).update_security_object(
                k.kid, {"custom_metadata": k.custom_metadata}
            )


def create_key(api_client, args):
    key = SecurityObjectsApi(api_client).generate_security_object(
        SobjectRequest(
            name=args.name,
            obj_type=ObjectType.EC,
            elliptic_curve=args.curve,
            key_ops=[
                KeyOperations.SIGN,
                KeyOperations.APPMANAGEABLE,
                KeyOperations.VERIFY,
            ],
        )
    )
    print(key.kid)


def output_status(args, msg):
    file = sys.stdout
    if args.status_fd == 2:
        file = sys.stderr
    print(msg, file=file)


def get_git_config_value(config1, config2):
    r = Repo(os.getcwd(), search_parent_directories=True)
    reader = r.config_reader()
    try:
        return reader.get_value(config1, config2)
    except:
        return None


def get_api_endpoint(args):
    if args.api_endpoint:
        return args.api_endpoint
    endpoint = get_git_config_value("sdkms", "endpoint")
    if endpoint is None:
        endpoint = os.getenv("SDKMS_API_ENDPOINT")
        if endpoint is None:
            raise Exception(
                "need to specify --api-endpoint or 'git config --local sdkms.endpoint <value>' or set SDKMS_API_ENDPOINT environment variable.",
            )
    return endpoint


def get_api_key(args):
    if args.api_key:
        return args.api_key
    api_key = get_git_config_value("sdkms", "apikey")
    if api_key is None:
        api_key = os.getenv("SDKMS_API_KEY")
        if api_key is None:
            raise Exception(
                "need to specify --api-key or 'git config --local sdkms.apikey <value>' or set SDKMS_API_KEY environment variable.",
            )
    return api_key


def auth_sdkms(args):
    api_key = base64.b64decode(get_api_key(args)).decode("ascii")
    parts = api_key.split(":")
    if len(parts) != 2:
        raise Exception("invalid API key provided")

    config = configuration.Configuration()
    config.username = parts[0]
    config.password = parts[1]

    config.verify_ssl = not args.no_verify_ssl
    config.host = get_api_endpoint(args)

    api_client = ApiClient(configuration=config)

    auth = AuthenticationApi(api_client).authorize()

    # The swagger interface calls this type of authorization an 'apiKey'.
    # This is not related to the SDKMS notion of an API key. The swagger
    # apiKey is our auth token.
    config.api_key["Authorization"] = auth.access_token
    config.api_key_prefix["Authorization"] = "Bearer"

    return api_client


def verify_signature(api_client, args):
    key_uuid = get_git_config_value("user", "signingkey")
    key = PrivKeySDKMS(api_client, key_uuid)
    data = sys.stdin.buffer.read()
    sig_data = Path(args.verify).read_text()
    signature = PGPSignature.from_blob(sig_data)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        signature_verification = key.verify(data, signature)

    sigsubj = next_or_none(signature_verification.good_signatures)
    if signature_verification.__bool__():
        print(
            "sdkms: Signature made {} using ECDSA key ID {}".format(
                sigsubj.signature.created, sigsubj.by
            ),
            file=sys.stderr,
        )
        output_status(args, f"\n[GNUPG:] GOODSIG {key_uuid}")
    else:
        raise Exception("sdkms: Signature could not be verified")


def sign(api_client, args):
    key_uuid = get_git_config_value("user", "signingkey")
    data = sys.stdin.buffer.read()
    key = PrivKeySDKMS(api_client, key_uuid)
    sig = key.sign(data)
    print(sig, end="")
    output_status(args, f"\n[GNUPG:] SIG_CREATED ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="utility for signing/verifying git commits with keys stored in Fortanix Data Security Manager.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--api-endpoint",
        action="store",
        help="SDKMS API endpoint to connect to. This can be specified using `git config sdkms.apikey` or by setting environment variable SDKMS_API_KEY.",
    )

    parser.add_argument(
        "--api-key",
        action="store",
        help="Env variable name of API Key",
    )

    # The following set of args are compatible with gpg
    parser.add_argument("--verify", metavar="FILE", help="verify signature")
    parser.add_argument(
        "--status-fd",
        metavar="FD",
        help="GPG style status fd",
        type=int,
        choices=[1, 2],
        default=1,
    )

    parser.add_argument("--no-verify-ssl", action="store_true", help="don't verify SSL")

    parser.add_argument("command", nargs="?", action="store")
    parser.add_argument("name", nargs="?", action="store")
    parser.add_argument("curve", nargs="?", action="store")

    args, _ = parser.parse_known_args()

    if args.command == "create":
        if args.name is None or args.curve is None:
            parser.error("create requires name and curve")

    return args


def main_impl():
    args = parse_args()
    api_client = auth_sdkms(args)

    if args.command == "create":
        create_key(api_client, args)
    elif args.verify is not None:
        verify_signature(api_client, args)
    else:
        sign(api_client, args)

    AuthenticationApi(api_client).terminate()


def main():
    try:
        main_impl()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
