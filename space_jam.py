from datetime import datetime
from google.appengine.api import validation
from google.appengine.api import yaml_object
from StringIO import StringIO


DATE_FORMATS = ["%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y"]


class DateTimeValidator(validation.Validator):

    def Validate(self, value, key='???'):
        """ Validate that a given 'value' is a datetime or a string
                that can be interpreted as one.
        """
        if isinstance(value, datetime):
            return value

        for date_format in DATE_FORMATS:
            try:
                return datetime.strptime(value, date_format)
            except ValueError:
                pass

        raise validation.ValidationError('Datetime validation error - \
                              must follow one of the formats {}'.format(DATE_FORMATS))

    def ToValue(self, value):
        """ Convert a given datetime to a string
                for writing back to YAML.
        """
        return value.strftime(DATE_FORMATS[0])


POSITIONS = ['PG', 'SG', 'PF', 'SF', 'C']


class Player(validation.Validated):
    ATTRIBUTES = {
        'name': validation.TYPE_UNICODE,
        'position': validation.Options(*POSITIONS),
    }


class InvalidRoster(validation.ValidationError):
    pass


class Roster(validation.Validated):
    ATTRIBUTES = {
        'name': validation.TYPE_UNICODE,
        'player_count': validation.TYPE_INT,
        'players': validation.Repeated(Player),
        'want_to_fly_like_an_eagle': validation.Optional(validation.TYPE_BOOL, True),
        'inception_date': DateTimeValidator(),
    }

    def has_every_position_filled(self):
        return all(position in [player.position for player in self.players] for position in POSITIONS)

    def CheckInitialized(self):
        super(Roster, self).CheckInitialized()
        if not self.has_every_position_filled():
            raise InvalidRoster('Every position must be filled.')


def build_objects(file_content, validated_class):
    """
    file_content - YAML file content
    validated_class - class to build the file content into
    """
    content_stream = StringIO(file_content)
    built_tuple = yaml_object.BuildObjects(validated_class, content_stream)
    if not built_tuple:
        return None
    return built_tuple[0]


def announce_squad(file_content):
    try:
        roster = build_objects(file_content, Roster)
    except validation.ValidationError, e:
        print 'Invalid roster file!'
        print e
    else:
        print 'Ladies and gentlemen: The starting lineup for {}!'.format(roster.name)
        for player in roster.players:
            print 'At {}, {}!'.format(player.position, player.name)

SAMPLE_YAML = """
    name: The Toon Squad
    player_count: 5
    players:
    - name: The Tasmanian Devil
      position: C
    - name: Lola Bunny
      position: SF
    - name: Daffy Duck
      position: PF
    - name: Bugs Bunny
      position: PG
    - name: Michael Jordan
      position: SG
    inception_date: 11/15/96
"""            

    
if __name__ == "__main__":
    announce_squad(SAMPLE_YAML)
