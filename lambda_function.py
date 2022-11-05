### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")

### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


#----------------------------------------#

def recommend_portfolio(intent_request):
    if intent_request["invocationSource"] == "DialogCodeHook":

        slots = get_slots(intent_request)

        if (slots["age"] == None) or (parse_int(slots["age"]) < 1 or parse_int(slots["age"]) >= 65):
            elicit_slot = {
                "sessionAttributes": intent_request["sessionAttributes"],
                "dialogAction": {
                    "type": "ElicitSlot",
                    "intentName": intent_request["currentIntent"]["name"],
                    "slots": slots,
                    "slotToElicit": slots["age"],
                    "message": "Age must be between 1 and 64",
                },
            }
            return elicit_slot
            

        elif (slots["investmentAmount"] == None) or (parse_int(slots["investmentAmount"]) < 5000):
            elicit_slot = {
                "sessionAttributes": intent_request["sessionAttributes"],
                "dialogAction": {
                    "type": "ElicitSlot",
                    "intentName": intent_request["currentIntent"]["name"],
                    "slots": slots,
                    "slotToElicit": slots["investmentAmount"],
                    "message": "You must invest at least $5000",
                },
            }
            return elicit_slot
        
        elif (slots["riskLevel"] == None) or ((slots["riskLevel"] in ['None', 'none', 'Low', 'low', 'Medium', 'medium', 'High', 'high']) == False):
            elicit_slot = {
                "sessionAttributes": intent_request["sessionAttributes"],
                "dialogAction": {
                    "type": "ElicitSlot",
                    "intentName": intent_request["currentIntent"]["name"],
                    "slots": slots,
                    "slotToElicit": slots["riskLevel"],
                    "message": "You must select from 'None, Low, Medium, High'",
                },
            }
            return elicit_slot
            

        else:
            output_session_attributes = intent_request["sessionAttributes"]
            delegate_slot = {
                "sessionAttributes": output_session_attributes,
                "dialogAction": {"type": "Delegate", "slots": slots},
            }


        risk_level = delegate_slot["dialogAction"]["slots"]["riskLevel"]

        if risk_level == ("None" or "none"):
            message = "100% bonds (AGG), 0% equities (SPY)"
        elif risk_level == ("Low" or "low"):
            message = "60% bonds (AGG), 40% equities (SPY)"
        elif risk_level == ("Medium" or "medium"):
            message = "40% bonds (AGG), 60% equities (SPY)"
        elif risk_level == ("High" or "high"):
            message = "20% bonds (AGG), 80% equities (SPY)"

        response = {
            "sessionAttributes": intent_request["sessionAttributes"],
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": message
                    }
                }
        }

        return response

#----------------------------------------#
### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    # Get the name of the current intent
    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
