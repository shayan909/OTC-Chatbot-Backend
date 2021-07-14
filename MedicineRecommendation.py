import sqlite3
conn = sqlite3.connect('chatbot.db', check_same_thread=False)


def recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness):
    # check for indication
    def matchIndication(inputSymptomsOrDiseases):
        IndicationID = []
        DrugIndicationIDs = []
        # Finds Indications matching input in Database
        for i in inputSymptomsOrDiseases:
            cursor = conn.execute('SELECT IndicationID from INDICATION where DISEASE_NAME=?', (i,))
            IndicationID.append(cursor.fetchone())
        IndicationID = [i for i in IndicationID if i]  # Remove None values
        IndicationID = [item for t in IndicationID for item in t]  # Convert to list
        # print("Matched Symptoms/Diseases Indication ID:", IndicationID)
        # Finds Drugs matching Indication in Database
        for i in IndicationID:
            cursor = conn.execute('SELECT DID,IndicationID from INDICATIONS_DRUGS where IndicationID=?', (i,))
            DrugIndicationIDs.append(cursor.fetchall())
        DrugIndicationIDs = [i for i in DrugIndicationIDs if i]  # Remove None values
        DrugIndicationIDs = [item for sublist in DrugIndicationIDs for item in sublist]  # Convert Double List to Single
        return DrugIndicationIDs


    def getDistinctDrugs(DrugIndicationIDs):
        DistinctDrugID = set()
        for i in DrugIndicationIDs:
            DistinctDrugID.add(i[0])
        return DistinctDrugID


    def matchContraindications(DistinctDrugID, CurrentIllness):
        DrugContraindicationID = []
        ContraindicationID = []
        if CurrentIllness is not None:
            CurrentIllness = [i for i in CurrentIllness if i]  #  Remove None Values
        # Finds Contraindications matching input in Database

            for i in CurrentIllness:
                cursor = conn.execute('SELECT ContraindicationID from CONTRAINDICATION where CONDITION_NAME=?', (i,))
                ContraindicationID.append(cursor.fetchone())
            ContraindicationID = [i for i in ContraindicationID if i]  # Remove None Values
            ContraindicationID = [item for t in ContraindicationID for item in t]
            for i in DistinctDrugID:
                for n in ContraindicationID:
                    cursor = conn.execute('SELECT DID,ContraindicationID from CONTRAINDICATIONS_DRUGS where DID=? '
                                      'AND ContraindicationID=?', (i, n))
                    DrugContraindicationID.append(cursor.fetchone())
            DrugContraindicationID = [i for i in DrugContraindicationID if i]  # Remove None Values
            DrugContraindicationID = set(DrugContraindicationID)
        else:
            return
        return DrugContraindicationID


    def matchInteractions(DistinctDrugID, CurrentMedication):
        InteractionID = []
        DrugInteractionID = []
        if CurrentMedication is not None:
            for i in CurrentMedication:
                cursor = conn.execute('SELECT INTERACTIONS_DRUGS.InteractionID '
                                      'from INTERACTIONS_DRUGS '
                                      'INNER JOIN BRAND ON INTERACTIONS_DRUGS.DID = BRAND.DID '
                                      'WHERE BRAND.NAME=?', (i,))
                InteractionID.append(cursor.fetchone())
            InteractionID = [i for i in InteractionID if i]  # Remove None Values
            InteractionID = [item for t in InteractionID for item in t]
        if DistinctDrugID is not None:
            for i in DistinctDrugID:
                for n in InteractionID:
                    cursor = conn.execute('SELECT DID,InteractionID from INTERACTIONS_DRUGS where DID=? '
                                      'AND InteractionID=?', (i, n))
                    DrugInteractionID.append(cursor.fetchone())
            DrugInteractionID = [i for i in DrugInteractionID if i]  # Remove None Values
            DrugInteractionID = set(DrugInteractionID)
        if CurrentMedication or DistinctDrugID is None:
            return
        return DrugInteractionID


    def getPreferredDrugs(DrugIndicationIDs):
        SeparatedDrugsIndications = set()
        DatabaseDrugs = set()
        DrugIndicationIDsSet = set(DrugIndicationIDs)
        for i in DrugIndicationIDs:
            count = 0
            for n in DrugIndicationIDs:
                if i[1] == n[1]:
                    count = count + 1
                    if count > 1:  # Getting sets of Drugs, Indications that have similar indications
                        SeparatedDrugsIndications.add(i)
                        break
        print("SeparatedDrugsIndications: ", SeparatedDrugsIndications)
        cursor = conn.execute('SELECT PreferredDrug,ForSymptom from PREFERRED_DRUG_FOR_SYMPTOM')
        DatabaseDrugs = cursor.fetchall()
        DatabaseDrugs = set(DatabaseDrugs)
        print("Drugs taken from Database: ", DatabaseDrugs)
        PreferredDrugsMatchedFromDatabase = SeparatedDrugsIndications.intersection(DatabaseDrugs)
        print("Preferred Drugs Matched: ", PreferredDrugsMatchedFromDatabase)
        DrugIndicationIDsSet.difference_update(SeparatedDrugsIndications)
        print("DrugIndicationIDsSet: ", DrugIndicationIDsSet)
        DrugIndicationIDs = set(DrugIndicationIDs)
        print("DrugIndicationIDs:", DrugIndicationIDs)
        print("DrugIndicationIDsSet:", DrugIndicationIDsSet)
        # DrugIndicationIDs.difference_update(DrugIndicationIDsSet)
        PreferredDrugsMatchedFromDatabase = DrugIndicationIDs.intersection(DrugIndicationIDsSet)
        print("DrugIndicationIDs: ",DrugIndicationIDs)
        print("DrugIndicationIDsSet: ", DrugIndicationIDsSet)
        PreferredDrugs = DrugIndicationIDs.union(PreferredDrugsMatchedFromDatabase)
        return PreferredDrugs


    def DiscardDrugs(DrugIndicationIDs, matchedDrugContraindicationID, matchedDrugInteractionID):
        DrugsToBeDeleted = []
        if matchedDrugContraindicationID is not None:
            for i in matchedDrugContraindicationID:
                DrugsToBeDeleted.append(i[0])
        if matchedDrugInteractionID is not None:
            for i in matchedDrugInteractionID:
                DrugsToBeDeleted.append(i[0])
        if DrugIndicationIDs is not None:
            for i in DrugIndicationIDs:
                for n in DrugsToBeDeleted:
                    if n in i:
                        DrugIndicationIDs.remove(i)
        if DrugIndicationIDs is None:
            return
        return DrugIndicationIDs


    def getDistinctDrugsIndications(PreferredDrugs):
        DistinctDrugIndicationSet = list(PreferredDrugs)
        if PreferredDrugs is not None:
            for i in DistinctDrugIndicationSet:
                count = 0
                for n in DistinctDrugIndicationSet:
                    if i[1] == n[1]:
                        count = count + 1
                        if count > 1:
                            DistinctDrugIndicationSet.remove(n)
            return DistinctDrugIndicationSet
        else:
            return DistinctDrugIndicationSet


    def getRecommendation(DistinctDrugIndicationSet):
        DistinctDrugIndicationSetDict = {}
        theOnesToskip = set()
        if DistinctDrugIndicationSetDict is not None:
            for i in DistinctDrugIndicationSet:
                for n in DistinctDrugIndicationSet:
                    if (i[0] == n[0]) and (i[0] not in theOnesToskip):
                        DistinctDrugIndicationSetDict.setdefault(i[0], [])
                        DistinctDrugIndicationSetDict[i[0]].append(n[1])
                for x in DistinctDrugIndicationSet:  # Removing all the values that have been worked on
                    if x[0] == i[0]:
                        theOnesToskip.add(i)
            Drugs = []
            Indications = []
            for key in DistinctDrugIndicationSetDict.keys():
                cursor = conn.execute('SELECT BRAND.name, DRUG.name, ADULT_USAGE.DOSE, BRAND.FORM, '
                                      'BRAND.MG '
                                      'FROM DRUG '
                                      'INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID '
                                      'INNER JOIN BRAND ON DRUG.DID = BRAND.DID '
                                      'WHERE DRUG.DID=?', (key,))
                Drugs.append(cursor.fetchone())
                for value in DistinctDrugIndicationSetDict.get(key):
                    cursor = conn.execute('SELECT DISEASE_NAME FROM INDICATION WHERE IndicationID=?', (value,))
                    Indications.append(cursor.fetchone())
            Drugs = [i for i in Drugs if i]  #  Remove None Values
            Drugs = [list(ele) for ele in Drugs]  # Convert List of Tuples to lists of List
            for index, drug in enumerate(Drugs):
                temp = [i for i in drug if i]  # Remove None Values
                temp = ' '.join([str(elem) for elem in temp])  # turn List into string
                Drugs[index] = temp
            if Drugs:
                Drugs = '\nTake these medications:\n' + '\n'.join([str(elem) for elem in Drugs])  # turn List into string
                return Drugs
        else:
            return "I couldn't suggest you any medicine, please Consult a Doctor to solve your " \
                                    "problem."


    def getDrugsSymptomsStatement(DistinctDrugIndicationSet,inputSymptomsOrDiseases):
        ResolvedSymptomsWithID = []
        UnresolvedSymptomsWithID = []
        ResolvedSymptoms = []
        UnresolvedSymptoms = []
        IndicationID = []
        # get IDs of inputSymptomsOrDiseases
        for i in inputSymptomsOrDiseases:
            cursor = conn.execute('SELECT IndicationID from INDICATION where DISEASE_NAME=?', (i,))
            temp = cursor.fetchone()
            # If no match of a symptom was found, store it as an unresolved symptom
            if not temp:
                UnresolvedSymptoms.append((i,))
            else:
                IndicationID.append(temp)
        IndicationID = [i for i in IndicationID if i]  # Removing None Values
        IndicationID = [item for t in IndicationID for item in t]  # Untupling
        # find IDs of resolved and unresolved symptoms by checking which IndicationIDs are in
        # DistinctDrugIndicationSet and which are not
        for t in DistinctDrugIndicationSet:
            if t[1] in IndicationID:
                ResolvedSymptomsWithID.append(t[1])
        if IndicationID:
            UnresolvedSymptomsWithID = [anIndicationID
                                        for anIndicationID in IndicationID
                                        if anIndicationID not in ResolvedSymptomsWithID]
        print(UnresolvedSymptomsWithID)
        if UnresolvedSymptomsWithID:
            for i in UnresolvedSymptomsWithID:
                cursor = conn.execute('SELECT DISEASE_NAME from INDICATION where IndicationID=?', (i,))
                UnresolvedSymptoms.append(cursor.fetchone())
        if UnresolvedSymptoms:
            UnresolvedSymptoms = [i for i in UnresolvedSymptoms if i]  # Removing None Values
            UnresolvedSymptoms = [item for t in UnresolvedSymptoms for item in t]  # Untupling
        if ResolvedSymptomsWithID:
            for i in ResolvedSymptomsWithID:
                cursor = conn.execute('SELECT DISEASE_NAME from INDICATION where IndicationID=?', (i,))
                ResolvedSymptoms.append(cursor.fetchone())
        if ResolvedSymptoms:
            ResolvedSymptoms = [i for i in ResolvedSymptoms if i]  # Removing None Values
            ResolvedSymptoms = [item for t in ResolvedSymptoms for item in t]  # Untupling
        # Removing Duplicates in Unresolved and Resolved Symptoms lists
        UnresolvedSymptoms = list(set(UnresolvedSymptoms))
        ResolvedSymptoms = list(set(ResolvedSymptoms))
        Statement = ""
        if UnresolvedSymptoms:
            Statement = Statement + "\n Unresolved Symptoms:"+" ".join([str(elem) for elem in UnresolvedSymptoms])
        if ResolvedSymptoms:
            Statement = Statement + "\n Your following symptoms should be resolved by taking these " \
                                    "medicines:\n"+" ".join([str(elem) for elem in ResolvedSymptoms])
        return Statement


    def getSubstituteMedicines(FilteredDrugsIndications, DistinctDrugIndicationSet):
        # Subtracting DistinctDrugIndicationSet from FilteredDrugsIndications to get the extra/substitute drugs
        ExtraDrugsIndications = [x for x in FilteredDrugsIndications if x not in DistinctDrugIndicationSet]
        # Store all the drugs in a manner; every already mentioned drug gets related to similar drugs using Dict
        SubstituteDrugs = {}
        if not ExtraDrugsIndications:
            return ""
        if ExtraDrugsIndications:
            for distinctDrug in DistinctDrugIndicationSet:
                cursor = conn.execute('SELECT BRAND.NAME'
                                      ' from DRUG'
                                      ' INNER JOIN BRAND ON DRUG.DID = BRAND.DID where DRUG.DID=?'
                                      ,  (distinctDrug[0],))
                key = ''.join(map(str, cursor.fetchone()))  # Convert Tuple to int
                SubstituteDrugs.update({key: []})
                # Remember to check if there a key has empty list when accessing values later
                # Pair Drugs that have same indications
                for extraDrug in ExtraDrugsIndications:
                    if distinctDrug[1] == extraDrug[1]:
                        cursor = conn.execute('SELECT BRAND.name, DRUG.name, ADULT_USAGE.DOSE, BRAND.FORM, '
                                              'BRAND.MG '
                                              'FROM DRUG '
                                              'INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID '
                                              'INNER JOIN BRAND ON DRUG.DID = BRAND.DID '
                                              'WHERE DRUG.DID=?', (extraDrug[0],))
                        value = ' '.join(map(str, cursor.fetchone()))
                        SubstituteDrugs[key].append(value)
        # print(FilteredDrugs,DistinctDrugs,SubstituteDrugsIndications)
        # Converting into a presentable statement
        SubstituteDrugsStatement = ""
        if SubstituteDrugs:
            for key in SubstituteDrugs.keys():
                if SubstituteDrugs[key] != []:
                    SubstituteDrugsStatement = SubstituteDrugsStatement + "\n If you cannot find "+ key +\
                                               " then you can take:\n"
                    count = 0
                    for substitueDrug in SubstituteDrugs[key]:
                        count = count + 1
                        SubstituteDrugsStatement = SubstituteDrugsStatement + substitueDrug + "\n"
                        if count > 0 and count != len(SubstituteDrugs[key]):
                            SubstituteDrugsStatement = SubstituteDrugsStatement + "OR "
        return SubstituteDrugsStatement


    DrugIndicationIDs = matchIndication(inputSymptomsOrDiseases)
    print("Matched Related Drug ID of Indications with their Indication IDs:", DrugIndicationIDs)

    DistinctDrugID = getDistinctDrugs(DrugIndicationIDs)
    print("\nDistinct Drugs set:", DistinctDrugID)

    matchedDrugContraindicationID = matchContraindications(DistinctDrugID, inputCurrentIllness)
    print("\nMatched Related Drugs ID with their Contraindications IDs:", matchedDrugContraindicationID)

    matchedDrugInteractionID = matchInteractions(DistinctDrugID, inputCurrentMedicine)
    print("\nMatched Related Drugs ID with their InteractionIDs:", matchedDrugInteractionID)

    FilteredDrugsIndications = DiscardDrugs(DrugIndicationIDs, matchedDrugContraindicationID, matchedDrugInteractionID)
    print("\nDrugs and Indications after minusing Contraindications/Interactions:", FilteredDrugsIndications)

    # PreferredDrugs = getPreferredDrugs(FilteredDrugsIndications)
    # print("\nThe Best Drugs after selecting Preferred Drugs:", PreferredDrugs)

    # DistinctDrugIndicationSet = getDistinctDrugsIndications(PreferredDrugs)
    DistinctDrugIndicationSet = getDistinctDrugsIndications(FilteredDrugsIndications)
    print("\nThe Best Drugs after removing extra Drugs for each Symptom:", DistinctDrugIndicationSet)

    Recommendation = getRecommendation(DistinctDrugIndicationSet)
    DrugsSymptomsStatement = getDrugsSymptomsStatement(DistinctDrugIndicationSet,inputSymptomsOrDiseases)
    SubstituteMedicines = getSubstituteMedicines(FilteredDrugsIndications, DistinctDrugIndicationSet)
    print("Recommendation:",Recommendation,"Symptoms Statement:",DrugsSymptomsStatement,"Substitute Medicine:",SubstituteMedicines)
    return Recommendation,DrugsSymptomsStatement,SubstituteMedicines


# Testing
# inputSymptomsOrDiseases = ['hives','Wheezing', 'Redness in one or both eyes', 'Itchiness in one or both eyes',
#                            'Watery Eyes', 'Allergy', 'Asthma', 'phlegm', 'Stuffy Nose']
# inputCurrentMedicine = ['Paracetamol']
# inputCurrentIllness = ['Fever']
# print(recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness))