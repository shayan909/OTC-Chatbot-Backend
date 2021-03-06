import flask
from flask import Flask, render_template, request, jsonify
from chat import medical_history, SpellCheck, medicine, critical_symptoms, showEntity, removeUnderscore, \
     intents
from GetOptions import getOptions,toJSON
from Driver import driver
from MedicineSearch import medicineSearch

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get')
def get_bot_response():
    global count
    global entities
    global symptomSuggestion
    global i
    global medical
    global disease
    global severity
    inp = request.args.get('msg')
    if inp:
        inp = inp.lower()
        if len(inp) > 3 and 'count' not in globals():
            correctInp = SpellCheck(inp)
            entities = showEntity(correctInp)
            optionList = []
            optionList = getOptions(entities)
            optionList = removeUnderscore(optionList)
            res = toJSON(optionList)
            print(res)
            if not entities:
                return "I didn't understand"
            else:
                count = 1
            # call symptom suggestion function
                return jsonify(res)

        elif len(inp) > 3 and count == 1:
            # receive suggested symptoms
            if 'i' not in globals():
                symptomSuggestion = inp.split(",")
                entities.extend(symptomSuggestion)
                print(entities)
                i = 0
            if len(entities) == 0:
                return "entities finished"

            elif i < len(entities) and critical_symptoms(entities[i]):
                msg = critical_symptoms(entities[i])
                i += 1
                count = 2
                res = toJSON(msg)
                return jsonify(res)

            # elif i >= len(entities) and count == 2:
            #     count = 3
            #     return "Mention Underlying illness"

#checking

        elif len(inp) > 3 and count == 2:
            count = 3
            for intent in intents["intents"]:
                # if inp in intent["responses"][3]:
                #     severity = "Some of your symptoms are severe"
                return "Mention Underlying illness"

        elif len(inp) > 3 and count == 3:
            count = 4
            disease = medical_history(inp)
            return "Mention Medicine you're currently taking"

        elif len(inp) > 3 and count == 4:
            medical = medicine(inp)
            # print(severity)
            pred, med = driver(medical, disease, entities)
            return pred+"\n"+med


@app.route('/search')
def search():
    inp = request.args.get('msg')
    return jsonify(medicineSearch(inp))


if __name__ == "__main__":
    app.run(debug=False)


