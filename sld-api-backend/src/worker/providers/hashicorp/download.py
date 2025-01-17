import os
import stat
import zipfile
from io import BytesIO

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from config.api import settings


class BinaryDownload:
    def __init__(self, version):
        self.version = version

    def get(self) -> dict:
        binary = f"{settings.TERRAFORM_BIN_REPO}/{self.version}/terraform_{self.version}_linux_amd64.zip"
        try:
            if not os.path.exists(f"/tmp/{self.version}"):
                os.mkdir(f"/tmp/{self.version}")
            if not os.path.isfile(f"/tmp/{self.version}/terraform"):
                req = requests.get(binary, verify=False)
                _zipfile = zipfile.ZipFile(BytesIO(req.content))
                _zipfile.extractall(f"/tmp/{self.version}")
                st = os.stat(f"/tmp/{self.version}/terraform")
                os.chmod(f"/tmp/{self.version}/terraform", st.st_mode | stat.S_IEXEC)
            return {
                "command": "binaryDownload",
                "rc": 0,
                "stdout": "Download Binary file",
            }

        except Exception as err:
            return {"command": "binaryDownload", "rc": 1, "stdout": err}
