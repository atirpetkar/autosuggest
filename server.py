from flask import Flask  # imported the Flask class
from trie import Trie
import json, re, os
import pickle
import sys
import string

'''Although your trie implementation may be simple, it uses recursion and can lead to issues when converting to a persistent data
structure.

My recommendation would be continue raising the recursion limit to see if there is an upper bound for the data you are working
with and the trie implementation you are using.

Other then that, you can try changing your tree implementation to be "less recursive",
if possible, or write an additional implementation that has data persistence built-in
(use pickles and shelves in your implementation). Hope that helps

'''
sys.setrecursionlimit(50000)

app = Flask(__name__)  # we create an instance of this class. The first argument is the name of the application’s module or package

# serializing the input data for faster loads
pickle_filename = 'sample_conversations.pickle'  # pickle file to keep your data in current folder
pickle_data_model = 'data_model.pickle'  # pickle file to keep your data model in current folder

replaceDict = {"'m": ' am', "'ve": ' have', "'ll": " will", "'d": " would", "'s": " is", "'re": " are", "  ": " ",
               "' s": " is"}


def string_preprocess(str):
    '''
        Method to preprocess the data
        cleaning the text by removing numerals,
        replacing the usual short hand used by people in chat found in replaceDict,
        by their relavant full form removing all the other punctuations
    '''
    clean_text = str.strip().lower()
    clean_text = re.sub(r'[0-9]+', ' ', clean_text)  # remove numerals
    clean_text = re.sub(r' +', ' ', clean_text)  # remove multi-spaces
    if len(clean_text) > 1:  # ??? needed???
        for item in replaceDict:
            clean_text = clean_text.replace(item, replaceDict[item])  # replace the terms in the keys of replaceDict
    clean_text = re.sub(r'[^\w\s]', '', clean_text)  # remove all the other punctuations
    return clean_text


def create_data_model(json_data):
    '''create serializable data from json data or if available load it'''
    if not os.path.exists(pickle_filename):
        # print "Pickle file does not exists"
        sample_conversations_data = json.load(open(json_data))
        output_data = open(pickle_filename, "w")
        pickle.dump(sample_conversations_data, output_data)
        output_data.close()
        # print "file created and closed"

    # load the pickle file to get the json data
    input_data = open(pickle_filename, "r")
    # print "pickle file opened successfully"
    sample_conversations_data = pickle.load(input_data)
    # print "data loaded from pickle file"
    input_data.close()

    text_data = []  # get all the sentences in your text data

    table = string.maketrans("", "")  # ???not needed???
    for index, issue in enumerate(sample_conversations_data['Issues'][:]):
        for message in issue['Messages']:
            clean_text = string_preprocess(message['Text'])
            text_data.append(clean_text)

    trie = Trie()  # create trie object to store your data

    # get the data in your trie object
    for sentence in text_data:
        trie.add(sentence)

    # create data model if it does not exist
    if not os.path.exists(pickle_data_model):
        data_model = open(pickle_data_model, "w")
        pickle.dump(trie, data_model)
        print "data model created"
        data_model.close()


create_data_model('sample_conversations.json')

input_data = open('data_model.pickle', "r")
trie = pickle.load(input_data)  # load the already existing trie => use of serializing
input_data.close()


# output should be of the format -> {"Suggestions": ["When did the", "When did the problem begin", "When did the problem"]}

# We then use the route() decorator to tell Flask what URL should trigger our function
@app.route('/query/<prefix>')  # <> is used to pass in the parameter
def query(prefix):
    '''given a prefix, give the list of suggestions'''
    output = '{"Suggestions": ['
    output_suggestions = []
    if '+' in prefix:
        prefix = ' '.join(prefix.split('+'))
        prefix = string_preprocess(prefix)
        output_suggestions = trie.start_with_state(prefix)


    else:  # if the prefix is just one or part of one word, since no '+' in it
        prefix = prefix.lower()
        s = trie.start_with_state(prefix)

        i = 0
        # the improvement over here would have been to have a function which instead of going all the way down the last nodes of the trie
        # a similar function as start_with_state but which does not go to children of a node if a word is found in a path
        while i < len(s):
            if len(s[i].split()) > 1:
                i += 1
                continue  # we want only 1 word suggestions, so remove multi word outputs
            else:
                output_suggestions.append(s[i])
                i += 1

    # the below code is just to have output in proper format
    for element in output_suggestions[:-1]:
        output += '"' + element + '", '

    if len(output_suggestions) >= 1:
        output += '"' + output_suggestions[-1] + '"'
    return output + ']}'


if __name__ == '__main__':
    app.run(debug=True, port=3133)