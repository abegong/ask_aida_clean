import json
import util

bot_ids = {
    "initial_schedule_request" : 24587,
    "second_chance" : 390699,
    "moved_on_to_someone_else" : 390708,
    "reminder" : 24589,
    "ask_for_updates" : 24592,
    "onboarding" : 24596,
}

class Motion(object):
    def __init__(self, mode, config=None):
        self.mode = mode
        self.config = config

    def get(self, message, exchange_context_obj):
        return ("Hi, I'm a dumb bot.", None, {})

        # print datetime.datetime.now(), "Fetching response from motion..."
        params = {
            "msg" : message,
            "bot" : bot_ids[exchange_context_obj["vars"]["exchange_bot_type"]],
            "session" : "askaida_"+str(int(exchange_context_obj["exchange_id"])),
            "key" : config['motion']['api_key']
        }
        print json.dumps(params, indent=2)
        response = requests.get(
            config['motion']['url'],
            params = params
        )


        # {
        #     "msg" : message,
        #     "bot" : bot_ids[exchange_context_obj["meta"]["exchange_bot_type"]],
        #     "session" : "askaida_"+str(int(exchange_context_obj["exchange_id"])),
        #     "key" : config['motion']['api_key']
        # }

        response = requests.get(config['motion']['url'], params)
        print '=== Motion response ==='
        response_json = response.json()
        # print response
        # print response.text
        print response_json
        # print response.json()["botResponse"]
        if response_json['code'] == 200:
            return_message = response_json["botResponse"]
            done = False
        else:
            # return_message = "I have no response to that."
            return_message = "Okay. Aida over and out."
            done = True

        return return_message, done, result


class Twilio(object):
    def __init__(self, mode, config=None):
        self.mode = mode
        self.config = config

        self.sent_message_queue = []

    def send_sms(self, number, message):
        self.sent_message_queue.append({
            "number": number,
            "message": message,
        })
        if self.mode == util.RUN_MODE:

            response = requests.post(
                config['twilio']['url']+config['twilio']['account_id']+'/Messages.json',
                data = {
                    'To' : number,
                    'From' : config['twilio']['from_number'],
                    'Body' : message,#str(random.choice(range(1000)))+" "+json.dumps(query_params)[:100],
                },
                auth=(config['twilio']['account_id'], config['twilio']['auth_token'])
            )

            # print response.text
            print response.text
            return response.text

        else:
            print '*'*80
            print 'Fake sending SMS:'
            print json.dumps({
                "number": number,
                "message": message,
            }, indent=2)
            print '*'*80


