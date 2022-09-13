import os
import sys
import json
import yaml
import requests
import base64

engine = sys.argv[1]
token = sys.argv[2]
vault = sys.argv[3]
try: 
    basepath = sys.argv[4]
except:
    basepath = './'

headers = {
    'X-Vault-Token': token
}

def remove_special(data:dict):
    sk = ['__filename__', '__type__', '__path__']
    newdata = {}
    for k, v in data.items():
        if k not in sk:
            newdata[k] = v
    return newdata

def write_env(data:dict, dest:str):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.isfile(dest):
        open(dest, 'w', encoding='utf-8').close()
    for k, v in data.items():
        with open(dest, 'a', encoding='utf-8') as f:
            f.write(f"{k}={v}\n")

def write_txt(data:dict, dest:str):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.isfile(dest):
        open(dest, 'w', encoding='utf-8').close()
    for k, v in dict(sorted(data.items(), key=lambda x: int(x[0]))).items():
        with open(dest, 'a', encoding='utf-8') as f:
            f.write(f"{data[k]}\n")

def write_yaml(data:dict, dest:str):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(yaml.dump(data))

def write_json(data:dict, dest:str):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
            
def write_file(data:dict, dest:str):
    data = base64.b64decode(data)
    with open(dest, 'w') as f:
        f.write(data.decode('utf-8').replace('\n', ''))

r = requests.request('LIST',f"{vault}/v1/{engine}/metadata", headers=headers)
secrets = json.loads(r.text)['data']['keys']


for s in secrets:
    r = requests.request('GET', f"{vault}/v1/{engine}/data/{s}", headers=headers)
    data = json.loads(r.text)['data']['data']
    try:
        stype = data['__type__']
    except:
        stype = s.split('.')[0]
    try:
        sname = data['__filename__']
    except:
        if '.' in s:
            sname = '.'.join(s.split('.')[1:])
        else:
            sname = s
    try:
        output = f"{basepath}/{data['__path__']}"
    except:
        output = f"{basepath}/"
    output = output.replace('///', '/').replace('//', '/')
    data = remove_special(data)
    if stype == 'env':
        write_env(data, f"{output}/{sname}")
    elif stype == 'file':
        if data['data'].startswith('data:application/octet-stream;base64,'):
            write_file(data['data'].replace('data:application/octet-stream;base64,',''), f"{output}/{data['filename']}")
    elif stype == 'yaml' or stype == 'yml':
        write_yaml(data, f"{output}/{sname}")
    elif stype == 'text' or stype == 'txt':
        write_txt(data, f"{output}/{sname}")
    else:
        write_json(data, f"{output}/{sname}")
    print(f"{s}\t\t{sname}\t\t{stype}\t\t{basepath}\t\t{output}")