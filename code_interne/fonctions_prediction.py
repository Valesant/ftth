
import pickle
import xlrd 

#from nltk.probability import FreqDist
import matplotlib.pyplot as plt
import string 
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from wordcloud import WordCloud
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
import random
import itertools
#import treetaggerwrapper
import pandas as pd
import os 
import csv
import io
import numpy as np 

#
#class Train : 
#    def __init__(self, InputFileName, TypeOfClassification='Binar', CleanerSelection=None,): 
#        self.InputFileName=os.path.join(os.getcwd(), InputFileName)
#        self.TypeOfClassification=TypeOfClassification
#        self.CleanerSelection=CleanerSelection
#        
        
def FormatageData(loc,OutputNameFile) : 
    
    pd.read_excel(loc, sheet_name='Mobile Initial').to_csv('temp.csv', index=False)
    data=pd.read_csv('temp.csv')    

    textes=[]
    cas=[]
    Nserviceprecedent=0
    
    ListTelechargement =['Cloud','Internet sur Mobile','Roaming Data','Portail Orange','USSD/Selfcare','TV VOD','Deezer','Sonnerie/logos']
    ListMessComm = ['Mail','SMS','MMS','Roaming SMS','Roaming service SMS']
    ListMobileVoix = ['Voix','Wi-fi','Roaming Voix','MV 888','Couverture Réseau','VVM']
    ListMulti = ['Femto','Flybox (4GHome)','Airbox/domino/Clés','Applewatch/Apple Store']
    ListSAutres = ['Autres','Orange et Moi / my sosh','Epresse/Izneo','Services Protections et Sécurités','Orange Cash','Orange Money']

    for i, row in data.iterrows():
        if row["Thème Libellé"]=='05 Assistance technique / SAV' :
            if int(row["N° Service Rendu"]) == Nserviceprecedent  : 
                Texte = row["Note Description"]
                textes.append(Texte)
            else :
                if Nserviceprecedent != 0:
                    cas.append([Nserviceprecedent,ConclusionLibele,'\n \n'.join(textes)])
                    textes=[]
                
                Nserviceprecedent = int(row["N° Service Rendu"])
                ConclusionLibele = row["Conclusion Libellé"]
                Texte = row["Note Description"]
                textes.append(Texte)
                
    cas.append([Nserviceprecedent,ConclusionLibele,'\n \n'.join(textes)])
    
    
    
    
    for row in cas :
        if row[1] in ListTelechargement:
            row.insert(1,"Acces contenu & telechargement")
        elif row[1] in ListMessComm:
            row.insert(1,"Messaging & communauté")
        elif row[1] in ListMobileVoix:
            row.insert(1,"Mobile Voix")
        elif row[1] in ListMulti:
            row.insert(1,"Multimedia/Lot et connexion")
        elif row[1] in ListSAutres:
            row.insert(1,"Mobile Service autres")
        else : 
            row.insert(1,"Obsolete")
    
    df = pd.DataFrame(cas, \
       columns=('N° Service Rendu','Label','Sous-Label','Texte'))
    os.remove('temp.csv')
    df.to_csv(OutputNameFile,index=False)
    

# =============================================================================
        #COMPARAISON DES DIFFERENTS LEMMATISEURS
#Token + Stop Words +Lemmatisation 
# =============================================================================
#Raw = only WordNet tokenization 
def SentenceProcessingRaw(DataFileName,OutputFileName ):  
    lemma = WordNetLemmatizer() 
        
    data=pd.read_csv(DataFileName)   
       
    newdata=[]   
    for i, row in data.iterrows():   
        # =============================================================================
        text=row["Texte"].lower()
        tok_words=word_tokenize(text, language = 'french')
        # =============================================================================
        data.at[i,"Texte"]=' '.join(tok_words)

    data.to_csv(OutputFileName,index=False)

        
#WordNet
def SentenceProcessingWordNet(DataFileName,OutputFileName ):  
    stop_words=stopwords.words("french")
    stop_words.extend(set(string.punctuation))
    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
    stop_words.extend(stopWadd)
    lemma = WordNetLemmatizer() 
    
    data=pd.read_csv(DataFileName)   
         
    for i, row in data.iterrows():   
        # =============================================================================
        text=row["Texte"].lower()
        tok_words=word_tokenize(text, language = 'french')
        wordsTokSWed = [word for word in tok_words if word not in stop_words]
        allwordsBOWED=[lemma.lemmatize(lemma.lemmatize(lemma.lemmatize(word, pos= 'a'), pos='v'),pos='n') for word in wordsTokSWed]
        # =============================================================================
        data.at[i,"Texte"]=' '.join(allwordsBOWED)

    data.to_csv(OutputFileName,index=False)

#Lefff
def SentenceProcessingLefff(DataFileName,OutputFileName ):  
    
    stop_words=stopwords.words("french")
    stop_words.extend(set(string.punctuation))
    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
    stop_words.extend(stopWadd)
    lemmatizer = FrenchLefffLemmatizer()
        
    data=pd.read_csv(DataFileName)   
    
    for i, row in data.iterrows(): 
    
        # =============================================================================
        text=row["Texte"].lower()
        tok_words=word_tokenize(text, language = 'french')
        wordsTokSWed = [word for word in tok_words if word not in stop_words]
        allwordsBOWED=[lemmatizer.lemmatize(word) for word in wordsTokSWed]
        # =============================================================================
        data.at[i,"Texte"]=' '.join(allwordsBOWED)
            
    data.to_csv(OutputFileName,index=False)

##TreeTaggerW 
#def SentenceProcessingTreeTaggerW(DataFileName,OutputFileName ):  
#    stop_words=stopwords.words("french")
#    stop_words.extend(set(string.punctuation))
#    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
#    stop_words.extend(stopWadd)
#    tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr')
#    
#    data=pd.read_csv(DataFileName)
#    
#    for i, row in data.iterrows(): 
#        # =============================================================================
#        text=row["Texte"].lower()
#        tok_words=word_tokenize(text, language = 'french')
#        wordsTokSWed = [word for word in tok_words if word not in stop_words]
#        tags = tagger.tag_text(wordsTokSWed)
#        lemmaprocess= []
#        for t in tags :  
#            if (t.split('\t')[-1] == '@card@') or (t.split('\t')[-1] =='@ord@'):
#                lemmaprocess.append(t.split('\t')[0])
#            else :
#                lemmaprocess.append(t.split('\t')[-1])
#        # =============================================================================
#        data.at[i,"Texte"]=' '.join(lemmaprocess)
#        
#    data.to_csv(OutputFileName,index=False)
#
#    
##TreeTaggerWO
#def SentenceProcessingTreeTaggerWO(DataFileName,OutputFileName ):     
#    stop_words=stopwords.words("french")
#    stop_words.extend(set(string.punctuation))
#    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
#    stop_words.extend(stopWadd)
#    tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr')
#    
#    data=pd.read_csv(DataFileName)
#    
#    for i, row in data.iterrows(): 
#            # =============================================================================
#            text=row["Texte"].lower()
#            tok_words=word_tokenize(text, language = 'french')
#            wordsTokSWed = [word for word in tok_words if word not in stop_words]
#            tags = tagger.tag_text(wordsTokSWed)
#            lemmaprocess= [t.split('\t')[-1] for t in tags]
#            # =============================================================================
#            data.at[i,"Texte"]=' '.join(lemmaprocess)
#    
#    data.to_csv(OutputFileName,index=False)
## =============================================================================
## ============================================================================= 
#        
#        
#        
        
        
def LabelBinarSeparation(PositiveName,InputFileName,OutputPositiveFileName,OutputNegativeFileName) :
    positiveData=[]
    negativeData=[]
    
    data=pd.read_csv(InputFileName)    

    for i, row in data.iterrows():             
        if row["Label"] == PositiveName :
            positiveData.append([row["Texte"],PositiveName])
        else:
            negativeData.append([row["Texte"],"Autre"])

    dfpos = pd.DataFrame(positiveData, columns=('Texte','Label'))
    dfneg = pd.DataFrame(negativeData, columns=('Texte','Label'))
    
    dfpos.to_csv(OutputPositiveFileName,index=False)
    dfneg.to_csv(OutputNegativeFileName,index=False)


def SousLabelBinarSeparation(PositiveName,InputFileName,OutputPositiveFileName,OutputNegativeFileName) :
    positiveData=[]
    negativeData=[]
    
    data=pd.read_csv(InputFileName)    

    for i, row in data.iterrows():             
        if row["SousLabel"] == PositiveName :
            positiveData.append([row["Texte"],PositiveName])
        else:
            negativeData.append([row["Texte"],"Autre"])

    dfpos = pd.DataFrame(positiveData, columns=('Texte','SousLabel'))
    dfneg = pd.DataFrame(negativeData, columns=('Texte','SousLabel'))
    
    dfpos.to_csv(OutputPositiveFileName,index=False)
    dfneg.to_csv(OutputNegativeFileName,index=False)



def Split (InputPositiveFileName, InputNegativeFileName, OutputTrainFileName,OutputTestFileName,TEST_SIZE):
    pos = pd.read_csv(InputPositiveFileName)    
    neg = pd.read_csv(InputNegativeFileName)    
        
    
    Ptrain, Ptest= train_test_split(pos, test_size = TEST_SIZE)
    Ntrain, Ntest= train_test_split(neg, test_size = TEST_SIZE)
    
    train=pd.concat([Ptrain,Ntrain],ignore_index=True)
    test= pd.concat([Ptest, Ntest],ignore_index=True)
    
    train = train.sample(frac=1).reset_index(drop=True)
    test = test.sample(frac=1).reset_index(drop=True)
    
    #    dftrain = pd.DataFrame(train, columns=('Texte','Label'))
    #    dftest = pd.DataFrame(test, columns=('Texte','Label'))
    
    train.to_csv(OutputTrainFileName,index=False)
    test.to_csv(OutputTestFileName,index=False)
    
    
#def BagsOfWordsDisplay(DataFileName,verbose=True ):  
#    stop_words=stopwords.words("french")
#    stop_words.extend(set(string.punctuation))
#    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
#    stop_words.extend(stopWadd)
#    lemma = WordNetLemmatizer() 
#    
#    
#    with open(DataFileName , "rb") as fp:   # Unpickling
#       data = pickle.load(fp)
#       
#    ListTextes=[]
#    for row in data :
#        for word in row[0] :
#            ListTextes.append(word)
#    
#
#    if verbose == True : 
#        print('=============================================================================')
#        print("                         POSITIVES BOWs ")
#        print('\n\nBOW lemma')
#        # Frequency Distribution Plot
#        filtered_fdist= FreqDist(ListTextes)
#        filtered_fdist.plot(30,cumulative=False)
#        plt.show()
#                
#        print("\n \n \nWordCloud etrange.... : .generate(str(' '.join(allwordsBOWED)))")
#        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(str(' '.join(ListTextes)))
#        plt.figure()
#        plt.imshow(wordcloud, interpolation="bilinear")
#        plt.axis("off")
#        plt.show()
#    
#    Count = [ list(stat) for stat in Counter(allwordsBOWED).most_common() ]
#    return Count 



def W2VectDisplay (DataFileName) : 
    with open(DataFileName , "rb") as fp:   # Unpickling
        data = pickle.load(fp)
       
    vectorizer = CountVectorizer()
    
    prew2vec= []
    finalmatrix= []
    for row in data :
        prew2vec.append(' '.join(row[3]))

    X= vectorizer.fit_transform(prew2vec)
    word2vec= list(X.toarray())
    
    print("Nombre total de colonnes dans le vecteur : ",len(vectorizer.get_feature_names()))     
    finalmatrix.append(vectorizer.get_feature_names())
    
    finalmatrix.append(word2vec)
        
    return finalmatrix
    
    

def make_param_grids(steps, param_grids):

    final_params=[]

    # Itertools.product will do a permutation such that 
    # (pca OR svd) AND (svm OR rf) will become ->
    # (pca, svm) , (pca, rf) , (svd, svm) , (svd, rf)
    for estimator_names in itertools.product(*steps.values()):
        current_grid = {}

        # Step_name and estimator_name should correspond
        # i.e preprocessor must be from pca and select.
        for step_name, estimator_name in zip(steps.keys(), estimator_names):
            for param, value in param_grids.get(estimator_name).items():
                if param == 'object':
                    # Set actual estimator in pipeline
                    current_grid[step_name]=[value]
                else:
                    # Set parameters corresponding to above estimator
                    current_grid[step_name+'__'+param]=value
        #Append this dictionary to final params            
        final_params.append(current_grid)

    return final_params


def SortByIndex (aList, index) : 
    aList.sort(key = lambda aList: aList[index]) 
    
    


#WordNet
def TextProcessingWordNet(text):  
    stop_words=stopwords.words("french")
    stop_words.extend(set(string.punctuation))
    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
    stop_words.extend(stopWadd)
    lemma = WordNetLemmatizer() 
    
    data= text
 
    # =============================================================================
    text=data.lower()
    tok_words=word_tokenize(text, language = 'french')
    wordsTokSWed = [word for word in tok_words if word not in stop_words]
    allwordsBOWED=[lemma.lemmatize(lemma.lemmatize(lemma.lemmatize(word, pos= 'a'), pos='v'),pos='n') for word in wordsTokSWed]
    # =============================================================================
    
    return ' '.join(allwordsBOWED)

def TextProcessingTreeTaggerW(text):  
    stop_words=stopwords.words("french")
    stop_words.extend(set(string.punctuation))
    stopWadd = [' ','', '``','"',"''","--","...","..","¿","¿-","»","==","//","///","«","*****************","**","++","+++","*****","****************","*************************************************************","***************","********************","*//","////","/////","____","***","*******","**********************","*************","*********************","*************"]
    stop_words.extend(stopWadd)
    tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr')

    data= text
  
    # =============================================================================
    text=data.lower()
    tok_words=word_tokenize(text, language = 'french')
    wordsTokSWed = [word for word in tok_words if word not in stop_words]
    tags = tagger.tag_text(wordsTokSWed)
    lemmaprocess= []
    for t in tags :  
        if (t.split('\t')[-1] == '@card@') or (t.split('\t')[-1] =='@ord@'):
            lemmaprocess.append(t.split('\t')[0])
        else :
            lemmaprocess.append(t.split('\t')[-1])
    # =============================================================================
    return   ' '.join(lemmaprocess)   



def CheckDirectory(name): 
    listname = name.split('/')
    directory = '/'.join(listname[:-1])
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    
def detection(texte): 
    #print('Modèle de detection Binaire : \n\tLabel : binaire sur Mobile Voix\n\tSous Label : binaire sur Voix\n\n')
    #print('Detection en cours ...')
    path = 'models/Binaire/'
    filename = 'Mobile Voix.joblib'
    with open(path+filename, "rb") as fp:   # Unpickling
        modelL = pickle.load(fp)
    
    textenettoye = TextProcessingWordNet(texte)
    predicted = modelL['model'].predict([textenettoye])
    print('Label prédit : ', predicted[0])
    
    
    if predicted == 'Mobile Voix' :
        path = 'models/Binaire/'
        filename = 'Voix.joblib'
        with open(path+filename, "rb") as fp:   # Unpickling
            modelSL = pickle.load(fp)
            predictedSL = modelSL['model'].predict([textenettoye])
            print('Sous Label prédit : ', predictedSL[0])
            #        print('\nLes prérequis nécéssaires au sous-label ', predictedSL[0],' sont :')
            #        print('\t- 1 horodatages au format hh:mm:ss dd/mm/yyyy datant de moins de 5 jours')
            #        print("\t- des tests croisés effectués où le mobile n'est pas mis en cause")
        return predicted, predictedSL

    return predicted, ""  
if __name__ == "__main__":
    #print('AAAAAAAAAAAAAAAAAAAAAAAA')
    texte = "blzlerlifgkusrtghstbheerg ersbere geqer ere qe qe gee"
    print(detection(texte))