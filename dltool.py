#!env python


import os
import sys

sys.path.append(os.path.abspath('plugin.video.xvisi/resources/lib'))

import argparse
import requests

from xvisi import all_sites, get_sources_for


class InputSource(object):
    def __init__(self, inputs=[]):
        self.inputs = inputs

    def next_line(self, prompt):
        print '%s:' % prompt,
        if self.inputs:
            val = self.inputs.pop(0)
            print val
            return val
        while True:
            inp = raw_input().decode('utf8').strip()
            if inp:
                return inp

    def get_int(self, msg, max=None):
        while True:
            v = self.get_str(msg)
            try:
                v = int(v)
            except ValueError:
                continue

            if max is not None:
                if v > max:
                    continue

            return v

    def get_str(self, msg):
        return self.next_line(msg)

    def get_choice(self, items, msg, multiple=False, everything='all'):
        msg = msg or 'Pick one'

        for num, (_, text) in enumerate(items):
            print '%s: %s' % (num, text)

        if multiple:
            msg += ' (space separated, "%s" for all items)' % (everything,)
            while True:
                values = []
                inp = self.get_str(msg)
                if inp == everything:
                    return [k for k, v in items]

                for v in inp.split():
                    try:
                        v = int(v)
                    except ValueError:
                        values = None
                        break
                    if v >= len(items):
                        values = None
                        break

                    values.append(items[v][0])

                if values is None:
                    continue

                return values
        else:
            choice = self.get_int(msg, max=num)
        return items[choice][0]


parser = argparse.ArgumentParser()
parser.add_argument('inputs', nargs='*')
args = parser.parse_args()

input_source = InputSource(args.inputs)

search = input_source.get_str('Enter search terms')
print 'Searching for %r' % search

choices = []
for site_id, site in all_sites.items():
    for t, key, title in site.search(search):
        choices.append((
            (site_id, key, t),
            '(%s) (%s) %s' % (site_id, t, title)
        ))

site_id, key, t = input_source.get_choice(choices, 'Select a result')

# now get seasons
site = all_sites[site_id]
assert t == 'TVSHOW'

seasons = input_source.get_choice(
    site.get_seasons(key), 'Select seasons', multiple=True,
)

for season in seasons:
    print 'Season', season
    all_episodes = site.get_episodes(season)
    episodes = input_source.get_choice(
        [(ep, ep[1]) for ep in all_episodes],
        'Select episode',
        multiple=True,
    )

    for episode, title in episodes:
        chosen_source = None
        for url, source_name in site.get_sources(episode):
            sources = get_sources_for(url)
            if sources:
                break

        if not sources:
            print 'no source for', title
            continue

        source = sources[0]
        video_url = source.get_video_url(url)

        r = requests.get(video_url, stream=True)
        outfile = title

        print 'video url', video_url
        print 'out', outfile
        with open(outfile, 'w') as out:
            for chunk in r.iter_content():
                out.write(chunk)

