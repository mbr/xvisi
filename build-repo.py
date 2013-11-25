#!env python

from cStringIO import StringIO
from dulwich.repo import Repo
import hashlib
import os
import requests
import subprocess
from urlparse import urlparse
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree
from tempdir import TempDir
from unleash.git import export_to_dir


def collect_addons(addons_root):
    repo_root = etree.Element('addons')
    for name in os.listdir(addons_root):
        path = os.path.join(addons_root, name)
        addon_xml = os.path.join(path, 'addon.xml')
        if not os.path.exists(addon_xml):
            continue

        addon_tree = etree.parse(addon_xml)
        repo_root.append(addon_tree.getroot())
    return etree.ElementTree(repo_root)


def package_addon(zipfn, addon_dir):
    print 'packaging from', addon_dir, 'into', zipfn

    with ZipFile(zipfn, 'w', ZIP_DEFLATED) as z:
        for dirpath, dirs, files in os.walk(addon_dir):
            relpath = os.path.join(
                os.path.basename(addon_dir),
                os.path.relpath(dirpath, addon_dir)
            )

            for fn in files:
                file_path = os.path.join(dirpath, fn)

                if os.path.exists(file_path):
                    z.write(file_path, arcname=os.path.join(relpath, fn))


REPO = 'repository.xvisi'
DEP_REPO_URL = ('http://mirrors.xbmc.org/addons/eden/'
                '%(addon)s/%(addon)s-%(version)s.zip')


if __name__ == '__main__':
    # create temporary directory
    with TempDir() as build_dir, TempDir() as root_dir:
        print 'checking out clean master...'
        repo = Repo(os.path.abspath(os.path.dirname(__name__)))
        master_commit_id = repo.refs['refs/heads/master']
        export_to_dir(repo, master_commit_id, root_dir)

        print 'collecting addons'
        # collect addon information
        addons_node = collect_addons(root_dir)
        buf = StringIO()
        addons_node.write(buf,
                          encoding='utf8',
                          xml_declaration=True)

        # write addons.xml and addons.xml.md5
        addons_xml_fn = os.path.join(build_dir, 'addons.xml')
        addons_sig_fn = addons_xml_fn + '.md5'
        infoxml = buf.getvalue()
        with open(addons_xml_fn, 'w') as addons_xml,\
                open(addons_sig_fn, 'w') as addons_sig:

                addons_xml.write(infoxml)
                addons_sig.write(hashlib.md5(infoxml).hexdigest())

        dependencies = set()
        # go over each addon and create zip file
        for addon in addons_node.findall('addon'):
            zipname = '%(id)s.%(version)s.zip' % addon.attrib
            addon_dir = os.path.join(build_dir, addon.attrib['id'])
            zippath = os.path.join(addon_dir, zipname)

            # create addon dir
            os.mkdir(addon_dir)

            package_addon(zippath, os.path.join(root_dir, addon.attrib['id']))

            # if the addon is our repo zip, link inside root
            if addon.attrib['id'] == REPO:
                os.symlink(os.path.join(addon.attrib['id'], zipname),
                           os.path.join(build_dir,
                                        addon.attrib['id'] + '.zip'))

            # collect dependencies
            reqs = addon.find('requires')
            if reqs is not None:
                for imp in reqs.findall('import'):
                    # skip xbmc. deps, those ship already
                    if imp.attrib['addon'].startswith('xbmc.'):
                        continue

                    dependencies.add((DEP_REPO_URL % imp.attrib,
                                      imp.attrib['addon']))

        print 'collecting dependencies...'
        for url, name in dependencies:
            print url
            fn = urlparse(url).path.rsplit('/', 1)[-1]
            dep_path = os.path.join(build_dir, name)

            if not os.path.exists(dep_path):
                os.mkdir(dep_path)

            target = os.path.join(dep_path, fn)
            r = requests.get(url)
            with open(target, 'w') as t:
                t.write(r.content)

        import pdb
        pdb.set_trace()
        print 'creating new commit'
        subprocess.check_call(
            ['gittar', 'file:%s/*' % build_dir, 'file:%s/.*' % build_dir,
             '-b', 'gh-pages']
        )
