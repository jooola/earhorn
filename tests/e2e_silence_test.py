from pathlib import Path
from time import sleep

from earhorn.silence import SilenceListener

here = Path(__file__).parent
SAMPLE = here / "sample.ogg"
HOOK = here / "fake-hook.sh"
LOG = Path("silence.log")


def test_silence_listener():
    thread = SilenceListener(SAMPLE, HOOK)
    thread.start()
    sleep(30)
    thread.join()

    assert LOG.is_file()
    assert len(LOG.read_text(encoding="utf-8").splitlines()) == 4
    LOG.unlink()
