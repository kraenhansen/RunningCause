from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from Running.models import User, Run
import requests
import json
import datetime
import time

class Command(BaseCommand):
    help = 'Updates the runs of all users that have registered with runkeeper'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        if datetime.datetime.today().weekday() == 0:
            users_with_tokens = User.objects.exclude(access_token="")
            for user in users_with_tokens:
                r = requests.get('https://api.runkeeper.com/fitnessActivities', headers={'Authorization': 'Bearer %s' % user.access_token})
                data = r.json()
                print data['items']
                for item in data['items']:
                    print item['total_distance']
                runkeeper_runs = user.runs.filter(source="runkeeper")
                registered_ids = [run.source_id for run in runkeeper_runs]
                for item in data['items']:
                    if item['uri'] not in registered_ids:
                        date = time.strptime(item['start_time'][5:16], "%d %b %Y")
                        date = datetime.datetime(*date[:6]).date()
                        new_run = Run(runner=user, distance=item['total_distance']/1000, start_date=date, end_date=date, source="runkeeper", source_id=item['uri'])
                        new_run.save()

            self.stdout.write('Successfully updated runs')

            everyone_else = User.objects.filter(access_token="")

            all_addresses = []
            for user in everyone_else:
                if user.email != None:
                    all_addresses += [user.email]
            all_addresses = [i for i in all_addresses if i != '']
            for address in all_addresses:
                if address:
                    send_mail('Reminder', 
                                'Hello! Since you\'re not using runkeeper to automatically keep your runs updated, you should probably enter your runs on Masanga Runners!' , 
                                'postmaster@appa4d174eb9b61497e90a286ddbbc6ef57.mailgun.org', 
                                [address], 
                                fail_silently=False)

            self.stdout.write('Sent reminder mail')