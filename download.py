#!/usr/bin/env python3

import argparse
from hashlib import sha256
import os
import requests

def hash_password(galleryPassword):
    return sha256(galleryPassword.encode('utf-8')).hexdigest()

def download_gallery(gallery_id, galleryPassword):

    print('[+] Preparing to download {gallery_id} using password {galleryPassword}'.format(gallery_id= gallery_id, galleryPassword=galleryPassword))
    
    galleryPasswordHashed=hash_password(galleryPassword)

    url = 'https://kruu.com/gallery/{gallery_id}'
    apiurl = 'https://api.kruu.com/api/gallery/{gallery_id}'
    downloadurl = 'https://api.kruu.com/api/gallery/{gallery_id}/download/{image_id}?galleryPassword={galleryPassword}'

    session = requests.Session()
    resp = session.get(url.format(gallery_id=gallery_id))

    resp = session.post(apiurl.format(gallery_id=gallery_id), json={"galleryPassword": galleryPasswordHashed})
    imagedata = resp.json()
    image_ids = [x['id'] for x in imagedata['images']]
    image_ids = []
    for image in imagedata['images']:
        image_ids.append((image.get('id'), image.get('filename')))
        image_ids.extend([(child['id'], child['filename']) for child in image.get('children')])

    if not os.path.exists(gallery_id):
        os.makedirs(gallery_id)

    for image_id, image_name in image_ids:
        resp = session.get(downloadurl.format(gallery_id= gallery_id, image_id=image_id, galleryPassword=galleryPasswordHashed))
        if resp.status_code == 200:
            print('[+] Downloaded {filename}'.format(filename=image_name))
            filename = resp.headers['content-disposition'].split('=')[1]
            with open(gallery_id + os.sep + filename, 'wb') as outfile:
                outfile.write(resp.content)
        else:
            print('[-] Failed to download {filename}'.format(filename=image_name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("gallery_id")
    parser.add_argument("gallery_password")
    args = parser.parse_args()

    download_gallery(args.gallery_id, args.gallery_password)