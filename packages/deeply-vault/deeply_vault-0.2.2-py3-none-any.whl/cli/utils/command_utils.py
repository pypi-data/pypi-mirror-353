import click


class CustomMultiCommand(click.Group):
    def command(self, *args, **kwargs):
        def decorator(f):
            if not args:
                return super(CustomMultiCommand, self).command(**kwargs)(f)
                
            if isinstance(args[0], list):
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    cmd = super(CustomMultiCommand, self).command(
                        alias, *args[1:], **kwargs)(f)
                    cmd.short_help = "Alias for '{}'".format(_args[0])
            else:
                _args = args
            cmd = super(CustomMultiCommand, self).command(
                *_args, **kwargs)(f)
            return cmd

        return decorator