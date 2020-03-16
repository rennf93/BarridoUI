import urllib.request


def download_file(external_source, local_destination):
    return urllib.request.urlretrieve(external_source, filename=local_destination)
