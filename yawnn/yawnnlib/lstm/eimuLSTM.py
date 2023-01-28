from yawnnlib.commons import commons, filters
from yawnnlib.structure.sessionData import SessionData

import numpy as np

TIMESTAMP_PREDICATE = lambda tList: sum(map(lambda t: t.type == 'yawn', tList))

# convert a single eimu file to a tuple of (trainX, trainY), (testX, testY)
def eimuToLSTMInput(eimuPath : str, dataFilter : filters.DataFilter, sessionGap : int = 3, fileNum : int = -1, totalFiles : int = -1) -> commons.AnnotatedData:
    print(f"Converting to LSTM input: {fileNum}/{totalFiles}...")
    session = SessionData.fromPath(eimuPath, fileNum, totalFiles)
    data, timestamps = session.getEimuData(dataFilter=dataFilter, sessionGap=sessionGap)
    annotations = np.array(list(map(TIMESTAMP_PREDICATE, timestamps)))
    annotations.resize(annotations.shape[0], 1)
    
    return data, annotations

class EimuLSTMInput(commons.ModelType):
    def __init__(self, dataFilter : filters.DataFilter = filters.NoneFilter(), sessionGap : int = 3):
        self.dataFilter = dataFilter
        self.sessionGap = sessionGap
    
    def fromPath(self, path : str, fileNum : int = -1, totalFiles : int = -1) -> commons.AnnotatedData:
        return eimuToLSTMInput(path, self.dataFilter, self.sessionGap, fileNum, totalFiles)
    
    def getType(self) -> str:
        return 'eimuLSTM'