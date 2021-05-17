# remote mover

A tool to efficiently move data on remote servers to mimic the PDS. It should be
run before robo copy whenever there is a change to the moves database.

## Deploy

Copy the repository to a test or production location. After testing, you can
delete the `test` folder. You will want to edit the `config_file.py` to change
from testing to production settings.

If you do not want to use the `--since` command line option, you will need to
create a file called `timestamp` in this folder. It should have one line with a
year,month,day,hour,minute,second,microsecond. For example: `2021,5,17,0,0,0,0`.
This should be the last time the remote mover was run, or the last time the
moves database was changed, or the last time robo copy to all parks was run,
which ever was most recent. No processing will occur if a valid timestamp for
`since` can be determined.

## Usage

`remote-mover` can be run from the command line or as a scheduled task
by someone with read permissions to the database path and write permission
to the remote servers.

use `remote-mover --help` to see the command options.

Defaults for database and remote server paths can be configured in
`config_file.py`. The values for "Production" should work with the standard
configuration of the AIS server.
