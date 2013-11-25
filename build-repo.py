#!env python

from cStringIO import StringIO
import hashlib
import os
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree
from tempdir import TempDir


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
        print 'walking', addon_dir
        for dirpath, dirs, files in os.walk(addon_dir):
            relpath = os.path.relpath(dirpath, addon_dir)

            for fn in files:
                file_path = os.path.join(dirpath, fn)

                if os.path.exists(file_path):
                    z.write(file_path, arcname=os.path.join(relpath, fn))


REPO = 'repository.xvisi'


if __name__ == '__main__':
    root_dir = os.path.abspath(os.path.dirname(__name__))

    # create temporary directory
    with TempDir() as _build_dir:
        # different tempdir versions =(
        if hasattr(_build_dir, 'name'):
            build_dir = _build_dir.name
        else:
            build_dir = _build_dir

        # first, create repo zip file
        repo_zipfn = os.path.join(build_dir, REPO + '.zip')
        repo_addon_fn = os.path.join(root_dir, REPO, 'addon.xml')
        with ZipFile(repo_zipfn, 'w', ZIP_DEFLATED) as z:
            z.write(repo_addon_fn,
                    arcname=os.path.basename(repo_addon_fn))

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

        # go over each addon and create zip file
        for addon in addons_node.findall('addon'):
            zipname = '%(id)s.%(version)s.zip' % addon.attrib
            addon_dir = os.path.join(build_dir, addon.attrib['id'])
            zippath = os.path.join(addon_dir, zipname)

            # create addon dir
            os.mkdir(addon_dir)

            package_addon(zippath, os.path.join(root_dir, addon.attrib['id']))
