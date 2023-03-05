from yawnnlib.utils import commons, filters
from yawnnlib.neural.modelInput import ModelInput
from yawnnlib.structure.fourierData import FourierData

import numpy as np

TIMESTAMP_PREDICATE = lambda tList: sum(map(lambda t: t.type == 'yawn', tList))

def eimuToTimeDistributedFftCNNInput(eimuPath : str, dataFilter : filters.DataFilter, chunkSize : float, chunkSeparation : float, fileNum : int = -1, totalFiles : int = -1) -> commons.AnnotatedData:
    """ Applies Fourier methods to a .eimu file to generate a tuple of (data, annotations).

    Parameters
    ----------
    eimuPath : str
        The path to the .eimu file.
    dataFilter : filters.DataFilter
        The filter to apply to the data.
    trainOnTimeAxis : bool, optional
        Whether to include the time axis as training data, by default False
    fileNum : int, optional
        The current file number, by default -1
    totalFiles : int, optional
        The total number of files, by default -1

    Returns
    -------
    commons.AnnotatedData
        A tuple of (data, annotations)
    """
    session = FourierData.fromPath(eimuPath, fileNum=fileNum, totalFiles=totalFiles)
    data, timestamps = session.getSpectrogramData(dataFilter=dataFilter, chunkSize=chunkSize, chunkSeparation=chunkSeparation)
    
    # the number of chunks is variable based on input data, the others depend on constants.
    # we can either train on (times, frequencies, axes) tuples via a CNN, or (frequency, axes) tuples via an LSTM.
    # the former will need significantly more data.
    
    # for this CNN method, we keep the data in the format (chunks, times, frequencies, axes); iterating through will give the tuples.
    
    annotations = np.array(timestamps)
    annotations.resize(annotations.shape[0], 1)
    
    originalLength = data.shape[0]
    
    #todo: make this a parameter
    timeDistributionLength = 5
    
    data = np.resize(data, (originalLength - originalLength%timeDistributionLength, data.shape[1], data.shape[2], data.shape[3]))
    data = np.reshape(data, (originalLength//timeDistributionLength, timeDistributionLength, data.shape[1], data.shape[2], data.shape[3]))
    
    annotations = np.resize(annotations, (originalLength - originalLength%timeDistributionLength, 1))
    annotations = np.reshape(annotations, (originalLength//timeDistributionLength, timeDistributionLength,  1))
    
    annotations = annotations[:, timeDistributionLength//2, :]
    annotations.reshape(annotations.shape[0], 1)

    return data, annotations

class TimeDistributedFftCNNInput(ModelInput):
    def __init__(self, dataFilter : filters.DataFilter = filters.NoneFilter(), chunkSize : float = commons.YAWN_TIME*2, chunkSeparation : float = commons.YAWN_TIME/2) -> None:
        self.dataFilter = dataFilter
        self.chunkSize = chunkSize
        self.chunkSeparation = chunkSeparation
    
    def fromPath(self, path : str, fileNum : int = -1, totalFiles : int = -1) -> commons.AnnotatedData:
        return eimuToTimeDistributedFftCNNInput(path, self.dataFilter, self.chunkSize, self.chunkSeparation, fileNum, totalFiles)
    
    def getType(self) -> str:
        return 'timeDistributedFftCNN'
    