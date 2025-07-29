import json
from utils import retry_on_json_error

@retry_on_json_error
def currency_question(openai_model, prompt):
        schema = """
       {
        "ask_logic": "",  # Capture any "ask_if" logic that specifies when a question should be asked.
        "questionLabel": "string",  # Capture the label exactly as it appears.
        "question": "string",  # Capture the main question text that we will be showing to the user taking the survey.
        "type": "currency",
        "currency": "USD"  # Capture the currency if mentioned. Default is USD. If the symbol is ¥, set it to CNY.
    }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are processing survey questions and will receive raw question text. Your task is to structure the question into a JSON format "},
                {"role": "user", "content": f"""
            
            You are a detailed survey question parser. 

            The schema to be used is: {schema}
            
                
           Parsing Rules:
            
            1. Question Label:  
               - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
               - Keep it exactly as written.  

            2. Question Text:  
               - The question_text in sync_json should be used in the question field of the json. 

            3. Ask If Logic:  
               - Capture any "ask if" condition that determines when a question should be asked.  
               - Store this in the `ask_logic` field.  

            4. Currency Handling:  
               - If a currency is explicitly mentioned (e.g., "in USD"), extract it.  
               - If a currency symbol is present (e.g., "¥"), map it to the correct code (`CNY`).  
               - If no currency is mentioned, default to `"currency": "USD"`.  

            5. Data Ranges: -> if you find any data range in the question, then please pick it up accodingly. Represent it as a list in the JSON using "data_range": [min, max].

            Examples:

            Input:
            ```
            Ask if Q3==0  
            QM. Demo Currecny question (Currency: ¥)  Range : min, max
            ```

            Output:
            ```json
            {{
                "ask_logic": "Ask if Q3==0",
                "questionLabel": "QM",
                "question": "Demo Currecny question",
                "type": "currency",
                "currency": "CNY",
                "data_range" : [min,max]
            }}
            ```

            Input:
            ```
            QM. Demo Currecny question 2 ?
            ```

            Output:
            ```json
            {{
                "ask_logic": "",
                "questionLabel": "QM",
                "question": "Demo Currecny question 2 ?",
                "type": "currency",
                "currency": "USD"
            }}
            ```

            CORE PRINCIPLES:
            - Ensure the JSON is always valid.  
            - Preserve all details exactly as written.  

            Important: please give me a valid json.
            If a question specifies a data range, represent it as a list in the JSON using "data_range": [min, max].
       
            Parse the following survey question according to these rules:
            
            {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


@retry_on_json_error
def currency_logic(openai_model, input_json,user_logic, input_text):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that deals with the logic evaluation."},
            {"role": "user", "content": f"""
            

            You will receive a JSON containing a currency question. 
            Your task is to identify and categorize any logic present, ensuring it falls within our supported logic types:

            1. Termination Logics: If the text explicitly indicates termination (e.g., disqualify, end survey etc), assign it accordingly.  
            2. Skip Logics: If the text explicitly mentions skipping to another question, classify it as "Skip" logic.  
            3. User-Defined Logics: Use the predefined logic structure provided by the user.  

            Important:  
            - The user's way of writing logic is: {user_logic}.  
            - Only use explicitly mentioned words as logic do not infer or introduce new logic.  
            - Pay close attention when identifying and assigning logic categories.  

            If there's no logic that we support. (rememebr there can be mutliple ways of writing any logic, we have to be smart enough to understand the bigger picture.).But if we dont support that logic or there is no logic, just return the json as it is. without making any changes.

            But if you see that there's any logic that we support 1. Termination, 2. Skip 3. User defined logics.  then we should follow the below steps.
            In the question if you observe any logic that we support. Then please add another field saying currency_logic and the key value pair will be the following. 
            For terminating the key should be "Terminating" and the value should be conditon but the condition will only be " [logical operator] [value]" 
            For skip conditions the key would be "SKIP TO [questionLabel of the question]" value would be " [logical operator] [value] " 
            important: The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. follow the convention of writing "==, >=, <=, != " even if the user has just one "=" we should eb using "=="
            Important: Provide the exact logic, but include the questionLabel (retrieved from the JSON) before every operator. Ensure the operators are in uppercase, like OR and AND. By questionLabel, I mean the actual value of the questionLabel field from the JSON, not the literal term questionLabel.
           
            If no supported logic is found (remember, there can be multiple ways of writing the same logic, and we need to smartly understand the bigger picture), then do not make any changes to the JSON. If no logic is supported or there is no logic at all, simply return the JSON as it is.
            However, if any logic that we support is identified (1. Termination, 2. Skip, or 3. User-defined logics), please follow these steps:
            1. Adding Logic to the JSON:
            - If you observe any logic that we support, add a new field called `"currency_logic"` with the following format:
            
                - For Termination Logic:
                - The key should be "Terminating".
                - The value should be the condition, formatted as `"[logical operator] [value]"`.
                
                - For Skip Logic:
                - The key should be `"SKIP TO [questionLabel]"`.
                - The value should be `"[logical operator] [value]"`.
                
            2. Logical Operators:
            - The logical operator should always be written with the questionLabel in front of it, as shown in the example below.
            - Operators such as `==`, `>=`, `<=`, and `!=` must be used, even if the user provided only one `=`.
            - Ensure the operators are in uppercase (e.g., `==`, `>=`, `<=`, `!=`).
            - Do not change the logic; provide the exact logic found in the original input.
            - Do not include any special characters if a number is given for any comparison. (like $, % etc..)


            3. Data Ranges: -> if you find any data range in the question, then please pick it up accodingly. Represent it as a list in the JSON using "data_range": [min, max].

            4. Example of Logic Handling
            - The logic should be formatted as follows:

            
            - For example, if the input JSON is:
                
                {{
                "ask_logic": "Ask if Q3==0",
                "questionLabel": "QM",
                "question": "Demo Question?",
                "type": "currency"
                }}
                
                
            and the raw text says: (Disqualify if QM=='XYZ')

            - The output JSON should look like this:
                
                {{
                "ask_logic": "Ask if Q3==0",
                "questionLabel": "QM",
                "question": "Demo Question?",
                "type": "currency",
                "currency_logic": {{
                    "Terminating": "QM=='XYZ'"
                }}
                }}
               

            4. Additional Notes:
            - Ensure that the `questionLabel` field from the JSON is used as part of the condition (not the literal term `questionLabel`).
            By following this structure, you will ensure consistency and correctness in handling the supported logics.
            example of a logic we dont understand.
            {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"currency",
                    
                 
            }}
            Raw text talks about no logic
            we will return it as it is:
            {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"currency",
                    
                 
            }}
            Important: There can be multiple logics in the currency_logic field, so ensure that you add all the logics you can infer from the provided data.
            Please pay special attention to the instructions for the logics and double-check the logic marking to ensure correctness.
            Your task is to return the valid JSON after applying the logics.
            The input JSON is: {input_json}
            The input raw text is :{input_text} 
            
            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

