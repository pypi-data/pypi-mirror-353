import json

import click

from . import register_parser

from . import NTFYClientRealTime

@click.group
def cli():
    pass

@cli.command()
def pub():
    @register_parser
    def return_json(raw_data):
        #  import json
        #  json_notification = json.dumps(raw_data)
        #
        #  print(json_notification)
        #
        #  #return json_notification

        client = NTFYClientRealTime()
        client.run_forever()

        ntfy_client = NTFYClient(hostname=NTFY_SERVER_HOSTNAME,
                                topic=NTFY_TOPIC,
                                token=NTFY_TOKEN,
                                args=args)

        r = ntfy_client.pub()
        response_data = json.dumps(r.json(), indent=2)
        print("Response data:", response_data, sep="\n")
#  @cli.command()
#  def json():
#      @register_parser
#      def return_json(raw_data):
#          import json
#          json_notification = json.dumps(raw_data)
#
#          print(json_notification)
#
#          #return json_notification
#
#      client = NTFYClientRealTime()
#      client.run_forever()

if __name__ == "__main__":

    cli()

