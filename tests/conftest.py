import os
import tempfile

os.environ.setdefault("SUPPORT_COPILOT_DATA", tempfile.mkdtemp(prefix="support-copilot-test-"))
