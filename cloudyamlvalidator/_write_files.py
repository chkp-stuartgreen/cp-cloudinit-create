import base64
import re
from pathlib import Path


def write_files(self, section):
    for file in section:
        path = file["path"]
        # Verify the path is not an existing directory
        if Path(path).is_dir():
            self._raise_error("While validate file %s: path is a directory. Please insert a different path.")

        content = file.get("content", "")
        # We check content's data type here since jsonschema do not support validation of binary datatype
        if type(content) not in [str, bytes]:
            self._raise_error("While validate file %s: Content's data type must be rather string OR bytes (Got %s)"
                              % (path, str(type(content))))

        # Encoding validation
        self._validate_encoding(file)


def _validate_encoding(self, file):
    path = file["path"]
    encoding = file.get("encoding", "text/plain")
    content = file.get("content", "")

    # No encoding validation
    if encoding == "text/plain":
        return
    # base64 validation
    elif encoding in ["b64", "base64"]:
        self._is_base64(path, content)
    # gzip validation
    elif encoding in ["gz", "gzip"]:
        self._is_gzip(path, content)
    # gzip + base64 validation
    else:
        self._is_base64(path, content)
        content = base64.b64decode(content)
        self._is_gzip(path, content)


def _is_base64(self, path, content):
    # Base64 format must be given as 'string' data-type
    content_type = type(content)
    if content_type is not str:
        self._raise_error("While validate file %s: 'base64' content must be in type 'str' (Got '%s')." %
                          (path, content_type.__name__))
    # Content must only include lower/upper case characters, '+', '/' and '=' (which must be used last as padding)
    re_str = r'^[a-zA-z0-9+/]*=*$'
    matched = re.match(re_str, content)
    if not bool(matched):
        self._raise_error("While validate file %s: 'base64' content is not match the pattern %s" % (path, re_str))

    # For every 3 input bytes (24 bits), four 6-bits base64 alphabets characters are used
    length = len(content)
    if length % 4 != 0:
        self._raise_error("While validate file %s: 'base64' content's length must be divided by 4 (Got %d)." %
                          (path, length))


def _is_gzip(self, path, content):
    # Base64 format must be given as 'binary' data-type
    content_type = type(content)
    if content_type is not bytes:
        self._raise_error("While validate file %s: 'gzip' content must be in type 'binary' (Got '%s')." %
                          (path, content_type.__name__))

    # Each gzip header must start with '\x1f\x8b' magic number
    hex_str = content.hex()
    if hex_str[:4] != '1f8b':
        self._raise_error("While validate file %s: 'gzip' content must start with 'magic number' prefix '\\x1f\\x8b'" % path)
