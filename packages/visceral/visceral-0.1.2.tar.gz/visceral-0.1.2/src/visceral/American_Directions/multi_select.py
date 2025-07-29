import json
from utils import retry_on_json_error


@retry_on_json_error
def multi_select_question_AMI(openai_model, prompt, sync_layer, general_tagged):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears.
            "question": "string",  # Capture the main question text that we will be showing to the user taking the survey. 
            "options": [  # List of options with their associated logic if any, if no options given then leave blank.
                {"add options here": "None"} #this is just an example dont add this
            ],
            "type"="multi_select",
            "keymap": "string"
            
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are processing survey questions and will receive raw question text. Your task is to structure the question into a JSON format"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser. 

                The schema to be used is: {schema}
                Sync_json guides you on capturing question_text (which maps to question in our JSON), logics, and options. Use the provided output as a reference to ensure proper mapping. Your output must align with it, especially for question, options, and logics. sync_json is : {sync_layer}.
                
                Parsing Rules:
                
                1. Question Label:  
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
                - Keep it exactly as written.  

                2. Question Text:  
                - Important - Capture the question text. capture the entire question till the options. donot miss anything

                3. Ask If Logic:  
                - Capture any "ask if" condition that determines when a question should be asked.  
                - Store this in the `ask_logic` field.  

                4. Options:
                - Be smart enough to understand the options from the text.
                - Create a list of dictionaries where each option is a key and value as None
                - example {{"Option text": None}}
                - example {{"Option text (Skip to Q4)": None}}
                - example: {{"Option text Terminate": None}}
                Important: If options have numbers in front of them, use the order the numbers indicate:

                For 04. a 03. b 02. c 01. d, capture the order as (d, c, b, a) (descending).
                For 01. a 02. b 03. c 04. d, capture the order as (a, b, c, d) (ascending).

                Make sure to follow the order as mentioned in the input text if it has the numbering in front of it.
                If the input text says to add some options then please make sure to add them accordingly.
                If the user requests the addition of states, countries, or regions, include them in the options. 
                

                5. Piping Logic

                If a question explicitly references options from a previous question, add a "piping" field. any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
                

                6. Port in response 
                
                If a question text references a previous question and requests to "pipe in" or "port in" results, follow these steps:
                Identify the referenced question.
                Example: If the prompt states:
                "Q3. Why do you like (port in response from Q2)?"
                Replace the placeholder with {{Q2}}, so the question becomes:
                "Why do you like {{Q2}}?"
                Ensure the label (e.g., Q2) matches the format of the referenced question.
                If the reference uses terms like "Recall #2" or similar, replace it with the corresponding question label in the format {{Q2}} (not {{Recall #2}}).
                Use the exact question label (e.g., Q2) as defined in the context.
                Do not include extra text or reference terms; only use the question label.

                7. Please capture the text after 'Ref' if it is given in the input text into a field called 'Ref'. For example, if the input text contains 'Ref:PHONEINTRO', then your output should include 'Ref': 'PHONEINTRO'.

                
                Examples:

                Input:
                ``` Ask Qm if QN==01 \n
                QM. Demo Question (Disqualify if <1) Randomize \n random text
                1. option a asjkdn
                2. option b Skip to Q3
                3. option c Terminate
                Must select one option
                ```
                for the option you dont have to use backticks.it will be dictionary.
                Output:
                {{
                    "ask_logic"="Ask Qm if QN==01",
                    "questionLabel": "QM",
                    "question": "Demo Question (Disqualify if <1) Randomize \n random text",
                    "options": [
                        {{"option a asjkdn": None}},
                        {{"option b Skip to Q3": None}},
                        {{"option c Terminate": None}}
                    ],
                    "type":"multi_select",
                }}
                


                

                Important: The spelling may be incorrect, but you must focus on understanding the user's intent and the logic they are trying to express rather than just the exact words.
                Important: Please provide a valid JSON.
                Do not remove any special markdown characters used in Markdown formatting, and ensure it is correctly formatted.
                If any option requires inserting a list of states or countries, include the full list of states/countries for the respective country.
                If a question specifies a data range, represent it as a list in the JSON using "data_range": [min, max].
                If the question involves a dropdown, set "dropdown": true.
                Ensure every item in the JSON includes a "type" field.
                Important: capture any formatting like < /lbr> and markdown formatting if any, domt delete.
                Also, here are some special mentions by the user: pay special attention and include them as well: {general_tagged}.
                Parse the following survey question according to these rules: {prompt}
                 
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


@retry_on_json_error
def multi_select_logic_AMI(openai_model,input_json,user_logic, input_text, logic_tagged):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures logic and rebuilds the JSON accordingly "},
            {"role": "user", "content": f"""

            You will receive a JSON containing a single-select question constructed from raw text, along with the original raw text itself.  
            Your task is to analyze any logic present and categorize it based on the predefined logic types we support. (Refer to both the raw text and the provided JSON.)  

            Logic Rules:
            - Any termination logic should be marked as: "THANK AND END".  
            - Any skip logic should be marked as: "SKIP TO [qstnLabel]", where qstnLabel represents the question label.  
            - If a question explicitly states to finish if an option is not selected, mark it as "NOT SELECTED".  
            - Example: "Skip to Term if not Q2=2" → "NOT SELECTED" (Only if explicitly mentioned.)  
            - Any option that includes "None of the above" should be marked as: "nota".  
            - Any option that includes "specify" or phrases like "please specify" should be marked as: "other".  
            - Any option that includes "(Prefer not to answer)" should be marked as: "optout".  
            - Any option that includes "Not applicable" should be marked as: "notapplicable".
            - Any optiom that includes "Dont' know" should be marked as "dontknow"  
            - If an option has no associated logic, mark it as None.  
             
            All these logic rules should be associated with the values of the options.
            If the raw text contains logic statements like:
            "Disqualify IF Q2 == '02'" or "Disqualify IF Q2 == '04'", then follow these rules:

            Apply the logic only to the specific option mentioned in the statement.
            Be smart in identifying which options are being referenced and update their values accordingly.
            Example:
            If Q2 has an option 02 and the text states: "Disqualify if Q2 == 02", assign "THANK AND END" to this option.
            You do not need to modify the key, just update the values of the relevant options.
            Similarly, handle "Skip to..." logic the same way—apply it only to the specified option and link it to the corresponding question label (qstnLabel).
            
             
            {{
                "ask_logic": "",
                "questionLabel": "LM",
                "question": "Demo Question?",
                "options": [
                    {{"op1": null}},
                    {{"op2": null}},
                    {{"op3": null}},
                    {{"op4": null}}
                ],
                "type": "single_select"
            }}
             

            Raw Text has : Disqualify IF Q3 == `01` Disqualify IF Q1 == `02` Disqualify IF Q1 == `04`
             
            Logic Applied:
            "Disqualify IF Q3 == '01'" → Ignored (since Q3 ≠ Q1)
            "Disqualify IF Q1 == '02'" → Matches Q1 → op2 → "THANK AND END"
            "Disqualify IF Q1 == '04'" → Matches Q1 → op4 → "THANK AND END"
             
            {{
                "ask_logic": "",
                "questionLabel": "LM",
                "question": "Demo Question?",
                "options": [
                    {{"op1": null}},
                    {{"op2": "THANK AND END"}},
                    {{"op3": null}},
                    {{"op4": "THANK AND END"}}
                ],
                "type": "multi_select"
            }}

             
            
            
            Do Not Introduce Logics on Your Own
            Only add logic if it is explicitly mentioned in the text.
            Handling Special Keywords:
            If the text contains "dropdown", add a new field: {{"dropdown": true}}
            If the text mentions a range, add a new field in the format: {{"data_range": [min, max]}} -> Ensure min and max values are correctly extracted.
            If the text contains the word "randomize", add a new field: {{"randomize": true}} if it refers to general randomization.
            If the text specifies that a set of options should be randomized, create a field called randomize_group as a list containing the option numbers that need to be randomized (always list the option number that should be randomized not the one which shoudl stay together). Represent the randomized options as a list of numbers: [1, 2, ...]. Determine from the text which options should be randomized and which should not. Be smart to understand the natural language user is writing.
            
        
                
            
            Understanding User Logic & Smart Interpretation:
            The user may write logic in different ways, so interpret their intent carefully.
            Use general understanding and the user-defined way of writing logic ({user_logic if user_logic else "User hasnt mentioned any specific logic of his own"} ) to assign values correctly.
            Use your general understanding and if provided usere's way of writing a logic
            Assigning Logics Based on User Input:
            Disqualify or Complete & Disqualify → "THANK AND END"
            Skip to a specific question → "SKIP TO [qstnLabel]"
            Do not change or introduce logic unless explicitly mentioned.
            Handling Option Formatting:
            Example Input:
            {{pizza (loppy)": None}}
            If "loppy" is marked as disqualify, Output:
            {{"pizza": "THANK AND END"}}
  
            
            Handling Non-English Logics:
            If the logic is written in another language,  interpret it correctly.
            Important: capture any formatting like < /lbr> and markdown formatting if any, domt delete.

            
            Do not assume "Did not vote", "None", "exclusive", etc., mean disqualified unless clearly specified.
            Double-check all logic assignments before finalizing the output.
            Make sure to properly tag all special instructions without missing any. These instructions are crucial and must always be categorized correctly. Here are the instructions: {logic_tagged}
            please give me the correct json. 
            The json is :{input_json}      
            The input text is : {input_text}
            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result
