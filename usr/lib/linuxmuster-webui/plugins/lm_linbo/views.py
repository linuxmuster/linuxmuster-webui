import os

from jadi import component
from aj.auth import authorize
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lm_common.api import lm_backup_file


@component(HttpPlugin)
class Handler(HttpPlugin):
    LINBO_PATH = '/var/linbo'

    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/linbo/configs')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_configs(self, http_context):
        r = []
        for file in os.listdir(self.LINBO_PATH):
            if file.startswith('start.conf.'):
                if not os.path.islink(os.path.join(self.LINBO_PATH, file)):
                    r.append(file)
        return r

    @url(r'/api/lm/linbo/examples')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.startswith('start.conf.'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo/icons')
    @authorize('lm:linbo:icons')
    @endpoint(api=True)
    def handle_api_icons(self, http_context):
        return os.listdir(os.path.join(self.LINBO_PATH, 'icons'))

    @url(r'/api/lm/linbo/images')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_images(self, http_context):
        r = []
        for file in os.listdir(self.LINBO_PATH):
            if file.endswith(('.cloop', '.rsync')):
                desc_file = os.path.join(self.LINBO_PATH, file + '.desc')
                info_file = os.path.join(self.LINBO_PATH, file + '.info')
                reg_file = os.path.join(self.LINBO_PATH, file + '.reg')
                r.append({
                    'name': file,
                    'cloop': file.endswith('.cloop'),
                    'rsync': file.endswith('.rsync'),
                    'size': os.stat(os.path.join(self.LINBO_PATH, file)).st_size,
                    'description': open(desc_file).read() if os.path.exists(desc_file) else None,
                    'info': open(info_file).read() if os.path.exists(info_file) else None,
                    'reg': open(reg_file).read() if os.path.exists(reg_file) else None,
                })
        return r

    @url(r'/api/lm/linbo/image/(?P<name>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_image(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        desc_file = path + '.desc'
        info_file = path + '.info'
        reg_file = path + '.reg'
        if http_context.method == 'POST':
            data = http_context.json_body()
            if 'description' in data:
                if data['description']:
                    with open(desc_file, 'w') as f:
                        f.write(data['description'])
                else:
                    if os.path.exists(desc_file):
                        os.unlink(desc_file)
            if 'info' in data:
                if data['info']:
                    with open(info_file, 'w') as f:
                        f.write(data['info'])
                else:
                    if os.path.exists(info_file):
                        os.unlink(info_file)
            if 'reg' in data:
                if data['reg']:
                    with open(reg_file, 'w') as f:
                        f.write(data['reg'])
                else:
                    if os.path.exists(reg_file):
                        os.unlink(reg_file)
        else:
            for p in [path, desc_file, info_file, reg_file]:
                if os.path.exists(p):
                    os.unlink(p)

    @url(r'/api/lm/linbo/config/(?P<name>.+)')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_config(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)

        if http_context.method == 'GET':
            config = {
                'config': {},
                'partitions': [],
                'os': [],
            }
            for line in open(path):
                line = line.decode('utf-8', errors='ignore')
                line = line.split('#')[0].strip()

                if line.startswith('['):
                    section = {}
                    section_name = line.strip('[]')
                    if section_name == 'Partition':
                        config['partitions'].append(section)
                    elif section_name == 'OS':
                        config['os'].append(section)
                    else:
                        config['config'][section_name] = section
                elif '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip()
                    if v in ['yes', 'no']:
                        v = v == 'yes'
                    section[k.strip()] = v
            return config
        elif http_context.method == 'DELETE':
            lm_backup_file(path)
            os.unlink(path)
        elif http_context.method == 'POST':
            content = ''
            data = http_context.json_body()

            def convert(v):
                if type(v) is bool:
                    return 'yes' if v else 'no'
                return v

            for section_name, section in data['config'].items():
                content += '[%s]\n' % section_name
                for k, v in section.items():
                    content += '%s = %s\n' % (k, convert(v))
                content += '\n'
            for partition in data['partitions']:
                content += '[Partition]\n'
                for k, v in partition.items():
                    if k[0] == '_':
                        continue
                    content += '%s = %s\n' % (k, convert(v))
                content += '\n'
            for partition in data['os']:
                content += '[OS]\n'
                for k, v in partition.items():
                    content += '%s = %s\n' % (k, convert(v))
                content += '\n'

            lm_backup_file(path)
            with open(path, 'w') as f:
                f.write(content)
