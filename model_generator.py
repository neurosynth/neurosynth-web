import os
import cPickle
import itertools

PWD = os.path.dirname(os.path.realpath(__file__))
MODELS_DIR = PWD + '/nsweb/models/'

studiesModels = open(MODELS_DIR + 'studies.py','wt')
featuresModels = open(MODELS_DIR + 'features.py','wt')

pickleData = open(PWD + '/pickled.txt','rb')
studies = cPickle.load(pickleData)
pickleData.close()
studiesKeys = studies[0].keys()

featuresTxt = open(PWD + '/abstract_features.txt', 'r')
features = featuresTxt.readline().split()
featuresTxt.close()

asdf = [max(len(str(study)) for study in studies) for line in zip(*foo)]

#
featuresModels.write('Class Features(dbModel):\n')