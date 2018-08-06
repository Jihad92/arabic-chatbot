import json

from flask import Flask, render_template, request

from bot import BotModel

bot = BotModel()

bot.readData(['rawan.txt', 'rashad.txt'])
bot.createTrainingModels()
bot.loadModelWeights('weights.h5')
bot.creatInferenceModels()

app = Flask(__name__)


@app.route('/')
def output():
    return render_template('index.html')


@app.route('/receiver', methods=['POST'])
def worker():
    data = request.get_json()
    ans = bot.predictAnswer(data)
    ans = ans.replace('_END', '')
    imgs = []
    if '$' in ans:
        ans = ans.split()
        ids = ans[-1].replace('$', '').split('-')
        for i in ids:
            imgs.append(int(i))
        ans = ' '.join(ans[:-1])
    ret = [ans, imgs]
    return json.dumps(ret)


if __name__ == '__main__':
    app.run()
