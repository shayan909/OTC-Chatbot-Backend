import sqlite3

conn = sqlite3.connect('chatbot.db', check_same_thread=False)


def medicineSearch(inp):
    def convert_to_dict(out):
        out = list(out)
        dict = {'Brand_Name': out[0], 'Drug_Name': out[1], 'Usage': out[2], 'Route': out[3], 'Form': out[4],
                'Dosage': out[5],
                'Retail_Price': out[6], 'Additional_Instruction': out[7], 'Warning': out[8]}
        return dict

    def byDrugName(inp):
        cursor = conn.execute("""SELECT BRAND.name as "BRAND NAME", DRUG.name as "DRUG NAME", ADULT_USAGE.DOSE, ADULT_USAGE.ROUTE, BRAND.FORM, BRAND.MG, BRAND.RETAILPRICE, ADULT_USAGE.INSTRUCTION, DRUG.WARNING
         FROM DRUG 
         INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID 
         INNER JOIN BRAND ON DRUG.DID = BRAND.DID 
         WHERE DRUG.NAME like ?""", (inp,))
        byDrugNameOutput = cursor.fetchall()
        if not byDrugNameOutput:
            return
        byDrugNameOutputDict = [{"title":"Drug(s) Found:"}]
        for tuples in byDrugNameOutput:
            byDrugNameOutputDict.append(convert_to_dict(tuples))
        return byDrugNameOutputDict

    def byBrandName(inp):
        cursor = conn.execute("""SELECT BRAND.name as "BRAND NAME", DRUG.name as "DRUG NAME", ADULT_USAGE.DOSE, ADULT_USAGE.ROUTE, BRAND.FORM, BRAND.MG, BRAND.RETAILPRICE, ADULT_USAGE.INSTRUCTION, DRUG.WARNING 
        FROM DRUG 
        INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID 
        INNER JOIN BRAND ON DRUG.DID = BRAND.DID 
        WHERE BRAND.NAME like ?""", (inp,))
        byBrandNameOutput = cursor.fetchall()
        if not byBrandNameOutput:
            return
        byBrandNameOutputDict = [{"title":"Brand(s) Found:"}]
        for tuples in byBrandNameOutput:
            byBrandNameOutputDict.append(convert_to_dict(tuples))
        return byBrandNameOutputDict

    def byIndication(inp):
        cursor = conn.execute('SELECT IndicationID from INDICATION where DISEASE_NAME like ?', (inp,))
        IndicationID = cursor.fetchone()
        if IndicationID == None:
            return
        cursor = conn.execute("""SELECT BRAND.name as "BRAND NAME", DRUG.name as "DRUG NAME", ADULT_USAGE.DOSE, ADULT_USAGE.ROUTE, BRAND.FORM, BRAND.MG, BRAND.RETAILPRICE, ADULT_USAGE.INSTRUCTION, DRUG.WARNING 
                              FROM DRUG 
                              INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID 
                              INNER JOIN BRAND ON DRUG.DID = BRAND.DID 
                              INNER JOIN INDICATIONS_DRUGS ON DRUG.DID = INDICATIONS_DRUGS.DID 
                              INNER JOIN INDICATION ON INDICATION.IndicationID = INDICATIONS_DRUGS.IndicationID 
                              WHERE INDICATION.IndicationID = ?""", IndicationID)
        byIndicationOutput = cursor.fetchall()
        if not byIndicationOutput:
            return
        byIndicationOutputDict = [{"title":"Medicine(s) given in " + inp + ":"}]
        for tuples in byIndicationOutput:
            byIndicationOutputDict.append(convert_to_dict(tuples))
        return byIndicationOutputDict

    def byInteraction(inp):
        cursor = conn.execute('SELECT InteractionID from INTERACTION where DRUG_NAME like ?', (inp,))
        InteractionID = cursor.fetchone()
        if InteractionID == None:
            return
        cursor = conn.execute("""SELECT BRAND.name as "BRAND NAME", DRUG.name as "DRUG NAME", ADULT_USAGE.DOSE, ADULT_USAGE.ROUTE, BRAND.FORM, BRAND.MG, BRAND.RETAILPRICE, ADULT_USAGE.INSTRUCTION, DRUG.WARNING 
                                      FROM DRUG 
                                      INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID 
                                      INNER JOIN BRAND ON DRUG.DID = BRAND.DID 
                                      INNER JOIN INTERACTIONS_DRUGS ON DRUG.DID = INTERACTIONS_DRUGS.DID 
                                      INNER JOIN INTERACTION ON INTERACTION.InteractionID = INTERACTIONS_DRUGS.InteractionID 
                                      WHERE INTERACTION.InteractionID = ?""", InteractionID)
        byInteractionOutput = cursor.fetchall()
        if not byInteractionOutput:
            return
        byInteractionOutputDict = [{"title":"Medicine(s) that interact with " + inp + ""}]
        for tuples in byInteractionOutput:
            byInteractionOutputDict.append(convert_to_dict(tuples))
        return byInteractionOutputDict

    def byContraindication(inp):
        cursor = conn.execute('SELECT ContraindicationID from CONTRAINDICATION where CONDITION_NAME like ?', (inp,))
        ContraindicationID = cursor.fetchone()
        if ContraindicationID == None:
            return
        cursor = conn.execute("""SELECT BRAND.name as "BRAND NAME", DRUG.name as "DRUG NAME", ADULT_USAGE.DOSE, ADULT_USAGE.ROUTE, BRAND.FORM, BRAND.MG, BRAND.RETAILPRICE, ADULT_USAGE.INSTRUCTION, DRUG.WARNING 
                                      FROM DRUG 
                                      INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID 
                                      INNER JOIN BRAND ON DRUG.DID = BRAND.DID 
                                      INNER JOIN CONTRAINDICATIONS_DRUGS ON DRUG.DID = CONTRAINDICATIONS_DRUGS.DID 
                                      INNER JOIN CONTRAINDICATION ON CONTRAINDICATION.ContraindicationID = CONTRAINDICATIONS_DRUGS.ContraindicationID 
                                      WHERE CONTRAINDICATION.ContraindicationID = ?""", ContraindicationID)
        byContraindicationOutput = cursor.fetchall()
        if not byContraindicationOutput:
            return
        byContraindicationOutputDict = [{"title":"Medicine(s) that Contraindicate " + inp + ":"}]
        for tuples in byContraindicationOutput:
            byContraindicationOutputDict.append(convert_to_dict(tuples))
        return byContraindicationOutputDict
        # return "Drug(s) that Contraindicate "+ inp + ":\n" + str(byContraindicationOutput)

    output = []
    output.append(byDrugName(inp))
    output.append(byBrandName(inp))
    output.append(byIndication(inp))
    output.append(byInteraction(inp))
    output.append(byContraindication(inp))
    output = [i for i in output if i]  # remove none values
    output = [item for sublist in output for item in sublist]
    return output


# Testing
# print(medicineSearch('FEXOFENADINE'))
# print(medicineSearch('cough'))
# print(medicineSearch('allergy'))
# print(medicineSearch('fever'))
# print(medicineSearch('RONDEC-C'))
# print(medicineSearch('IBUPROFEN'))
