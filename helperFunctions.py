# helperFunction.py

from tokens import *
from azure.storage import QueueService, Entity
import json
import urllib2
import datetime


#filled with data from tokens.py
queue_service = QueueService(account_name=myaccount, account_key=mykey)

queueName = 'mlqueue'

def getQueueName():
    '''
    returns string of current working queue
    '''
    return queueName
    
def getAzureQueue():
    '''
    returns QueueService object of current storage account in use
    '''
    return queue_service

def getMessage():
    ''' 
    returns a unicode string object of the contents of the queue 
    TODO: Make get message and getDict more elegant
    '''
    messages = queue_service.get_messages(getQueueName())
    for message in messages:
        messageText = message.message_text
        queue_service.delete_message(getQueueName(), message.message_id, message.pop_receipt)
        return messageText

def clear_queue():
    ''' 
    Clears out all message from the Queue, to be used when we need to start fresh
    or when we need to catch up.  
    '''
    queue = getAzureQueue()
    queue.clear_messages(getQueueName())
	
def getQueueCount():
    ''' 
    returns the current count of messages  in the Queue in str type
    '''
    queue_metadata = queue_service.get_queue_metadata(getQueueName())
    return queue_metadata['x-ms-approximate-messages-count']

def get_state_managed_queue():
    qCount = eval(getQueueCount())
    if qCount <= 0:
        print 'Queue Empty'
        return False
    else:
        state = eval(getMessage())[0]
        print state
        if qCount > 3:
            print 'Queue too large -- clearing'
            clear_queue()
        else:
            print 'Queue just right'
        return state