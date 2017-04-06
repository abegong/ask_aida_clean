import datetime
import json
import random
import requests
import humanize

import util, logic

def get_dynamo_connection(config):
    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    from boto.dynamodb2.items import Item
    from boto.dynamodb2.fields import HashKey, GlobalAllIndex
    from boto.dynamodb2.types import NUMBER

    connection = boto.dynamodb2.connect_to_region(
        config['aws']['region'],
        aws_access_key_id=config['aws']['access_key'],
        aws_secret_access_key=config['aws']['secret_key'],
    )

    table = Table(
        config['dynamo']['exchange_table_name'],
        connection=connection
    )

    return connection, table


#Testing, Staging, Prod
def get_connections(config, connection_list):
    connections = {}
    
    for connection_type in connection_type_list:
        if connection_type == 'dynamo':
            connections[connection_type] = get_dynamo_connection(config)

    return connections

class DataManager(object):
    """docstring for DataManager"""
    
    def __init__(self, mode, config=None, test_db_obj=None):
        self.mode = mode
        self.config = config

        if mode == util.TEST_MODE:
            self.test_db_obj = test_db_obj

        elif mode == util.RUN_MODE:
            self.dynamo_connection, self.dynamo_exchange_table = get_dynamo_connection(config)

    def get_task(self, task_id):
        if self.mode == util.TEST_MODE:
            return self.test_db_obj['tasks'][task_id]

        else:

            response = requests.get(auth_config['sandman']['url']+'tasks/'+str(task_id))
            return response.json()

    def get_exchange(self, exchange_id):
        if self.mode == util.TEST_MODE:
            return self.test_db_obj['exchanges'][exchange_id]

        else:
            # print datetime.datetime.now(), "Fetching exchange_context_obj..."
            # exchange_results = dynamo_exchange_table.query(index='SecondaryIndexName', user_phone_number__eq=user_phone_number)
            # #!!! Some error handling here would be a really great idea
            # exchange_context_obj = exchange_results.next()
            # print json.dumps(dict(exchange_context_obj), indent=2, cls=DecimalEncoder)
            raise NotImplementedError

    def get_exchange_by_phone_number(self, phone_number):
        if self.mode == util.TEST_MODE:
            return [e for e in self.test_db_obj['exchanges'] if json.loads(e['exchange_context_obj'])['user_phone_number']==phone_number]

        else:
            # print datetime.datetime.now(), "Fetching exchange_context_obj..."
            # exchange_results = dynamo_exchange_table.query(index='SecondaryIndexName', user_phone_number__eq=user_phone_number)
            # #!!! Some error handling here would be a really great idea
            # exchange_context_obj = exchange_results.next()
            # print json.dumps(dict(exchange_context_obj), indent=2, cls=DecimalEncoder)
            raise NotImplementedError


    def get_incomplete_tasks(self):
        if self.mode == util.TEST_MODE:
            incomplete_tasks = []
            for task in self.test_db_obj['tasks']:
                if task["is_complete"] == False:
                    incomplete_tasks.append(task)

        else:
            response = requests.get(auth_config['sandman']['url']+'tasks/?is_complete=false')
            incomplete_tasks = response.json()["resources"]

        return incomplete_tasks

    def post_task(self, task_obj):
        if self.mode == util.RUN_MODE:
            response = requests.post(
                self.config['sandman']['url']+'tasks/',
                data = json.dumps(task_obj)
            )
            # print response
            # print response.text
            return response.json()

        elif self.mode == util.TEST_MODE:
            task_obj["task_id"] = len(self.test_db_obj['tasks'])
            self.test_db_obj['tasks'].append(task_obj)
            return task_obj

    def post_exchange(self, exchange_obj):
        if self.mode == util.RUN_MODE:
            response = requests.post(
                self.config['sandman']['url']+'exchanges/',
                data = json.dumps(exchange_obj)
            )
            # print response
            # print response.text
            return response.json()

        elif self.mode == util.TEST_MODE:
            exchange_obj["exchange_id"] = len(self.test_db_obj['exchanges'])
            self.test_db_obj['exchanges'].append(exchange_obj)
            return exchange_obj

    def put_task(self, task_obj):
        # temp_task_obj = 

        if self.mode == util.RUN_MODE:
            response = requests.put(
                config['sandman']['url']+'tasks/'+str(task_obj["task_id"]),
                json = task_obj
            )
            return response.json()

        elif self.mode == util.TEST_MODE:
            self.test_db_obj['tasks'][task_obj["task_id"]] = task_obj
            return task_obj

    def put_exchange(self, exchange_obj):
        # temp_task_obj = 

        if self.mode == util.RUN_MODE:
            response = requests.put(
                config['sandman']['url']+'exchanges/'+str(exchange_obj["exchange_id"]),
                json = task_obj
            )
            return response.json()

        elif self.mode == util.TEST_MODE:
            self.test_db_obj['exchanges'][exchange_obj["exchange_id"]] = exchange_obj
            return exchange_obj


    def get_context_vars_for_exchange(self, recipient_user_id, next_recipient_user_id, patient_user_id, current_task_deadline, next_task_deadline):
        if self.mode == util.RUN_MODE:
            recipient_user_obj = requests.get(
                self.config["sandman"]["url"]+"users/"+str(recipient_user_id)
            ).json()

            next_recipient_user_obj = requests.get(
                self.config["sandman"]["url"]+"users/"+str(next_recipient_user_id)
            ).json()

            patient_user_obj = requests.get(
                self.config["sandman"]["url"]+"users/"+str(patient_user_id)
            ).json()

        elif self.mode == util.TEST_MODE:
            recipient_user_obj = self.test_db_obj['users'][recipient_user_id]
            next_recipient_user_obj = self.test_db_obj['users'][next_recipient_user_id]
            patient_user_obj = self.test_db_obj['users'][patient_user_id]

        current_task_deadline_dt = datetime.datetime.fromtimestamp(current_task_deadline)
        next_task_deadline_dt = datetime.datetime.fromtimestamp(next_task_deadline)

        #Create context object---this should happen externally. Tasks have the context to create exchanges; exchanges only have to context to update themselves.
        # print datetime.datetime.now(), "Creating context obj..."
        exchange_context_obj = {
            "user_phone_number" : recipient_user_obj['mobile_number'],

            "current_caregiver_first_name" : recipient_user_obj["first_name"],
            "next_caregiver_first_name" : next_recipient_user_obj["first_name"],
                    
            "current_deadline_day_hmnrdbl" : humanize.naturaldate(current_task_deadline_dt),
            "current_deadline_hour_hmnrdbl" : current_task_deadline_dt.strftime('%I:%M%p'),#"%s:%s" % (current_task_deadline_dt.hour, current_task_deadline_dt.minute),

            "next_deadline_day_hmnrdbl" : humanize.naturaldate(next_task_deadline_dt),
            "next_deadline_hour_hmnrdbl" : next_task_deadline_dt.strftime('%I:%M%p'),#"%s:%s" % (next_task_deadline_dt.hour, next_task_deadline_dt.minute),
        
            "patient_name" : patient_user_obj["first_name"],
            "patient_pronoun" : logic.pronouns[patient_user_obj["is_female"]],
            "patient_possessive_pronoun" : logic.possessive_pronouns[patient_user_obj["is_female"]],
            "patient_phone_number" : patient_user_obj["mobile_number"],        

            "task_contact_mode" : "call",
        }

        return exchange_context_obj

    def get_context_vars_for_task(self, group_id, deadline, shuffle=True):
        if self.mode == util.RUN_MODE:
            # print datetime.datetime.now(), "Fetching group context from sandman..."
            response = requests.get(self.config['sandman']['url']+'groups/'+str(group_id))
            group_context_obj = response.json()['group_context_obj']

            # print datetime.datetime.now(), "Creating task object..."
            # task_flow = json.load(file('task_flows/'+task_type))

            response = requests.get(self.config['sandman']['url']+'group_roles/?group_id='+str(group_id)+'&group_role_type_id=1')
            #!!! Brittle! Assumes 1 and only 1 patient in each group.
            patient_user_obj = response.json()["resources"][0]

            #Get the caregiver_id_list
            response = requests.get(self.config['sandman']['url']+'group_roles/?group_id='+str(group_id))
            group_role_list_obj = response.json()["resources"]

        else:
            group_context_obj = self.test_db_obj['groups'][group_id]['group_context_obj']

            group_role_list_obj = []
            
            #!!! We have to skip the first object because it's empty in the mocked up JSON db.
            #!!! Search for `{}` in test_db.json
            for gr in self.test_db_obj['group_roles'][1:]: 
                if gr['group_id'] == group_id:
                    group_role_list_obj.append(gr)
                    
                    if gr['group_role_type_id'] == 1:
                        patient_user_obj = gr


        caregiver_id_list = [user_obj["user_id"] for user_obj in group_role_list_obj if user_obj["user_id"] != patient_user_obj["user_id"]]
        if shuffle:
            random.shuffle(caregiver_id_list)

        task_context_var_obj = {
            # "caregivers" : group_role_list_obj,
            "caregiver_id_list" : caregiver_id_list,
            "deadline" : deadline,
            "patient_user_id" : patient_user_obj['user_id'],
        }

        return task_context_var_obj

    def get_task_count(self):
        if self.mode == util.TEST_MODE:
            if 'tasks' in self.test_db_obj:
                return len(self.test_db_obj['tasks'])
            else:
                return 0

        else:

            #!!! Gross and inefficient
            response = requests.get(auth_config['sandman']['url']+'tasks/')
            return len(response.json()["resources"])


    def get_exchange_count(self):
        if self.mode == util.TEST_MODE:
            if 'exchanges' in self.test_db_obj:
                return len(self.test_db_obj['exchanges'])
            else:
                return 0

        else:

            #!!! Gross and inefficient
            response = requests.get(auth_config['sandman']['url']+'exchanges/')
            return len(response.json()["resources"])


