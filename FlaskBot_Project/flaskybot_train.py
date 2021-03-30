# importing chatterbot
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from listQueries import *

# Creating a new instance of the ChatBot class as FlaskyBot

FlaskyBot = ChatBot(name='FlaskyBot',
                    logic_adapters=['chatterbot.logic.MathematicalEvaluation',
                                    'chatterbot.logic.BestMatch']
                    )

#getting all the reply and answers and training it
training_list = ListTrainer(FlaskyBot)
for item in (greet_data, fees, basic_qus, timings , signing_of_data):
    training_list.train(item)

def chat_response(msg):
    return FlaskyBot.get_response(msg)
