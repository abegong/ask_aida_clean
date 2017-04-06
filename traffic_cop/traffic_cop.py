import datetime
import json
import random
import decimal
import urlparse
import re
import time

import requests
# import boto.dynamodb2
# from boto.dynamodb2.table import Table
# from boto.dynamodb2.items import Item
# from boto.dynamodb2.fields import HashKey, GlobalAllIndex
# from boto.dynamodb2.types import NUMBER

from flask import Flask, request, jsonify

from taskmeister import state_machine
import util, logic, services, data

config = json.load(file('auth_config.json'))
dm = data.DataManager(mode=util.TEST_MODE, test_db_obj=json.load(file('test_db.json')))
twilio = services.Twilio(mode=util.TEST_MODE, config=config)
motion = services.Motion(mode=util.TEST_MODE, config=config)

def validate_arguments(request, required_fields):
    # print "=== request.form ==="
    # print request.form

    # print "=== request.json ==="
    # print request.get_json(force=True)

    # request.form.get('event')
    json_obj = request.get_json(force=True)
    if json_obj == None:
        return json.dumps({"msg" : "Missing required json object"}), 500
        # raise APIException("Missing required json object")

    for field in required_fields:
        if not field in json_obj:
            return json.dumps({"msg" : "Missing required field: "+field}), 500

    return json_obj, None

def create_exchange_if_applicable(dm, motion, task_flow, task_obj, task_context_var_obj, now):
    """
    Given a task_flow, task_obj, and task_context_var_obj, 
    """
    if task_context_var_obj["recipient"] == None:
        return None

    if task_context_var_obj["exchange_bot_type"] == None:
        return None

    exchange_context_var_obj = dm.get_context_vars_for_exchange(
        task_context_var_obj['requested_caregiver_id'],
        task_context_var_obj['next_recipient'],
        task_context_var_obj['patient_user_id'],
        task_context_var_obj['deadline'],
        next_task_deadline=-1, #!!!
    )
    # new_exchange_context_obj = logic.create_exchange_context_obj_from_current_state(exchange_context_var_obj)#task_flow, task_obj, task_context_obj["vars"])
    exchange_context_obj = {
        "exchange_id" : None, #!!!
        "user_phone_number" : exchange_context_var_obj['user_phone_number'],
        "vars" : exchange_context_var_obj,
        "history" : []
    }
    new_exchange_obj = logic.create_new_exchange_object(task_obj, exchange_context_obj, now)
    exchange_obj = dm.post_exchange(new_exchange_obj)

    exchange_context_obj["exchange_id"] = exchange_obj["exchange_id"]
    #Add first motion callback to exchange
    # print datetime.datetime.now(), "Fetching response from motion..."
    # params = {
    #     "msg" : "[Empty: Starting Message]",
    #     "bot" : bot_ids[exchange_context_obj["meta"]["exchange_bot_type"]],
    #     "session" : "askaida_"+str(int(exchange_context_obj["exchange_id"])),
    #     "key" : config['motion']['api_key']
    # }
    # print json.dumps(params, indent=2)
    # response = requests.get(
    #     config['motion']['url'],
    #     params = params
    # )

    #!!! This would be a good place for a yield
    message, bot_module, result = motion.get("[Empty: Starting Message]", exchange_context_obj)

    # response_json = response.json()
    # print "=== Motion response ==="
    # print response_json
    # message = response_json['botResponse']

    new_history_obj = {
        "timestamp" : now,
        "from" : "Aida",
        "to" : exchange_context_obj["vars"]["current_caregiver_first_name"], #!!!???
        "message" : message,
    }
    if bot_module:
        new_history_obj["motion_module"] = bot_module

    # # exchange_context_obj["history"].append({
    # # new_item["history"].append({
    # #     "timestamp" : str(datetime.datetime.now()),
    # #     "from" : "Aida",
    # #     "to" : exchange_context_obj["meta"]["user_id"],
    # #     "message" : message,
    # # })
    exchange_context_obj["history"].append(new_history_obj)
    # new_item.save(overwrite=True)

    # #Send first line to twilio
    twilio.send_sms(exchange_context_obj["user_phone_number"], message)

    exchange_obj["exchange_context_obj"] = json.dumps(exchange_context_obj)
    dm.put_exchange(exchange_obj)

    return exchange_obj

    #     # print datetime.datetime.now(), "Create the initial exchange in traffic_cop..."
    #     # response = requests.post(
    #     #     config['traffic_cop']['lambda_functions']['create_new_exchange']["url"],
    #     #     data=json.dumps(new_exchange_obj)
    #     # )
    #     # print response


    # exchange_context_obj = logic.create_exchange_context_obj_from_current_state(task_flow, task_obj, task_context_var_obj)

    # if exchange_context_obj == None:
    #     return None

    # exchange_obj = logic.create_new_exchange(task_obj, exchange_context_obj)
    # #!!! post_exchange needs to know about Dynamo AND sandman
    # exchange_obj = dm.post_exchange(exchange_obj)

    # response = requests.post(
    #     config['sandman']['url']+'exchanges/',
    #     data = json.dumps()
    # )

    # return exchange_obj

def check_and_handle_task_updates(dm, task_obj, task_context_obj, task_flow, now):
    assert(type(now)==type(task_context_obj["vars"]["state_deadline"]))
    if now >= task_context_obj["vars"]["state_deadline"]:
        # updated_task_id_list.append(task_id)

        task_context_obj = state_machine.update_on_trigger(task_flow, task_context_obj, now, 'deadline', 'exceeded')
        # print task_context_obj
        task_obj["task_context_obj"] = json.dumps(task_context_obj)

        create_exchange_if_applicable(dm, motion, task_flow, task_obj, task_context_obj["vars"], now)

        # #!!! Add a check here to make sure we need a new exchange...?
        # # print json.dumps(task_context_obj["vars"], indent=2)
        # exchange_context_var_obj = dm.get_context_vars_for_exchange(
        #     task_context_obj["vars"]['requested_caregiver_id'],
        #     task_context_obj["vars"]['next_recipient'],
        #     task_context_obj["vars"]['patient_user_id'],
        #     task_context_obj["vars"]['deadline'],
        #     -1
        # )
        # print json.dumps(exchange_context_var_obj, indent=2)
        # # new_exchange_context_obj = logic.create_exchange_context_obj_from_current_state(exchange_context_var_obj)#task_flow, task_obj, task_context_obj["vars"])
        # exchange_context_obj = {
        #     "exchange_id" : None,
        #     "user_phone_number" : exchange_context_var_obj['patient_phone_number'],
        #     "vars" : exchange_context_var_obj,
        #     "history" : []
        # }
        # print '#'*80
        # print new_exchange_context_obj

        # if new_exchange_context_obj != None:
        #     new_exchange_obj = logic.create_new_exchange_object(task_obj, exchange_context_obj)
        #     dm.post_exchange(new_exchange_obj)
        #     # print datetime.datetime.now(), "Create the initial exchange in traffic_cop..."
        #     # response = requests.post(
        #     #     config['traffic_cop']['lambda_functions']['create_new_exchange']["url"],
        #     #     data=json.dumps(new_exchange_obj)
        #     # )
        #     # print response

        dm.put_task(task_obj)

        # print datetime.datetime.now(), "Update task_obj in database..."
        # task_obj["task_context_obj"] = json.dumps(task_context_obj)

        # response = requests.put(
        #     config['sandman']['url']+'tasks/'+str(task_obj["task_id"]),
        #     json = task_obj
        # )
        # print response
        # print response.json()

    
    # else:
        # nonupdated_task_id_list.append(task_id)
################################################################################
# Exposed Lambda Methods #

app = Flask(__name__)

@app.errorhandler(405)
def method_not_allowed(e):
    return json.dumps({"msg" : "Method not allowed"}), 405

@app.route("/create_new_task", methods=['POST'])
def create_new_task():
    json_obj, status_code = validate_arguments(
        request,
        [
            "task_type",
            "group_id",
            "deadline",
        ]
    )
    if status_code != None:
        return json_obj, status_code

    if app.debug and 'now' in json_obj:
        now = json_obj['now']
    else:
        now = time.mktime(datetime.datetime.now().timetuple())

    if app.debug and 'shuffle' in json_obj:
        shuffle = json_obj['shuffle']
    else:
        shuffle = True

    task_flow = logic.task_flow_index[json_obj["task_type"]]
    task_context_var_obj = dm.get_context_vars_for_task(json_obj["group_id"], json_obj["deadline"], shuffle=shuffle)
    
    # Use state_machine to initialize_task_context_obj
    task_context_obj = state_machine.initialize_task_context_obj(task_flow, task_context_var_obj, now)

    # Create task object and store it to sandman
    task_obj = logic.create_new_task_object(json_obj["group_id"], json_obj["task_type"], task_context_obj, now)
    task_obj = dm.post_task(task_obj)

    # Create initial exchange
    create_exchange_if_applicable(dm, motion, task_flow, task_obj, task_context_obj["vars"], now)
    # Return a (mostly meaningless) result object

    return json.dumps({
        "msg": "success"
    })

#This shouldn't really live in an endpoint, should it?
#Meh. Why not? It'll simplify logging.
@app.route("/check_for_updates", methods=['POST'])
def check_for_updates():
    # Fetch all task objects
    json_obj, status_code = validate_arguments(
        request,
        []
    )
    if status_code != None:
        return json_obj, status_code

    if app.debug and 'now' in json_obj:
        now = json_obj['now']
    else:
        now = time.mktime(datetime.datetime.now().timetuple())

    task_obj_list = dm.get_incomplete_tasks()

    for task_obj in task_obj_list:
        task_context_obj = json.loads(task_obj["task_context_obj"])
        task_flow = logic.task_flow_index[task_obj["task_type"]]#json.load(file('task_flows/'+task_obj["task_type"]))

        check_and_handle_task_updates(dm, task_obj, task_context_obj, task_flow, now)

    return json.dumps({
        "msg": "success"
    })

@app.route("/twilio_webhook", methods=['POST'])
def twilio_webhook():
    # Unpack arguments
    json_obj, status_code = validate_arguments(
        request,
        [
            "body",
            "fromNumber",
        ]
    )
    if status_code != None:
        return json_obj, status_code


    if app.debug and 'now' in json_obj:
        now = json_obj['now']
    else:
        now = time.mktime(datetime.datetime.now().timetuple())

    try:
        exchange = dm.get_exchange_by_phone_number(json_obj["fromNumber"])[0]
    except IndexError:
        return json.dumps({"msg": "Not good"}), 500

    exchange_context_obj = json.loads(exchange['exchange_context_obj'])

    # print datetime.datetime.now(), "Fetching results and response from motion..."
    # return_message, done = motion.get({
    #     "msg" : json_obj["body"],
    #     "bot" : logic.bot_ids[exchange_context_obj["vars"]["exchange_bot_type"]],
    #     "session" : "askaida_"+str(int(exchange_context_obj["exchange_id"])),
    #     "key" : config['motion']['api_key']
    # })
    message, bot_module, result = motion.get(json_obj["body"], exchange_context_obj)

    if message == None:
        message = "Okay. Aida over and out."
        done = True
    else:
        done = False


    print message
    # response = requests.get(
    #     config['motion']['url'],
    #     params = {
    #         "msg" : message,
    #         "bot" : bot_ids[exchange_context_obj["meta"]["exchange_bot_type"]],
    #         "session" : "askaida_"+str(int(exchange_context_obj["exchange_id"])),
    #         "key" : config['motion']['api_key']
    #     }
    # )
    # print '=== Motion response ==='
    # response_json = response.json()
    # # print response
    # # print response.text
    # print response_json
    # # print response.json()["botResponse"]
    # if response_json['code'] == 200:
    #     return_message = response_json["botResponse"]
    #     done = False
    # else:
    #     # return_message = "I have no response to that."
    #     return_message = "Okay. Aida over and out."
    #     done = True


    # print datetime.datetime.now(), "Updating context history..."
    new_history_obj = {
        "timestamp" : now, #!!!
        "to" : "Aida",
        "from" : exchange_context_obj["vars"]["current_caregiver_first_name"],
        "message" : message,
    }
    if result:
        new_history_obj["motion_result"] = result
    exchange_context_obj["history"].append(new_history_obj)

    new_history_obj ={
        "timestamp" : now,
        "from" : "Aida",
        "to" : exchange_context_obj["vars"]["current_caregiver_first_name"],
        "message" : message,
    }
    if bot_module:
        new_history_obj["motion_module"] = bot_module
    exchange_context_obj["history"].append(new_history_obj)

    if not done:
        # print datetime.datetime.now(), "Saving updated exchange context to dynamodb..."
        # exchange_context_obj.save()
        dm.put_exchange(exchange_context_obj)
    
    else:
        # print datetime.datetime.now(), "Saving exchange row to sandman..."
        # print config['sandman']['url']+'exchanges/'+str(int(exchange_context_obj["exchange_id"]))

        outcome = logic.determine_outcome(exchange_context_obj)
        print json.dumps(exchange_context_obj, indent=2)
        dm.put_exchange(exchange_context_obj)    
        # response = requests.put(
        #     config['sandman']['url']+'exchanges/'+str(int(exchange_context_obj["exchange_id"])),
        #     json = {
        #         "exchange_id" : int(exchange_context_obj["exchange_id"]),
        #         "task_id" : int(exchange_context_obj["meta"]["task_id"]),
        #         # "task_subnode_id" : int(exchange_context_obj["meta"]["task_subnode_id"]),
        #         "start_timestamp" : exchange_context_obj["meta"]["created_timestamp"],
        #         "exchange_context_obj" : json.dumps(dict(exchange_context_obj), cls=DecimalEncoder),
        #         "is_complete" : True,
        #         "was_successful" : None,
        #         "created_timestamp" : exchange_context_obj["meta"]["created_timestamp"],
        #         "update_timestamp" : exchange_context_obj["meta"]["created_timestamp"],
        #     }
        # )

        # print '=== Sandman response ==='
        # # print response
        # # print response.text
        # response_json = response.json()
        # print response_json

        # print datetime.datetime.now(), "Deleting exchange from DynamoDB..."
        # exchange_context_obj.delete()

        # print '=== Taskmaster response ==='
        # print datetime.datetime.now(), int(exchange_context_obj["meta"]["task_id"]), outcome
        # response = requests.get(
        #     config['taskmeister']['lambda_functions']['handle_callback_from_exchange']['url'],
        #     params = {
        #         "task_id" : int(exchange_context_obj["meta"]["task_id"]),
        #         "outcome" : outcome,
        #     }
        # )
        # # print int(exchange_context_obj["meta"]["task_id"])
        # # print outcome
        # # print response
        # # print response.text
        # response_json = response.json()
        # print response_json

    # Fetch exchange object from dynamo
    # Fetch response from motion
    # Extract the return_message
    # Append to history
    # if done:
    #     Save to dynamo
    # else:
    #     Save to sandman
    #     Delete from dynamo
    #     Update task
    # Return the return_message to twilio

    return message

@app.route("/motion_webhook", methods=['POST'])
def motion_webhook():
    # Unpack arguments
    if app.debug and 'now' in json_obj:
        now = json_obj['now']
    else:
        now = time.mktime(datetime.datetime.now().timetuple())

    # Fetch from dynamo
    # Return the exchange_context

    return json.dumps({
        "msg": "success"
    })

# @app.route("/")
# def handle_callback_from_exchange():
#     pass
#     # Unpack arguments
#     # Fetch task object
#     # update_on_trigger
#     # create_new_exchange
#     # update_task_object

# @app.route("/")
# def create_new_exchange():
#     # Unpack arguments
    #     # Fetch user data for recipient, next_recipient, and patient
    #     # Get deadlines from current and next task
    #     # Create exchange_context_obj
#     # Save row to sandman
#     # Save to Dynamo
#     # Fetch first response from motion
#     # Append to history
#     # Save to Dynamo again
#     # Send to twilio
#     # Return a (mostly meaningless) result object

if __name__ == "__main__":
    app.run(debug=True)

