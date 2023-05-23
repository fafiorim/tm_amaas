import argparse
import time
import pathlib
import os
import sys
import json

import amaas.grpc

files_scanned_count = 0
files_excluded_count = 0

def results_json(result,pfile,elapsed):
   """"This function returns the data 
   formated as JSON"""

    # make a hash object
   result_json = result.rstrip(result[-1])
   result_json = result_json+","+'"filepath":'+'"'+str(pfile)+'"'+',"elapsedTime":'+'"'+str(round(elapsed,2))+'"'+'}'
   # open file for reading in binary mode
   #result_json_object = result_json
   result_json_object = json.loads(result_json)
   #json_formatted_str = result_json_object
   json_formatted_str = json.dumps(result_json_object, indent=2)

   return json_formatted_str

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
                            files_excluded_count += 1
                            continue
                        else:
                            s = time.perf_counter()
                            result = amaas.grpc.scan_file(p, handle)
                            elapsed = time.perf_counter() - s
                            result_toprint = results_json(result,p,elapsed)
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
                                    s = time.perf_counter()
                                    result = amaas.grpc.scan_file(f, handle)
                                    elapsed = time.perf_counter() - s
                                    result_toprint = results_json(result,f,elapsed)
                                    print(f"{result_toprint}")
                                    files_scanned_count += 1
    else:
        if args.exclude != None:
            if args.exclude in args.filepath:
                files_excluded_count += 1
            else:
                s = time.perf_counter()
                result = amaas.grpc.scan_file(args.filepath, handle)
                elapsed = time.perf_counter() - s
                result_toprint = results_json(result,args.filepath,elapsed)
                files_scanned_count += 1
        else:
            s = time.perf_counter()
            result = amaas.grpc.scan_file(args.filepath, handle)
            elapsed = time.perf_counter() - s
            result_toprint = results_json(result,args.filepath,elapsed)
            files_scanned_count += 1
    
    amaas.grpc.quit(handle)
    total_elapsed = time.perf_counter() - total_time
    #print(f"\nTOTAL TIME ELAPSED: {total_elapsed:0.2f} seconds.")
    #print(f"TOTAL FILE(s) SCANNED: {files_scanned_count} files.")
    #print(f"TOTAL FILE(s) EXCLUDED OF THE SCAN: {files_excluded_count} files.")
