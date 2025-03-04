# Issues

### Crazy issue with autorun left behind on windows

After uninstalling a bungled miniforge install, a weir issue surfaced
that any start of cmd.exe triggered a `The system cannot find the path
specified` error. This was super-difficult to track down and pinpoint
the cause. It also made using any of the `subprocess.run` commands
fail as they all got a non-zero return value. Arggggh!

After much googling and testing various hypotheses I came across this
post:

https://superuser.com/questions/727316/error-in-command-line-the-system-cannot-find-the-path-specified

This was the solution. It turned out to be an autorun left behind from
that previous miniforge install. I edited the registry and unset the
autorun value to an empty string. Windows is crazy!

###  Things that may need attention

- when environment name given needs to make build dir name derived on that
 - on creation of new conda env check for uniqueness of build_dir
 