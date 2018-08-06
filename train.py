from argparse import ArgumentParser

from bot import BotModel

parser = ArgumentParser()

# LSTM networks dimentionality or neurons numbers
parser.add_argument('-n', nargs=1, default=['256'])
# Tringing batch size
parser.add_argument('-bs', nargs=1, default=['64'])
# Number of epoches
parser.add_argument('-ep', nargs=1, default=['100'])

args = parser.parse_args()
n = int(args.n[0])
bs = int(args.bs[0])
ep = int(args.ep[0])

bot = BotModel()

bot.readData(['drive/Fashion/rawan.txt', 'drive/Fashion/rashad.txt'],
             ['drive/Fashion/sims.txt'])
bot.fillTrainingMatrices()
bot.createTrainingModels(neurons=n)
bot.loadModelWeights('drive/Fashion/weights.h5')
bot.trainModel(batchSize=bs, epochs=ep)
