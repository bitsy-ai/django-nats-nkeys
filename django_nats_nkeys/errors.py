import subprocess


class NscError(Exception):
    def __init__(self, message: str, error: subprocess.CalledProcessError):
        super().__init__(message)

        self.error = error

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d. Output: %s" % (
            self.error.cmd,
            self.error.returncode,
            self.error.output,
        )


class NscConflict(NscError):
    def __init__(self, message: str, error: subprocess.CalledProcessError):
        super().__init__(message, error)

    def __str__(self):
        return "Command %s returned error code %s. Resource already exists: %s" % (
            self.error.cmd,
            self.error.returncode,
            self.error.output,
        )


class NscStreamExportConflict(NscError):
    def __init__(self, message: str, error: subprocess.CalledProcessError):
        super().__init__(message, error)

    def __str__(self):
        return "Command %s returned error code %s. Stream export already exists. %s" % (
            self.error.cmd,
            self.error.returncode,
            self.account,
        )
