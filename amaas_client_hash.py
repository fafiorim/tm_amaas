import argparse
import time
import pathlib
import os
import json
import hashlib

import amaas.grpc

files_scanned_count = 0
files_excluded_count = 0
output=''

def results_json(result,pfile,elapsed,message_md5,message_sha1,message_sha256):
   """"This function returns the data 
   formated as JSON"""

   result_json = result.rstrip(result[-1])
   result_json = result_json+","+'"filePath":'+'"'+str(pfile)+'"'+',"elapsedTime":'+'"'+str(round(elapsed,2))+'"'+","+'"MD5":'+'"'+message_md5+'"'+","+'"SHA-1":'+'"'+message_sha1+'"'+","+'"SHA-256":'+'"'+message_sha256+'"'+'},'
   return result_json

def final_format_json(output):
    output = "["+output
    output = output.rstrip(output[-1])
    output = output+"]"
    result_json_object = json.loads(output)
    json_formatted_str = json.dumps(result_json_object, indent=2)
    return json_formatted_str

def json_with_mutiple_objects():

    return json_mutiple_obj

def hash_file(filename, algorith):
   """"This function returns the SHA-1 hash
   of the file passed into it"""

   if algorith == "md5":
    h = hashlib.md5()
    # open file for reading in binary mode
    with open(filename,'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

   # make a hash object
   if algorith == "sha1":
    h = hashlib.sha1()
    # open file for reading in binary mode
    with open(filename,'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

   if algorith == "sha256":
    h = hashlib.sha256()
    # open file for reading in binary mode
    with open(filename,'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()


if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument('--recursive', action='store_true',
                        required=False, help='scan directory recursively')
    parser.add_argument('-f', '--filepath', action='store',
                        required=True, help='Path of the file or directory to be scanned')
    parser.add_argument('-a', '--addr', action='store', default='127.0.0.1:50051', required=False,
                        help='gRPC server address and port (default 127.0.0.1:50051)')
    parser.add_argument('-r', '--region', action='store',
                        help='AMaaS service region; e.g. us-1 or dev')
    parser.add_argument('--api_key', action='store',
                        help='api key for authentication')
    parser.add_argument('--tls', type=bool, action='store', default=True,
                        help='enable TLS gRPC ')
    parser.add_argument('--ca_cert', action='store', help='CA certificate')
    parser.add_argument('-e', '--exclude', action='store',
                        required=False, help='exclude a file or extension from the scan')
    parser.add_argument('-hash', action='store_true',
                        required=False, help='generate the hash to be presented in the output')
    args = parser.parse_args()

if args.region:
    handle = amaas.grpc.init_by_region(args.region, args.api_key, args.tls, args.ca_cert)
else:
    handle = amaas.grpc.init(args.addr, args.api_key, args.tls, args.ca_cert)  

#adding recursive scan option to the client.py
total_time = time.perf_counter()
if args.recursive != False:
    path = args.filepath
    #list files in the directory
    for p in pathlib.Path(path).iterdir():
        if p.is_dir():
            #check if is a file or a folder
            if os.path.isfile(p):
                if args.exclude != None:
                    if args.exclude in p.suffix or args.exclude in p.name:
                        #for future if want to add the hash for files that were excluded by the scan
                        #message = hash_file(p)
                        files_excluded_count += 1
                        continue
                    else:
                        message_md5 = hash_file(p,"md5")
                        message_sha1 = hash_file(p,"sha1")
                        message_sha256 = hash_file(p,"sha256")
                        s = time.perf_counter()
                        result = amaas.grpc.scan_file(p, handle)
                        elapsed = time.perf_counter() - s
                        result_toprint = results_json(result,p,elapsed,message_md5,message_sha1,message_sha256)
                        output = output + result_toprint
                        files_scanned_count += 1
            else:
                #list files in the folder
                for f in pathlib.Path(p).iterdir():
                    if os.path.isfile(f):
                        if args.exclude != None:
                            if args.exclude in f.suffix or args.exclude in f.name:
                                files_excluded_count += 1
                                continue
                            else:
                                message_md5 = hash_file(f,"md5")
                                message_sha1 = hash_file(f,"sha1")
                                message_sha256 = hash_file(f,"sha256")
                                s = time.perf_counter()
                                result = amaas.grpc.scan_file(f, handle)
                                elapsed = time.perf_counter() - s
                                result_toprint = results_json(result,f,elapsed,message_md5,message_sha1,message_sha256)     
                                output = output + result_toprint
                                files_scanned_count += 1
else:
    if args.exclude != None:
        if args.exclude in args.filepath:
            files_excluded_count += 1
        else:
            message = hash_file(args.filepath)
            s = time.perf_counter()
            result = amaas.grpc.scan_file(args.filepath, handle)
            elapsed = time.perf_counter() - s
            result_toprint = results_json(result,args.filepath,elapsed,message)
            output = output + result_toprint
            files_scanned_count += 1
    else:
        message = hash_file(args.filepath)
        s = time.perf_counter()
        result = amaas.grpc.scan_file(args.filepath, handle)
        elapsed = time.perf_counter() - s
        result_toprint = results_json(result,args.filepath,elapsed,message)
        output = output + result_toprint
        files_scanned_count += 1

amaas.grpc.quit(handle)
total_elapsed = time.perf_counter() - total_time

t_print = final_format_json(output)
print(f"{t_print}")
#print(f"\nTOTAL TIME ELAPSED: {total_elapsed:0.2f} seconds.")
#print(f"TOTAL FILE(s) SCANNED: {files_scanned_count} files.")
#print(f"TOTAL FILE(s) EXCLUDED OF THE SCAN: {files_excluded_count} files.")
