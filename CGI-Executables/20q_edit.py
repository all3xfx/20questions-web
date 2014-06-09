#!/usr/bin/python

import sys
import os 
import re
import urllib

import cgi 
import cgitb; cgitb.enable()

#import config
import mod20q as tq
import htmlgen as html
#global tq

# variables
from mod20q import newline
from mod20q import tab
#from mod20q import DB_FIELD_SEP


###############
# CGI HTML output functions
def output_head(doctitle_suffix = '') :
#        doctitle = 'log(2)255 Editor' + ' - ' + doctitle_suffix
        doctitle = 'Editor'
        print "Content-Type: text/html"
	print                               # blank line, end of headers
        
        print '<head>'
	print "<TITLE>" + doctitle + "</TITLE>"
	print '<link rel="icon" type="image/png" href="../images/riktov-icon.png">'
	
        print html.make_open_tag('link', {'rel':'stylesheet', 'type':'text/css', 'href':tq.config['css'] })

        #print "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\" />" % tq.config['css']
        
        print '<meta content="text/html; charset=utf-8" http-equiv="Content-Type">'
	print '</head>'

        print '<html>'
        print '<body>'

        print '<div class="TopMenu">'
#	print '<a href="../">Home</a> | '
        print '<a href="20q_play.py">Play</a> |'
	print '<a href="20q_edit.py">Editor</a>'
	print '<hr>'
        print '</div>'


        print '<div class="PageTitle">'
	print "<h1>%s</h1>" % doctitle
        print '</div>'

###############
# CGI HTML form output functions



	
###################
# question and thing records


###################
# extracting fields from records

########################
# operations on trails

####################################
# extracting information from questions or things

#question_id in mod
def responses(q_id, yn) :
	"""Get all the specified responses to a question"""
	resp = '-' + q_id + yn
	return filter(lambda th: re.search(resp, thing_trail(th)), things)

##################
# actions
def action_remove_responder(q_id, things_to_remove):
	#load the databases, only things db is needed
	things    = tq.db_load_things()

	print "Remove responses by the following people to question %s" % q_id 
        print '<ul>'
	for name in things_to_remove:
                print "<li>%s</li>" % name

		thing = tq.get_thing_by_name(name, things)
                thing.responses.pop(q_id, None)
                tq.db_update_thing(thing)
        print '</ul>'
	
        params = {'q_id':q_id }

	print "<a href=\"?%s\">Return to editing question: %s</a>" % (urllib.urlencode(params), q_id)
	print '</body></html>'	


def action_remove_response(question_ids, thing_name):
#	print "Remove responses by %s to questions" % thing_name 
#	print question_ids

	#load the databases
	questions = tq.db_load_questions()
	
	thing = tq.db_get_thing_by_name(thing_name)
	responses = thing.responses

	for q_id in question_ids:
                responses.pop(q_id, None)

	tq.db_update_thing(thing)

        params = {'name':thing_name }

	print "<a href=\"?%s\">Return to editing question: %s</a>" % (urllib.urlencode(params), q_id)
	print '</body></html>'	
#	sys.exit()


def first_name(name_str) :
	#return name_str
	return re.sub(' .+', '', name_str)

###########################
# screen output functions

def selection_class(a, b):
        if a == b:
                return {'class':'Selected'}
        return {}

#duplicated in play
def response_class(resp):
        if resp == 'y':
                name = 'Yes'
        elif resp == 'n':
                name = 'No'
        else:
                return {}

        return { 'class':name }

def print_questions_list(questions, things=None, selected_q_id=None, selected_th_name=None):
        #build some parallel lists for zipping
        q_ids = [ tq.question_id(q) for q in questions ]

        #create a dictionary of lists of tag args, for each type of tag (identified by tag name)
        tag_args = {}
        tag_args['a']     = [ {'href':"?q_id=%s" % q_id} for q_id in q_ids ]

        if selected_th_name:
                thing = tq.get_thing_by_name(selected_th_name, things)

                tag_args['input'] = [ {'type':'checkbox', 'name':'q_id', 'value':q_id} for q_id in q_ids ]
                checkboxes = [ html.make_open_tag('input', t_a) for t_a in tag_args['input'] ]

                class_list = [ response_class(thing.response(q_id)) for q_id in q_ids ]
        else:
                class_list = [ selection_class(selected_q_id, q_id) for q_id in q_ids ]

        tag_args_list = [ dict(class_arg.items() + href_arg.items()) for (class_arg, href_arg) in zip(class_list, tag_args['a'])]

        #the anchors contain both href and CSS class for selected question, or response to selected thing
        anchors  = [ html.make_tag('a', q, tag_args) for (q, tag_args) in zip(questions, tag_args_list) ]
        
        if selected_th_name:
                li_items_list = [ cb + anc for (cb, anc) in zip(checkboxes, anchors) ]                
        else:
                li_items_list = anchors

        #final wrap with li, no tag args
        lis = [ html.make_tag('li', anc) for anc in li_items_list ]

	print '<ul class="Questions">' + '\n'.join(lis) + '</ul>'

def print_things_list(things, selected_th_name=None, selected_q_id=None):
        names = [ th.name for th in things ]
        href_list = [ {'href':'?' + urllib.urlencode({'name':"%s" % name})} for name in names ]

        if selected_q_id:
                checkboxes = [ html.make_open_tag('input', {'type':'checkbox', 'name':'name', 'value':name}) for name in names ]
                class_list = [ response_class(th.response(selected_q_id)) for th in things ]
        else:
                class_list = [ selection_class(selected_th_name, name) for name in names ]
                
        tag_args_list = [ dict(class_arg.items() + href_arg.items()) for (class_arg, href_arg) in zip(class_list, href_list)]

        #the anchors contain both href and CSS class for selected question, or response to selected thing
        anchors  = [ html.make_tag('a', first_name(name), tag_args) for (name, tag_args) in zip(names, tag_args_list) ]
        
        if selected_q_id:
                li_items_list = [ cb + anc for (cb, anc) in zip(checkboxes, anchors) ]                
        else:
                li_items_list = anchors

        #final wrap with li, no tag args
        lis = [ html.make_tag('li', anc) for anc in li_items_list ]

        print '<ul class="Things">' + '\n'.join(lis) + '<br style="clear:both" />' + '</ul>'

###################
# utility functions

def strip_tags(html):
	return re.sub('<.+?>', '', html)

def q_checkname(question_html):
	question_text = re.sub('<.+?>', '', question_html)
	return 'q' + tq.question_id(question_text)
	
def th_checkname(thing_html):
	"""Assume thing_html is an anchor"""
	found = re.search('name=(.+)"', thing_html)
	if found :
		return 'th_' + found.group(1)
	return ''

#def adjoin(seq1, seq2, key=None, test=None)

#def missing_questions(questions):
 
def questions_num_range(questions):
        """Return a range of questions from the existing ids"""
        q_ids = [ int(tq.question_id(q)) for q in questions ]
        full_range = range(min(q_ids), max(q_ids))
        return full_range
	
def missing_questions(questions):
        q_num_range = questions_num_range(questions)
        q_nums = [ int(tq.question_id(q)) for q in questions ]
        return set(q_num_range).difference(q_nums)

def debug_dump(things, questions_html, trail, q_id, dbg_evenness) :
	print "<div class=\"Debug\">" + newline
	print "<p>DEBUG<p>" + newline
	print '<small>'
	print "<p>Responses %d <span class=\"Yes\">%d</span> <span class=\"No\">%d</class>" % response_counts(q_id, things)
	print "<p>Evenness: %f" % dbg_evenness
	print "<p>%d Things: <br>\n" % len(things)
	print "<div class=\"NameBlock\">\n"
	print ''.join(html_highlight_thinglist(things, q_id))
	print "</div>\n"
	print "<p style=\"clear:left\">%d Questions: <br>\n" % len(questions)
	print "<form name=\"edit_answers\" method=\"post\">" + newline
	print '<ul class="Questions">' + newline
	print questions_html
	print '</ul>' + newline
	print '<p>Trail: ', trail
	print '</small>'
	print '</div>'
	print "<form>" + newline

def edit_by_question(things, questions, q_id):
        question = tq.find_question(q_id, questions)
        print '<h2>' + question + '</h2>'
	
	print '<div id="left_column">'
        print_questions_list(questions, things, q_id, None)
	print '</div>'

        print '<br/>'

	print '<div id="right_column">'
        #
        print '<form method="POST" action=20q_rmq.py>'
        ##
        print '<div>'
        ###
        print "<input type=hidden name='action' value='remove_responder'>"
        print "<input type=hidden name='question' value='%s'>" % q_id
        print "<input type=submit value='Remove Responses by the checked people to Question %s'>" % q_id
        print "<br><a href=\"20q_mvq.py?q_id=%s\">Remove question: %s</a>" % (q_id, question)
        ###
        print '</div>'

        print_things_list(things, None, q_id)

        ##
        print '</form>'
        #
        print '</div>'


        #print missing_qs
        for q in missing_questions(questions):
                print q
                print tq.response_counts(str(q), things)
                thing_names = map(tq.thing_name, tq.responders_to(str(q), things))
                thing_names = [ "<a href=\"%s?name=%s\">%s</a>" % (cgi_url, name, name) for name in thing_names  ]
                print thing_names
                #for name in thing_names:
                #        print name + '<br />'

        #end testing

def edit_by_thing(things, questions, th_name):
	thing = tq.get_thing_by_name(th_name, things)
	th_name = re.sub('"', '', th_name)
	
	print '<h2>' + th_name + '</h2>'

	responses = thing.responses	
        for q in missing_questions(questions):
                if '-' + str(q) in tq.thing_trail(thing):
                        print "Has answered missing question %d" % q + '<br/>'

                        params = { 'name':tq.thing_name(thing), 'q_id':q }
                        print "<a href=\"20q_rmq.py?%s\">Remove response</a>" % urllib.urlencode(params)

	print '<div id="left_column">'
	print '<form method=POST>'

        print '<div>'
        #
	print "<input type=hidden name='action' value='remove_response'>"
	print "<input type=hidden name='thing' value='%s'>" % th_name 	
	print "<input type=submit value='Remove Responses by %s to Checked Questions'>" % th_name
        #
        print '</div>'

	print_questions_list(questions, things, None, th_name)

	print '</form>'
        print '</div>'

        print '<div id="left_column">'
        #print the block of names
        print_things_list(things, th_name, None)
        print '</div>'

def edit_by_none(things, questions):
	print '<h2></h2>'

	print_questions_list(questions)
        print_things_list(things)


        

######################################################
## main

#form data should be retrieved first, because it exists even before the program runs!
form = cgi.FieldStorage()
g_q_id    = form.getvalue('q_id')
g_th_name = form.getvalue('name') 
g_action    = form.getvalue('action')

cgi_url = os.path.basename(sys.argv[0])

head_suffix = g_th_name or g_q_id or ''

rcfilename = '.' + re.sub('_.+py', 'rc', cgi_url)
tq.configure(rcfilename)

output_head(head_suffix)

if g_action == 'remove_response':
	questions_to_remove = form.getlist('q_id')
	thing_name = form.getvalue('thing')

        action_remove_response(questions_to_remove, thing_name)

#elif action == 'remove_responder' :
#        things_to_remove = form.getlist('thing_name')
#	q_id = form.getvalue('question')
#        action_remove_responder(q_id, things_to_remove)
#	sys.exit()

# no action, just display

if 'name' in form:
	query_by = 'thing'
elif 'q_id' in form:
	query_by = 'question'
else:
        query_by = 'none'
#load the databases
g_things    = tq.db_load_things()
g_questions = tq.db_load_questions()

g_things    = sorted(g_things, key = lambda x:x.name )
g_questions = sorted(g_questions, key = lambda x : int(tq.question_id(x)))

if query_by == 'question':
        edit_by_question(g_things, g_questions, g_q_id)
elif query_by == 'thing' :	#by thing
        edit_by_thing(g_things, g_questions, g_th_name)
else:
        edit_by_none(g_things, g_questions)

#######################
# HTML output
#tq.print_debug_console()
print '</body></html>'
