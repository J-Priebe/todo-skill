from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder

from . import db

class Todo(MycroftSkill):
    '''
    What's on my todo list?
    - lists all active tasks

    What should I do today?
    - suggests a todo item that has been on your list 
      the longest

    Delete/Remove/Archive item # from my to do list

    Mark item # as complete/Complete item # on my todo list

    Give me stats on my todo list
    - # of tasks completed
    - average completion time


    Because ToDos are so generic, and can basically span
    the entirety of language, I suspect Padacious is a better choice
    for intent parsing. Otherwise it will collide with other skills 
    too frequently. We'll try both and see.
    
    '''
    def __init__(self):
        MycroftSkill.__init__(self)     
        db.init_db()

    # @intent_handler(IntentBuilder('suggest')) # Adapt-style
    @intent_handler('list_items.intent') # Padacious-style
    def handle_list_items(self, message):
        items = db.get_active_items()
        if not items:
            self.speak_dialog('empty_list')
            return
    
        self.speak_dialog('list_items')
        # row_number/partitioning requires version 3.x of sqlite3, 
        # so we simply enumerate in code
        for (i, item) in enumerate(items):
            self.speak_dialog(
                'item_description', 
                {
                    'item_number':i+1, 
                    'item_description': item[0]
                }
            )

    @intent_handler('add_item.intent')
    def handle_add_item(self, message):
        item_description = message.data.get('item')
        db.add_item(item_description)
        self.speak_dialog('item_added', {'item_description': item_description})

    @intent_handler('suggest_item.intent') # Padacious
    def handle_suggest_item(self, message):
        suggested_item = db.get_random_active_item()
        if suggested_item is None:
            self.speak_dialog('empty_list')
        else:
            self.speak_dialog(
                'suggest_item', 
                {
                    'item_description': suggested_item
                }
            )

    # delete kind of sounds like complete... just how good is the STT :)              
    @intent_handler('delete_item.intent')
    def handle_delete_item(self, message):
        item_number = message.data.get('item_number')
        item_description = message.data.get('item_description')

        # TODO: confirmation followup conversation
        success = False
        if item_number:
            success = db.close_item_by_row_number(item_number, 'archived')
        elif item_description:
            success = db.close_item_by_description(item_description, 'archived')
        
        if success:
            self.speak_dialog('I deleted that for you')
        else:
            self.speak_dialog('Sorry, I could not do that for you')


    @intent_handler('complete_item.intent')
    def handle_complete_item(self, message):
        item_number = message.data.get('item_number')
        item_description = message.data.get('item_description')

        success = False
        if item_number:
            success = db.close_item_by_row_number(item_number, 'complete')
        elif item_description:
            success = db.close_item_by_description(item_description, 'complete')
        
        if success:
            self.speak_dialog('I marked that one off for you. Nice job!')
        else:
            self.speak_dialog('Sorry, I could not do that for you')

    # TODO

    @intent_handler('report.intent')
    def handle_report(self, message):
        num_completed = db.get_num_completed_items()
        # average time to completion
        # total completed
        # completed per week
        self.speak_dialog('coming soon')


    @intent_handler('help.intent')
    def handle_help(self, message):
        self.speak_dialog('coming soon')
