import numpy as np
from keras.callbacks import Callback, ModelCheckpoint
from keras.layers import LSTM, Dense, Embedding, Input, TimeDistributed
from keras.models import Model
from matplotlib import pyplot as plt


class WriteEpoch(Callback):
    ''' Callback class, can be used to do some callback operations between epochs, batch update, ... etc
    '''

    def on_epoch_end(self, epoch, logs={}):
        f = open('drive/Fashion/epochs.txt', 'w')
        f.write(str(epoch+1))
        f.close()


class DataHolder():
    '''A class for holding training data as well as synonyms words
    '''

    def __init__(self):
        self.questions = list()
        self.answers = list()
        self.notNeededChars = set('ًٌٍَُِّ~ْ' + '؟?,!.')
        self.inWordsIds = dict()
        self.outWordsIds = dict()
        self.synonyms = dict()
        self.reverseOutWordsIds = dict()
        self.maxSentenceLen = 0

    def readSynonyms(self, fileNameList):
        '''Read a list of text files (.txt) containing synonyms.

        The files encoding should be Unicode-16'''

        for fileName in fileNameList:
            with open(fileName, encoding='U16') as f:
                for line in f:
                    tmp = ''
                    for i in line:
                        if i not in self.notNeededChars:
                            tmp += i
                    tmp = tmp.split()
                    self.synonyms.setdefault(tmp[0], tmp[1:])

    def readDataFiles(self, fileNameList):
        '''Read a text file (.txt) containing traingin data

        training data = questions + answers

        The files encoding should be Unicode-16'''

        qCounter, aCounter = 0, 0
        self.inWordsIds['UNK'] = qCounter
        qCounter += 1
        self.outWordsIds['START_'] = aCounter
        aCounter += 1
        self.outWordsIds['_END'] = aCounter
        aCounter += 1

        for fileName in fileNameList:
            with open(fileName, encoding='U16') as f:
                for line in f:
                    tmp = ''
                    for i in line:
                        if i not in self.notNeededChars:
                            tmp += i

                    qst, ans = tmp.split('\t')
                    ans = 'START_ ' + ans + ' _END'

                    qst = qst.split()
                    ans = ans.split()

                    for i in sorted(self.synonyms.keys()):
                        for j in range(len(qst)):
                            if qst[j] in self.synonyms[i]:
                                qst[j] = i

                    qst = sorted(qst)

                    if self.maxSentenceLen < len(qst):
                        self.maxSentenceLen = len(qst)
                    if self.maxSentenceLen < len(ans):
                        self.maxSentenceLen = len(ans)

                    self.questions.append(' '.join(qst))
                    self.answers.append(' '.join(ans))

                    for w in qst:
                        if self.inWordsIds.get(w) == None:
                            self.inWordsIds[w] = qCounter
                            qCounter += 1
                    for w in ans:
                        if self.outWordsIds.get(w) == None:
                            self.outWordsIds[w] = aCounter
                            aCounter += 1

        self.reverseOutWordsIds = dict((i, w)
                                       for w, i in self.outWordsIds.items())


class BotModel():
    ''' A class ressembling a chatbot, built on the concept of seq2seq encoder-decoder model.
    Provides core functionality for building keras seq2seq model as well as inference model that can
    predict 'answers' based on provided 'questions' as strings
    '''

    def __init__(self):
        self.dataHolder = DataHolder()

        # Encoder-decoder matrices
        self.encoderInputs = np.zeros(0)
        self.decoderInputs = np.zeros(0)
        self.decoderOutputs = np.zeros(0)

        # Training model
        self.model = None

        # Reference to some training model layers used by inference model
        self.encInputs = None
        self.decInputs = None
        self.embeddedDecInputs = None
        self.encoderStates = None
        self.decoder = None
        self.decoderDense = None

        # Inference model
        self.encoderModel = None
        self.decoderModel = None

    def readData(self, dataFileList=['rawan.txt', 'rashad.txt'], synonymsFileList=['sims.txt']):
        self.dataHolder.readSynonyms(synonymsFileList)
        self.dataHolder.readDataFiles(dataFileList)

    def fillTrainingMatrices(self):
        qSamples = len(self.dataHolder.questions)
        aSamples = len(self.dataHolder.answers)
        aWordsLen = len(self.dataHolder.outWordsIds)
        maxLen = self.dataHolder.maxSentenceLen

        self.encoderInputs = np.zeros((qSamples, maxLen), dtype='float32')
        self.decoderInputs = np.zeros((aSamples, maxLen), dtype='float32')
        self.decoderOutputs = np.zeros(
            (qSamples, maxLen, aWordsLen), dtype='float32')

        for i, (qst, ans) in enumerate(zip(self.dataHolder.questions, self.dataHolder.answers)):
            for t, word in enumerate(qst.split()):
                self.encoderInputs[i, t] = self.dataHolder.inWordsIds[word]
            for t, word in enumerate(ans.split()):
                self.decoderInputs[i, t] = self.dataHolder.outWordsIds[word]
                if t > 0:
                    self.decoderOutputs[i, t-1,
                                        self.dataHolder.outWordsIds[word]] = 1.

    def createTrainingModels(self, neurons=256, latentDim=256, recDrop=0.5):
        # Encoder
        encoderInputs = Input(shape=(None,))
        embeddedEncInputs = Embedding(
            len(self.dataHolder.inWordsIds), latentDim)(encoderInputs)
        encoder = LSTM(
            neurons, recurrent_dropout=recDrop, return_state=True)
        _, stateH, stateC = encoder(embeddedEncInputs)
        encoderStates = [stateH, stateC]

        # Decoder
        decoderInputs = Input(shape=(None,))
        embeddedDecInputs = Embedding(
            len(self.dataHolder.outWordsIds), latentDim)(decoderInputs)
        decoder = LSTM(neurons, recurrent_dropout=recDrop,
                       return_sequences=True, return_state=True)
        decoderOutputs, _, _ = decoder(
            embeddedDecInputs, initial_state=encoderStates)
        decoderDense = TimeDistributed(
            Dense(len(self.dataHolder.outWordsIds), activation='softmax'))
        decoderOutputs = decoderDense(decoderOutputs)

        # Training model
        model = Model([encoderInputs, decoderInputs], decoderOutputs)
        model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy', metrics=['acc'])

        self.model = model
        self.encInputs = encoderInputs
        self.decInputs = decoderInputs
        self.embeddedDecInputs = embeddedDecInputs
        self.encoderStates = encoderStates
        self.decoder = decoder
        self.decoderDense = decoderDense

    def loadModelWeights(self, wightsFileName):
        try:
            print('Loading weights...')
            self.model.load_weights(wightsFileName)
            print('Weights loaded')
        except Exception as e:
            print('Error:')
            print(str(e))

    def trainModel(self, batchSize=64, epochs=100, valSplit=0.165):
        writeEpoch = WriteEpoch()
        history = self.model.fit([self.encoderInputs, self.decoderInputs],
                                 self.decoderOutputs,
                                 batch_size=batchSize,
                                 epochs=epochs,
                                 verbose=2,
                                 validation_split=valSplit,
                                 callbacks=[writeEpoch,
                                            ModelCheckpoint('drive/Fashion/weights.h5',
                                                            verbose=2,
                                                            save_weights_only=True)])
        plt.plot(history.history['acc'])
        if valSplit > 0.0:
            plt.plot(history.history['val_acc'])
        plt.title('model accuracy')
        plt.ylabel('accuracy')
        plt.xlabel('epoch')
        plt.xticks(np.arange(0, epochs+1, 20.0))
        plt.yticks(np.arange(
            history.history['acc'][0]-0.05, history.history['acc'][-1]+0.05, 0.02))
        plt.legend(['train'], loc='upper left')
        if valSplit > 0.0:
            plt.legend(['val'], loc='upper left')
        plt.savefig('drive/Fashion/acc.png')
        plt.clf()

        plt.plot(history.history['loss'])
        if valSplit > 0.0:
            plt.plot(history.history['val_loss'])
        plt.title('model loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.xticks(np.arange(0, epochs+1, 20.0))
        plt.yticks(np.arange(
            history.history['loss'][0]-0.05, history.history['loss'][-1]+0.05, 0.1))
        plt.legend(['train'], loc='upper left')
        if valSplit > 0.0:
            plt.legend(['val'], loc='upper left')
        plt.savefig('drive/Fashion/loss.png')

        with open('drive/Fashion/acc_loss.txt', 'w') as f:
            f.write(str(history.history['acc']))
            f.write('#')
            f.write(str(history.history['loss']))

    def creatInferenceModels(self):
        # Encoder
        self.encoderModel = Model(self.encInputs, self.encoderStates)

        decoderStateInputH = Input(shape=(None,))
        decoderStateInputC = Input(shape=(None,))
        decoderStatesInputs = [decoderStateInputH, decoderStateInputC]

        decoderOutputs, stateH, stateC = self.decoder(self.embeddedDecInputs,
                                                      initial_state=decoderStatesInputs)
        decoderStates = [stateH, stateC]
        decoderOutputs = self.decoderDense(decoderOutputs)

        # Decoder
        self.decoderModel = Model(
            [self.decInputs] + decoderStatesInputs,
            [decoderOutputs] + decoderStates)

    def predictAnswer(self, question):
        tmp = np.zeros((1, self.dataHolder.maxSentenceLen))

        qst = ''
        for i in question:
            if i not in self.dataHolder.notNeededChars:
                qst += i

        qst = qst.split()
        for i in sorted(self.dataHolder.synonyms.keys()):
            for j in range(len(qst)):
                if qst[j] in self.dataHolder.synonyms[i]:
                    qst[j] = i

        qst = sorted(qst)
        print(qst)

        for i, w in enumerate(qst):
            tmp[0, i] = self.dataHolder.inWordsIds.get(w, 0)

        print(tmp)
        statesValue = self.encoderModel.predict(tmp)

        targetSeq = np.zeros((1, 1))
        targetSeq[0, 0] = self.dataHolder.outWordsIds['START_']

        stopCondition = False
        decodedSentence = ''
        while not stopCondition:
            outputTokens, h, c = self.decoderModel.predict(
                [targetSeq] + statesValue)

            sampledTokenIndex = np.argmax(outputTokens[0, -1, :])
            sampledWord = self.dataHolder.reverseOutWordsIds[sampledTokenIndex]
            decodedSentence += ' ' + sampledWord

            if (sampledWord == '_END'
                    or len(decodedSentence) > 100):
                stopCondition = True

            targetSeq = np.zeros((1, 1))
            targetSeq[0, 0] = sampledTokenIndex

            statesValue = [h, c]

        return decodedSentence

    def evaluateModelPrediction(self):
        ''' 
        '''
        total = len(self.dataHolder.questions)
        matches = 0
        for qst, ans in zip(self.dataHolder.questions, self.dataHolder.answers):
            pred = self.predictAnswer(qst)
            pred = ['START_'] + pred.split()
            tmp1 = len(ans)
            tmp2 = len(pred)
            if tmp1 > tmp2:
                tmp1, tmp2 = tmp2, tmp1

            tmp = 0
            for i in range(tmp1):
                if ans[i] == pred[i]:
                    tmp = 0

            matches += (tmp / tmp2)
        return matches / total
