import os

from linktools import utils
from linktools.cli import UpdateCommand, DevelopUpdater, GitUpdater, PypiUpdater

from . import metadata

command = UpdateCommand(
    metadata.__name__,
    updater=utils.coalesce(*[
        DevelopUpdater(os.path.dirname(__file__)) if metadata.__develop__ else None,
        GitUpdater() if not metadata.__release__ else None,
        PypiUpdater()
    ])
)
if __name__ == '__main__':
    command.main()
