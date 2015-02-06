from django.db.migrations.operations.base import Operation


class LoadExtension(Operation):

    reversible = True

    def __init__(self, name):
        self.name = name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS %s" % self.name)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("DROP EXTENSION %s" % self.name)

    def describe(self):
        return "Creates extension %s" % self.name


class AddRule(Operation):

    reversible = True

    def __init__(self, name, table, event, rule):
        self.name = name
        self.table = table
        self.event = event
        self.rule = rule

    def state_forwards(self, *args, **kwargs):
        pass

    def get_rule(self):
        return 'CREATE RULE "%s" AS ON %s TO "%s" %s' % (
            self.name,
            self.event,
            self.table,
            self.rule,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(self.get_rule())

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute('DROP RULE "%s" ON "%s"' % (self.name, self.table))

    def describe(self):
        return "Creates rule: %s" % (self.get_rule(),)
