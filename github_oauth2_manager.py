#!/usr/bin/python

import base64
import getpass
import json
import urllib2

URL = "https://api.github.com/authorizations"

username = raw_input("Username: ")
password = getpass.getpass()
encoded = base64.encodestring("{0}:{1}".format(username, password)).strip()
auth_header = "Basic {0}".format(encoded)

def do_request(url, data=None, method=None):
    request = urllib2.Request(url)
    request.add_header("Authorization", auth_header)
    if data:
        request.add_data(json.dumps(data))
    if method:
        request.get_method = lambda: method
    response = urllib2.urlopen(request)
    if response.code == 204: # No Content
        return None
    jsonresponse = json.load(response)
    return jsonresponse

def do_list():
    jsonresponse = do_request(URL)
    print "{0} keys".format(len(jsonresponse))
    for item in jsonresponse:
        print "ID: {id}, Scopes: {scopes}, Note: {note}".format(**item)

def internal_show(dictionary):
    for key, val in dictionary:
        print "  {0}: {1}".format(key, val)

def do_show(items):
    for item in items:
        print "Item {0}:".format(item)
        response = do_request("{url}/{id}".format(url=URL, id=item))
        internal_show(response.items())

def parse_token_data(items):
    scopes = [i for i in items[0].split(",") if i != "none"]
    note = items[1] if len(items) > 1 else None
    note_url = items[2] if len(items) > 2 else None
    data = { "scopes":scopes, "note":note, "note_url":note_url }
    return data

def do_create(items):
    if not items:
        print """Format: create <scope[, scope[, scope...]]> [note] [note_url]
Scope is one of: repo, public_repo, repo:state, user, delete_repo, gist, none
Note is an arbitrary note for your own use
The same applies to note_url"""
        return
    data = parse_token_data(items)
    response = do_request(URL, data)
    internal_show(response.items())

def do_update(items):
    token = items[0]
    data = parse_token_data(items[1:])
    url = "{url}/{id}".format(url=URL, id=token)
    response = do_request(url, data=data, method="PATCH")
    internal_show(response.items())

def do_delete(items):
    for item in items:
        do_request("{url}/{id}".format(url=URL, id=item), method="DELETE")

def handle_input(command):
    if command == "help":
        print """Possible commands:
list
show [id]*
create [scope,scope,scope...] [note] [note_url]
update <id> <scope,scope,scope...> [note] [note_url]
delete [id]*
exit
"""
    elif command == "list":
        do_list()
    elif command.startswith("show"):
        do_show(command.split()[1:])
    elif command.startswith("create"):
        do_create(command.split()[1:])
    elif command.startswith("update"):
        do_update(command.split()[1:])
    elif command.startswith("delete"):
        do_delete(command.split()[1:])
    elif command in ("quit", "exit"):
        raise SystemExit
    else:
        print "Try help"

while True:
    try:
        command = raw_input("> ")
        handle_input(command)
    except EOFError:
        break
    except Exception as e:
        print e
    except KeyboardInterrupt:
        print "Caught ^C, exiting..."
        break

