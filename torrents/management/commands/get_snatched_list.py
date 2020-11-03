from django.core.management import BaseCommand
from plugins.redacted.client import RedactedClient
from trackers.registry import TrackerRegistry, PluginMissingException
import sys
class Command(BaseCommand):
    help='Outputs snatch list for a tracker. If no output specified, prints to STDOUT'

    def get_snatched(self, tracker, tracker_name, output):
        output.write(tracker_name)

        # if getattr(tracker, 'get_snatched', None) is None:
        #     print('Tracker plugin does not support get_snatched')
        #     return
        # This API does not exist
        # snatched_list = tracker.get_snatched(offset, limit)


        client = RedactedClient()
        offset = 0
        limit = 500
        snatch_list = []
        snatch_part_list = client.get_snatched(offset, limit)['snatched']
        while len(snatch_part_list) != 0:
            for torrent in snatch_part_list:
                snatch_list.append(int(torrent['torrentId']))
            offset += limit
            snatch_part_list = client.get_snatched(offset, limit)['snatched']
        for id in snatch_list:
            output.write('\n' + str(id))
        return

    def add_arguments(self, parser):
        parser.add_argument(
            '--tracker',
            help='Name of tracker, example: redacted',
            type=str,
            required=True
        )
        parser.add_argument(
            '--output',
            help='Where to output the list\nExample: /path/to/redacted_snatched.txt',
            type=str
        )

    def handle(self, *args, **options):
        try:
            tracker = TrackerRegistry.get_plugin(options['tracker'], self.__class__.__name__)
        except PluginMissingException:
            print('Tracker plugin not found')
            return

        if options['tracker'] != 'redacted':
            print('Only redacted supported so far')
            return

        output = sys.stdout
        if options['output']:
            output = open(options['output'],'w')
        self.get_snatched(tracker, options['tracker'], output)