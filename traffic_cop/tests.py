import json
import requests
import unittest
import tempfile
import datetime

from nose.tools import assert_equal, assert_dict_equal, assert_raises

import util, logic, services, data, traffic_cop
from taskmeister import state_machine

url = 'http://localhost:5000/'
auth_config = json.load(file('auth_config.json'))
test_db_obj = json.load(file('test_db.json'))

class TestAppRoutes():

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_task(self):
        # create_new_task accepts POST, not GET
        response = requests.get(url+'create_new_task')
        assert_equal(
            response.status_code,
            405
        )
        assert_dict_equal(
            response.json(),
            {"msg" : "Method not allowed"}
        )

        response = requests.post(
            url+'create_new_task',
            json = {
                "hello" : "world"
            }
        )
        assert_equal(
            response.status_code,
            500
        )
        assert_dict_equal(
            response.json(),
            {"msg": "Missing required field: task_type"}
        )

        ### Inputs:
        # Fetch group context from sandman to create a temporary meta_object (AAA)
        # Use state_machine to initialize_task_context_obj

        json_obj = {
            "task_type" : "arrange_impatient_visit",
            "group_id" : 1,
            "deadline" : 10000,        
        }

        # old_task_count = dm.get_task_count()
        response = requests.post(
            url+'create_new_task',
            json = json_obj,
        )
        print '$'*80
        print response.text
        assert_dict_equal(
            response.json(),
            {"msg": "success"}
        )
        # new_task_count = dm.get_task_count()

        # assert_equal(old_task_count+1, new_task_count)


        ### Outputs:
        # Create task object and store it to sandman
        # Create initial exchange
        # Post to traffic cop
        # Return a (mostly meaningless) result object


    def test_twilio_webhook(self):

        # create_new_task accepts POST, not GET
        response = requests.get(url+'twilio_webhook')
        assert_equal(
            response.status_code,
            405
        )
        assert_dict_equal(
            response.json(),
            {"msg" : "Method not allowed"}
        )

        response = requests.post(
            url+'twilio_webhook',
            json = {
                "hello" : "world"
            }
        )
        assert_equal(
            response.status_code,
            500
        )
        assert_dict_equal(
            response.json(),
            {"msg": "Missing required field: body"}
        )

        ### Inputs ###
        # Fetch exchange object from dynamo
        # Fetch response from motion
        # Extract the return_message

        json_obj = {}

        response = requests.post(
            url+'twilio_webhook',
            json = json_obj
        )
        assert_equal(
            response.status_code,
            500
        )
        assert_dict_equal(
            response.json(),
            {"msg": "Missing required field: body"}
        )

        ### Outputs ###
        # Append to history
        # if done:
        #     Save to dynamo
        # else:
        #     Save to sandman
        #     Delete from dynamo
        #     Update task
        # Return the return_message to twilio


class DataManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.dm = data.DataManager(util.TEST_MODE, test_db_obj=test_db_obj)
        
        #!!! This version will only work as long as the DB has the same contents as the test DB.
        # dm = data.DataManager(data.RUN_MODE, config=auth_config)

    def tearDown(self):
        pass

    def test_get_context_vars_for_exchange(self):

        #!!! We should add json-schema checking to all these returned objectes

        print json.dumps(
            self.dm.get_context_vars_for_task(3, 25000),
            indent=2
        )
        # assert_equal(0,1)

        assert_dict_equal(
            self.dm.get_context_vars_for_exchange(1, 2, 3, 10000, 15000),
            {
                "current_caregiver_first_name": "George", 
                "next_deadline_hour_hmnrdbl": "08:10PM", 
                "current_deadline_hour_hmnrdbl": "06:46PM", 
                "patient_pronoun": "he", 
                "patient_possessive_pronoun": "his", 
                "task_contact_mode": "call", 
                "next_caregiver_first_name": "Abe", 
                "current_deadline_day_hmnrdbl": "Dec 31 1969", 
                "user_phone_number": None, 
                "next_deadline_day_hmnrdbl": "Dec 31 1969", 
                "patient_name": "Peter", 
                "patient_phone_number": "+14158602014"
            }
        )

        assert_dict_equal(
            self.dm.get_context_vars_for_exchange(4, 5, 6, 10000, 15000),
            {
                "current_caregiver_first_name": "Adi", 
                "next_deadline_hour_hmnrdbl": "08:10PM", 
                "current_deadline_hour_hmnrdbl": "06:46PM", 
                "patient_pronoun": "he", 
                "patient_possessive_pronoun": "his", 
                "task_contact_mode": "call", 
                "next_caregiver_first_name": "Jane", 
                "current_deadline_day_hmnrdbl": "Dec 31 1969", 
                "user_phone_number": "+16176105085", 
                "next_deadline_day_hmnrdbl": "Dec 31 1969", 
                "patient_name": "Abe A", 
                "patient_phone_number": "+18018307029"
            }
        )

    def test_get_context_vars_for_task(self):

        #!!! We should add json-schema checking to all these returned objectes

        assert_dict_equal(
            self.dm.get_context_vars_for_task(1, 20000, shuffle=False),
            {
                "caregiver_id_list": [
                    2, 
                    3,
                    4
                ], 
                "deadline": 20000, 
                "patient_user_id": 5
            }
        )

        assert_dict_equal(
            self.dm.get_context_vars_for_task(3, 25000, shuffle=False),
            {
                "caregiver_id_list": [
                    4
                ], 
                "deadline": 25000, 
                "patient_user_id": 5
            }
        )

    def test_put_and_post_exchange(self):

        #!!! We should add json-schema checking to all these returned objectes

        assert_equal(
            self.dm.get_exchange_count(),
            0,
        )

        with assert_raises(KeyError):
            self.dm.put_exchange({})

        assert_equal(
            self.dm.get_exchange_count(),
            0,
        )

        exchange = self.dm.post_exchange({"hi": "mom"})

        assert_equal(
            self.dm.get_exchange_count(),
            1,
        )
        assert_dict_equal(
            self.dm.get_exchange(0),
            {
                "exchange_id": 0,
                "hi": "mom",
            }
        )

        exchange = self.dm.post_exchange({"hi": "dad"})

        assert_equal(
            self.dm.get_exchange_count(),
            2,
        )

        self.dm.put_exchange(exchange)
        assert_equal(
            self.dm.get_exchange_count(),
            2,
        )
        assert_dict_equal(
            self.dm.get_exchange(0),
            {
                "exchange_id": 0,
                "hi": "mom",
            }
        )
        assert_dict_equal(
            self.dm.get_exchange(1),
            {
                "exchange_id": 1,
                "hi": "dad",
            }
        )


        exchange["other"] = "more stuff"
        self.dm.put_exchange(exchange)
        assert_equal(
            self.dm.get_exchange_count(),
            2,
        )
        assert_dict_equal(
            self.dm.get_exchange(1),
            {
                "exchange_id": 1,
                "hi": "dad",
                "other": "more stuff"
            }
        )




class ImpatientScheduleVisitTaskFlowTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_arrange_visit(self):
        arrange_visit_logic = json.loads(file('task_flows/arrange_visit_logic_20170213.json').read())

        task_state_obj = state_machine.initialize_task_context_obj(
            arrange_visit_logic,
            {
                "deadline" : 30000,
                "caregiver_id_list" : ["Alvin", "Simon", "Theodore"]
            },
            1000
        )
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Alvin" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 4600 )
        assert_equal( task_state_obj["vars"]["deadline"], 30000 )
        assert_equal( task_state_obj["vars"]["recipient"], "Alvin" )
        assert_equal( len(task_state_obj["history"]), 1 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 2000, 'exchange', 'reject')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 5600 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 2 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 5800, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit_second_try" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 9400 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 3 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 9500, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "abandon_scheduling_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 9560 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 4 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 9600, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 13200 )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( len(task_state_obj["history"]), 5 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 12000, 'exchange', 'accept')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "remind_about_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 22800 )
        assert_equal( len(task_state_obj["history"]), 6 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 22900, 'deadline', 'exceeded')
        print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "follow_up_after_visit" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 33600 )
        assert_equal( len(task_state_obj["history"]), 7 )


    def test_impatient_arrange_visit(self):
        arrange_visit_logic = json.loads(file('task_flows/impatient_arrange_visit_logic_20170213.json').read())

        task_state_obj = state_machine.initialize_task_context_obj(
            arrange_visit_logic,
            {
                "deadline" : 1000,
                "caregiver_id_list" : ["Alvin", "Simon", "Theodore"]
            },
            0
        )

        assert_equal( task_state_obj["vars"]["$state"], "wait" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 95 )
        assert_equal( task_state_obj["vars"]["deadline"], 1000 )
        assert_equal( task_state_obj["vars"]["recipient"], None )
        assert_equal( task_state_obj["vars"]["exchange_bot_type"], None )
        assert_equal( len(task_state_obj["history"]), 1 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 150, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Alvin" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 205 )
        assert_equal( task_state_obj["vars"]["deadline"], 1000 )
        assert_equal( task_state_obj["vars"]["recipient"], "Alvin" )
        assert_equal( len(task_state_obj["history"]), 2 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 200, 'exchange', 'reject')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 255 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 3 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 260, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit_second_try" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 315 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 4 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 380, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "abandon_scheduling_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 435 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 5 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 500, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 555 )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( len(task_state_obj["history"]), 6 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 510, 'exchange', 'accept')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "wait_until_reminder" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], None )
        assert_equal( task_state_obj["vars"]["exchange_bot_type"], None )
        assert_equal( task_state_obj["vars"]["deadline"], 1000 )
        assert_equal( task_state_obj["vars"]["state_deadline"], 945 )
        assert_equal( len(task_state_obj["history"]), 7 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 950, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "remind_about_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 945 )
        assert_equal( len(task_state_obj["history"]), 8 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 950, 'deadline', 'exceeded')
        print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "wait_until_after_visit" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], None )
        assert_equal( task_state_obj["vars"]["exchange_bot_type"], None )
        assert_equal( task_state_obj["vars"]["state_deadline"], 1055 )
        assert_equal( len(task_state_obj["history"]), 9 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 1060, 'deadline', 'exceeded')
        print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "follow_up_after_visit" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        # assert_equal( task_state_obj["vars"]["state_deadline"], 955 )
        assert_equal( len(task_state_obj["history"]), 10 )


class LogicTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_initialize_task_context_obj(self):
        task_flow = json.load(file('task_flows/impatient_arrange_visit_logic_20170213.json'))
        task_context_var_obj = {"caregiver_id_list": [4, 2, 3], "deadline": 10000, "patient_user_id": 5}
        now = 1488061520

        result = state_machine.initialize_task_context_obj(task_flow, task_context_var_obj, now)

        assert_dict_equal(
            result,
            {
                "vars": {
                    "caregiver_id_list": [4, 2, 3],
                    "state_deadline": 9095,
                    "$state": "wait",
                    "patient_user_id": 5,
                    "exchange_bot_type": None,
                    "deadline": 10000,
                    "recipient": None
                },
                "history": [{
                    "new_state": "wait",
                    "vars": {
                        "caregiver_id_list": [4, 2, 3],
                        "state_deadline": 9095,
                        "$state": "wait",
                        "patient_user_id": 5,
                        "exchange_bot_type": None,
                        "deadline": 10000,
                        "recipient": None
                    },
                    "trigger_type": "init",
                    "timestamp": 1488061520.0,
                    "old_state": None,
                    "trigger_value": None
                }]
            }
        )

       # task_flow
        # task_obj
        # task_context_var_obj

    def test_create_new_task_object(self):
        assert_dict_equal(
            logic.create_new_task_object(10, "wootwoot", {"baby":"giraffe"}, 10000),
            {
                "group_id" : 10,
                "task_type_id" : -1, #!!! This is made up
                "task_type" : "wootwoot",
                "task_context_obj" : '{\"baby\": \"giraffe\"}',
                "is_complete" : False,
                "was_successful" : None,
                "outcomes_obj" : "{}",
                "outcomes_obj_id" : None,
                "created_timestamp" : "10000",
                "update_timestamp" : "10000",
            }
        )

class TwilioWebHookTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, app2.app.config['DATABASE'] = tempfile.mkstemp()
        traffic_cop.app.config['TESTING'] = True
        traffic_cop.app.config['DEBUG'] = True
        self.app = traffic_cop.app.test_client()
        # with app2.app.app_context():
            # app2.init_db()

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(app2.app.config['DATABASE'])
        pass

    def test_webhook(self):

        #fromPhone is wrong: should be fromNumber
        response = self.app.post(
            '/twilio_webhook',
            data=json.dumps({
                'fromPhone': '+18015555555',
                'body': 'hello hello',
            })
        )
        assert_dict_equal(
            json.loads(response.data),
            {"msg": "Missing required field: fromNumber"}
        )

        json_obj = {
            "task_type" : "arrange_impatient_visit",
            "group_id" : 1,
            "deadline" : 1000,
            "shuffle" : False,
            "now" : 0,
        }
        self.app.post(
            '/create_new_task',
            data=json.dumps(json_obj),
        )
        self.app.post(
            '/check_for_updates',
            data=json.dumps({'now': 150})
        )

        exchange_context_obj = json.loads(traffic_cop.dm.get_exchange(0)["exchange_context_obj"])
        print '******************'
        # print json.dumps(exchange_context_obj, indent=2)

        response = self.app.post(
            '/twilio_webhook',
            data=json.dumps({
                'fromNumber': '+18018307029',
                'body': 'hello hello',
            })
        )
        print response, "???"
        # assert_dict_equal(
        #     json.loads(response.data),
        #     {"msg": "Not good"},
        # )

        # assert_equal(0,1)


class AppTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, app2.app.config['DATABASE'] = tempfile.mkstemp()
        traffic_cop.app.config['TESTING'] = True
        traffic_cop.app.config['DEBUG'] = True
        self.app = traffic_cop.app.test_client()
        # with app2.app.app_context():
            # app2.init_db()

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(app2.app.config['DATABASE'])
        pass

    def test_task_and_exchange_history_1(self):

        json_obj = {
            "task_type" : "arrange_impatient_visit",
            "group_id" : 1,
            "deadline" : 1000,
            "shuffle" : False,
            "now" : 0,
        }

        old_task_count = traffic_cop.dm.get_task_count()
        self.app.post(
            '/create_new_task',
            data=json.dumps(json_obj),
        )
        new_task_count = traffic_cop.dm.get_task_count()

        assert_equal(old_task_count+1, new_task_count)
        # print json.dumps(app2.dm.get_task(0), indent=2)
        # print '^'*80
        # print json.dumps(json.loads(app2.dm.get_task(0)["task_context_obj"]), indent=2)
        task_context_obj = json.loads(traffic_cop.dm.get_task(0)["task_context_obj"])

        assert_equal(traffic_cop.dm.get_exchange_count(), 0)
        assert_equal( len(task_context_obj["history"]), 1 )
        assert_equal( task_context_obj["vars"]["$state"], "wait" )
        assert_equal( task_context_obj["vars"]["state_deadline"], 95 )
        assert_equal( task_context_obj["vars"]["deadline"], 1000 )
        assert_equal( task_context_obj["vars"]["recipient"], None )
        assert_equal( task_context_obj["vars"]["exchange_bot_type"], None )
        
        self.app.post(
            '/check_for_updates',
            data=json.dumps({'now': 150})
        )
        task_context_obj = json.loads(traffic_cop.dm.get_task(0)["task_context_obj"])
        # task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 150, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        
        assert_equal(traffic_cop.dm.get_task_count(), 1)
        assert_equal(traffic_cop.dm.get_exchange_count(), 1)
        assert_equal( len(task_context_obj["history"]), 2 )
        assert_equal( task_context_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_context_obj["vars"]["requested_caregiver_id"], 2 )
        assert_equal( task_context_obj["vars"]["state_deadline"], 205 )
        assert_equal( task_context_obj["vars"]["deadline"], 1000 )
        assert_equal( task_context_obj["vars"]["recipient"], 2 )

        # return

        #Exchange.reject 200
        self.app.post(
            '/check_for_updates',
            data=json.dumps({'now': 150})
        )
        task_context_obj = json.loads(traffic_cop.dm.get_task(0)["task_context_obj"])
        return

        ###!!! Not implemented past this point
        print json.dumps(task_context_obj["vars"], indent=2)
        assert_equal( task_context_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_context_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_context_obj["vars"]["state_deadline"], 255 )
        assert_equal( task_context_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_context_obj["history"]), 3 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 200, 'exchange', 'reject')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 255 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 3 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 260, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit_second_try" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 315 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 4 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 380, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "abandon_scheduling_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Simon" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 435 )
        assert_equal( task_state_obj["vars"]["recipient"], "Simon" )
        assert_equal( len(task_state_obj["history"]), 5 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 500, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "schedule_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 555 )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( len(task_state_obj["history"]), 6 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 510, 'exchange', 'accept')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "wait_until_reminder" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], None )
        assert_equal( task_state_obj["vars"]["exchange_bot_type"], None )
        assert_equal( task_state_obj["vars"]["deadline"], 1000 )
        assert_equal( task_state_obj["vars"]["state_deadline"], 945 )
        assert_equal( len(task_state_obj["history"]), 7 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 950, 'deadline', 'exceeded')
        # print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "remind_about_visit" )
        assert_equal( task_state_obj["vars"]["requested_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        assert_equal( task_state_obj["vars"]["state_deadline"], 945 )
        assert_equal( len(task_state_obj["history"]), 8 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 950, 'deadline', 'exceeded')
        print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "wait_until_after_visit" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], None )
        assert_equal( task_state_obj["vars"]["exchange_bot_type"], None )
        assert_equal( task_state_obj["vars"]["state_deadline"], 1055 )
        assert_equal( len(task_state_obj["history"]), 9 )

        task_state_obj = state_machine.update_on_trigger(arrange_visit_logic, task_state_obj, 1060, 'deadline', 'exceeded')
        print json.dumps(task_state_obj["vars"], indent=2)
        assert_equal( task_state_obj["vars"]["$state"], "follow_up_after_visit" )
        assert_equal( task_state_obj["vars"]["confirmed_caregiver_id"], "Theodore" )
        assert_equal( task_state_obj["vars"]["recipient"], "Theodore" )
        # assert_equal( task_state_obj["vars"]["state_deadline"], 955 )
        assert_equal( len(task_state_obj["history"]), 10 )


class ExchangeTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_exchange_if_applicable(self):
        #!!! These data objects are here to ensure backwards compatibility.
        #!!! I'm NOT CERTAIN that they are the responses thay we really want!
        test_db_obj = json.load(file('test_db.json'))
        task_flow = json.load(file('task_flows/impatient_arrange_visit_logic_20170213.json'))
        dm = data.DataManager(util.TEST_MODE, test_db_obj=test_db_obj)
        motion = services.Motion(util.TEST_MODE, None)
        # task_context_var_obj = {"caregiver_id_list": [4, 2, 3], "deadline": 10000, "patient_user_id": 5}
        now = 1488061520



        assert_equal(
            dm.get_exchange_count(),
            0
        )

        task_obj = {
            "vars": {
                "caregiver_id_list": [4, 2, 3],
                "state_deadline": 9095,
                "$state": "wait",
                "patient_user_id": 5,
                "exchange_bot_type": None,
                "deadline": 10000,
                "recipient": None
            },
            "history": [{
                "new_state": "wait",
                "vars": {
                    "caregiver_id_list": [4, 2, 3],
                    "state_deadline": 9095,
                    "$state": "wait",
                    "patient_user_id": 5,
                    "exchange_bot_type": None,
                    "deadline": 10000,
                    "recipient": None
                },
                "trigger_type": "init",
                "timestamp": 1488061520.0,
                "old_state": None,
                "trigger_value": None
            }]
        }

        #This exchange isn't applicable (recipient=None; exchange_bot_type=None), so it shouldn't create a new exchange
        traffic_cop.create_exchange_if_applicable(dm, motion, task_flow, task_obj, task_obj["vars"], now)
        assert_equal(
            dm.get_exchange_count(),
            0
        )

        task_obj = {
            "task_id" : 1,
            "vars": {
                "caregiver_id_list": [4, 2, 3],
                "state_deadline": 9095,
                "$state": "wait",
                "patient_user_id": 5,
                "exchange_bot_type": "testtest",
                "deadline": 10000,
                "recipient": 4,
                "requested_caregiver_id": 1,
                "next_recipient": 2,
            },
            "history": [{
                "new_state": "wait",
                "vars": {
                    "caregiver_id_list": [4, 2, 3],
                    "state_deadline": 9095,
                    "$state": "wait",
                    "patient_user_id": 5,
                    "exchange_bot_type": None,
                    "deadline": 10000,
                    "recipient": None
                },
                "trigger_type": "init",
                "timestamp": 1488061520.0,
                "old_state": None,
                "trigger_value": None
            }]
        }

        traffic_cop.create_exchange_if_applicable(dm, motion, task_flow, task_obj, task_obj["vars"], now)
        assert_equal(
            dm.get_exchange_count(),
            1
        )

        ex = dm.get_exchange(0)
        assert_equal(ex["update_timestamp"], 1488061520)
        assert_equal(ex["task_id"], 1)
        assert_equal(ex["exchange_id"], 0)
        assert_equal(ex["was_successful"], None)
        assert_equal(ex["created_timestamp"], 1488061520)
        assert_equal(ex["is_complete"], False)
        assert_equal(ex["task_subnode_id"], None)

        exchange_context_obj = json.loads(dm.get_exchange(0)["exchange_context_obj"])
        assert_dict_equal(
            exchange_context_obj["vars"],
            {
                "next_caregiver_first_name": "Abe", 
                "current_caregiver_first_name": "George", 
                "next_deadline_hour_hmnrdbl": "03:59PM", 
                "user_phone_number": None, 
                "next_deadline_day_hmnrdbl": "Dec 31 1969", 
                "current_deadline_day_hmnrdbl": "Dec 31 1969", 
                "current_deadline_hour_hmnrdbl": "06:46PM", 
                "patient_name": "Jane", 
                "patient_pronoun": "she", 
                "patient_possessive_pronoun": "her", 
                "patient_phone_number": "+16505555555", 
                "task_contact_mode": "call"
            }
        )

        assert_equal(
            exchange_context_obj["user_phone_number"],
            None)
        assert_equal(
            exchange_context_obj["exchange_id"],
            0)

        assert_equal(
            len(exchange_context_obj["history"]),
            1
        )
        assert_dict_equal(
            exchange_context_obj["history"][0],
            {
                "timestamp": 1488061520, 
                "message": "Hi, I'm a dumb bot.", 
                "from": "Aida", 
                "to": "George"
            }
        )

        # print json.dumps(exchange_context_obj["history"], indent=2) 
        # assert_equal(0,1)






