from mycroft import MycroftSkill, intent_file_handler


class Todo(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('todo.intent')
    def handle_todo(self, message):
        self.speak_dialog('todo')


def create_skill():
    return Todo()

