import openai
import pandas as pd
import re

# Mapping of unique number to end_result value
end_results = {'1': 'B3', '0': 'L5', '2': 'N4', '3': 'A4', '4': 'B2', '5': 'BBA1', '6': 'A3', '7': 'N1', '8': 'L7', '9': 'A1', '10': 'N5', '11': 'N10', '12': 'N14', '13': 'N9', '14': 'N13', '15': 'A10', '16': 'B1', '17': 'P2', '18': 'N8', '20': 'N6', '21': 'N7', '22': 'N2', '23': 'N3', '25': 'B8', '30': 'A11'}

openai.api_key = ''

fine_tuned_model = "curie:ft-proriteringar-2023-09-18-09-56-24"

# This creates the prompt taking the clinical info and the doctor's question into account
def create_prompt(question, clinical_info):
    question_ = f"Doktorn ifrågasätter '{question}'"
    prompt_ = f"""Bestäm antalet protokoll som ska utföras på vilken kroppsdel ​​baserat på informationen nedan, \n
          {clinical_info}\n
          {question_}
          \n\n###\n\n
          """
    return prompt_


def extract_number_before_colon(string):
    match = re.search(r"\b(\d+):", string)
    if match:
        return str(match.group(1))
    else:
        return 'nothing'


def finetuned_model_completion(fine_tuned_model, sample_utterance):
    end_res = ''
    res = openai.Completion.create(model=fine_tuned_model, max_tokens=8, prompt=sample_utterance, temperature=0)
    completion = res['choices'][0]['text']

    for key, val in end_results.items():
        if extract_number_before_colon(completion) == key:
            end_res = val
    return end_res


def evaluate_model_on_dataset(model, dataset_path):
    # Load your dataset into a DataFrame
    df = pd.read_csv(dataset_path, delimiter=';')


    correct_predictions = 0
    total_predictions = len(df)

    for index, row in df.iterrows():
        clinical_info = row['Clinical Data']
        question = row['Question']
        expected_result = row['Result']

        # Create the prompt
        prompt_q = create_prompt(question, clinical_info)

        # Predict the end result
        prediction = finetuned_model_completion(model, prompt_q)

        # Print the results for analysis
        print(f"Row {index + 1}:")
        print(f"Question: {question}")
        print(f"Clinical Info: {clinical_info}")
        print(f"Expected Result: {expected_result}")
        print(f"Prediction: {prediction}")
        print("=" * 50)

        if prediction == expected_result:
            correct_predictions += 1

    accuracy = correct_predictions / total_predictions
    print(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    # Provide the path to your dataset CSV file
    dataset_path = 'Testpriosar.csv'
    
    evaluate_model_on_dataset(fine_tuned_model, dataset_path)
