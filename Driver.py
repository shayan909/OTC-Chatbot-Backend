from MedicineRecommendation import recommmendation
from DiseaseIdentification import identifier


def driver(inputCurrentMedicine, inputCurrentIllness, inputSymptoms):
    predictions = []
    inputSymptomsOrDiseases = [] # Symptoms from user + Diseases Identified for Medicine Recommendation
    predictions = identifier(inputSymptoms)
    if predictions:
        inputSymptomsOrDiseases.extend(predictions)
        predictionString = 'You might be experiencing these problems/diseases: ' + ' '.join([str(elem) for elem in predictions])  # turn list into string
    else:
        predictionString = "Sorry I couldn't identify any disease, either there is none or there is something that I don't " \
                           "know about."
    inputSymptomsOrDiseases.extend(inputSymptoms)
    inputSymptomsOrDiseases = list(set(inputSymptomsOrDiseases))  # Remove Duplicates
    Recommendation,DrugsSymptomsStatement,SubstituteMedicines = recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness)
    recommmendationString = Recommendation+"\n"+DrugsSymptomsStatement+"\n"+SubstituteMedicines
    return predictionString, recommmendationString


# # Testing
# inputCurrentMedicine = ['Paracetamol']
# inputCurrentIllness = ['fever']
# inputSymptoms = ['hives','Wheezing', 'Redness in one or both eyes', 'Itchiness in one or both eyes',
#                            'Watery Eyes', 'Allergy', 'Asthma', 'phlegm', 'Stuffy Nose']
# predictionDisease, recommmendationString = driver(inputCurrentMedicine, inputCurrentIllness, inputSymptoms)
# print(predictionDisease, recommmendationString)
