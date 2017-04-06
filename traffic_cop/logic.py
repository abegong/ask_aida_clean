import json

# from taskmeister import state_machine

#!!! Should load these files once here, instead of making load calls elsewhere.
task_flow_index = {
    'arrange_visit' : 'arrange_visit_logic_20170213.json',
    'arrange_impatient_visit' : 'impatient_arrange_visit_logic_20170213.json',
}

#Pre-load all the json files
for k,v in task_flow_index.items():
    task_flow_index[k] = json.load(file('task_flows/'+v))

# final_modules = {
#     "initial_schedule_request" : 24587,
#     "reminder" : 24598,
#     "ask_for_updates" : 24592,
#     "onboarding" : 24596,    
# }

pronouns = {
    True : "she",
    False : "he"
}

possessive_pronouns = {
    True : "her",
    False : "his"
}

# def create_task_meta_obj_from_something():
#     pass

def create_exchange_context_obj_from_current_state(task_flow, task_obj, task_context_var_obj):
    """
    task_flow is the generalized workflow for this task
    task_obj is the instantiated task object

    If this state does not create a new exchange, return None.
    """

    raise DeprecatedError

    # current_state = task_context_obj["vars"]["$state"]
    # caregiver_id = task_obj["vars"]["requested_caregiver"]
    # recipient = task_obj["vars"]["recipient"]
    # next_recipient = task_obj["vars"]["next_recipient"] 
    # deadline = task_obj["vars"]["deadline"]

    # response = requests.get(config['sandman']['url']+'users/'+str(caregiver_id))
    # user_obj = response.json()

    # user_obj = task_obj["vars"]["caregivers"][recipient]
    
    # print '===== User obj ====='
    # print user_obj
    # print '#'*80

    # print json.dumps(task_context_var_obj, indent=2)

    #If there's no recipient or exchange_bot_type, then return None
    if task_context_var_obj["recipient"] == None:
        return None

    if task_context_var_obj["exchange_bot_type"] == None:
        return None

    # exchange_context_obj =  {
    #     "task_meta_obj": {
    #         "task_id": task_obj["task_id"],
    #         "task_subnode_id": task_context_var_obj["$state"],
    #         "user_id": task_context_var_obj["recipient"],
    #         "exchange_type_id": None,
    #         "exchange_bot_type": task_context_var_obj["exchange_bot_type"],
    #         "created_timestamp": task_obj["created_timestamp"],
    #     },
    #     "recipient_user_id": task_context_var_obj["recipient"],
    #     "next_recipient_user_id": task_context_var_obj["next_recipient"],
    #     "patient_user_id": task_context_var_obj["patient_user_id"],
    #     "current_task_deadline": task_context_var_obj["deadline"],
    #     "next_task_deadline": task_context_var_obj["deadline"] #!!! This is wrong.
    # }
    # print '===== exchange_context_obj ====='
    # print json.dumps(exchange_context_obj)

    # exchange_context_obj = {
    #     "exchange_id" : None,
    #     "user_phone_number" : recipient_user_obj['mobile_number'],

    #     "meta" : event_obj["task_meta_obj"],

    #     "context" : {
    #         "current_caregiver_first_name" : recipient_user_obj["first_name"],
    #         "next_caregiver_first_name" : next_recipient_user_obj["first_name"],
                    
    #         "current_deadline_day_hmnrdbl" : humanize.naturaldate(current_task_deadline_dt),
    #         "current_deadline_hour_hmnrdbl" : current_task_deadline_dt.strftime('%I:%M%p'),#"%s:%s" % (current_task_deadline_dt.hour, current_task_deadline_dt.minute),

    #         "next_deadline_day_hmnrdbl" : humanize.naturaldate(next_task_deadline_dt),
    #         "next_deadline_hour_hmnrdbl" : next_task_deadline_dt.strftime('%I:%M%p'),#"%s:%s" % (next_task_deadline_dt.hour, next_task_deadline_dt.minute),
        
    #         "patient_name" : patient_user_obj["first_name"],
    #         "patient_pronoun" : pronouns[patient_user_obj["is_female"]],
    #         "patient_possessive_pronoun" : possessive_pronouns[patient_user_obj["is_female"]],
    #         "patient_phone_number" : patient_user_obj["mobile_number"],        

    #         "task_contact_mode" : "call",
    #     },

    #     "history" : [],
    # }

    exchange_context_obj = {
        "exchange_id" : None,
        "user_phone_number" : recipient_user_obj['mobile_number'],

        # "meta" : event_obj["task_meta_obj"],

        "context" : {
            "current_caregiver_first_name" : recipient_user_obj["first_name"],
            "next_caregiver_first_name" : next_recipient_user_obj["first_name"],
                    
            "current_deadline_day_hmnrdbl" : humanize.naturaldate(current_task_deadline_dt),
            "current_deadline_hour_hmnrdbl" : current_task_deadline_dt.strftime('%I:%M%p'),#"%s:%s" % (current_task_deadline_dt.hour, current_task_deadline_dt.minute),

            "next_deadline_day_hmnrdbl" : humanize.naturaldate(next_task_deadline_dt),
            "next_deadline_hour_hmnrdbl" : next_task_deadline_dt.strftime('%I:%M%p'),#"%s:%s" % (next_task_deadline_dt.hour, next_task_deadline_dt.minute),
        
            "patient_name" : patient_user_obj["first_name"],
            "patient_pronoun" : pronouns[patient_user_obj["is_female"]],
            "patient_possessive_pronoun" : possessive_pronouns[patient_user_obj["is_female"]],
            "patient_phone_number" : patient_user_obj["mobile_number"],

            "task_contact_mode" : "call",
        },

        "history" : [],
    }

    return exchange_context_obj

def create_new_exchange_object(task_obj, exchange_context_obj, now):
    return {
        "task_id" : task_obj["task_id"],
        "task_subnode_id" : None,#!!!task_obj["task_subnode_id"],
        # "start_timestamp" : task_obj["created_timestamp"],
        "exchange_context_obj" : json.dumps(exchange_context_obj),
        "is_complete" : False,
        "was_successful" : None,
        "created_timestamp" : now,
        "update_timestamp" : now,
    }

    # return {
    #     "task_id" : exchange_context_obj["meta"]["task_id"],
    #     "task_subnode_id" : exchange_context_obj["meta"]["task_subnode_id"],
    #     "start_timestamp" : exchange_context_obj["meta"]["created_timestamp"],
    #     "exchange_context_obj" : json.dumps(exchange_context_obj),
    #     "is_complete" : False,
    #     "was_successful" : None,
    #     "created_timestamp" : exchange_context_obj["meta"]["created_timestamp"],
    #     "update_timestamp" : exchange_context_obj["meta"]["created_timestamp"],
    # }


def create_new_task_object(group_id, task_type, task_context_obj, now):
    return {
        "group_id" : group_id,
        "task_type_id" : -1, #!!! This is made up
        "task_type" : task_type,
        "task_context_obj" : json.dumps(task_context_obj),
        "is_complete" : False,
        "was_successful" : None,
        "outcomes_obj" : json.dumps({}),
        "outcomes_obj_id" : None,
        "created_timestamp" : str(now),
        "update_timestamp" : str(now),
    }


# def determine_outcome(exchange_context_obj):
#     if exchange_context_obj["meta"]["task_subnode_id"] == "schedule_visit":
#         for h in exchange_context_obj["history"]:
#             if "motion_result" in h:
#                 if h["motion_result"] == "yes":
#                     return "accept"
#         return "reject"


# def handle_trigger_updates():
#     pass

# def check_and_handle_all_task_updates(task_obj_list, now):
    # updated_task_id_list = []
    # nonupdated_task_id_list = []
        # if logic.check_and_handle_task_updates(task_id, task_context_obj, task_flow):
        #     updated_task_id_list.append(task_id)
        # else:
        #     nonupdated_task_id_list.append(task_id)


# def append_to_exchange_history():
#     new_history_obj ={
#         "timestamp" : str(datetime.datetime.now()),
#         "from" : "Aida",
#         "to" : exchange_context_obj["meta"]["user_id"],
#         "message" : message,
#     }
#     print 'Here'
#     if u"module" in response_json:
#         print 'Hererrerere!'
#         new_history_obj["motion_module"] = response_json["module"]

