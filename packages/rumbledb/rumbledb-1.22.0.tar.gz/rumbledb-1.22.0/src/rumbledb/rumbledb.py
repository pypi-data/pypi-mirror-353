from IPython.core.magic import Magics, cell_magic, magics_class
import requests, json, time
import os
from pprint import pprint

@magics_class
class RumbleDBServerMagic(Magics):
    def run(self, line, cell=None, timed=False):
        if cell is None:
            data = line
        else:
            data = cell

        start = time.time()
        try:
            r = requests.post(os.environ["RUMBLEDB_SERVER"], data=data)
        except ConnectionError as e:
            print("Query unsuccessful.")
            print("Usual reasons: firewall, misconfigured proxy, no RumbleDB server running at this host and port.")
            print("Error message:")
            print(e.args[0])
            return
        except Exception as e:
            print("Query unsuccessful.")
            print("Usual reasons: firewall, misconfigured proxy, no RumbleDB server running at this host and port.")
            print("Error message:")
            print(e.args[0])
            return
        except:
            print("Query unsuccessful.")
            print("Usual reasons: firewall, misconfigured proxy, no RumbleDB server running at this host and port.")
            return
        end = time.time()
        if(r.status_code != 200):
            print("Query unsuccessful. Status code: %s" % r.status_code)
            print("Usual reasons: firewall, misconfigured proxy, no RumbleDB server running at this host and port.")
            print("HTTP response body:")
            print(r.text)
            return
        response = r.json()
        if(timed):
           print("Response time: %s ms" % (end - start))

        if 'warning' in response:
            print(json.dumps(response['warning']))
        if 'values' in response:
            for e in response['values']:
                print(json.dumps(e))
        elif 'error-message' in response:
            return print(response['error-message'])
        else:
            return print(response)

    @cell_magic
    def jsoniq(self, line, cell=None):
        return self.run(line, cell, False)

    @cell_magic
    def timedjsoniq(self, line, cell=None):
        return self.run(line, cell, True)

