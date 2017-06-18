import re


class Activity:
    def __init__(self, fill=None, flip=True, **kwargs):
        self.defaults = {
            'action': None,
            'attachments': None,          # Attachment[]
            'attachmentLayout': None,
            'channelData': None,          # ChannelData object
            'channelId': None,
            'conversation': None,         # ConversationAccount object
            'entities': None,             # mentioned entities ie Mention or Place objects
            'fromAccount': None,          # ChannelAccount
            'historyDisclosed': None,
            'id': None,                   # ActivityId - may not be required in response?
            'inputHint': None,            # (acceptingInput, expectingInput, ignoringInput)
            'locale': None,               # <language>-<country>
            'localTimestamp': None,
            'membersAdded': None,         # This will be passed only in conversationUpdates
            'membersRemoved': None,       # This will be passed only in conversationUpdates
            'recipient': None,            # ChannelAccount
            'relatesTo': None,            # ConversationReferece - references a specific point in a convo
            'replyToId': None,            # Used to reply to a thread / specific activity.
            'serviceUrl': None,
            'speak': None,                # Text to be spoken
            'suggestedActions': None,
            'summary': None,              # A summary of information
            'text': None,                 # The text to be sent to a user
            'textFormat': None,           # [markdown, plain, xml]
            'timestamp': None,            # UTC
            'topicName': None,
            'type': None,                 # [contactRelationUpdate, conversationUpdate, deleteUserData, message, ping, typing, endOfConversation]
        }

        # Used to grab the activityId for responses
        self.activityId = None

        # Used in create Conversation - not is not required and will default to from
        self.isGroup = setattr(self, 'isGroup', kwargs.get('isGroup', None))
        self.members = setattr(self, 'members', kwargs.get('members', None))
        self.bot = setattr(self, 'bot', kwargs.get('bot', None))

        for (prop, default) in self.defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

        if fill is not None:
            self.fill(fill)

        # Clean up the conversationId if Microsoft has added messageid to it. (bug?)
        if re.search(';', self.conversation['id']):
            self.conversation['id'] = re.match('[^;]+', self.conversation['id']).group()

        if flip:
            self.flip()

    def flip(self):
        recipient = self.recipient
        self.recipient = self.fromAccount
        self.fromAccount = recipient

    def fill(self, message):
        skip = ['timestamp', 'localTimestamp', 'entities', 'text', 'id', 'membersAdded', 'membersRemoved', 'attachments']
        for key, value in message.items():
            if key == 'from':
                if getattr(self, 'fromAccount') is None:
                    setattr(self, 'fromAccount', value)
            if key == 'type':
                if getattr(self, 'type') is None:
                    setattr(self, 'type', 'message')
            elif key not in skip:
                if getattr(self, key, None) is None:
                    setattr(self, key, value)
            elif key == 'id':
                self.activityId = value

    def to_dict(self):
        json = {}
        for key in self.defaults:
            attribute = getattr(self, key)
            if attribute is not None:
                if key == 'fromAccount':
                    json['from'] = attribute
                else:
                    json[key] = attribute
        return json