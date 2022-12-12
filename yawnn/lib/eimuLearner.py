import commons
from eimuReader import SessionData

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

trainPercent = 0.8
timestampPredicate = lambda tList: sum(map(lambda t: t.type == 'yawn', tList))

# convert a single eimu file to a tuple of (trainX, trainY), (testX, testY)
def eimuToLSTMInput(eimuPath : str, shuffle=True) -> tuple[tuple, tuple]:
    session = SessionData.fromPath(eimuPath)
    data, timestamps = session.toRaw()
    predicates = np.array(list(map(timestampPredicate, timestamps)))
    predicates.resize(predicates.shape[0], 1)
    
    if shuffle:
        pair = list(zip(data, predicates))
        np.random.shuffle(pair)
        data, predicates = list(map(lambda x: x[0], pair)), list(map(lambda x: x[1], pair))
    
    trainLength = int(len(data) * trainPercent)
    return (data[:trainLength], predicates[:trainLength]), (data[trainLength:], predicates[trainLength:])

# convert a directory of eimu files to a tuple of (trainX, trainY), (testX, testY)
def directoryToLSTMInput(path : str) -> tuple[tuple, tuple]:
    inputs = commons.mapToDirectory(eimuToLSTMInput, path)
    # combine all the inputs. each is a tuple of (trainX, trainY), (testX, testY),
    # and the result is a combination of all the trainX, trainY, testX, testY individually
    return (np.concatenate(list(map(lambda x: x[0][0], inputs))), np.concatenate(list(map(lambda x: x[0][1], inputs)))), (np.concatenate(list(map(lambda x: x[1][0], inputs))), np.concatenate(list(map(lambda x: x[1][1], inputs))))

if __name__ == "__main__":
    model = Sequential()
    model.add(LSTM(units=10, return_sequences=True))
    model.add(Dense(units=1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    (trainX, trainY), (testX, testY) = directoryToLSTMInput("./yawnn/data")
    model.fit(trainX, trainY, epochs=100, batch_size=32)
    model.evaluate(testX, testY)
    