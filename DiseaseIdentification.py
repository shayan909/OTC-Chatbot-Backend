import pandas as pd
import pickle

def convert_symptoms_to_integer(inputSymptoms):
    diseases = pd.read_pickle("Disease_Dataset_Multilabel.pickle")
    df = pd.DataFrame(diseases)
    df = df.loc[:, :'TARGET']
    df.drop('TARGET', axis='columns')

    # Converting symptoms to integers
    inputSymptoms = [x.lower() for x in inputSymptoms]
    inputSymptomsIntegers = list(df.columns.drop('TARGET'))
    inputSymptomsIntegers = [x.lower() for x in inputSymptomsIntegers]
    for i in range(len(inputSymptomsIntegers)):
        found = False
        for n in range(len(inputSymptoms)):
            if inputSymptoms[n] == inputSymptomsIntegers[i]:
                inputSymptomsIntegers[i] = 1
                found = True
        if not found:
            inputSymptomsIntegers[i] = 0
    return inputSymptomsIntegers


def identifier(inputSymptoms):
    # predict
    inputSymptomsIntegers = convert_symptoms_to_integer(inputSymptoms)
    print("\n")
    print("Input Symptoms", inputSymptomsIntegers)

    # unpickling the classifier
    with open('DiseaseClassifier.pickle', 'rb') as f:
        multi_target_model = pickle.load(f)
        one_hot = pickle.load(f)


    prediction = multi_target_model.predict([inputSymptomsIntegers])
    # transforming prediction to alphabets/actual column names
    NamedPrediction = list(one_hot.inverse_transform(prediction))
    NamedPrediction = [item for sublist in NamedPrediction for item in sublist]  # Convert list of lists into a list
    print(NamedPrediction)
    return NamedPrediction


# # Testing
# inputSymptoms = ['fever','sore_throat','cough']
# print("Entered Symptoms:", inputSymptoms)
# print(identifier(inputSymptoms))
