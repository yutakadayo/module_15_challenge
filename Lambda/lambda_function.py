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


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": {
                "contentType": "PlainText",
                "content": message
            },
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


"""
Step 3: Enhance the Robo Advisor with an Amazon Lambda Function

In this section, you will create an Amazon Lambda function that will validate the data provided by the user on the Robo Advisor.

1. Start by creating a new Lambda function from scratch and name it `recommendPortfolio`. Select Python 3.7 as runtime.

2. In the Lambda function code editor, continue by deleting the AWS generated default lines of code, then paste in the starter code provided in `lambda_function.py`.

3. Complete the `recommend_portfolio()` function by adding these validation rules:

    * The `age` should be greater than zero and less than 65.
    * The `investment_amount` should be equal to or greater than 5000.

4. Once the intent is fulfilled, the bot should respond with an investment recommendation based on the selected risk level as follows:

    * **none:** "100% bonds (AGG), 0% equities (SPY)"
    * **low:** "60% bonds (AGG), 40% equities (SPY)"
    * **medium:** "40% bonds (AGG), 60% equities (SPY)"
    * **high:** "20% bonds (AGG), 80% equities (SPY)"

> **Hint:** Be creative while coding your solution, you can have all the code on the `recommend_portfolio()` function, or you can split the functionality across different functions, put your Python coding skills in action!

5. Once you finish coding your Lambda function, test it using the sample test events provided for this Challenge.

6. After successfully testing your code, open the Amazon Lex Console and navigate to the `recommendPortfolio` bot configuration, integrate your new Lambda function by selecting it in the “Lambda initialization and validation” and “Fulfillment” sections.

7. Build your bot, and test it with valid and invalid data for the slots.

"""
#----------------------------------------#
def elicit_or_delegate(intent_request):

    slots = get_slots(intent_request)
    
    if slots["age"] == None:
        output_session_attributes = intent_request["sessionAttributes"]
        return delegate(output_session_attributes, get_slots(intent_request))        

    elif (parse_int(slots["age"]) < 1 or parse_int(slots["age"]) >= 65):
        slots["age"] = None
        return elicit_slot(
            intent_request["sessionAttributes"],
            intent_request["currentIntent"]["name"],
            slots,
            "age",
            "Age must be between 1 and 64",
            )
        
    if slots["investmentAmount"] == None:
        output_session_attributes = intent_request["sessionAttributes"]
        return delegate(output_session_attributes, get_slots(intent_request))
        

    elif (parse_int(slots["investmentAmount"]) < 5000):
        slots["investmentAmount"] = None
        return elicit_slot(
            intent_request["sessionAttributes"],
            intent_request["currentIntent"]["name"],
            slots,
            "investmentAmount",
            "You must invest at least $5000",
        )
        
    if slots["riskLevel"] == None:
        output_session_attributes = intent_request["sessionAttributes"]
        return delegate(output_session_attributes, get_slots(intent_request))        
    
    elif (slots["riskLevel"] in ['None', 'none', 'Low', 'low', 'Medium', 'medium', 'High', 'high']) == False:
        slots["riskLevel"] = None
        return elicit_slot(
            intent_request["sessionAttributes"],
            intent_request["currentIntent"]["name"],
            slots,
            "riskLevel",
            "You must select from 'None, Low, Medium, High'",            
        )
    
    output_session_attributes = intent_request["sessionAttributes"]
    return delegate(output_session_attributes, get_slots(intent_request))

def return_message(risk_level):
    if risk_level == ("None" or "none"):
        message = "100% bonds (AGG), 0% equities (SPY)"
    elif risk_level == ("Low" or "low"):
        message = "60% bonds (AGG), 40% equities (SPY)"
    elif risk_level == ("Medium" or "medium"):
        message = "40% bonds (AGG), 60% equities (SPY)"
    elif risk_level == ("High" or "high"):
        message = "20% bonds (AGG), 80% equities (SPY)"
    return message

#----------------------------------------#

### Intents Handlers ###
def recommend_portfolio(intent_request):
    
    intent_request["invocationSource"]
    
    if intent_request["invocationSource"] == "DialogCodeHook":
        result =  elicit_or_delegate(intent_request)
        return result
        
    risk_level = get_slots(intent_request)["riskLevel"]
    name = get_slots(intent_request)["firstName"]

    message = return_message(risk_level)

    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": f"{name}, The best option for your retirement investment is {message}",
        },
    )

### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

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
