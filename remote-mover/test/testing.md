# Testing

In lieu of automated testing, I am providing some instructions and files for
doing semi automated testing.

The folder `servers` is the mount point for the simulated servers.
`moves.csv` is a sample moves database.  These two paths can be set as the
defaults for `MOUNT_POINT` and  `MOVES_DB` respectively in `config_file.py`
or they can be provided as command line options `-m` and `-d` respectively to
`remote_mover.py`.

Before and after testing `servers/serverA` and `servers/serverB` can be
checked and or restored to their original state by comparing with
`server_backup`.  If needed restore the server to it's original state, or
remove and replace with a copy of `server_backup`.

## Tests

Each of the Configuration defaults in `config_file.py` should be tested with
no value, various valid values, and various invalid values. Similarly for each
command line option (provide command line option `-h` to see the other options).

The moves database should have some records before the `since` date in the
timestamp file (or command line option) that will not happen (or generate a
warning), as well as other records that will be tested.  Move tests should
include:

* Valid: source directory exists and destination does not - change occurs.
  Make sure source directory does not exist, and destination does exist (
  with the source contents) after the test.
* Invalid: source directory does not exist - warning with no change.
  Make sure source directory exists unchanged after the test.
* Invalid: destination directory exists - warning with no change.
  Make sure destination folder exists unchanged after the test.

Verify the tests occur on both servers (if a mount point is specified), or
only on the single server specified (if the `-s` option is used).
