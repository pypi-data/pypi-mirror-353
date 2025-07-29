import json
import asyncio

async def annotation(openai_model,prompt,keymap, type_of_question):
    
    template="""
    {
    "nodes": [
        {
            "type": "",
            "text": "",
            "data": {  // Include this field only if the type is "logic"
                "subtype": ""  
            }
        }
    ],
    "questionType": "questionType"
}

"""

    parsed_text = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        # model="o1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""
            

                You are a precise survey question annotator. Your task is to tag all parts of a survey question into a JSON structure following a node-based annotation system. 
                The most important rule is to NEVER delete, modify, or rearrange any part of the input text. Each part of the text must be categorized appropriately without loss.
                line breaks should be explicitly captured using {{type: “linebreak”}}. Important: Line breaks in the input will be explicitly marked as <lbr />
                
                We currently support the following logics: randomize, skips, terminate, range, ask_if, piping. (these will be the values of the subtype in the data)
                If you encounter any of these logics, ensure they are captured under the logic type.
                There may be multiple ways to write a logic. For example:
                Variants such as "End," "Route to terminate," and "Terminate" should all be categorized under Terminate.
             
                Additionally: 
                If a user explicitly tags a logic, it will appear in the input like:
                <logic type="disqualify"> demo logic text here </logic>
                In this case, return the node as:
                {{type: "logic", text: "demo logic text here", data: {{subtype: "terminate"}} }}
             
             
                Make sure to add the question type in the JSON under a field called questionType, this question has been catrgorized as : {type_of_question}

                Annotation Guidelines:
                - Use the following node types:
                  - {{type: “label”, text: “S5_Q20”}}: Represents a label for the question. (The label is the unique identifier given before the question starts)
                  - {{type: “question_text”, text: “Demo question main text?”}}:  The main text of the question shown to the survey taker.
                  - {{type: “linebreak”}}: Indicates a line break character in the input. Line breaks in the input will be explicitly marked as <lbr />
                  - {{type: “instructions”, text: “any other random text”}}: Any text we wont be showing it to the person taking the survey. 
                  - {{type: “unknown”, text: “any unclear or ambiguous text”}}: For anything that cannot be categorized. For unclear or ambiguous text that cannot be categorized. This will appear as a red line to the user, indicating that the input is not understood.
                  - {{type: “logic”, text: “Any text that shows a logic”, data: {{subtype: ""}} }}:  Represents logical conditions or rules. Include a data field for subtypes. (The subtype can be  : Randomize, Skips, Terminate, Range, Ask if, Piping. )
                  - {{type: “options”, text: “India”}}: For selectable options in the survey.
                  - {{type: "variable", text:""}} : A user-defined list of variables (e.g., [{keymap}]) will be provided. if blank, ignore this. But If a variable from the list appears in the input text, capture it.
                {{type: "questionType","text":""}} : the questionType for this question is : {type_of_question}
             
                Each question must have exactly one “label” and one “question_text.” The “label” serves as a unique identifier and will not be a complete sentence. Always ensure that the label is short and appears before the question starts. like "Qm, Q8, Qnkl." something like this. 
                Important: A question label must be a unique identifier and cannot consist of more than one word. Examples include "Q1.", "5Kn.", etc. Pay close attention to this requirement.
                A label can be followed by instructions and then the question_text. Be thoughtful and precise when choosing the label.
                The “label” may be followed by an instruction, so exercise judgment when determining this.
                Keep in mind that a label cannot be a complete sentence; it is just a concise identifier that precedes the question text.
                - Do not interpret or deduce meaning. Just tag text based on the input.
                - Explicitly tag any <lbr /> in the input as {{type: "linebreak"}}.
                - Preserve all formatting from the input.
                - backslash tab indicates spacing, so make sure to capture the spacing properly, we should not lose even a space.
                - the incoming text can be in any language so please make sure to capture everything accordingly.

                Example Input:
                S5_Q20 <lbr />
                Demo Question Main text? <lbr />
                Any terminate logical statement  for example<lbr />
                op1, op2, op3<lbr />
                random unclear text that we cant understand.

                Example Output:
                {{
                "nodes": [
                {{
                  {{type: "label", text: "S5_Q20"}},
                  {{type: “linebreak”}}
                  {{type: "question_text", text: "Demo Question Main text?"}},
                  {{type: “linebreak”}}
                  {{type: "logic", text: "Any terminate logical statement  for example", "data" : {{"subtype":"terminate"}}}},
                  {{type: “linebreak”}}
                  {{type: "options", text: "op1"}}
                  {{type: “instructions”, text: “, ”}}
                  {{type: "options", text: "op2}}
                  {{type: “instructions”, text: “, ”}}
                  {{type: "options", text: "op3}}
                  {{type: “linebreak”}}
                  {{type: “unknown”, text: “random unclear text that we cant understand.”}}
                }}
                ],
                "questionType":"single_select"
                }}

                please follow this template to structure your output: {template}
                Most important: 
                1. We should not lose even a single dot.
                2. There will always be 1 question_text and 1 label in the output.
                2. Nothing should be moved, we should capture each and everything in order.
                3. Line breaks will only be there is explicitly there in the text
                4. Preserve all formatting from the input.
                you are not supposed to add anything or modify the text. 
                the input text is : {prompt}
                Please give me a valid json
                

            """
            }
        ]
    ) )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result




