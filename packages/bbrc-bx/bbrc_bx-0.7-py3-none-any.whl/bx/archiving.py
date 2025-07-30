from bx.command import Command


class ArchivingCommand(Command):
    """Archiving - Collect automatic tests from MRI or PET session Validators.

    Available subcommands:
     mri:\t\tcreates an Excel table with all automatic tests outcomes from `ArchivingValidator`
     pet:\t\tcreates an Excel table with all automatic tests outcomes from `PetSessionValidator`

    Usage:
     bx archiving <subcommand> <resource_id>
    """
    nargs = 2
    validator_name = 'ArchivingValidator'
    subcommands = ['mri', 'pet']

    def __init__(self, *args, **kwargs):
        super(ArchivingCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]
        if subcommand == 'pet':
            self.validator_name = 'PetSessionValidator'

        version = ['*', '0390c55f']

        from bx import validation as val
        df = self.run_id(id, val.validation_scores,
                         validator=self.validator_name,
                         version=version, max_rows=25)
        self.to_excel(df)
