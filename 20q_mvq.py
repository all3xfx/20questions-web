#!/usr/bin/python

#20q_mvq.py
#Move question, or remove a null question, and replace it with the highest-numbered question, updating all the answers accordingly
import os
import sys
import re

import cgi
import cgitb

import mod20q as tq

rcfilename = '.' + re.sub('_.+py', 'rc', os.path.basename(sys.argv[0]))
tq.configure(rcfilename)

form = cgi.FieldStorage()

q_id = form.getvalue('q_id')

is_cgi = 'GATEWAY_INTERFACE' in os.environ
#[GATEWAY_INTERFACE]

if is_cgi:
    print "Content-Type: text/html"
    print
    cgitb.enable()
    cgi_url = os.path.basename(sys.argv[0])
else:
    print "Running on command line"
    print
    q_id = sys.argv[1]

#print "FOO"
#sys.exit()

if q_id == None or q_id == '':
    print "No question_id provided"
else:
    things    = tq.db_load_things()
    questions = tq.db_load_questions()

    highest_id = str(max([ int(tq.question_id(q)) for q in questions ]))

    q_text = tq.question_text(tq.find_question(highest_id, questions))

    print q_text 

    for th in things:
        responses = tq.thing_responses(th)
        # print tr_dict

        if highest_id in responses:
            print th
            responses[q_id] = responses[highest_id]
            responses.pop(highest_id, None)
            
            #        print tq.make_thing(tq.thing_name(th), tq.responses_to_trail(responses))
            
            tq.db_update_thing(th)

            tq.db_replace_question_text(q_id, q_text)

#print ques + highest_id
if is_cgi:
    print "<br/><a href=\"%s\">Return</a>" % '20q_edit.py'
